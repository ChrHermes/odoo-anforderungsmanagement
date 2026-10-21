from odoo import Command
from odoo.exceptions import AccessError, ValidationError
from odoo.tests import Form, tagged

from .common import HelpdeskCase


@tagged("post_install", "-at_install")
class TestHelpdesk(HelpdeskCase):
    def test_snapshot_capture_many_to_many_and_immutability(self):
        ticket = self.ticket_a.with_user(self.support)
        self.assertEqual(ticket.gc_requirement_count, 0)
        req = self.linked_requirement()
        other = self.make_requirement()
        other.with_user(self.support).link_ticket(self.ticket_a.id)
        self.assertEqual(ticket.gc_requirement_count, 2)
        req.with_user(self.support).link_ticket(self.ticket_a.id)
        self.assertEqual(req.ticket_count, 2)
        source = (
            self.env["gc.requirement.ticket.source"]
            .sudo()
            .search([("requirement_id", "=", req.id), ("ticket_id", "=", self.ticket_a.id)])
        )
        self.assertEqual(len(source), 1)
        original = source.description_snapshot
        self.ticket_a.sudo().description = "<p>CHANGED_AFTER_CAPTURE</p>"
        self.assertEqual(source.description_snapshot, original)
        self.assertEqual(source.captured_by_id, self.support)
        with self.assertRaises(AccessError), self.cr.savepoint():
            source.write({"description_snapshot": "<p>tampered</p>"})
        rows = req.with_user(self.support).get_authorized_sources()
        self.assertIn("SNAPSHOT_ALPHA", rows[0]["description_snapshot"])
        self.assertNotIn("CHANGED_AFTER_CAPTURE", rows[0]["description_snapshot"])

    def test_customer_organizations_and_live_customer_change(self):
        req = self.linked_requirement(
            manual_customer_ids=[Command.link(self.contact_a.id), Command.link(self.company_partner.id)]
        )
        self.assertEqual(req.customer_count, 1)
        other_customer = self.env["res.partner"].create(
            {"name": "Synthetic second customer", "is_company": True}
        )
        req.manual_customer_ids = [Command.link(other_customer.id)]
        self.assertEqual(req.customer_count, 2)
        self.ticket_a.sudo().partner_id = other_customer
        self.ticket_b.sudo().partner_id = other_customer
        self.assertEqual(req.customer_count, 2)  # Manual membership stays independent.
        req.manual_customer_ids = [Command.clear()]
        self.assertEqual(req.customer_count, 1)

    def test_ticket_wizard_requires_editorial_description(self):
        Wizard = (
            self.env["gc.requirement.from.ticket"]
            .with_user(self.support)
            .with_context(default_ticket_id=self.ticket_a.id)
        )
        defaults = Wizard.default_get(["ticket_id", "name", "description", "mode"])
        form = Form(Wizard)
        self.assertEqual(form.name, self.ticket_a.name)
        self.assertFalse(form.description)
        self.assertEqual(defaults["name"], self.ticket_a.name)
        self.assertFalse(defaults.get("description"))
        wizard = Wizard.create(
            {
                "ticket_id": self.ticket_a.id,
                "name": "Synthetischer Titel",
                "mode": "new",
                "request_type": "bug",
                "product_id": self.node.id,
            }
        )
        with self.assertRaises(ValidationError), self.cr.savepoint():
            wizard.action_apply()
        wizard.description = "<p>Vom Mitarbeiter formulierter Inhalt.</p>"
        action = wizard.action_apply()
        req = self.Requirement.browse(action["res_id"])
        self.assertEqual(req.ticket_count, 1)
        self.assertEqual(req.customer_count, 1)
        self.assertNotIn("SNAPSHOT_ALPHA", req.description)
        self.assertNotIn(self.company_partner, req.message_partner_ids)
        wizard.write({"mode": "existing", "requirement_id": req.id})
        wizard.action_apply()
        self.assertEqual(req.ticket_count, 1)

    def test_status_notes_are_internal_once_and_do_not_notify(self):
        req = self.linked_requirement(name="<script>unsafe title</script>")
        stage = self.env["helpdesk.stage"].sudo().create({"name": "Synthetic closed", "fold": True})
        tickets = self.ticket_a | self.ticket_b
        tickets.sudo().write({"stage_id": stage.id, "priority": "3"})
        tickets.sudo().message_subscribe(partner_ids=self.company_partner.ids)
        Message = self.env["mail.message"].sudo()
        baseline = Message.search([("model", "=", "helpdesk.ticket"), ("res_id", "in", tickets.ids)])
        existing_mail = self.env["mail.mail"].sudo().search([])
        existing_notifications = self.env["mail.notification"].sudo().search([])
        for state in ("planned", "implemented", "rejected"):
            vals = {"state": state}
            if state == "rejected":
                vals["decision_reason"] = "<img src=x onerror=alert(1)>"
            req.write(vals)
            req.write(vals)  # no actual state change, no second ticket note
        notes = Message.search([("model", "=", "helpdesk.ticket"), ("res_id", "in", tickets.ids)]) - baseline
        self.assertEqual(len(notes), 6)
        self.assertEqual(notes.subtype_id, self.env.ref("mail.mt_note"))
        self.assertFalse(notes.partner_ids)
        self.assertFalse(self.env["mail.mail"].sudo().search([]) - existing_mail)
        self.assertFalse(self.env["mail.notification"].sudo().search([]) - existing_notifications)
        self.assertNotIn("<script>", "".join(notes.mapped("body")))
        self.assertNotIn("<img src=x", "".join(notes.mapped("body")))
        self.assertEqual(tickets.stage_id, stage)
        self.assertEqual(set(tickets.mapped("priority")), {"3"})
        self.assertFalse(tickets.activity_ids)
        self.assertFalse(req.activity_ids)

    def test_bindings_and_bidirectional_navigation(self):
        req = self.linked_requirement()
        viewer_action = req.with_user(self.limited).action_view_sources()
        viewer = (
            self.env["gc.requirement.source.viewer"].with_user(self.limited).browse(viewer_action["res_id"])
        )
        self.assertIn("SNAPSHOT_ALPHA", viewer.read(["source_html"])[0]["source_html"])
        self.assertNotIn("SNAPSHOT_SECRET_BETA", viewer.read(["source_html"])[0]["source_html"])
        action = self.ticket_a.with_user(self.support).action_gc_requirements()
        self.assertIn(req, self.Requirement.search(action["domain"]))
        action = req.with_user(self.limited).action_view_tickets()
        self.assertEqual(
            self.env["helpdesk.ticket"].with_user(self.limited).search(action["domain"]),
            self.ticket_a.with_user(self.limited),
        )
        for xmlid in ("action_ticket_requirement", "action_ticket_requirements"):
            binding = self.env.ref("gc_requirements." + xmlid)
            self.assertEqual(binding.binding_model_id.model, "helpdesk.ticket")

    def test_native_wizard_views_and_grouped_search(self):
        for model in (
            "gc.requirement.decision",
            "gc.requirement.from.ticket",
            "gc.requirement.source.viewer",
            "gc.requirement.merge",
        ):
            self.env[model].with_user(self.support).get_view(view_type="form")
        req = self.make_requirement()
        self.assertIn(req.id, [item[0] for item in self.Requirement.name_search(req.reference)])
        for field in ("product_id", "request_type", "assigned_user_id", "priority", "state"):
            self.assertTrue(self.Requirement.read_group([("id", "=", req.id)], [field], [field]))
