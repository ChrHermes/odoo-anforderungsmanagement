from odoo import fields, models, _
from odoo.exceptions import ValidationError

from ..models.milestone import PLANNING_STATES


class MilestoneComplete(models.TransientModel):
    _name = "gc.requirement.milestone.complete"
    _description = "Release- / Meilensteinstatus ändern"

    milestone_id = fields.Many2one(
        "gc.requirement.milestone", string="Planungseintrag", required=True, readonly=True
    )
    open_count = fields.Integer(related="milestone_id.open_count", string="Offene Anforderungen")
    state = fields.Selection(PLANNING_STATES, string="Neuer Status", required=True, default="done")
    not_implemented_count = fields.Integer(related="milestone_id.not_implemented_count")
    completed_on = fields.Date(string="Abgeschlossen / veröffentlicht am", default=fields.Date.context_today)
    confirmed = fields.Boolean(string="Abschluss trotz offener Anforderungen ausdrücklich bestätigen")

    def action_apply(self):
        self.ensure_one()
        self.check_access("read")
        milestone = self.milestone_id
        milestone._lock_planning()
        milestone.invalidate_recordset()
        if self.state == "done" and milestone.not_implemented_count and not self.confirmed:
            raise ValidationError(
                _("Bitte bestätigen Sie den Abschluss trotz offener Anforderungen ausdrücklich.")
            )
        if self.state == "done":
            if not self.completed_on:
                raise ValidationError(_("Bitte ein Abschlussdatum eingeben."))
            milestone._complete(self.completed_on)
        else:
            milestone.write({"state": self.state})
        return {"type": "ir.actions.act_window_close"}
