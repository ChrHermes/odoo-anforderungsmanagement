from markupsafe import Markup

from odoo import api, fields, models, _
from odoo.exceptions import AccessError, ValidationError


class RequirementFromTicket(models.TransientModel):
    _name = "gc.requirement.from.ticket"
    _description = "Anforderung aus Ticket"

    ticket_id = fields.Many2one("helpdesk.ticket", string="Quellticket", required=True, readonly=True)
    mode = fields.Selection([("existing", "Vorhandene verknüpfen"), ("new", "Neue Anforderung")], required=True, default="existing", string="Aktion")
    requirement_id = fields.Many2one("gc.requirement", string="Vorhandene Anforderung", domain=[("active", "=", True)])
    name = fields.Char(string="Titel")
    description = fields.Html(string="Redaktionelle Beschreibung", sanitize=True)
    request_type = fields.Selection([("feature", "Funktionswunsch"), ("improvement", "Verbesserung"), ("bug", "Fehler")], string="Typ")
    product_id = fields.Many2one("gc.requirement.product", string="Produkt")
    category_id = fields.Many2one("gc.requirement.category", string="Funktionsbereich")
    similar_requirement_ids = fields.Many2many("gc.requirement", string="Ähnliche Anforderungen", compute="_compute_similar", compute_sudo=False)

    @api.depends("name", "product_id")
    @api.depends_context("uid")
    def _compute_similar(self):
        for wizard in self:
            wizard.similar_requirement_ids = self.env["gc.requirement"]._find_similar(wizard.name, wizard.product_id.id)

    @api.model
    def default_get(self, field_names):
        result = super().default_get(field_names)
        self.env["gc.requirement"]._check_app_user()
        if result.get("ticket_id"):
            ticket = self.env["helpdesk.ticket"].browse(result["ticket_id"])
            ticket.check_access("read")
            if "name" in field_names:
                result["name"] = ticket.read(["name"])[0]["name"]
        return result

    def action_apply(self):
        self.ensure_one()
        self.check_access("read")
        self.env["gc.requirement"]._check_app_user()
        self.ticket_id.check_access("read")
        if self.mode == "new":
            requirement = self.env["gc.requirement"].create({"name": self.name, "description": self.description, "request_type": self.request_type, "product_id": self.product_id.id, "category_id": self.category_id.id})
        else:
            requirement = self.requirement_id
            if not requirement:
                raise ValidationError(_("Bitte wählen Sie eine vorhandene Anforderung."))
        requirement.link_ticket(self.ticket_id.id)
        return {"type": "ir.actions.act_window", "res_model": "gc.requirement", "res_id": requirement.id, "view_mode": "form", "target": "current"}


class RequirementSourceViewer(models.TransientModel):
    _name = "gc.requirement.source.viewer"
    _description = "Autorisierte Ticketquellen"

    requirement_id = fields.Many2one("gc.requirement", string="Anforderung", required=True, readonly=True)
    source_html = fields.Html(string="Ticketquellen", compute="_compute_source_html", sanitize=True, compute_sudo=False)

    def _read_format(self, fnames, load="_classic_read"):
        # read/search_read/web_read must reauthorize even if a viewer was
        # already evaluated earlier in the same transaction before revocation.
        if "source_html" in fnames:
            self.invalidate_recordset(["source_html"])
        return super()._read_format(fnames, load=load)

    def export_data(self, fields_to_export):
        self.invalidate_recordset(["source_html"])
        return super().export_data(fields_to_export)

    @api.depends("requirement_id")
    @api.depends_context("uid", "company")
    def _compute_source_html(self):
        for viewer in self:
            pieces = []
            for source in viewer.requirement_id.get_authorized_sources():
                header = Markup('<h3><a href="/odoo/helpdesk.ticket/%s">Ticket #%s: %s</a></h3><p>%s · %s · %s</p>') % (
                    source["ticket_id"], source["ticket_id"], source["ticket_name"],
                    source["customer"][1] if source["customer"] else _("Kein Kunde"), source["captured_at"], source["captured_by"],
                )
                if source["origin_requirement"]:
                    header += Markup("<p>%s: %s</p>") % (_("Übernommen aus"), source["origin_requirement"])
                pieces.append(header + Markup(source["description_snapshot"]))
            viewer.source_html = Markup("<hr/>").join(pieces) if pieces else Markup("<p>%s</p>") % _("Keine zugänglichen Ticketquellen. Die Anzahl kann auch geschützte Tickets umfassen.")
