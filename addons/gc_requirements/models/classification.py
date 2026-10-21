from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, UserError


class RequirementProduct(models.Model):
    _name = "gc.requirement.product"
    _description = "Anforderungsprodukt"
    _order = "sequence, name, id"

    name = fields.Char(string="Produkt", required=True, translate=True)
    active = fields.Boolean(default=True, string="Aktiv")
    sequence = fields.Integer(default=10, string="Reihenfolge")
    description = fields.Text(string="Beschreibung", translate=True)

    @api.ondelete(at_uninstall=False)
    def _prevent_deletion(self):
        raise UserError(_("Bitte archivieren Sie Produkte, statt sie zu löschen."))


class RequirementCategory(models.Model):
    _name = "gc.requirement.category"
    _description = "Funktionsbereich"
    _parent_store = True
    _rec_name = "complete_name"
    _order = "sequence, name, id"

    name = fields.Char(string="Funktionsbereich", required=True, translate=True)
    product_id = fields.Many2one(
        "gc.requirement.product", string="Produkt", required=True, ondelete="restrict", index=True
    )
    parent_id = fields.Many2one(
        "gc.requirement.category", string="Übergeordneter Bereich", ondelete="restrict", index=True
    )
    parent_path = fields.Char(index=True)
    child_ids = fields.One2many("gc.requirement.category", "parent_id", string="Unterbereiche")
    active = fields.Boolean(default=True, string="Aktiv")
    sequence = fields.Integer(default=10, string="Reihenfolge")
    complete_name = fields.Char(string="Pfad", compute="_compute_complete_name", store=True, recursive=True)
    selectable = fields.Boolean(
        string="Auswählbar", compute="_compute_selectable", store=True, recursive=True
    )

    @api.depends("active", "product_id.active", "parent_id.selectable")
    def _compute_selectable(self):
        for category in self:
            category.selectable = (
                category.active
                and category.product_id.active
                and (not category.parent_id or category.parent_id.selectable)
            )

    @api.depends("name", "parent_id.complete_name", "product_id.name")
    def _compute_complete_name(self):
        for category in self:
            prefix = category.parent_id.complete_name or category.product_id.name
            category.complete_name = "%s / %s" % (prefix, category.name)

    @api.constrains("parent_id", "product_id")
    def _check_tree(self):
        if self._has_cycle():
            raise ValidationError(_("Ein Funktionsbereich darf keinen Kreis bilden."))
        for category in self:
            if category.parent_id and category.parent_id.product_id != category.product_id:
                raise ValidationError(_("Über- und Unterbereich müssen zum selben Produkt gehören."))
            if any(
                child.product_id != category.product_id
                for child in category.with_context(active_test=False).child_ids
            ):
                raise ValidationError(_("Unterbereiche müssen zum selben Produkt gehören."))

    def write(self, vals):
        if "product_id" in vals:
            changing = self.filtered(lambda c: c.product_id.id != vals["product_id"])
            if changing:
                subtree = self.with_context(active_test=False).search([("id", "child_of", changing.ids)])
                # A classification must not become invalid outside requirement.write().
                if (
                    self.env["gc.requirement"]
                    .sudo()
                    .with_context(active_test=False)
                    .search_count([("category_id", "in", subtree.ids)], limit=1)
                ):
                    raise ValidationError(
                        _(
                            "Dieser Bereich ist zugeordnet. Ein Produktwechsel benötigt eine geprüfte Migration."
                        )
                    )
        return super().write(vals)

    @api.ondelete(at_uninstall=False)
    def _prevent_deletion(self):
        raise UserError(_("Bitte archivieren Sie Funktionsbereiche, statt sie zu löschen."))
