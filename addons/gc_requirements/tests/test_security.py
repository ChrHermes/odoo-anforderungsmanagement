from odoo.exceptions import AccessError, UserError
from odoo.tests import tagged

from .common import HelpdeskCase


@tagged("post_install", "-at_install")
class TestSourceSecurity(HelpdeskCase):
    def test_raw_sources_denied_through_all_generic_interfaces(self):
        req = self.linked_requirement()
        raw = self.env["gc.requirement.ticket.source"].sudo().search([("requirement_id", "=", req.id)])
        for user in (self.support, self.limited, self.app_user, self.config_user, self.portal, self.outsider):
            model = self.env["gc.requirement.ticket.source"].with_user(user)
            for operation in (
                lambda: model.browse(raw.ids).read(["description_snapshot"]),
                lambda: model.search_read([], ["description_snapshot"]),
                lambda: model.read_group([], ["description_snapshot:count"], []),
                lambda: model.browse(raw.ids).export_data(["description_snapshot"]),
                lambda: model.search_count([]),
            ):
                with self.subTest(user=user.login), self.assertRaises(UserError), self.cr.savepoint():
                    operation()

    def test_exact_ticket_rule_acl_and_revocation(self):
        req = self.linked_requirement()
        self.assertEqual(len(req.with_user(self.support).get_authorized_sources()), 2)
        limited = req.with_user(self.limited)
        rows = limited.get_authorized_sources()
        self.assertEqual([r["ticket_id"] for r in rows], self.ticket_a.ids)
        self.assertNotIn("SNAPSHOT_SECRET_BETA", str(rows))
        self.assertEqual(req.with_user(self.app_user).get_authorized_sources(), [])
        viewer = self.env["gc.requirement.source.viewer"].with_user(self.limited).create({"requirement_id": req.id})
        self.assertIn("SNAPSHOT_ALPHA", viewer.read(["source_html"])[0]["source_html"])
        self.ticket_rule.domain_force = "[('id', '=', 0)] if user.id == %s else [(1, '=', 1)]" % self.limited.id
        self.assertEqual(limited.get_authorized_sources(), [])
        self.assertNotIn("SNAPSHOT_ALPHA", viewer.read(["source_html"])[0]["source_html"])
        self.assertNotIn("SNAPSHOT_ALPHA", str(viewer.export_data(["source_html"])))
        self.assertNotIn("SNAPSHOT_ALPHA", str(viewer.search_read([("id", "=", viewer.id)], ["source_html"])))
        self.assertFalse(viewer._fields["source_html"].store)

    def test_no_ticket_link_or_snapshot_oracle(self):
        req = self.linked_requirement()
        with self.assertRaises(AccessError), self.cr.savepoint():
            self.make_requirement().with_user(self.limited).link_ticket(self.ticket_b.id)
        self.assertNotIn("source_link_ids", req.fields_get())
        with self.assertRaises(ValueError), self.cr.savepoint():
            self.Requirement.search([("source_link_ids.description_snapshot", "ilike", "SECRET")])
        # Counts are approved, ticket identities and ticket-only customers aren't.
        self.assertEqual(req.with_user(self.app_user).ticket_count, 2)
        self.assertEqual(req.with_user(self.app_user).action_view_tickets()["domain"], [("id", "in", [])])
        self.assertEqual(req.with_user(self.app_user).action_view_customers()["domain"], [("id", "in", [])])

    def test_portal_and_outside_app_denial(self):
        req = self.linked_requirement()
        for user in (self.portal, self.outsider):
            with self.assertRaises(AccessError), self.cr.savepoint():
                req.with_user(user).read(["name", "description"])
            with self.assertRaises(AccessError), self.cr.savepoint():
                req.with_user(user).get_authorized_sources()
            with self.assertRaises(AccessError), self.cr.savepoint():
                self.ticket_a.with_user(user).action_gc_requirement()

    def test_parent_requirement_record_rule_is_checked(self):
        req = self.linked_requirement()
        self.env["ir.rule"].create({"name": "SYNTHETIC requirement restriction", "model_id": self.env["ir.model"]._get_id("gc.requirement"), "domain_force": "[('id', '=', 0)] if user.id == %s else [(1, '=', 1)]" % self.limited.id})
        with self.assertRaises(AccessError), self.cr.savepoint():
            req.with_user(self.limited).get_authorized_sources()
