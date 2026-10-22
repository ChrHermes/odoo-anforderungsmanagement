import re

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, UserError


PRODUCT_DEFAULTS = (
    ("product_node", "GridCal Node", "#0068b1", 10),
    ("product_operator", "GridCal Operator", "#40d0d7", 20),
    ("product_core", "GridCal Core", "#4a0a7c", 30),
    ("product_nexus", "GridCal Nexus", "#c51a82", 40),
    ("product_general", "GridCal Allgemeines", "#fa4d0f", 50),
)


class RequirementProduct(models.Model):
    _name = "gc.requirement.product"
    _description = "Anforderungsprodukt"
    _order = "sequence, name, id"

    name = fields.Char(string="Produkt", required=True, translate=True)
    active = fields.Boolean(default=True, string="Aktiv")
    sequence = fields.Integer(default=10, string="Reihenfolge")
    description = fields.Text(string="Beschreibung", translate=True)
    color_hex = fields.Char(string="Produktfarbe (Hex)", help="Optionaler Farbwert im Format #RRGGBB.")
    color_text = fields.Char(string="Kontrastfarbe", compute="_compute_color_text")

    @api.constrains("color_hex")
    def _check_color_hex(self):
        for product in self:
            if product.color_hex and not re.fullmatch(r"#[0-9a-fA-F]{6}", product.color_hex):
                raise ValidationError(_("Die Produktfarbe muss ein Hex-Wert im Format #RRGGBB sein."))

    @api.depends("color_hex")
    def _compute_color_text(self):
        def luminance(color):
            channels = [int(color[index : index + 2], 16) / 255 for index in (1, 3, 5)]
            linear = [
                value / 12.92 if value <= 0.04045 else ((value + 0.055) / 1.055) ** 2.4 for value in channels
            ]
            return sum(value * weight for value, weight in zip(linear, (0.2126, 0.7152, 0.0722), strict=True))

        dark = luminance("#212529")
        for product in self:
            background = luminance(product.color_hex or "#6c757d")
            white_ratio = 1.05 / (background + 0.05)
            dark_ratio = (max(background, dark) + 0.05) / (min(background, dark) + 0.05)
            product.color_text = "#ffffff" if white_ratio >= dark_ratio else "#212529"

    @api.model
    def _ensure_default_products(self):
        """Install/upgrade only: adopt existing seeds, fill missing colors, never reset edits."""
        products = self.with_context(active_test=False, lang=False)
        for xmlid, name, color, sequence in PRODUCT_DEFAULTS:
            product = self.env.ref("gc_requirements." + xmlid, raise_if_not_found=False)
            if product and product._name != self._name:
                raise ValidationError(_("Die Produktreferenz %(reference)s ist ungültig.", reference=xmlid))
            if not product:
                # Reuse a manually created matching product, including archived ones.
                product = products.search([("name", "=", name)], order="id", limit=1)
                if not product:
                    product = products.create({"name": name, "sequence": sequence})
                self.env["ir.model.data"].create(
                    {
                        "module": "gc_requirements",
                        "name": xmlid,
                        "model": self._name,
                        "res_id": product.id,
                        "noupdate": True,
                    }
                )
            if not product.color_hex:
                product.color_hex = color

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
