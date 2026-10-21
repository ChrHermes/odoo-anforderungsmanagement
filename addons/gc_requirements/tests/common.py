from odoo.tests.common import TransactionCase, new_test_user


class RequirementCase(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.app_user = new_test_user(cls.env, login="gc_pilot", groups="base.group_user,gc_requirements.group_user")
        cls.config_user = new_test_user(cls.env, login="gc_config", groups="base.group_user,gc_requirements.group_config")
        cls.outsider = new_test_user(cls.env, login="gc_outsider", groups="base.group_user")
        cls.node = cls.env.ref("gc_requirements.product_node")
        cls.operator = cls.env.ref("gc_requirements.product_operator")
        cls.Requirement = cls.env["gc.requirement"].with_user(cls.app_user)

    @classmethod
    def values(cls, **overrides):
        return dict({"name": "Synthetische Anforderung", "description": "<p>Redaktionell geprüfter Testinhalt.</p>", "request_type": "feature", "product_id": cls.node.id}, **overrides)

    def make_requirement(self, **overrides):
        return self.Requirement.create(self.values(**overrides))
