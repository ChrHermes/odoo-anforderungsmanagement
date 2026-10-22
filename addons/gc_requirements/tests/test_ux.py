from odoo.exceptions import AccessError, ValidationError
from odoo.tests import tagged

from .common import HelpdeskCase


@tagged("post_install", "-at_install")
class TestRequirementsUX(HelpdeskCase):
    def test_all_state_groups_in_workflow_order_even_without_records(self):
        expected = [
            "new",
            "review",
            "evaluated",
            "planned",
            "in_progress",
            "implemented",
            "deferred",
            "rejected",
        ]
        # Use an empty domain result, then deliberately create states out of order.
        for state in ("rejected", "planned", "review", "deferred", "new"):
            self.make_requirement(state=state, decision_reason="Synthetic reason", priority="3")
        for domain in ([("id", "=", 0)], [], [("state", "=", "review")]):
            groups = self.Requirement.read_group(domain, ["state"], ["state"], orderby="state asc")
            self.assertEqual([group["state"] for group in groups], expected)

    def test_product_defaults_colors_contrast_and_acl(self):
        expected = {
            "node": ("#0068b1", "#ffffff"),
            "operator": ("#40d0d7", "#212529"),
            "core": ("#4a0a7c", "#ffffff"),
            "nexus": ("#c51a82", "#ffffff"),
            "general": ("#fa4d0f", "#212529"),
        }
        # Upgrade fixtures may contain user colors: verify gap filling in this
        # rolled-back test transaction, without demanding that an upgrade reset them.
        products = self.env["gc.requirement.product"].browse(
            [self.env.ref("gc_requirements.product_" + key).id for key in expected]
        )
        products.write({"color_hex": False})
        products._ensure_default_products()
        for key, (color, foreground) in expected.items():
            product = self.env.ref("gc_requirements.product_" + key)
            self.assertEqual(product.color_hex, color)
            self.assertEqual(product.color_text, foreground)
            if key in ("nexus", "general"):
                category_seeds = self.env["ir.model.data"].search(
                    [("module", "=", "gc_requirements"), ("model", "=", "gc.requirement.category")]
                )
                self.assertFalse(
                    self.env["gc.requirement.category"].search_count(
                        [("id", "in", category_seeds.mapped("res_id")), ("product_id", "=", product.id)]
                    )
                )
                self.make_requirement(product_id=product.id)
        with self.assertRaises(AccessError), self.cr.savepoint():
            self.node.with_user(self.app_user).color_hex = "#123456"
        self.node.with_user(self.config_user).color_hex = "#123456"
        for bad in ("red", "#123", "#12345678", "#12345g", "#000000; color:red"):
            with self.subTest(color=bad), self.assertRaises(ValidationError), self.cr.savepoint():
                self.node.color_hex = bad
        self.node.color_hex = False
        self.assertEqual(self.node.color_text, "#ffffff")

    def test_default_initializer_is_idempotent_and_preserves_edits(self):
        products = self.env["gc.requirement.product"].with_context(active_test=False)
        before = products.search([]).ids
        self.node.write({"color_hex": "#123456", "name": "Umbenanntes Produkt", "sequence": 876})
        products._ensure_default_products()
        products._ensure_default_products()
        self.assertCountEqual(products.search([]).ids, before)
        self.assertEqual(self.node.color_hex, "#123456")
        self.assertEqual(self.node.name, "Umbenanntes Produkt")
        self.assertEqual(self.node.sequence, 876)
        # Simulate an existing manually created Nexus before its XML ID is introduced.
        nexus = self.env.ref("gc_requirements.product_nexus")
        nexus.color_hex = "#abcdef"
        self.env["ir.model.data"].search(
            [("module", "=", "gc_requirements"), ("name", "=", "product_nexus")]
        ).unlink()
        products._ensure_default_products()
        self.assertEqual(self.env.ref("gc_requirements.product_nexus"), nexus)
        self.assertEqual(nexus.color_hex, "#abcdef")
        self.assertCountEqual(products.search([]).ids, before)

    def test_relative_category_and_source_empty_state(self):
        requirement = self.make_requirement(
            category_id=self.env.ref("gc_requirements.category_node_mailing").id
        )
        self.assertEqual(requirement.category_path, "ANALYTIC / Events / Mailing")
        self.assertEqual(requirement.product_color_hex, self.node.color_hex)
        form = self.Requirement.get_view(view_type="form")["arch"]
        self.assertIn("Keine Helpdesk-Tickets verknüpft", form)
        self.assertIn("Ursprüngliche Ticketbeschreibungen anzeigen", form)
        kanban = self.Requirement.get_view(view_type="kanban")["arch"]
        self.assertIn("gc_product_badge", kanban)
        self.assertIn("category_path", kanban)
        self.assertIn("gc_requirement_type_", kanban)
        self.env["gc.requirement.product"].with_user(self.config_user).get_view(view_type="form")

    def test_source_viewer_positive_negative_and_no_requirement_copy(self):
        requirement = self.linked_requirement()
        for user, allowed in ((self.support, True), (self.app_user, False)):
            viewer = (
                self.env["gc.requirement.source.viewer"]
                .with_user(user)
                .create({"requirement_id": requirement.id})
            )
            text = viewer.read(["source_html"])[0]["source_html"]
            self.assertEqual("SNAPSHOT_ALPHA" in text, allowed)
            self.assertEqual("SNAPSHOT_SECRET_BETA" in text, allowed)
        # Ordinary form/read/export contains only editorial fields and aggregate counts.
        rows = requirement.with_user(self.app_user).read()
        self.assertNotIn("SNAPSHOT_ALPHA", str(rows))
        self.assertNotIn("SNAPSHOT_SECRET_BETA", str(rows))
        self.assertNotIn("source_html", requirement.fields_get())
