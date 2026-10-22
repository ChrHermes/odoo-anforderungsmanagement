from odoo import Command, fields
from odoo.exceptions import AccessError, ValidationError
from odoo.tests import Form, tagged

from .common import HelpdeskCase


@tagged("post_install", "-at_install")
class TestMilestones(HelpdeskCase):
    def transition(self, plan, state, **values):
        action = plan.action_change_state()
        wizard = (
            self.env[action["res_model"]]
            .with_user(self.app_user)
            .with_context(**action["context"])
            .create(dict(state=state, **values))
        )
        wizard.action_apply()
        return wizard

    def milestone(self, **values):
        return (
            self.env["gc.requirement.milestone"]
            .with_user(self.app_user)
            .create(
                dict(
                    {"name": "Synthetisches Release", "kind": "release", "product_id": self.node.id}, **values
                )
            )
        )

    def test_create_edit_reference_and_archive(self):
        release = self.milestone()
        self.assertRegex(release.reference, r"^MS-\d{4,}$")
        self.assertNotEqual(release.reference, release.copy().reference)
        with self.assertRaises(ValidationError), self.cr.savepoint():
            release.reference = "MS-0000"
        with self.assertRaises(ValidationError), self.cr.savepoint():
            self.milestone(reference="MS-0000")
        release.write({"version": "2027.1", "planned_start": "2027-01-01", "planned_date": "2027-03-01"})
        for state in ("planned", "active", "cancelled", "draft"):
            release.state = state
        release.action_archive()
        self.assertFalse(release.active)
        release.action_unarchive()
        self.assertTrue(release.active)
        with self.assertRaises(AccessError), self.cr.savepoint():
            release.unlink()
        for values in ({"name": "  "}, {"planned_date": "2026-01-01"}, {"product_id": False}):
            with self.assertRaises(ValidationError), self.cr.savepoint():
                release.write(values)

    def test_product_invariants_both_directions_and_archived(self):
        release = self.milestone()
        req = self.make_requirement(milestone_id=release.id)
        with self.assertRaises(ValidationError), self.cr.savepoint():
            self.make_requirement(product_id=self.operator.id, milestone_id=release.id)
        with self.assertRaises(ValidationError), self.cr.savepoint():
            req.write({"product_id": self.operator.id})
        req.action_archive()
        with self.assertRaises(ValidationError), self.cr.savepoint():
            release.write({"product_id": self.operator.id})
        release.kind = "milestone"
        release.product_id = False
        req.write({"product_id": self.operator.id})
        self.make_requirement(milestone_id=release.id)
        with self.assertRaises(ValidationError), self.cr.savepoint():
            release.write({"kind": "release", "product_id": self.operator.id})

    def test_assignment_switch_remove_and_native_selection(self):
        first, second = self.milestone(), self.milestone()
        req = self.make_requirement(
            state="implemented", implemented_version="REAL-1", implementation_note="Published"
        )
        actual = req.read(["state", "implemented_on", "implemented_version", "implementation_note"])[0]
        req.milestone_id = first
        second.assignment_ids = [Command.set(req.ids)]
        self.assertEqual(req.milestone_id, second)
        self.assertFalse(first.assignment_ids)
        second.assignment_ids = [Command.clear()]
        self.assertFalse(req.milestone_id)
        self.assertEqual(
            req.read(["state", "implemented_on", "implemented_version", "implementation_note"])[0], actual
        )
        self.assertFalse(self.make_requirement().milestone_id)
        # The native inverse performs ordinary requirement writes, including validation.
        wrong = self.make_requirement(product_id=self.operator.id)
        with self.assertRaises(ValidationError), self.cr.savepoint():
            first.assignment_ids = [Command.link(wrong.id)]

    def test_counts_and_completion_confirmation(self):
        release = self.milestone()
        for state in (
            "new",
            "review",
            "evaluated",
            "planned",
            "in_progress",
            "implemented",
            "deferred",
            "rejected",
        ):
            self.make_requirement(milestone_id=release.id, state=state, decision_reason="Synthetic reason")
        archived = self.make_requirement(milestone_id=release.id)
        archived.action_archive()
        self.assertEqual(release.requirement_count, 9)
        self.assertEqual(release.archived_count, 1)
        self.assertEqual(release.open_count, 6)
        self.assertEqual(release.rejected_count, 1)
        self.assertAlmostEqual(release.progress, 100 / 7)
        for context in ({}, {"gc_planning_completion": True}, {"gc_planning_completion": "confirmed"}):
            with self.assertRaises(ValidationError), self.cr.savepoint():
                release.with_context(**context).write({"state": "done"})
        wizard = (
            self.env["gc.requirement.milestone.complete"]
            .with_user(self.app_user)
            .create({"milestone_id": release.id})
        )
        with self.assertRaises(ValidationError), self.cr.savepoint():
            wizard.action_apply()
        before = release.requirement_ids.read(["state", "implemented_on", "implemented_version"])
        wizard.confirmed = True
        wizard.action_apply()
        self.assertEqual(release.state, "done")
        self.assertEqual(release.completed_on, fields.Date.today())
        self.assertEqual(
            release.requirement_ids.read(["state", "implemented_on", "implemented_version"]), before
        )
        self.assertTrue(
            release.message_ids.filtered(lambda msg: "Offene aktive Anforderungen: 6" in str(msg.body))
        )
        release.state = "active"
        self.assertTrue(release.completed_on)

    def test_confirmation_rechecks_current_membership(self):
        release = self.milestone()
        wizard = (
            self.env["gc.requirement.milestone.complete"]
            .with_user(self.app_user)
            .create({"milestone_id": release.id})
        )
        self.assertFalse(wizard.open_count)
        self.make_requirement(milestone_id=release.id)
        with self.assertRaises(ValidationError), self.cr.savepoint():
            wizard.action_apply()
        with self.assertRaises(ValidationError), self.cr.savepoint():
            self.milestone(state="done")
        empty = self.milestone()
        empty.write({"state": "done"})
        self.assertTrue(empty.completed_on)

    def test_plan_changes_never_trigger_ticket_notes_or_actual_release_changes(self):
        release = self.milestone()
        req = self.linked_requirement()
        before = req.read(["state", "implemented_version", "implemented_on"])
        notes = self.env["mail.message"].search_count([("model", "=", "helpdesk.ticket")])
        req.milestone_id = release
        release.write({"state": "planned", "version": "TARGET", "planned_date": "2027-05-01"})
        self.env["gc.requirement.milestone.complete"].with_user(self.app_user).create(
            {
                "milestone_id": release.id,
                "confirmed": True,
            }
        ).action_apply()
        self.assertEqual(req.read(["state", "implemented_version", "implemented_on"]), before)
        self.assertEqual(self.env["mail.message"].search_count([("model", "=", "helpdesk.ticket")]), notes)
        self.assertFalse(req.with_user(self.app_user).get_authorized_sources())
        self.assertEqual(len(req.with_user(self.support).get_authorized_sources()), 2)
        with self.assertRaises(AccessError), self.cr.savepoint():
            self.env["gc.requirement.ticket.source"].with_user(self.app_user).search_read([])
        self.assertFalse(any("snapshot" in name or "ticket" in name for name in release._fields))

    def test_internal_access_chatter_followers_activities(self):
        release = self.milestone(assigned_user_id=self.config_user.id)
        self.assertEqual(
            set(release.message_partner_ids.ids),
            {self.app_user.partner_id.id, self.config_user.partner_id.id},
        )
        for user in (self.portal, self.outsider):
            with self.assertRaises(AccessError), self.cr.savepoint():
                release.with_user(user).read(["name"])
            with self.assertRaises(AccessError), self.cr.savepoint():
                release.with_user(user).write({"name": "Denied"})
            with self.assertRaises(AccessError), self.cr.savepoint():
                release.with_user(user).create({"name": "Denied", "kind": "milestone"})
            with self.assertRaises(AccessError), self.cr.savepoint():
                release.with_user(user).action_complete()
            with self.assertRaises(AccessError), self.cr.savepoint():
                release.with_user(user).action_change_state()
        # Global rule still denies a portal account accidentally assigned the pilot group.
        self.portal.write({"groups_id": [Command.link(self.env.ref("gc_requirements.group_user").id)]})
        self.assertFalse(release.with_user(self.portal).has_access("read"))
        partner = self.company_partner
        for operation in (
            lambda: release.message_subscribe(partner_ids=partner.ids),
            lambda: release.message_post(body="Denied", partner_ids=partner.ids),
            lambda: self.env["mail.followers"]
            .sudo()
            .create({"res_model": release._name, "res_id": release.id, "partner_id": partner.id}),
        ):
            with self.assertRaises(ValidationError), self.cr.savepoint():
                operation()
        mail_before = self.env["mail.mail"].search_count([])
        msg = release.message_post(body="Interne Planungsnotiz")
        self.assertEqual(msg.subtype_id, self.env.ref("mail.mt_note"))
        self.assertEqual(self.env["mail.mail"].search_count([]), mail_before)
        self.assertFalse(release.activity_ids)
        release.activity_schedule("mail.mail_activity_data_todo", user_id=self.app_user.id)
        activity = release.activity_ids
        release.action_archive()
        self.assertEqual(release.activity_ids, activity)
        release.action_unarchive()
        activity.action_feedback(feedback="Done")
        self.assertFalse(release.activity_ids)

    def test_views_filters_native_form_and_tracking(self):
        milestone_model = self.env["gc.requirement.milestone"].with_user(self.app_user)
        with Form(milestone_model) as form:
            form.name = "Form release"
            form.product_id = self.node
        release = form.record
        self.make_requirement(milestone_id=release.id)
        self.assertIn("milestone_id", str(release.action_view_requirements()["domain"]))
        for view_type in ("kanban", "list", "form", "search"):
            self.assertTrue(milestone_model.get_view(view_type=view_type)["arch"])
        search = milestone_model.get_view(view_type="search")["arch"]
        for name in ("planned_period", "without_date", "by_kind", "by_product", "archived"):
            self.assertIn(name, search)
        self.assertEqual(release.product_color_hex, self.node.color_hex)
        self.assertIn("milestone_id", self.env.ref("gc_requirements.action_unplanned_requirements").domain)
        self.assertTrue(self.Requirement._fields["milestone_id"].tracking)

    def test_counters_respect_requirement_record_rules(self):
        release = self.milestone()
        visible = self.make_requirement(milestone_id=release.id)
        self.make_requirement(milestone_id=release.id, state="implemented")
        self.env["ir.rule"].create(
            {
                "name": "Synthetic planning requirement restriction",
                "model_id": self.env["ir.model"]._get_id("gc.requirement"),
                "domain_force": "[('id', '=', %s)] if user.id == %s else [(1, '=', 1)]"
                % (visible.id, self.app_user.id),
            }
        )
        release.invalidate_recordset()
        self.assertEqual(release.requirement_count, 1)
        self.assertEqual(release.open_count, 1)
        self.assertEqual(release.assignment_ids, visible)

    def test_worktimes_url_independent_editable_and_validated(self):
        req = self.make_requirement(development_url="Internal task reference")
        self.assertFalse(req.worktimes_url)
        req.worktimes_url = "https://gitlab.example.invalid/worktimes/42?view=week#day"
        self.assertEqual(req.development_url, "Internal task reference")
        req.worktimes_url = "https://gitlab.example.invalid/worktimes/43"
        for bad in (
            "javascript:alert(1)",
            "//example.invalid/path",
            "not a url",
            "https://example.invalid/space here",
        ):
            with self.assertRaises(ValidationError), self.cr.savepoint():
                req.worktimes_url = bad
        req.worktimes_url = False
        self.assertEqual(req.development_url, "Internal task reference")

    def test_manual_status_for_both_kinds_without_requirements(self):
        for kind in ("release", "milestone"):
            plan = self.milestone(kind=kind)
            self.assertFalse(plan._fields["state"].compute)
            self.assertTrue(plan._fields["state"].store)
            for state in ("planned", "active", "done", "active", "cancelled", "draft", "done"):
                self.transition(plan, state)
                self.assertEqual(plan.state, state)
            self.assertTrue(plan.completed_on)
            self.assertEqual(plan.requirement_count, 0)
            self.assertEqual(plan.progress, 0)
            self.assertEqual(plan.implementation_summary, "Keine Anforderungen zugeordnet")

    def test_requirement_mutations_never_change_planning_status(self):
        for kind in ("release", "milestone"):
            plan = self.milestone(kind=kind)
            self.transition(plan, "active")
            req = self.make_requirement()
            plan.assignment_ids = [Command.link(req.id)]
            for state in ("planned", "in_progress", "implemented", "deferred", "rejected"):
                req.write({"state": state, "decision_reason": "Synthetic decision"})
                self.assertEqual(plan.state, "active")
                self.assertFalse(plan.completed_on)
                if state == "implemented":
                    self.assertEqual(plan.progress, 100)
                    self.assertEqual(plan.implementation_summary, "1 von 1 Anforderungen umgesetzt")
            req.action_archive()
            self.assertEqual(plan.state, "active")
            plan.assignment_ids = [Command.clear()]
            self.assertEqual(plan.state, "active")
            self.assertFalse(plan.completed_on)
            self.assertEqual(plan.progress, 0)

    def test_reopen_preserves_dates_and_completion_history(self):
        for kind in ("release", "milestone"):
            plan = self.milestone(kind=kind)
            req = self.make_requirement(milestone_id=plan.id)
            before = req.read(["state", "implemented_on", "implemented_version"])
            self.transition(plan, "done", confirmed=True, completed_on="2026-10-01")
            self.transition(plan, "active")
            self.assertEqual(str(plan.completed_on), "2026-10-01")
            for values in (
                {"completed_on": False},
                {"completed_on": "2026-10-02"},
                {"state": "planned", "completed_on": False},
            ):
                with self.assertRaises(ValidationError), self.cr.savepoint():
                    plan.write(values)
            self.transition(plan, "done", confirmed=True, completed_on="2026-10-22")
            self.assertEqual(str(plan.completed_on), "2026-10-22")
            notes = " ".join(str(msg.body) for msg in plan.message_ids)
            self.assertIn("2026-10-01", notes)
            self.assertIn("2026-10-22", notes)
            self.assertEqual(req.read(["state", "implemented_on", "implemented_version"]), before)
            self.assertFalse(plan.copy().completed_on)
        with self.assertRaises(ValidationError), self.cr.savepoint():
            self.milestone(completed_on="2026-10-01")

    def test_warning_includes_rejected_archived_and_rechecks_state(self):
        plan = self.milestone()
        self.make_requirement(milestone_id=plan.id, state="rejected", decision_reason="Synthetic")
        self.make_requirement(milestone_id=plan.id).action_archive()
        self.assertEqual(plan.open_count, 0)
        self.assertEqual(plan.not_implemented_count, 2)
        with self.assertRaises(ValidationError), self.cr.savepoint():
            self.transition(plan, "done")
        with self.assertRaises(ValidationError), self.cr.savepoint():
            plan.with_context(gc_planning_completion=True).write({"state": "done"})
        self.transition(plan, "active")  # Warning must never block other target states.
        self.transition(plan, "done", confirmed=True)
        self.assertEqual(plan.state, "done")
        self.assertTrue(
            plan.message_ids.filtered(lambda msg: "Noch nicht umgesetzte Anforderungen: 2" in str(msg.body))
        )

    def test_mixed_batch_completion_retains_previous_date(self):
        old, new = self.milestone(), self.milestone()
        self.transition(old, "done", completed_on="2026-10-01")
        (old | new).write({"state": "done"})
        self.assertEqual(str(old.completed_on), "2026-10-01")
        self.assertEqual(new.completed_on, fields.Date.today())

    def test_status_dialog_and_progress_labels_in_all_views(self):
        plan = self.milestone()
        form = plan.get_view(view_type="form")["arch"]
        self.assertIn('name="action_change_state"', form)
        self.assertIn('widget="statusbar"', form)
        self.assertIn("Umgesetzte Anforderungen", form)
        for view_type in ("kanban", "list", "form"):
            arch = plan.get_view(view_type=view_type)["arch"]
            self.assertIn('name="implementation_summary"', arch)
            self.assertNotIn('string="Fortschritt"', arch)
        action = plan.action_change_state()
        wizard = self.env[action["res_model"]].with_user(self.app_user).with_context(**action["context"])
        with Form(wizard) as dialog:
            self.assertEqual(dialog.state, "draft")
            dialog.state = "planned"
        dialog.record.action_apply()
        self.assertEqual(plan.state, "planned")
        self.assertEqual(
            dict(wizard._fields["state"].selection).keys(), dict(plan._fields["state"].selection).keys()
        )

    def test_status_transitions_have_native_chatter_tracking(self):
        plan = self.milestone()
        # Flush creation before testing native tracking of an existing record.
        plan._track_finalize()
        self.transition(plan, "planned")
        plan._track_finalize()
        tracking = plan.sudo().message_ids.tracking_value_ids.filtered(
            lambda value: value.field_id.name == "state"
        )
        self.assertTrue(tracking)
