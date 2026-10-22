from odoo import api, models, _
from odoo.exceptions import AccessError, ValidationError


class RequirementCollaboration(models.Model):
    _inherit = "gc.requirement"

    def _permitted_partner_ids(self, partner_ids):
        """Validate internal app membership and actual access, never partner names."""
        users = (
            self.env["res.users"]
            .sudo()
            .search(
                [
                    ("partner_id", "in", partner_ids),
                    ("share", "=", False),
                    ("active", "=", True),
                    ("all_group_ids", "in", self.env.ref("gc_requirements.group_user").id),
                ]
            )
        )
        return {u.partner_id.id for u in users if self.with_user(u).has_access("read")}

    def _subscribe_responsible(self):
        # Batch identical followers on multi-create, retaining actual per-user
        # record-rule checks before adding them to any requirement.
        for user in self.creator_user_id | self.assigned_user_id:
            if not user.active or user.share or not user.has_group("gc_requirements.group_user"):
                continue
            records = self.filtered(lambda r, user=user: user in (r.creator_user_id | r.assigned_user_id))
            readable = records.with_user(user)._filtered_access("read").with_user(self.env.user)
            if readable:
                readable.message_subscribe(partner_ids=user.partner_id.ids)

    def _message_subscribe(self, partner_ids=None, subtype_ids=None, customer_ids=None):
        if set(partner_ids or []) - self._permitted_partner_ids(partner_ids or []):
            raise ValidationError(_("Nur freigeschaltete interne Mitarbeiter dürfen Anforderungen folgen."))
        return super()._message_subscribe(partner_ids, subtype_ids, customer_ids=customer_ids)

    def message_post(self, **kwargs):
        self._check_app_user()
        self.check_access("write")
        if set(kwargs.get("partner_ids") or []) - self._permitted_partner_ids(
            kwargs.get("partner_ids") or []
        ):
            raise ValidationError(_("Anforderungsnachrichten dürfen nur interne App-Benutzer erreichen."))
        # All requirement chatter is internal, including calls from RPC/composers.
        kwargs.update(subtype_xmlid="mail.mt_note", subtype_id=False, message_type="comment")
        return super().message_post(**kwargs)

    def message_notify(self, **kwargs):
        raise AccessError(_("Bitte verwenden Sie eine interne Notiz an der Anforderung."))

    def _notify_get_recipients(self, message, **kwargs):
        recipients = super()._notify_get_recipients(message, **kwargs)
        allowed = self._permitted_partner_ids([r["id"] for r in recipients])
        return [r for r in recipients if r["id"] in allowed]


class RequirementFollower(models.Model):
    _inherit = "mail.followers"

    @api.constrains("res_model", "res_id", "partner_id")
    def _check_requirement_followers(self):
        # Covers direct RPC and One2many commands, not just message_subscribe().
        for follower in self.filtered(lambda f: f.res_model == "gc.requirement"):
            requirement = self.env["gc.requirement"].browse(follower.res_id)
            if not requirement.exists() or follower.partner_id.id not in requirement._permitted_partner_ids(
                follower.partner_id.ids
            ):
                raise ValidationError(_("Externe oder nicht berechtigte Follower sind nicht zulässig."))


class RequirementActivity(models.Model):
    _inherit = "mail.activity"

    @api.constrains("res_model_id", "res_id", "user_id")
    def _check_requirement_assignee(self):
        for activity in self.filtered(lambda a: a.res_model == "gc.requirement"):
            requirement = self.env["gc.requirement"].browse(activity.res_id)
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
            remaining = self.filtered(lambda activity: activity.res_model != "gc.requirement")
            return super(RequirementActivity, remaining).unlink()
        return super().unlink()
