from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class RequirementMergeWizard(models.TransientModel):
    _name = "gc.requirement.merge"
    _description = "Bestätigte Zusammenführung von Anforderungen"

    source_id = fields.Many2one(
        "gc.requirement", string="Zu archivierende Anforderung", required=True, readonly=True
    )
    target_id = fields.Many2one("gc.requirement", string="Führende Anforderung", required=True)
    confirmed = fields.Boolean(string="Zusammenführung ausdrücklich bestätigen")
    preview = fields.Text(string="Vorschau", compute="_compute_preview")

    @api.depends("source_id", "target_id")
    def _compute_preview(self):
        for wizard in self:
            if not wizard.source_id or not wizard.target_id:
                wizard.preview = _(
                    "Bitte wählen Sie die führende Anforderung. Titel, Status und Klassifikation des Ziels bleiben maßgeblich."
                )
                continue
            requirements = wizard.source_id | wizard.target_id
            requirements._check_app_user()
            requirements.check_access("read")
            sources = (
                self.env["gc.requirement.ticket.source"]
                .sudo()
                .search([("requirement_id", "in", requirements.ids)])
            )
            ticket_ids = sources.ticket_id.ids
            customers = set(sources.ticket_id.partner_id.commercial_partner_id.ids) | set(
                requirements.manual_customer_ids.commercial_partner_id.ids
            )
            wizard.preview = _(
                "Ergebnis: %(tickets)s eindeutige Tickets, %(customers)s Kundenorganisationen. Die Quelle wird archiviert. Quellen, Historie, Anhänge und Aktivitäten bleiben auf dem Original zugänglich. Bei überlappenden Tickets bleibt die Momentaufnahme des Ziels bestehen.",
                tickets=len(ticket_ids),
                customers=len(customers),
            )

    def action_apply(self):
        self.ensure_one()
        self.check_access("read")
        if not self.confirmed:
            raise ValidationError(_("Bitte bestätigen Sie die Zusammenführung ausdrücklich."))
        target = self.source_id._merge_into(self.target_id)
        return {
            "type": "ir.actions.act_window",
            "res_model": "gc.requirement",
            "res_id": target.id,
            "view_mode": "form",
            "target": "current",
        }
