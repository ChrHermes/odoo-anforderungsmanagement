"""Synthetic upgrade fixture; only invoked inside the isolated contract DB."""

import base64

from odoo import Command


def check_environment(env):
    assert env.cr.dbname == "gc_requirements_contract", "Not the disposable contract database"
    module = env["ir.module.module"].search([("name", "=", "helpdesk")])
    assert "synthetic" in module.shortdesc.lower(), "Never run this fixture against Enterprise/customer data"


def prepare(env):
    check_environment(env)
    node = env.ref("gc_requirements.product_node")
    node.write({"name": "SYNTHETIC UPGRADE SENTINEL", "sequence": 987})
    category = env.ref("gc_requirements.category_node_modbus")
    category.write({"name": "SYNTHETIC EDITED CATEGORY", "active": False})
    actor = (
        env["res.users"]
        .with_context(no_reset_password=True)
        .create(
            {
                "name": "Synthetic upgrade actor",
                "login": "synthetic-upgrade-actor",
                "email": "upgrade@example.invalid",
                "groups_id": [
                    Command.set(
                        [
                            env.ref(xmlid).id
                            for xmlid in (
                                "base.group_user",
                                "gc_requirements.group_user",
                                "helpdesk.group_helpdesk_user",
                            )
                        ]
                    )
                ],
            }
        )
    )
    requirement = (
        env["gc.requirement"]
        .with_user(actor)
        .create(
            {
                "name": "Synthetic upgrade evidence",
                "description": "<p>Manually authored synthetic description.</p>",
                "product_id": node.id,
                "request_type": "bug",
            }
        )
    )
    team = env["helpdesk.team"].create({"name": "Synthetic upgrade team"})
    ticket = env["helpdesk.ticket"].create(
        {
            "name": "Synthetic upgrade ticket",
            "description": "<p>UPGRADE_IMMUTABLE_SNAPSHOT</p>",
            "team_id": team.id,
        }
    )
    requirement.link_ticket(ticket.id)
    ticket.description = "<p>Later ticket revision</p>"
    attachment = env["ir.attachment"].create(
        {
            "name": "synthetic-upgrade.txt",
            "datas": base64.b64encode(b"synthetic upgrade evidence"),
            "res_model": "gc.requirement",
            "res_id": requirement.id,
        }
    )
    parameters = env["ir.config_parameter"]
    for key, value in {
        "requirement_id": requirement.id,
        "attachment_id": attachment.id,
        "reference": requirement.reference,
        "actor_id": actor.id,
    }.items():
        parameters.set_param("gc_requirements.contract." + key, value)
    env.cr.commit()
    print("CONTRACT_UPGRADE_PREPARED")


def verify(env):
    check_environment(env)
    node = env.ref("gc_requirements.product_node")
    category = env.ref("gc_requirements.category_node_modbus")
    assert node.name == "SYNTHETIC UPGRADE SENTINEL" and node.sequence == 987
    assert category.name == "SYNTHETIC EDITED CATEGORY" and not category.active
    parameters = env["ir.config_parameter"]
    actor = env["res.users"].browse(int(parameters.get_param("gc_requirements.contract.actor_id")))
    requirement = (
        env["gc.requirement"]
        .with_user(actor)
        .browse(int(parameters.get_param("gc_requirements.contract.requirement_id")))
    )
    assert requirement.reference == parameters.get_param("gc_requirements.contract.reference")
    rows = requirement.get_authorized_sources()
    assert len(rows) == 1 and "UPGRADE_IMMUTABLE_SNAPSHOT" in rows[0]["description_snapshot"]
    attachment = env["ir.attachment"].browse(
        int(parameters.get_param("gc_requirements.contract.attachment_id"))
    )
    assert base64.b64decode(attachment.datas) == b"synthetic upgrade evidence"
    assert attachment.res_id == requirement.id
    print("CONTRACT_UPGRADE_VERIFIED: seeds, reference, source snapshot, attachment")
