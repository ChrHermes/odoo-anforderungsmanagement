from odoo import fields, models

from ..models.requirement import STATES


class RequirementDecision(models.TransientModel):
    _name = "gc.requirement.decision"
    _description = "Anforderungsstatus ändern"

    requirement_id = fields.Many2one("gc.requirement", string="Anforderung", required=True, readonly=True)
    state = fields.Selection(STATES, string="Neuer Status", required=True)
    reason = fields.Text(string="Neue Begründung")
    implemented_version = fields.Char(string="Veröffentlichte Version")
    implementation_note = fields.Text(string="Umsetzungshinweis")
    implemented_on = fields.Date(string="Veröffentlicht am")

    def action_apply(self):
        self.ensure_one()
        self.check_access("read")
        vals = {"state": self.state}
        if self.state in ("deferred", "rejected"):
            vals["decision_reason"] = self.reason
        if self.state == "implemented":
            for key in ("implemented_version", "implementation_note", "implemented_on"):
                if self[key]:
                    vals[key] = self[key]
        self.requirement_id.write(vals)
        return {"type": "ir.actions.act_window_close"}
