"""Synthetic upgrade fixture; only invoked inside the isolated contract DB."""

import base64
import json

from odoo import Command


def check_environment(env):
    assert env.cr.dbname == "gc_requirements_contract", "Not the disposable contract database"
    module = env["ir.module.module"].search([("name", "=", "helpdesk")])
    assert "synthetic" in module.shortdesc.lower(), "Never run this fixture against Enterprise/customer data"


def prepare(env, audit_capture):
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
                "category_id": env.ref("gc_requirements.category_node_base").id,
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
    survivor = requirement.copy({"name": "Synthetic surviving requirement"})
    survivor.link_ticket(ticket.id)
    second_ticket = ticket.copy({"name": "Synthetic second upgrade ticket"})
    requirement.link_ticket(second_ticket.id)
    manual_customer = env["res.partner"].create({"name": "Synthetic manual customer"})
    requirement.write({"manual_customer_ids": [Command.link(manual_customer.id)], "state": "planned"})
    requirement.message_post(body="Synthetic history preserved through upgrade")
    activity = (
        env["mail.activity"]
        .with_user(actor)
        .create(
            {
                "res_model_id": env["ir.model"]._get_id("gc.requirement"),
                "res_id": requirement.id,
                "activity_type_id": env.ref("mail.mail_activity_data_todo").id,
                "user_id": actor.id,
                "summary": "Synthetic manual activity",
            }
        )
    )
    attachment = env["ir.attachment"].create(
        {
            "name": "synthetic-upgrade.txt",
            "datas": base64.b64encode(b"synthetic upgrade evidence"),
            "res_model": "gc.requirement",
            "res_id": requirement.id,
        }
    )
    env["gc.requirement.merge"].with_user(actor).create(
        {
            "source_id": requirement.id,
            "target_id": survivor.id,
            "confirmed": True,
        }
    ).action_apply()
    denied = actor.copy({"name": "Synthetic denied reader", "login": "synthetic-denied-reader"})
    env["ir.rule"].create(
        {
            "name": "Synthetic upgrade exact ticket restriction",
            "model_id": env["ir.model"]._get_id("helpdesk.ticket"),
            "domain_force": "[('id', '=', %s)] if user.id == %s else [(1, '=', 1)]" % (ticket.id, denied.id),
        }
    )
    parameters = env["ir.config_parameter"]
    for key, value in {
        "requirement_id": requirement.id,
        "attachment_id": attachment.id,
        "reference": requirement.reference,
        "actor_id": actor.id,
        "denied_id": denied.id,
        "survivor_id": survivor.id,
        "activity_id": activity.id,
    }.items():
        parameters.set_param("gc_requirements.contract." + key, value)
    # Persist creation first: native mail deliberately suppresses tracking of
    # changes made within the original creation transaction.
    env.cr.commit()
    survivor.write({"priority": "2", "assigned_user_id": actor.id})
    survivor._track_finalize()
    assert survivor.sudo().message_ids.tracking_value_ids, "Fixture must contain structured history"
    baseline = audit_capture(env, [actor.id, denied.id])
    parameters.set_param("gc_requirements.contract.audit", json.dumps(baseline))
    env.cr.commit()
    print("CONTRACT_UPGRADE_PREPARED")


def verify(env, audit_verify):
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
        .with_context(active_test=False)
        .browse(int(parameters.get_param("gc_requirements.contract.requirement_id")))
    )
    assert requirement.reference == parameters.get_param("gc_requirements.contract.reference")
    rows = requirement.get_authorized_sources()
    assert len(rows) == 2 and "UPGRADE_IMMUTABLE_SNAPSHOT" in rows[0]["description_snapshot"]
    attachment = env["ir.attachment"].browse(
        int(parameters.get_param("gc_requirements.contract.attachment_id"))
    )
    assert base64.b64decode(attachment.datas) == b"synthetic upgrade evidence"
    assert attachment.res_id == requirement.id
    baseline = json.loads(parameters.get_param("gc_requirements.contract.audit"))
    audit_verify(env, baseline)
    assert not requirement.active and requirement.merged_into_id.id == int(
        parameters.get_param("gc_requirements.contract.survivor_id")
    )
    assert (
        env["mail.activity"]
        .browse(int(parameters.get_param("gc_requirements.contract.activity_id")))
        .exists()
    )
    assert env.ref("gc_requirements.menu_root").name == "Anforderungen"
    assert env["ir.module.module"].search([("name", "=", "gc_requirements")]).shortdesc == "Anforderungen"

    # Prove that the auditor fails closed, rather than merely writing a marker.
    class ProbeRollback(Exception):
        pass

    for section, record, values in (
        ("requirements", requirement, {"name": "Synthetic deliberate preservation failure"}),
        ("attachments", attachment, {"datas": base64.b64encode(b"deliberate corruption")}),
    ):
        try:
            with env.cr.savepoint():
                record.write(values)
                try:
                    audit_verify(env, baseline)
                except ValueError as error:
                    assert section in str(error)
                else:
                    raise AssertionError("Audit failed to detect " + section)
                raise ProbeRollback()
        except ProbeRollback:
            pass
    audit_verify(env, baseline)
    print(
        "CONTRACT_UPGRADE_VERIFIED: naming, hierarchy, references, snapshots/provenance, customers, merge originals, history, activities, physical attachments, memberships and access boundaries; negative audit probes passed"
    )
