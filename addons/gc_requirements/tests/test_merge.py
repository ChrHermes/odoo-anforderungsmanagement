from odoo import Command
from odoo.exceptions import AccessError, ValidationError
from odoo.tests import tagged

from .common import HelpdeskCase


@tagged("post_install", "-at_install")
class TestMerge(HelpdeskCase):
    def merge(self, source, target, confirmed=True):
        wizard = (
            self.env["gc.requirement.merge"]
            .with_user(self.app_user)
            .create({"source_id": source.id, "target_id": target.id, "confirmed": confirmed})
        )
        return wizard.action_apply()

    def test_merge_preserves_overlapping_snapshots_history_and_attachments(self):
        source = self.linked_requirement(manual_customer_ids=[Command.link(self.company_partner.id)])
        source_reference = source.reference
        source.message_post(body="HISTORICAL_ORIGINAL_NOTE")
        source.activity_schedule(
            "mail.mail_activity_data_todo", user_id=self.app_user.id, summary="Original activity"
        )
        attachment = (
            self.env["ir.attachment"]
            .with_user(self.app_user)
            .create(
                {
                    "name": "synthetic.txt",
                    "raw": b"synthetic evidence",
                    "res_model": "gc.requirement",
                    "res_id": source.id,
                }
            )
        )
        original_messages = source.message_ids
        original_activity = source.activity_ids
        original_links = (
            self.env["gc.requirement.ticket.source"].sudo().search([("requirement_id", "=", source.id)])
        )
        original_a = original_links.filtered(lambda s: s.ticket_id == self.ticket_a)
        self.ticket_a.sudo().description = "<p>LATER_TARGET_SNAPSHOT</p>"
        target = self.make_requirement()
        target.with_user(self.support).link_ticket(self.ticket_a.id)
        self.merge(source, target)
        self.assertFalse(source.active)
        self.assertEqual(source.merged_into_id, target)
        self.assertEqual(source.reference, source_reference)
        self.assertEqual(target.ticket_count, 2)
        self.assertEqual(target.customer_count, 1)
        self.assertIn(self.company_partner, target.manual_customer_ids)
        self.assertEqual(
            self.env["gc.requirement.ticket.source"].sudo().search([("requirement_id", "=", source.id)]),
            original_links,
        )
        target_links = (
            self.env["gc.requirement.ticket.source"].sudo().search([("requirement_id", "=", target.id)])
        )
        target_a = target_links.filtered(lambda s: s.ticket_id == self.ticket_a)
        self.assertIn("LATER_TARGET_SNAPSHOT", target_a.description_snapshot)
        self.assertIn("SNAPSHOT_ALPHA", original_a.description_snapshot)
        copied_b = target_links.filtered(lambda s: s.ticket_id == self.ticket_b)
        original_b = original_links.filtered(lambda s: s.ticket_id == self.ticket_b)
        self.assertEqual(copied_b.description_snapshot, original_b.description_snapshot)
        self.assertEqual(copied_b.captured_at, original_b.captured_at)
        self.assertEqual(copied_b.captured_by_id, original_b.captured_by_id)
        self.assertEqual(copied_b.origin_requirement_id, source)
        self.assertTrue(original_messages <= source.message_ids)
        self.assertEqual(source.activity_ids, original_activity)
        self.assertEqual(attachment.res_id, source.id)
        attachment.invalidate_recordset()
        self.assertEqual(attachment.with_user(self.app_user).raw.content, b"synthetic evidence")
        self.assertIn(source, target.merged_source_ids)
        self.assertEqual(target.with_user(self.app_user).get_authorized_sources(), [])

    def test_confirmation_self_cycle_direct_and_repeat_denial(self):
        source, target = self.make_requirement(), self.make_requirement()
        with self.assertRaises(ValidationError), self.cr.savepoint():
            self.merge(source, target, confirmed=False)
        with self.assertRaises(ValidationError), self.cr.savepoint():
            self.merge(source, source)
        with self.assertRaises(ValidationError), self.cr.savepoint():
            source.write({"merged_into_id": target.id})
        with self.assertRaises(ValidationError), self.cr.savepoint():
            self.make_requirement(merged_into_id=target.id)
        with self.assertRaises(ValidationError), self.cr.savepoint():
            self.Requirement.with_context(default_merged_into_id=target.id).create(self.values())
        self.merge(source, target)
        with self.assertRaises(ValidationError), self.cr.savepoint():
            self.merge(source, target)
        with self.assertRaises(ValidationError), self.cr.savepoint():
            self.merge(target, source)
        third = self.make_requirement()
        self.merge(target, third)
        self.assertEqual(source.action_open_survivor()["res_id"], third.id)
        source.action_unarchive()
        self.assertTrue(source.active)
        self.assertEqual(source.merged_into_id, target)  # Permanent audit link.

    def test_cross_permission_merge_is_atomic(self):
        source, target = self.linked_requirement(), self.make_requirement()
        self.env["ir.access"].create(
            {
                "name": "SYNTHETIC hidden merge target",
                "operation": "crud",
                "model_id": self.env["ir.model"]._get_id("gc.requirement"),
                "domain": "[('id', '!=', %s)] if user.id == %s else [(1, '=', 1)]"
                % (target.id, self.app_user.id),
            }
        )
        with self.assertRaises(AccessError), self.cr.savepoint():
            self.merge(source, target)
        self.assertTrue(source.active)
        self.assertFalse(source.merged_into_id)
        self.assertEqual(target.with_user(self.support).ticket_count, 0)

    def test_similarity_is_bounded_and_product_scoped(self):
        expected = self.make_requirement(name="IEC104 Verbindung verbessern")
        other_product = self.make_requirement(
            name="IEC104 Verbindung verbessern", product_id=self.operator.id
        )
        draft = self.Requirement.new(self.values(name="IEC104 Verbindung"))
        self.assertIn(expected, draft.similar_requirement_ids._origin)
        self.assertNotIn(other_product, draft.similar_requirement_ids._origin)
        self.assertLessEqual(len(draft.similar_requirement_ids), 5)
