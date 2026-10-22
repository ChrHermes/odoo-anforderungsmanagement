from odoo import Command
from odoo.exceptions import AccessError, UserError, ValidationError
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
                lambda model=model: model.browse(raw.ids).read(["description_snapshot"]),
                lambda model=model: model.search_read([], ["description_snapshot"]),
                lambda model=model: model.read_group([], aggregates=["description_snapshot:count"]),
                lambda model=model: model.browse(raw.ids).export_data(["description_snapshot"]),
                lambda model=model: model.search_count([]),
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
        viewer = (
            self.env["gc.requirement.source.viewer"]
            .with_user(self.limited)
            .create({"requirement_id": req.id})
        )
        self.assertIn("SNAPSHOT_ALPHA", viewer.read(["source_html"])[0]["source_html"])
        self.ticket_rule.domain = "[('id', '=', 0)] if user.id == %s else [(1, '=', 1)]" % self.limited.id
        self.assertEqual(limited.get_authorized_sources(), [])
        self.assertNotIn("SNAPSHOT_ALPHA", viewer.read(["source_html"])[0]["source_html"])
        self.assertNotIn("SNAPSHOT_ALPHA", str(viewer.export_data(["source_html"])))
        self.assertNotIn("SNAPSHOT_ALPHA", str(viewer.search_read([("id", "=", viewer.id)], ["source_html"])))
        self.assertFalse(viewer._fields["source_html"].store)

    def test_direct_source_mutations_are_denied(self):
        req = self.linked_requirement()
        source = (
            self.env["gc.requirement.ticket.source"].sudo().search([("requirement_id", "=", req.id)], limit=1)
        )
        normal = source.with_user(self.support)
        with self.assertRaises(AccessError), self.cr.savepoint():
            normal.copy()
        with self.assertRaises(AccessError), self.cr.savepoint():
            normal.write({"ticket_id": self.ticket_b.id})
        with self.assertRaises(UserError), self.cr.savepoint():
            normal.unlink()
        with self.assertRaises(UserError), self.cr.savepoint():
            source.unlink()

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
        self.env["ir.access"].create(
            {
                "name": "SYNTHETIC requirement restriction",
                "operation": "crud",
                "model_id": self.env["ir.model"]._get_id("gc.requirement"),
                "domain": "[('id', '=', 0)] if user.id == %s else [(1, '=', 1)]" % self.limited.id,
            }
        )
        with self.assertRaises(AccessError), self.cr.savepoint():
            req.with_user(self.limited).get_authorized_sources()

        action = self.ticket_a.with_user(self.limited).action_gc_requirements()
        self.assertNotIn(req.id, action["domain"][0][2])

    def test_portal_with_accidental_app_group_and_external_activity(self):
        req = self.make_requirement()
        self.portal.sudo().write({"group_ids": [Command.link(self.env.ref("gc_requirements.group_user").id)]})
        self.assertTrue(self.portal.share)
        with self.assertRaises(AccessError), self.cr.savepoint():
            req.with_user(self.portal).read(["description"])
        with self.assertRaises(AccessError), self.cr.savepoint():
            req.with_user(self.portal).get_authorized_sources()
        with self.assertRaises(ValidationError), self.cr.savepoint():
            req.activity_schedule("mail.mail_activity_data_todo", user_id=self.portal.id)
