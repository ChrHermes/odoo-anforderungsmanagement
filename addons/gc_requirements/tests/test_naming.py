from odoo.tests import tagged

from .common import RequirementCase


@tagged("post_install", "-at_install")
class TestGermanNaming(RequirementCase):
    def test_german_launcher_actions_groups_and_fields(self):
        self.env["res.lang"]._activate_lang("de_DE")
        self.env["ir.module.module"]._load_module_terms(["gc_requirements"], ["de_DE"])
        for xmlid in (
            "menu_root",
            "menu_requirements",
            "action_requirements",
            "module_category_requirements",
        ):
            self.assertEqual(
                self.env.ref("gc_requirements." + xmlid).with_context(lang="de_DE").name, "Anforderungen"
            )
        for xmlid, name in (
            ("group_user", "Anforderungen: Benutzer"),
            ("group_config", "Anforderungen: Konfiguration"),
        ):
            self.assertEqual(self.env.ref("gc_requirements." + xmlid).with_context(lang="de_DE").name, name)
        module = self.env["ir.module.module"].search([("name", "=", "gc_requirements")])
        self.assertEqual(module.with_context(lang="de_DE").shortdesc, "Anforderungen")
        fields = self.Requirement.with_context(lang="de_DE").fields_get(
            ["name", "state", "request_type", "priority", "activity_ids", "create_date"]
        )
        self.assertEqual(fields["name"]["string"], "Titel")
        self.assertEqual(dict(fields["state"]["selection"])["implemented"], "Umgesetzt")
        self.assertEqual(dict(fields["request_type"]["selection"])["feature"], "Funktionswunsch")
        self.assertEqual(dict(fields["priority"]["selection"])["3"], "Dringend")
        self.assertEqual(fields["activity_ids"]["string"], "Aktivitäten")
        self.assertEqual(fields["create_date"]["string"], "Erstellt am")
