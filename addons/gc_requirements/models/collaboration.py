from odoo import api, models, _
from odoo.exceptions import AccessError, ValidationError


class RequirementCollaboration(models.Model):
    _inherit = "gc.requirement"

    def _permitted_partner_ids(self, partner_ids):
        """Validate internal app membership and actual access, never partner names."""
        users = self.env["res.users"].sudo().search([
            ("partner_id", "in", partner_ids), ("share", "=", False), ("active", "=", True),
            ("groups_id", "in", self.env.ref("gc_requirements.group_user").id),
        ])
        return {u.partner_id.id for u in users if self.with_user(u).has_access("read")}

    def _subscribe_responsible(self):
        for record in self:
            users = record.creator_user_id | record.assigned_user_id
            partners = record._permitted_partner_ids(users.partner_id.ids)
            if partners:
                record.message_subscribe(partner_ids=list(partners))

    def _message_subscribe(self, partner_ids=None, subtype_ids=None, customer_ids=None):
        if set(partner_ids or []) - self._permitted_partner_ids(partner_ids or []):
            raise ValidationError(_("Nur freigeschaltete interne Mitarbeiter dürfen Anforderungen folgen."))
        return super()._message_subscribe(partner_ids, subtype_ids, customer_ids=customer_ids)

    def message_post(self, **kwargs):
        self._check_app_user()
        self.check_access("write")
        if set(kwargs.get("partner_ids") or []) - self._permitted_partner_ids(kwargs.get("partner_ids") or []):
            raise ValidationError(_("Anforderungsnachrichten dürfen nur interne App-Benutzer erreichen."))
        # All requirement chatter is internal, including calls from RPC/composers.
        kwargs.update(subtype_xmlid="mail.mt_note", subtype_id=False, message_type="comment")
        return super().message_post(**kwargs)

    def message_notify(self, **kwargs):
        raise AccessError(_("Bitte verwenden Sie eine interne Notiz an der Anforderung."))

    def _notify_get_recipients(self, message, msg_vals, **kwargs):
        recipients = super()._notify_get_recipients(message, msg_vals, **kwargs)
        allowed = self._permitted_partner_ids([r["id"] for r in recipients])
        return [r for r in recipients if r["id"] in allowed]


class RequirementFollower(models.Model):
    _inherit = "mail.followers"

    @api.constrains("res_model", "res_id", "partner_id")
    def _check_requirement_followers(self):
        # Covers direct RPC and One2many commands, not just message_subscribe().
        for follower in self.filtered(lambda f: f.res_model == "gc.requirement"):
            requirement = self.env["gc.requirement"].browse(follower.res_id)
            if not requirement.exists() or follower.partner_id.id not in requirement._permitted_partner_ids(follower.partner_id.ids):
                raise ValidationError(_("Externe oder nicht berechtigte Follower sind nicht zulässig."))
