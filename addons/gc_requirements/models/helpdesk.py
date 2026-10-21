from collections import defaultdict

from markupsafe import Markup

from odoo import api, fields, models, _
from odoo.exceptions import AccessError, ValidationError
from odoo.tools import html_sanitize

from .requirement import STATES


class RequirementHelpdesk(models.Model):
    _inherit = "gc.requirement"

    # Deliberately NO public One2many to the source model: domains on related
    # private fields could otherwise become a search oracle despite its ACL.
    manual_customer_ids = fields.Many2many(
        "res.partner",
        "gc_requirement_manual_partner_rel",
        "requirement_id",
        "partner_id",
        string="Manuell betroffene Kunden",
        tracking=True,
    )
    ticket_count = fields.Integer(string="Tickets", compute="_compute_source_counts")
    customer_count = fields.Integer(string="Betroffene Kunden", compute="_compute_source_counts")

    @api.depends("manual_customer_ids.commercial_partner_id")
    def _compute_source_counts(self):
        sources = self.env["gc.requirement.ticket.source"].sudo().search([("requirement_id", "in", self.ids)])
        tickets = defaultdict(set)
        customers = defaultdict(set)
        # Sudo is restricted to the explicitly approved aggregate indicators.
        for source in sources:
            tickets[source.requirement_id.id].add(source.ticket_id.id)
            partner = source.ticket_id.partner_id.commercial_partner_id
            if partner:
                customers[source.requirement_id.id].add(partner.id)
        for record in self:
            record.ticket_count = len(tickets[record.id])
            record.customer_count = len(
                customers[record.id] | set(record.manual_customer_ids.commercial_partner_id.ids)
            )

    def link_ticket(self, ticket_id):
        self.ensure_one()
        self._check_app_user()
        self.check_access("write")
        if not self.active:
            raise ValidationError(
                _("Archivierte Anforderungen können nicht neu mit Tickets verknüpft werden.")
            )
        if type(ticket_id) is not int or ticket_id <= 0:
            raise ValidationError(_("Bitte wählen Sie ein gültiges Ticket."))
        ticket = self.env["helpdesk.ticket"].browse(ticket_id).exists()
        if not ticket:
            raise AccessError(_("Das Ticket ist nicht verfügbar."))
        self.env["gc.requirement.ticket.source"]._capture(self, ticket)
        return True

    def get_authorized_sources(self):
        """Narrow RPC adapter: never returns ticket details before exact access."""
        self.ensure_one()
        self._check_app_user()
        self.check_access("read")
        sources = self.env["gc.requirement.ticket.source"].sudo().search([("requirement_id", "=", self.id)])
        tickets = self.env["helpdesk.ticket"].with_context(active_test=False).browse(sources.ticket_id.ids)
        allowed = tickets._filtered_access("read")
        result = []
        for source in sources:
            ticket = self.env["helpdesk.ticket"].browse(source.ticket_id.id)
            if ticket not in allowed:
                continue
            try:
                ticket.check_access("read")
                data = ticket.read(["name", "partner_id", "description"])[0]
            except AccessError:
                continue
            origin = self.env["gc.requirement"].browse(source.origin_requirement_id.id)
            # Only now may the source snapshot and provenance cross the boundary.
            result.append(
                {
                    "ticket_id": ticket.id,
                    "ticket_name": data["name"],
                    "customer": data["partner_id"],
                    "description_snapshot": html_sanitize(source.description_snapshot or ""),
                    "captured_at": fields.Datetime.to_string(source.captured_at),
                    "captured_by": source.captured_by_id.display_name,
                    "origin_requirement": origin.reference if origin and origin.has_access("read") else False,
                }
            )
        return result

    def action_view_sources(self):
        self.ensure_one()
        self._check_app_user()
        self.check_access("read")
        viewer = self.env["gc.requirement.source.viewer"].create({"requirement_id": self.id})
        return {
            "type": "ir.actions.act_window",
            "name": _("Autorisierte Ticketquellen"),
            "res_model": "gc.requirement.source.viewer",
            "res_id": viewer.id,
            "view_mode": "form",
            "target": "new",
            "context": {"default_requirement_id": self.id},
        }

    def action_view_tickets(self):
        self.ensure_one()
        ticket_ids = [row["ticket_id"] for row in self.get_authorized_sources()]
        return {
            "type": "ir.actions.act_window",
            "name": _("Zugängliche Tickets"),
            "res_model": "helpdesk.ticket",
            "view_mode": "list,form",
            "domain": [("id", "in", ticket_ids)],
            "context": {"active_test": False},
        }

    def action_view_customers(self):
        self.ensure_one()
        sources = self.get_authorized_sources()
        partners = self.manual_customer_ids
        partners |= self.env["res.partner"].browse([row["customer"][0] for row in sources if row["customer"]])
        partners = partners.commercial_partner_id._filtered_access("read")
        return {
            "type": "ir.actions.act_window",
            "name": _("Zugängliche Kunden"),
            "res_model": "res.partner",
            "view_mode": "list,form",
            "domain": [("id", "in", partners.ids)],
        }

    def _after_state_transition(self):
        super()._after_state_transition()
        for record in self.filtered(lambda r: r.state in ("planned", "implemented", "rejected")):
            record._post_ticket_transition_notes()

    def _post_ticket_transition_notes(self):
        """Private, fixed-content service. No message_post notification/reopen hooks.

        Native mail.message internal notes are inserted directly: no recipients,
        no notification pipeline and no general sudo ticket write endpoint.
        Custom automated actions still require a neutralized Enterprise review.
        """
        self.ensure_one()
        sources = self.env["gc.requirement.ticket.source"].sudo().search([("requirement_id", "=", self.id)])
        note = Markup('<p><a href="/odoo/gc.requirement/%s">%s</a>: %s – %s</p>') % (
            self.id,
            self.reference,
            self.name,
            dict(STATES)[self.state],
        )
        detail = self.decision_reason if self.state == "rejected" else self.implementation_note
        if detail:
            note += Markup("<p>%s</p>") % detail
        self.env["mail.message"].sudo().create(
            [
                {
                    "model": "helpdesk.ticket",
                    "res_id": ticket.id,
                    "body": note,
                    "message_type": "comment",
                    "subtype_id": self.env.ref("mail.mt_note").id,
                    "author_id": self.env.user.partner_id.id,
                }
                for ticket in sources.ticket_id
            ]
        )


class HelpdeskTicket(models.Model):
    _inherit = "helpdesk.ticket"

    gc_requirement_count = fields.Integer(
        string="Anforderungen", compute="_compute_gc_requirement_count", groups="gc_requirements.group_user"
    )

    def _compute_gc_requirement_count(self):
        sources = self.env["gc.requirement.ticket.source"].sudo().search([("ticket_id", "in", self.ids)])
        grouped = defaultdict(set)
        for source in sources:
            if source.requirement_id.with_user(self.env.user).has_access("read"):
                grouped[source.ticket_id.id].add(source.requirement_id.id)
        for ticket in self:
            ticket.gc_requirement_count = len(grouped[ticket.id])

    def action_gc_requirement(self):
        self.ensure_one()
        self.env["gc.requirement"]._check_app_user()
        self.check_access("read")
        return {
            "type": "ir.actions.act_window",
            "name": _("Anforderung erstellen/verknüpfen"),
            "res_model": "gc.requirement.from.ticket",
            "view_mode": "form",
            "target": "new",
            "context": {"default_ticket_id": self.id},
        }

    def action_gc_requirements(self):
        self.env["gc.requirement"]._check_app_user()
        self.check_access("read")
        sources = self.env["gc.requirement.ticket.source"].sudo().search([("ticket_id", "in", self.ids)])
        requirements = sources.requirement_id.with_user(self.env.user)._filtered_access("read")
        return {
            "type": "ir.actions.act_window",
            "name": _("Verknüpfte Anforderungen"),
            "res_model": "gc.requirement",
            "view_mode": "list,form",
            "domain": [("id", "in", requirements.ids)],
            "context": {"active_test": False},
        }

    def write(self, vals):
        result = super().write(vals)
        if "partner_id" in vals:
            sources = self.env["gc.requirement.ticket.source"].sudo().search([("ticket_id", "in", self.ids)])
            sources.requirement_id.invalidate_recordset(["customer_count"])
        return result
