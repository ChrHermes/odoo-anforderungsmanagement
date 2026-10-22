from urllib.parse import urlsplit

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError

from .requirement import STATES


PLANNING_STATES = [
    ("draft", "Entwurf"),
    ("planned", "Geplant"),
    ("active", "Aktiv"),
    ("done", "Abgeschlossen / Veröffentlicht"),
    ("cancelled", "Abgesagt"),
]
# Only the private completion service can supply this identity. RPC context
# booleans/strings cannot bypass the explicit open-requirements confirmation.
_COMPLETION_CONFIRMED = object()


class RequirementMilestone(models.Model):
    _name = "gc.requirement.milestone"
    _description = "Release / Meilenstein"
    _inherit = ["gc.requirement.internal.chatter"]
    _order = "planned_date, reference, id"
    _rec_names_search = ["reference", "name", "version"]

    reference = fields.Char(string="Nummer", readonly=True, required=True, copy=False, default="Neu")
    name = fields.Char(string="Bezeichnung", required=True, tracking=True)
    kind = fields.Selection(
        [("release", "Release"), ("milestone", "Meilenstein")],
        string="Typ",
        required=True,
        default="release",
        tracking=True,
    )
    product_id = fields.Many2one(
        "gc.requirement.product", string="Produkt", ondelete="restrict", tracking=True, index=True
    )
    product_color_hex = fields.Char(related="product_id.color_hex", string="Produktfarbe")
    product_color_text = fields.Char(related="product_id.color_text", string="Produkt-Kontrastfarbe")
    version = fields.Char(string="Geplante Version", tracking=True)
    description = fields.Html(string="Beschreibung", sanitize=True)
    planned_start = fields.Date(string="Geplant ab", tracking=True)
    planned_date = fields.Date(string="Geplant am / bis", tracking=True, index=True)
    completed_on = fields.Date(string="Abgeschlossen / veröffentlicht am", tracking=True)
    state = fields.Selection(
        PLANNING_STATES,
        string="Planungsstatus",
        required=True,
        default="draft",
        tracking=True,
        index=True,
        group_expand=True,
    )
    assigned_user_id = fields.Many2one(
        "res.users",
        string="Verantwortlich",
        tracking=True,
        domain=lambda self: [
            ("share", "=", False),
            ("active", "=", True),
            ("all_group_ids", "in", self.env.ref("gc_requirements.group_user").ids),
        ],
    )
    active = fields.Boolean(string="Aktiv", default=True, tracking=True)
    requirement_ids = fields.One2many("gc.requirement", "milestone_id", string="Anforderungen")
    assignment_ids = fields.Many2many(
        "gc.requirement",
        string="Enthaltene Anforderungen",
        compute="_compute_assignment_ids",
        inverse="_inverse_assignment_ids",
        help="Bestehende Anforderungen hinzufügen oder entfernen; Status und Veröffentlichungsdaten bleiben erhalten.",
    )
    requirement_count = fields.Integer(string="Anforderungen gesamt", compute="_compute_counts")
    archived_count = fields.Integer(string="Davon archiviert", compute="_compute_counts")
    open_count = fields.Integer(
        string="Offen (aktiv, einschließlich zurückgestellt)", compute="_compute_counts"
    )
    progress = fields.Float(string="Umgesetzt (%)", compute="_compute_counts")
    new_count = fields.Integer(string="Neu", compute="_compute_counts")
    review_count = fields.Integer(string="In Prüfung", compute="_compute_counts")
    evaluated_count = fields.Integer(string="Bewertet", compute="_compute_counts")
    planned_count = fields.Integer(string="Geplant", compute="_compute_counts")
    in_progress_count = fields.Integer(string="In Umsetzung", compute="_compute_counts")
    implemented_count = fields.Integer(string="Umgesetzt", compute="_compute_counts")
    deferred_count = fields.Integer(string="Zurückgestellt", compute="_compute_counts")
    rejected_count = fields.Integer(string="Abgelehnt", compute="_compute_counts")

    _reference_unique = models.Constraint("UNIQUE(reference)", "Die Planungsnummer muss eindeutig sein.")

    def _check_app_user(self):
        self.env["gc.requirement"]._check_app_user()

    def _lock_planning(self):
        """Serialize membership and product/closure changes after authorization."""
        self._check_app_user()
        self.check_access("write")
        if self.ids:
            self.env.cr.execute(
                "SELECT id FROM gc_requirement_milestone WHERE id IN %s ORDER BY id FOR UPDATE",
                [tuple(self.ids)],
            )

    @api.depends("reference", "name")
    def _compute_display_name(self):
        for record in self:
            record.display_name = "%s – %s" % (record.reference or "", record.name or "")

    @api.depends("requirement_ids")
    @api.depends_context("uid")
    def _compute_assignment_ids(self):
        for record in self:
            record.assignment_ids = (
                self.env["gc.requirement"]
                .with_context(active_test=False)
                .search([("milestone_id", "=", record.id)])
                if record.id
                else self.env["gc.requirement"]
            )

    def _inverse_assignment_ids(self):
        for record in self:
            record._lock_planning()
            desired = record.assignment_ids
            desired.check_access("write")
            existing = (
                self.env["gc.requirement"]
                .with_context(active_test=False)
                .search([("milestone_id", "=", record.id)])
            )
            (existing - desired).write({"milestone_id": False})
            (desired - existing).write({"milestone_id": record.id})

    @api.depends("requirement_ids.state", "requirement_ids.active")
    @api.depends_context("uid")
    def _compute_counts(self):
        # Ordinary ORM, never sudo: future requirement rules also scope counters.
        groups = (
            self.env["gc.requirement"]
            .with_context(active_test=False)
            .read_group([("milestone_id", "in", self.ids)], ["milestone_id", "active", "state"], ["__count"])
            if self.ids
            else []
        )
        counts = {}
        for milestone, active, state, count in groups:
            bucket = counts.setdefault(milestone, {})
            key = state if active else "archived"
            bucket[key] = bucket.get(key, 0) + count
        for record in self:
            bucket = counts.get(record.id, {})
            for state, _label in STATES:
                record[state + "_count"] = bucket.get(state, 0)
            record.archived_count = bucket.get("archived", 0)
            record.requirement_count = sum(bucket.values())
            eligible = sum(bucket.get(state, 0) for state, _label in STATES if state != "rejected")
            record.open_count = eligible - bucket.get("implemented", 0)
            record.progress = 100 * bucket.get("implemented", 0) / eligible if eligible else 0

    @api.model_create_multi
    def create(self, vals_list):
        self._check_app_user()
        prepared = []
        for incoming in vals_list:
            vals = dict(incoming)
            if vals.get("reference"):
                raise ValidationError(_("Die Planungsnummer wird automatisch vergeben."))
            if vals.get("state", self.env.context.get("default_state")) == "done":
                # Create drafts first, then use the same audited completion path.
                raise ValidationError(_("Bitte zuerst speichern und anschließend ausdrücklich abschließen."))
            vals["reference"] = self.env["ir.sequence"].next_by_code("gc.requirement.milestone")
            prepared.append(vals)
        records = super().create(prepared)
        records._subscribe_planning_responsible()
        return records

    def write(self, vals):
        self._lock_planning()
        if "reference" in vals:
            raise ValidationError(_("Die Planungsnummer ist unveränderlich."))
        changes = self.filtered(lambda record: vals.get("state") == "done" and record.state != "done")
        if changes:
            changes.invalidate_recordset()
            if (
                any(record.open_count for record in changes)
                and self.env.context.get("gc_planning_completion") is not _COMPLETION_CONFIRMED
            ):
                raise ValidationError(
                    _("Es gibt offene Anforderungen. Bitte den Abschlussdialog bestätigen.")
                )
            vals = dict(vals)
            vals.setdefault("completed_on", fields.Date.context_today(self))
        writer = (
            self.with_context(gc_preserve_requirement_activities=True)
            if vals.get("active") is False
            else self
        )
        result = super(RequirementMilestone, writer).write(vals)
        if {"product_id", "kind"} & vals.keys():
            self.env["gc.requirement"].with_context(active_test=False).search(
                [("milestone_id", "in", self.ids)]
            )._check_milestone_product()
        if "assigned_user_id" in vals:
            self._subscribe_planning_responsible()
        for record in changes:
            record.message_post(
                body=_(
                    "%(decision)s. Offene aktive Anforderungen: %(open)s; abgelehnt: %(rejected)s; archiviert: %(archived)s. Anforderungsstatus und Veröffentlichungsdaten bleiben erhalten.",
                    decision=_("Release veröffentlicht")
                    if record.kind == "release"
                    else _("Meilenstein abgeschlossen"),
                    open=record.open_count,
                    rejected=record.rejected_count,
                    archived=record.archived_count,
                )
            )
        return result

    @api.constrains(
        "name",
        "kind",
        "product_id",
        "planned_start",
        "planned_date",
        "state",
        "completed_on",
        "assigned_user_id",
    )
    def _check_planning(self):
        for record in self:
            if not (record.name or "").strip():
                raise ValidationError(_("Bitte eine Bezeichnung eingeben."))
            if record.kind == "release" and not record.product_id:
                raise ValidationError(_("Ein Release benötigt ein Produkt."))
            if record.planned_start and record.planned_date and record.planned_start > record.planned_date:
                raise ValidationError(_("Der Planungsbeginn darf nicht nach dem Endtermin liegen."))
            if record.state == "done" and not record.completed_on:
                raise ValidationError(_("Ein abgeschlossener Planungseintrag benötigt ein Abschlussdatum."))
            if record.assigned_user_id and (
                record.assigned_user_id.share
                or not record.assigned_user_id.has_group("gc_requirements.group_user")
            ):
                raise ValidationError(_("Verantwortliche müssen interne App-Benutzer sein."))

    def _subscribe_planning_responsible(self):
        for record in self:
            for user in record.create_uid | record.assigned_user_id:
                if user.active and user.partner_id.id in record._permitted_partner_ids(user.partner_id.ids):
                    record.message_subscribe(partner_ids=user.partner_id.ids)

    def action_complete(self):
        self.ensure_one()
        self._lock_planning()
        return {
            "type": "ir.actions.act_window",
            "name": _("Abschluss bestätigen"),
            "res_model": "gc.requirement.milestone.complete",
            "view_mode": "form",
            "target": "new",
            "context": {"default_milestone_id": self.id},
        }

    def _complete(self):
        self.with_context(gc_planning_completion=_COMPLETION_CONFIRMED).write({"state": "done"})

    def action_view_requirements(self):
        self.ensure_one()
        self._check_app_user()
        self.check_access("read")
        action = self.env["ir.actions.actions"]._for_xml_id("gc_requirements.action_requirements")
        action.update(
            domain=[("milestone_id", "=", self.id)],
            context={
                "active_test": False,
                "default_milestone_id": self.id,
                "default_product_id": self.product_id.id,
                "read_group_expand": True,
            },
        )
        return action

    def toggle_active(self):
        return models.Model.toggle_active(self)

    def copy(self, default=None):
        return super().copy(dict(default or {}, reference=False, state="draft", completed_on=False))

    @api.ondelete(at_uninstall=False)
    def _prevent_deletion(self):
        raise UserError(_("Planungseinträge dürfen nur archiviert, nicht gelöscht werden."))


class RequirementPlanning(models.Model):
    _inherit = "gc.requirement"

    milestone_id = fields.Many2one(
        "gc.requirement.milestone",
        string="Zielrelease / Meilenstein",
        tracking=True,
        ondelete="restrict",
        index=True,
        copy=False,
    )
    milestone_start = fields.Date(related="milestone_id.planned_start", string="Geplant ab")
    milestone_date = fields.Date(related="milestone_id.planned_date", string="Geplant am / bis")
    worktimes_url = fields.Char(string="Worktimes (GitLab)", tracking=True, copy=False)

    @api.constrains("milestone_id", "product_id")
    def _check_milestone_product(self):
        for requirement in self:
            milestone = requirement.milestone_id
            if milestone.kind == "release" and milestone.product_id != requirement.product_id:
                raise ValidationError(_("Anforderung und Zielrelease müssen zum selben Produkt gehören."))

    @api.constrains("worktimes_url")
    def _check_worktimes_url(self):
        for requirement in self:
            if requirement.worktimes_url:
                url = urlsplit(requirement.worktimes_url)
                if (
                    url.scheme not in ("https", "http")
                    or not url.hostname
                    or any(char.isspace() for char in requirement.worktimes_url)
                ):
                    raise ValidationError(_("Worktimes benötigt eine vollständige HTTP- oder HTTPS-URL."))

    @api.model_create_multi
    def create(self, vals_list):
        milestone_ids = {vals.get("milestone_id") for vals in vals_list if vals.get("milestone_id")}
        default_id = self.env.context.get("default_milestone_id")
        if default_id:
            milestone_ids.add(default_id)
        self.env["gc.requirement.milestone"].browse(milestone_ids)._lock_planning()
        return super().create(vals_list)

    def write(self, vals):
        if {"milestone_id", "product_id", "state", "active"} & vals.keys():
            self.check_access("write")
            milestones = self.milestone_id | self.env["gc.requirement.milestone"].browse(
                vals.get("milestone_id") or []
            )
            milestones._lock_planning()
        return super().write(vals)
