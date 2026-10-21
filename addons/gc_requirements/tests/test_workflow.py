from odoo import Command
from odoo.exceptions import ValidationError
from odoo.tests import tagged

from .common import RequirementCase


@tagged("post_install", "-at_install")
class TestWorkflow(RequirementCase):
    def test_flexible_states_and_fresh_reasons(self):
        req = self.make_requirement()
        for state in ("review", "evaluated", "planned", "in_progress", "implemented", "new"):
            req.state = state
        self.assertTrue(req.implemented_on)
        for state in ("deferred", "rejected"):
            with self.assertRaises(ValidationError), self.cr.savepoint():
                req.write({"state": state})
            req.write({"state": state, "decision_reason": "Synthetische Begründung " + state})
            req.state = "review"
            with self.assertRaises(ValidationError), self.cr.savepoint():
                req.write({"state": state})
        req._track_finalize()
        reasons = req.message_ids.filtered(lambda m: "Synthetische Begründung" in str(m.body))
        self.assertGreaterEqual(len(reasons), 2)
        for state in ("deferred", "rejected"):
            with self.assertRaises(ValidationError), self.cr.savepoint():
                self.make_requirement(state=state)

    def test_decision_wizard(self):
        req = self.make_requirement()
        wizard = self.env["gc.requirement.decision"].with_user(self.app_user).create({"requirement_id": req.id, "state": "deferred", "reason": "Später prüfen"})
        wizard.action_apply()
        self.assertEqual(req.state, "deferred")
        wizard.write({"state": "implemented", "implemented_version": "2.0"})
        wizard.action_apply()
        self.assertTrue(req.implemented_on)
        self.assertEqual(req.implemented_version, "2.0")

    def test_internal_followers_and_manual_activities(self):
        req = self.make_requirement(assigned_user_id=self.config_user.id)
        self.assertEqual(set(req.message_partner_ids.ids), {self.app_user.partner_id.id, self.config_user.partner_id.id})
        customer = self.env["res.partner"].create({"name": "Synthetischer Kunde", "email": "customer@example.invalid"})
        with self.assertRaises(ValidationError), self.cr.savepoint():
            req.message_subscribe(partner_ids=customer.ids)
        with self.assertRaises(ValidationError), self.cr.savepoint():
            self.env["mail.followers"].sudo().create({"res_model": req._name, "res_id": req.id, "partner_id": customer.id})
        with self.assertRaises(ValidationError), self.cr.savepoint():
            req.message_post(body="Test", partner_ids=customer.ids)
        note = req.message_post(body="Interne Notiz")
        self.assertEqual(note.subtype_id, self.env.ref("mail.mt_note"))
        self.assertFalse(req.activity_ids)
        req.activity_schedule("mail.mail_activity_data_todo", user_id=self.app_user.id, summary="Manuelle Prüfung")
        self.assertEqual(len(req.activity_ids), 1)
        self.assertEqual(req.activity_ids.user_id, self.app_user)
