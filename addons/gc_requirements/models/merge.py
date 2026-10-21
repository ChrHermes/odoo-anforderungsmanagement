import re

from markupsafe import Markup

from odoo import api, Command, fields, models, _
from odoo.exceptions import ValidationError
from odoo.osv import expression
from odoo.tools import SQL


class RequirementMerge(models.Model):
    _inherit = "gc.requirement"

    merged_into_id = fields.Many2one("gc.requirement", string="Zusammengeführt in", readonly=True, copy=False, ondelete="restrict", index=True)
    merged_source_ids = fields.One2many("gc.requirement", "merged_into_id", string="Erhaltene Originale", readonly=True, context={"active_test": False})
    similar_requirement_ids = fields.Many2many("gc.requirement", compute="_compute_similar", string="Ähnliche Anforderungen", compute_sudo=False)

    @api.model_create_multi
    def create(self, vals_list):
        if self.env.context.get("default_merged_into_id") or self.env.context.get("default_merged_source_ids") or any(v.get("merged_into_id") or v.get("merged_source_ids") for v in vals_list):
            raise ValidationError(_("Zusammenführungsverweise werden ausschließlich durch den bestätigten Dialog gesetzt."))
        return super().create(vals_list)

    def write(self, vals):
        if {"merged_into_id", "merged_source_ids"} & vals.keys():
            raise ValidationError(_("Zusammenführungsverweise sind dauerhaft und dürfen nicht direkt verändert werden."))
        changed_active = self.filtered(lambda r: "active" in vals and r.active != vals["active"])
        result = super().write(vals)
        for record in changed_active:
            record.message_post(body=_("Anforderung wiederhergestellt.") if record.active else _("Anforderung archiviert."))
        return result

    @api.depends("name", "product_id")
    @api.depends_context("uid")
    def _compute_similar(self):
        for record in self:
            record.similar_requirement_ids = self._find_similar(record.name, record.product_id.id, record._origin.id)

    @api.model
    def _find_similar(self, name, product_id, exclude_id=False):
        terms = sorted(set(re.findall(r"\w{3,}", (name or "").casefold())), key=lambda term: (-len(term), term))[:3]
        if not terms or not product_id:
            return self.browse()
        domain = expression.AND([
            [("product_id", "=", product_id), ("id", "!=", exclude_id or 0), ("active", "=", True)],
            expression.OR([[("name", "ilike", term)] for term in terms]),
        ])
        return self.search(domain, limit=5, order="write_date desc, id desc")

    def action_merge(self):
        self.ensure_one()
        self._check_app_user()
        self.check_access("write")
        return {"type": "ir.actions.act_window", "name": _("Duplikat zusammenführen"), "res_model": "gc.requirement.merge", "view_mode": "form", "target": "new", "context": {"default_source_id": self.id}}

    def _merge_into(self, target):
        """Only called by the confirmed wizard. No caller-controlled sudo values."""
        self.ensure_one()
        target.ensure_one()
        self._check_app_user()
        (self | target).check_access("write")
        if self == target:
            raise ValidationError(_("Eine Anforderung kann nicht mit sich selbst zusammengeführt werden."))
        # Serialize competing merges after ORM authorization. The ORM continues
        # to own every mutation; this query only locks the two existing rows.
        (self | target).flush_recordset(["active", "merged_into_id"])
        self.env.cr.execute(SQL("SELECT id FROM gc_requirement WHERE id IN %s ORDER BY id FOR UPDATE", tuple(sorted((self | target).ids))))
        (self | target).invalidate_recordset(["active", "merged_into_id"])
        if not self.active or not target.active or self.merged_into_id or target.merged_into_id:
            raise ValidationError(_("Quelle und Ziel müssen aktiv und noch nicht zusammengeführt sein."))
        sources = self.env["gc.requirement.ticket.source"].sudo().search([("requirement_id", "in", (self | target).ids)])
        existing_ticket_ids = set(sources.filtered(lambda s: s.requirement_id.id == target.id).ticket_id.ids)
        copies = []
        for source in sources.filtered(lambda s: s.requirement_id.id == self.id):
            if source.ticket_id.id not in existing_ticket_ids:
                copies.append({
                    "requirement_id": target.id, "ticket_id": source.ticket_id.id,
                    "description_snapshot": source.description_snapshot,
                    "captured_at": source.captured_at, "captured_by_id": source.captured_by_id.id,
                    "origin_requirement_id": source.origin_requirement_id.id or self.id,
                })
        # Private storage is copied without leaking content to the merge actor.
        if copies:
            self.env["gc.requirement.ticket.source"].sudo().create(copies)
        target.write({"manual_customer_ids": [Command.link(p.id) for p in self.manual_customer_ids]})
        target.invalidate_recordset(["ticket_count", "customer_count", "merged_source_ids"])
        # Bypass only this class's public redirect guard, never ORM permissions.
        super(RequirementMerge, self).write({"merged_into_id": target.id, "active": False})
        body = Markup('<p>%s <a href="/odoo/gc.requirement/%s">%s</a> → <a href="/odoo/gc.requirement/%s">%s</a>. %s</p>') % (
            _("Zusammengeführt:"), self.id, self.reference, target.id, target.reference,
            _("Originalquellen, Anhänge, Chatter und Aktivitäten bleiben am Original erhalten."),
        )
        self.message_post(body=body)
        target.message_post(body=body)
        return target

    @api.constrains("merged_into_id")
    def _check_merge_cycles(self):
        for record in self:
            seen = set()
            current = record
            while current:
                if current.id in seen:
                    raise ValidationError(_("Zusammenführungen dürfen keine Kreise bilden."))
                seen.add(current.id)
                current = current.merged_into_id

    def action_open_survivor(self):
        self.ensure_one()
        self._check_app_user()
        current, seen = self, set()
        while current.merged_into_id:
            current.check_access("read")
            if current.id in seen:
                raise ValidationError(_("Ungültige Zusammenführungskette."))
            seen.add(current.id)
            current = current.merged_into_id
        current.check_access("read")
        return {"type": "ir.actions.act_window", "res_model": "gc.requirement", "res_id": current.id, "view_mode": "form", "target": "current"}
