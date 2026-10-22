from odoo.exceptions import AccessError, UserError, ValidationError
from odoo.tests import Form, tagged

from .common import RequirementCase


@tagged("post_install", "-at_install")
class TestRequirements(RequirementCase):
    def test_native_form_creation(self):
        form = Form(self.Requirement)
        form.name = "Native Formularerfassung"
        form.product_id = self.node
        form.request_type = "feature"
        form.description = "<p>Redaktionell im Formular erfasst.</p>"
        requirement = form.save()
        self.assertRegex(requirement.reference, r"^REQ-\d{4,}$")
        self.assertEqual(requirement.creator_user_id, self.app_user)

    def test_reference_required_content_and_priority(self):
        first = self.make_requirement()
        second = self.make_requirement()
        self.assertRegex(first.reference, r"^REQ-\d{4,}$")
        self.assertNotEqual(first.reference, second.reference)
        self.assertEqual(first.priority, "0")
        for priority in ("0", "1", "2", "3"):
            first.priority = priority
        with self.assertRaises(ValueError), self.cr.savepoint():
            first.priority = "4"
        for bad in ("", "<p><br></p>", "<p> </p>"):
            with self.assertRaises(ValidationError), self.cr.savepoint():
                self.make_requirement(description=bad)
        for key in ("name", "description", "request_type", "product_id"):
            with self.assertRaises(ValidationError), self.cr.savepoint():
                self.make_requirement(**{key: False})
            with self.assertRaises(ValidationError), self.cr.savepoint():
                first.write({key: False})
        with self.assertRaises(ValidationError), self.cr.savepoint():
            first.write({"reference": "REQ-9999"})
        with self.assertRaises(ValidationError), self.cr.savepoint():
            self.make_requirement(reference="REQ-9999")
        with self.assertRaises(AccessError), self.cr.savepoint():
            self.Requirement.with_user(self.outsider).create(self.values())

    def test_classification_acl_and_consistency(self):
        node_base = self.env.ref("gc_requirements.category_node_base")
        operator_base = self.env.ref("gc_requirements.category_operator_base")
        self.assertNotEqual(node_base, operator_base)
        req = self.make_requirement(category_id=node_base.id)
        with self.assertRaises(ValidationError), self.cr.savepoint():
            req.category_id = operator_base
        with self.assertRaises(AccessError), self.cr.savepoint():
            node_base.with_user(self.app_user).write({"name": "Nicht erlaubt"})
        with self.assertRaises(ValidationError), self.cr.savepoint():
            node_base.with_user(self.config_user).parent_id = operator_base
        with self.assertRaises(UserError), self.cr.savepoint():
            node_base.with_user(self.config_user).parent_id = node_base
        with self.assertRaises(ValidationError), self.cr.savepoint():
            node_base.with_user(self.config_user).product_id = self.operator
        node_base.with_user(self.config_user).active = False
        self.assertEqual(req.category_id, node_base)
        req.write({"category_id": node_base.id, "name": "Bestehende Zuordnung erhalten"})
        self.assertFalse(self.env.ref("gc_requirements.category_node_meters").selectable)
        with self.assertRaises(ValidationError), self.cr.savepoint():
            self.make_requirement(category_id=node_base.id)

    def test_archive_restore_and_delete_denial(self):
        req = self.make_requirement()
        req.action_archive()
        self.assertNotIn(req, self.Requirement.search([]))
        self.assertIn(req, self.Requirement.with_context(active_test=False).search([]))
        req.action_unarchive()
        self.assertTrue(req.active)
        with self.assertRaises(UserError), self.cr.savepoint():
            req.unlink()
        with self.assertRaises(UserError), self.cr.savepoint():
            req.sudo().unlink()

    def test_views_and_seed_upgrade_protection(self):
        for kind in ("form", "list", "kanban", "search"):
            self.Requirement.get_view(view_type=kind)
        seeds = self.env["ir.model.data"].search(
            [
                ("module", "=", "gc_requirements"),
                ("model", "in", ["gc.requirement.product", "gc.requirement.category"]),
            ]
        )
        self.assertEqual(len(seeds), 20)
        self.assertTrue(all(seeds.mapped("noupdate")))
