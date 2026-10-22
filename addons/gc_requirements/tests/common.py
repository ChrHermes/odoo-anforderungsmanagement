from odoo.tests.common import TransactionCase, new_test_user


class RequirementCase(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        fixture_env = cls.env(context=dict(cls.env.context, no_reset_password=True))
        cls.app_user = new_test_user(
            fixture_env, login="gc_pilot", groups="base.group_user,gc_requirements.group_user"
        )
        cls.config_user = new_test_user(
            fixture_env, login="gc_config", groups="base.group_user,gc_requirements.group_config"
        )
        cls.outsider = new_test_user(fixture_env, login="gc_outsider", groups="base.group_user")
        cls.node = cls.env.ref("gc_requirements.product_node")
        cls.operator = cls.env.ref("gc_requirements.product_operator")
        cls.Requirement = cls.env["gc.requirement"].with_user(cls.app_user)

    @classmethod
    def values(cls, **overrides):
        return dict(
            {
                "name": "Synthetische Anforderung",
                "description": "<p>Redaktionell geprüfter Testinhalt.</p>",
                "request_type": "feature",
                "product_id": cls.node.id,
            },
            **overrides,
        )

    def make_requirement(self, **overrides):
        return self.Requirement.create(self.values(**overrides))


class HelpdeskCase(RequirementCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        fixture_env = cls.env(context=dict(cls.env.context, no_reset_password=True))
        cls.support = new_test_user(
            fixture_env,
            login="gc_support",
            groups="base.group_user,base.group_allow_export,gc_requirements.group_user,helpdesk.group_helpdesk_user",
        )
        cls.limited = new_test_user(
            fixture_env,
            login="gc_limited",
            groups="base.group_user,base.group_allow_export,gc_requirements.group_user,helpdesk.group_helpdesk_user",
        )
        cls.portal = new_test_user(fixture_env, login="gc_portal", groups="base.group_portal")
        cls.company_partner = cls.env["res.partner"].create(
            {"name": "Synthetic Customer GmbH", "is_company": True, "email": "company@example.invalid"}
        )
        cls.contact_a, cls.contact_b = cls.env["res.partner"].create(
            [
                {"name": "Synthetic A", "parent_id": cls.company_partner.id},
                {"name": "Synthetic B", "parent_id": cls.company_partner.id},
            ]
        )
        cls.team = cls.env["helpdesk.team"].sudo().create({"name": "Synthetic Support"})
        cls.ticket_a, cls.ticket_b = (
            cls.env["helpdesk.ticket"]
            .sudo()
            .create(
                [
                    {
                        "name": "SYNTHETIC ALLOWED TICKET",
                        "description": "<p>SNAPSHOT_ALPHA</p>",
                        "partner_id": cls.contact_a.id,
                        "team_id": cls.team.id,
                    },
                    {
                        "name": "SYNTHETIC RESTRICTED TICKET",
                        "description": "<p>SNAPSHOT_SECRET_BETA</p>",
                        "partner_id": cls.contact_b.id,
                        "team_id": cls.team.id,
                    },
                ]
            )
        )
        # A global, conditional rule verifies exact current customized ticket
        # permissions. Group rules alone could be widened by other group rules.
        cls.ticket_rule = cls.env["ir.access"].create(
            {
                "name": "SYNTHETIC exact ticket access boundary",
                "operation": "crud",
                "model_id": cls.env["ir.model"]._get_id("helpdesk.ticket"),
                "domain": "[('id', 'in', %s)] if user.id == %s else [(1, '=', 1)]"
                % ([cls.ticket_a.id], cls.limited.id),
            }
        )

    def linked_requirement(self, **overrides):
        requirement = self.make_requirement(**overrides)
        requirement.with_user(self.support).link_ticket(self.ticket_a.id)
        requirement.with_user(self.support).link_ticket(self.ticket_b.id)
        return requirement
