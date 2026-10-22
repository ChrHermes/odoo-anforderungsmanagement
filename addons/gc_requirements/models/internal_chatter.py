from odoo import models, _
from odoo.exceptions import AccessError, ValidationError


class RequirementInternalChatter(models.AbstractModel):
    _name = "gc.requirement.internal.chatter"
    _description = "Interne Zusammenarbeit für Anforderungen und Planung"
    _inherit = ["mail.thread", "mail.activity.mixin"]

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
                    ("groups_id", "in", self.env.ref("gc_requirements.group_user").id),
                ]
            )
        )
        return {u.partner_id.id for u in users if self.with_user(u).has_access("read")}

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

    def _notify_get_recipients(self, message, msg_vals, **kwargs):
        recipients = super()._notify_get_recipients(message, msg_vals, **kwargs)
        allowed = self._permitted_partner_ids([r["id"] for r in recipients])
        return [r for r in recipients if r["id"] in allowed]
