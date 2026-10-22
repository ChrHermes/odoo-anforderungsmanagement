from odoo import fields, models, _
from odoo.exceptions import ValidationError


class MilestoneComplete(models.TransientModel):
    _name = "gc.requirement.milestone.complete"
    _description = "Release- / Meilensteinabschluss bestätigen"

    milestone_id = fields.Many2one(
        "gc.requirement.milestone", string="Planungseintrag", required=True, readonly=True
    )
    open_count = fields.Integer(related="milestone_id.open_count", string="Offene Anforderungen")
    confirmed = fields.Boolean(string="Abschluss trotz offener Anforderungen ausdrücklich bestätigen")

    def action_apply(self):
        self.ensure_one()
        self.check_access("read")
        milestone = self.milestone_id
        milestone._lock_planning()
        milestone.invalidate_recordset()
        if milestone.open_count and not self.confirmed:
            raise ValidationError(
                _("Bitte bestätigen Sie den Abschluss trotz offener Anforderungen ausdrücklich.")
            )
        milestone._complete()
        return {"type": "ir.actions.act_window_close"}
