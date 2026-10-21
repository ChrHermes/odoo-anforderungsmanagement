from odoo import api, fields, models, _
from odoo.exceptions import AccessError, UserError


class RequirementTicketSource(models.Model):
    _name = "gc.requirement.ticket.source"
    _description = "Private unveränderliche Ticketquelle"
    _rec_name = "id"
    _order = "captured_at, id"

    requirement_id = fields.Many2one("gc.requirement", required=True, ondelete="restrict", index=True)
    ticket_id = fields.Many2one("helpdesk.ticket", required=True, ondelete="restrict", index=True)
    description_snapshot = fields.Html(sanitize=True, readonly=True)
    captured_at = fields.Datetime(required=True, readonly=True)
    captured_by_id = fields.Many2one("res.users", required=True, readonly=True, ondelete="restrict")
    origin_requirement_id = fields.Many2one("gc.requirement", readonly=True, ondelete="restrict")

    _sql_constraints = [("requirement_ticket_unique", "unique(requirement_id, ticket_id)", "Das Ticket ist bereits verknüpft.")]

    @api.model_create_multi
    def create(self, vals_list):
        if not self.env.su:
            raise AccessError(_("Ticketquellen dürfen nur über die geprüfte Ticketaktion angelegt werden."))
        return super().create(vals_list)

    def write(self, vals):
        raise AccessError(_("Ticketquellen und ihre Herkunft sind unveränderlich."))

    @api.ondelete(at_uninstall=False)
    def _prevent_deletion(self):
        raise UserError(_("Historische Ticketquellen dürfen nicht gelöscht werden."))

    @api.model
    def _capture(self, requirement, ticket):
        """Private service: checks caller rights BEFORE opening private storage."""
        requirement._check_app_user()
        requirement.ensure_one()
        requirement.check_access("write")
        ticket.ensure_one()
        ticket.check_access("read")
        # read() also enforces field-level/custom read restrictions.
        description = ticket.read(["description"])[0]["description"]
        Source = self.sudo()
        existing = Source.search([("requirement_id", "=", requirement.id), ("ticket_id", "=", ticket.id)])
        if existing:
            return existing
        source = Source.create({"requirement_id": requirement.id, "ticket_id": ticket.id, "description_snapshot": description, "captured_at": fields.Datetime.now(), "captured_by_id": self.env.uid})
        requirement.invalidate_recordset(["ticket_count", "customer_count"])
        return source
