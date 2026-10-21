from odoo import api, fields, models, _
from odoo.exceptions import AccessError, UserError, ValidationError
from odoo.tools import html2plaintext


STATES = [
    ("new", "Neu"), ("review", "In Prüfung"), ("evaluated", "Bewertet"),
    ("planned", "Geplant"), ("in_progress", "In Umsetzung"),
    ("implemented", "Umgesetzt"), ("deferred", "Zurückgestellt"), ("rejected", "Abgelehnt"),
]


class Requirement(models.Model):
    _name = "gc.requirement"
    _description = "Anforderung"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "priority desc, write_date desc, id desc"
    _rec_names_search = ["reference", "name"]

    name = fields.Char(string="Titel", required=True, tracking=True)
    reference = fields.Char(string="Nummer", required=True, readonly=True, copy=False, index=True)
    description = fields.Html(string="Redaktionelle Beschreibung", required=True, sanitize=True)
    request_type = fields.Selection(
        [("feature", "Funktionswunsch"), ("improvement", "Verbesserung"), ("bug", "Fehler")],
        string="Typ", required=True, tracking=True,
    )
    state = fields.Selection(STATES, string="Status", default="new", required=True, tracking=True, index=True)
    priority = fields.Selection(
        [("0", "Normal"), ("1", "Mittel"), ("2", "Hoch"), ("3", "Dringend")],
        string="Priorität", default="0", required=True, tracking=True,
    )
    product_id = fields.Many2one("gc.requirement.product", string="Produkt", required=True, ondelete="restrict", tracking=True, index=True)
    category_id = fields.Many2one("gc.requirement.category", string="Funktionsbereich", ondelete="restrict", tracking=True)
    assigned_user_id = fields.Many2one("res.users", string="Verantwortlich", tracking=True, domain=[("share", "=", False)])
    creator_user_id = fields.Many2one("res.users", string="Erstellt von", readonly=True, required=True, copy=False)
    active = fields.Boolean(default=True, string="Aktiv", tracking=True)
    affected_version = fields.Char(string="Betroffene Version")
    implemented_version = fields.Char(string="Veröffentlichte Version", tracking=True)
    implementation_note = fields.Text(string="Umsetzungshinweis", tracking=True)
    development_url = fields.Char(string="Entwicklungsreferenz")
    implemented_on = fields.Date(string="Veröffentlicht am", tracking=True)
    decision_reason = fields.Text(string="Begründung", tracking=True)

    _sql_constraints = [("reference_unique", "unique(reference)", "Die Anforderungsnummer muss eindeutig sein.")]

    def _check_app_user(self):
        if self.env.user.share or not self.env.user.has_group("gc_requirements.group_user"):
            raise AccessError(_("Nur freigeschaltete interne Mitarbeiter dürfen Anforderungen bearbeiten."))

    @api.depends("reference", "name")
    def _compute_display_name(self):
        for requirement in self:
            requirement.display_name = "%s – %s" % (requirement.reference or "", requirement.name or "")

    @api.model_create_multi
    def create(self, vals_list):
        self._check_app_user()
        prepared = []
        defaults = self.default_get(["name", "description", "product_id", "request_type", "state", "decision_reason"])
        for incoming in vals_list:
            vals = dict(defaults, **incoming)
            if vals.get("reference") or vals.get("creator_user_id"):
                raise ValidationError(_("Nummer und Ersteller werden automatisch vergeben."))
            self._validate_required_values(vals)
            vals["reference"] = self.env["ir.sequence"].next_by_code("gc.requirement")
            vals["creator_user_id"] = self.env.uid
            state = vals.get("state", self.default_get(["state"]).get("state"))
            self._validate_transition_values(state, vals)
            if state == "implemented" and not vals.get("implemented_on"):
                vals["implemented_on"] = fields.Date.context_today(self)
            prepared.append(vals)
        records = super().create(prepared)
        records._check_active_classification()
        records._subscribe_responsible()
        for record in records.filtered(lambda r: r.state in ("deferred", "rejected")):
            record._post_decision_reason()
        return records

    def write(self, vals):
        self._check_app_user()
        if {"reference", "creator_user_id"} & vals.keys():
            raise ValidationError(_("Nummer und Ersteller sind unveränderlich."))
        self.check_access("write")
        self._validate_required_values(vals, partial=True)
        changes = self.filtered(lambda r: "state" in vals and r.state != vals["state"])
        if changes:
            self._validate_transition_values(vals["state"], vals)
        vals = dict(vals)
        if changes and vals["state"] == "implemented" and not vals.get("implemented_on"):
            vals["implemented_on"] = fields.Date.context_today(self)
        # Odoo's activity mixin deletes activities on archive. Requirement
        # history must retain them; the scoped unlink guard only preserves
        # requirement activities and never grants additional permissions.
        writer = self.with_context(gc_preserve_requirement_activities=True) if vals.get("active") is False else self
        result = super(Requirement, writer).write(vals)
        if {"product_id", "category_id"} & vals.keys():
            self._check_active_classification()
        if "assigned_user_id" in vals:
            self._subscribe_responsible()
        for record in changes.filtered(lambda r: r.state in ("deferred", "rejected")):
            record._post_decision_reason()
        changes._after_state_transition()
        return result

    def toggle_active(self):
        # Skip mail.activity.mixin's destructive pre-archive cleanup, while
        # keeping the normal ORM write path, authorization and audit intact.
        return models.Model.toggle_active(self)

    @api.model
    def _validate_required_values(self, vals, partial=False):
        for key in ("name", "description", "request_type", "product_id"):
            if partial and key not in vals:
                continue
            value = vals.get(key)
            if key == "description":
                value = html2plaintext(value or "").strip()
            elif key == "name":
                value = (value or "").strip()
            if not value:
                raise ValidationError(_("Titel, Beschreibung, Typ und Produkt sind erforderlich."))

    @api.model
    def _validate_transition_values(self, state, vals):
        if state in ("deferred", "rejected") and not (vals.get("decision_reason") or "").strip():
            raise ValidationError(_("Bei jeder Zurückstellung oder Ablehnung ist eine neue Begründung erforderlich."))

    @api.constrains("state", "decision_reason", "implemented_on")
    def _check_decision(self):
        for record in self:
            if record.state in ("deferred", "rejected") and not (record.decision_reason or "").strip():
                raise ValidationError(_("Eine Begründung ist erforderlich."))
            if record.state == "implemented" and not record.implemented_on:
                raise ValidationError(_("Für veröffentlichte Anforderungen ist das Veröffentlichungsdatum erforderlich."))

    def _post_decision_reason(self):
        self.ensure_one()
        self.message_post(body=_("Begründung (%(state)s): %(reason)s", state=dict(STATES)[self.state], reason=self.decision_reason))

    def _after_state_transition(self):
        """Extension point for the narrowly scoped Helpdesk note service."""

    def action_decision(self):
        self.ensure_one()
        self._check_app_user()
        self.check_access("write")
        return {"type": "ir.actions.act_window", "name": _("Status ändern"), "res_model": "gc.requirement.decision", "view_mode": "form", "target": "new", "context": {"default_requirement_id": self.id, "default_state": self.state}}

    @api.onchange("product_id")
    def _onchange_product(self):
        if self.category_id.product_id != self.product_id:
            self.category_id = False

    def copy(self, default=None):
        return super().copy(dict(default or {}, reference=False, creator_user_id=False))

    def _check_active_classification(self):
        for requirement in self:
            category = requirement.category_id
            if not requirement.product_id.active:
                raise ValidationError(_("Bitte wählen Sie ein aktives Produkt."))
            while category:
                if not category.active:
                    raise ValidationError(_("Bitte wählen Sie einen aktiven Funktionspfad."))
                category = category.parent_id

    @api.constrains("name", "description", "product_id", "category_id", "assigned_user_id")
    def _check_content(self):
        for requirement in self:
            if not (requirement.name or "").strip() or not html2plaintext(requirement.description or "").strip():
                raise ValidationError(_("Titel und eine inhaltliche redaktionelle Beschreibung sind erforderlich."))
            if requirement.category_id and requirement.category_id.product_id != requirement.product_id:
                raise ValidationError(_("Der Funktionsbereich gehört nicht zum gewählten Produkt."))
            if requirement.assigned_user_id and (
                requirement.assigned_user_id.share or not requirement.assigned_user_id.has_group("gc_requirements.group_user")
            ):
                raise ValidationError(_("Verantwortliche müssen freigeschaltete interne App-Benutzer sein."))

    @api.ondelete(at_uninstall=False)
    def _prevent_deletion(self):
        raise UserError(_("Anforderungen dürfen nur archiviert, nicht gelöscht werden."))
