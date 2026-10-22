from odoo import api, models, _
from odoo.exceptions import ValidationError


INTERNAL_MODELS = ("gc.requirement", "gc.requirement.milestone")


class RequirementCollaboration(models.Model):
    _inherit = "gc.requirement"

    def _subscribe_responsible(self):
        # Batch identical followers, retaining per-user record-rule checks.
        for user in self.creator_user_id | self.assigned_user_id:
            if not user.active or user.share or not user.has_group("gc_requirements.group_user"):
                continue
            records = self.filtered(lambda r, user=user: user in (r.creator_user_id | r.assigned_user_id))
            readable = records.with_user(user)._filtered_access("read").with_user(self.env.user)
            if readable:
                readable.message_subscribe(partner_ids=user.partner_id.ids)


class RequirementFollower(models.Model):
    _inherit = "mail.followers"

    @api.constrains("res_model", "res_id", "partner_id")
    def _check_requirement_followers(self):
        # Covers direct RPC and One2many commands, not just message_subscribe().
        for follower in self.filtered(lambda f: f.res_model in INTERNAL_MODELS):
            requirement = self.env[follower.res_model].browse(follower.res_id)
            if not requirement.exists() or follower.partner_id.id not in requirement._permitted_partner_ids(
                follower.partner_id.ids
            ):
                raise ValidationError(_("Externe oder nicht berechtigte Follower sind nicht zulässig."))


class RequirementActivity(models.Model):
    _inherit = "mail.activity"

    @api.constrains("res_model_id", "res_id", "user_id")
    def _check_requirement_assignee(self):
        for activity in self.filtered(lambda a: a.res_model in INTERNAL_MODELS):
            requirement = self.env[activity.res_model].browse(activity.res_id)
            if activity.user_id.partner_id.id not in requirement._permitted_partner_ids(
                activity.user_id.partner_id.ids
            ):
                raise ValidationError(
                    _(
                        "Anforderungsaktivitäten dürfen nur berechtigten internen App-Benutzern zugewiesen werden."
                    )
                )

    def unlink(self):
        if self.env.context.get("gc_preserve_requirement_activities"):
            self.check_access("unlink")
            remaining = self.filtered(lambda activity: activity.res_model not in INTERNAL_MODELS)
            return super(RequirementActivity, remaining).unlink()
        return super().unlink()
