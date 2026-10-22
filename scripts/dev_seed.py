"""Execute only inside the isolated local-development Odoo shell."""

import json
from pathlib import Path

from odoo import Command, fields


def seed(env):
    if env.cr.dbname != "gc_requirements_dev":
        raise RuntimeError("Local development database required")
    params = env["ir.config_parameter"]
    if params.get_param("gc_local_dev.seeded"):
        print("LOCAL_DEV_ALREADY_SEEDED")
        return
    credentials = json.loads(Path("/run/local-dev/credentials.json").read_text())
    env["ir.cron"].with_context(active_test=False).search([]).write({"active": False})
    env["ir.mail_server"].with_context(active_test=False).search([]).write({"active": False})
    params.set_param("web.base.url", "http://localhost:8069")
    params.set_param("web.base.url.freeze", "True")
    params.set_param("database.is_neutralized", "True")
    env.ref("base.main_company").write({"name": "Lokale UI-Demo – synthetische Daten", "email": False})
    env.ref("base.user_admin").with_context(no_reset_password=True).write(
        {"password": credentials["admin_password"]}
    )
    groups = [
        env.ref(xmlid).id
        for xmlid in ("base.group_user", "gc_requirements.group_config", "helpdesk.group_helpdesk_user")
    ]
    user = (
        env["res.users"]
        .with_context(no_reset_password=True)
        .create(
            {
                "name": "Lokale Entwicklung",
                "login": credentials["login"],
                "password": credentials["password"],
                "email": credentials["login"],
                "lang": "de_DE",
                "tz": "Europe/Berlin",
                "notification_type": "inbox",
                "action_id": env.ref("gc_requirements.action_requirements").id,
                "groups_id": [Command.set(groups)],
            }
        )
    )

    # Stable local-only XML IDs support inspection without fixed database IDs.
    def remember(name, record):
        env["ir.model.data"].create(
            {
                "module": "gc_local_dev",
                "name": name,
                "model": record._name,
                "res_id": record.id,
                "noupdate": True,
            }
        )
        return record

    remember("developer", user)
    company = remember(
        "customer", env["res.partner"].create({"name": "Beispielenergie (synthetisch)", "is_company": True})
    )
    contact_a = env["res.partner"].create({"name": "Demo Kontakt A", "parent_id": company.id})
    contact_b = env["res.partner"].create({"name": "Demo Kontakt B", "parent_id": company.id})
    other = env["res.partner"].create({"name": "Demo Netzbetrieb (synthetisch)", "is_company": True})
    team = env["helpdesk.team"].create({"name": "Lokaler synthetischer Support"})
    stage = env["helpdesk.stage"].create({"name": "Neu (lokal)"})
    tickets = []
    for index, partner in enumerate((contact_a, contact_b, other), 1):
        ticket = (
            env["helpdesk.ticket"]
            .with_context(mail_create_nosubscribe=True)
            .create(
                {
                    "name": "Demo-Ticket %s: Messwerte und Bedienung" % index,
                    "description": "<p>Synthetische Originalbeschreibung %s. Keine Kundendaten.</p>" % index,
                    "partner_id": partner.id,
                    "team_id": team.id,
                    "stage_id": stage.id,
                    "priority": str(index % 4),
                }
            )
        )
        tickets.append(remember("ticket_%s" % index, ticket))
    examples = [
        ("new", "0", "Messgerät in der Übersicht ergänzen", "node", "node_meters", "feature"),
        ("review", "1", "IEC104-Einstellungen verständlicher benennen", "node", "node_iec104", "improvement"),
        ("evaluated", "2", "Mailing von Ereignissen zusammenfassen", "node", "node_mailing", "feature"),
        ("planned", "3", "Asset-Filter für große Anlagen", "operator", "operator_assets", "feature"),
        (
            "in_progress",
            "2",
            "Suchfeld in der Bedienoberfläche verbessern",
            "operator",
            "operator_ui",
            "improvement",
        ),
        ("implemented", "1", "Versionsanzeige im Core korrigieren", "core", None, "bug"),
        ("deferred", "0", "Modbus-Diagnose erweitern", "node", "node_modbus", "feature"),
        ("rejected", "1", "Doppelte Anlagenliste vermeiden", "operator", "operator_ui", "improvement"),
    ]
    for index, (state, priority, title, product, category, kind) in enumerate(examples, 1):
        values = {
            "name": title,
            "description": "<p>Redaktionell formuliertes Entwicklungsbeispiel: %s.</p><p>Nur synthetische Daten zum Ausprobieren der Anwendung.</p>"
            % title,
            "request_type": kind,
            "product_id": env.ref("gc_requirements.product_" + product).id,
            "category_id": env.ref("gc_requirements.category_" + category).id if category else False,
            "priority": priority,
            "assigned_user_id": user.id if index % 2 else False,
        }
        requirement = env["gc.requirement"].with_user(user).create(values)
        remember("requirement_%s" % index, requirement)
        if index <= 3:
            requirement.link_ticket(tickets[(index - 1) % 3].id)
        if index == 1:
            requirement.link_ticket(tickets[1].id)
            requirement.write({"manual_customer_ids": [Command.link(other.id)]})
        changes = {"state": state}
        if state in ("deferred", "rejected"):
            changes["decision_reason"] = "Synthetische Entscheidung: zunächst andere Themen priorisiert."
        if state == "implemented":
            changes.update(
                {
                    "implemented_version": "DEMO-1.0",
                    "implementation_note": "Nur im synthetischen Beispiel veröffentlicht.",
                }
            )
        requirement.write(changes)
        if index == 1:
            requirement.message_post(
                body="Interne Beispielnotiz für die lokale Entwicklung.", subtype_xmlid="mail.mt_note"
            )
            requirement.activity_schedule(
                "mail.mail_activity_data_todo",
                user_id=user.id,
                summary="Beispiel manuell prüfen",
                date_deadline=fields.Date.today(),
            )
    params.set_param("gc_local_dev.seeded", "True")
    env.cr.commit()
    print("LOCAL_DEV_SEEDED: 8 requirements, all states/priorities, 3 tickets, manual activity")


def seed_ux_demo(env):
    """Add only missing local synthetic UX fixtures, including a denied reader."""
    if env.cr.dbname != "gc_requirements_dev":
        raise RuntimeError("Local development database required")
    helpdesk = env["ir.module.module"].search([("name", "=", "helpdesk")])
    if "ui-demo" not in helpdesk.with_context(lang="en_US").shortdesc.lower():
        return
    credentials = json.loads(Path("/run/local-dev/credentials.json").read_text())

    def remember(name, record):
        env["ir.model.data"].create(
            {
                "module": "gc_local_dev",
                "name": name,
                "model": record._name,
                "res_id": record.id,
                "noupdate": True,
            }
        )
        return record

    restricted = env.ref("gc_local_dev.restricted_developer", raise_if_not_found=False)
    if not restricted:
        restricted = (
            env["res.users"]
            .with_context(no_reset_password=True)
            .create(
                {
                    "name": "Demo ohne Helpdesk-Rechte",
                    "login": credentials["restricted_login"],
                    "password": credentials["restricted_password"],
                    "email": credentials["restricted_login"],
                    "lang": "de_DE",
                    "notification_type": "inbox",
                    "action_id": env.ref("gc_requirements.action_requirements").id,
                    "groups_id": [
                        Command.set(
                            [
                                env.ref(key).id
                                for key in (
                                    "base.group_user",
                                    "base.group_allow_export",
                                    "gc_requirements.group_user",
                                )
                            ]
                        )
                    ],
                }
            )
        )
        remember("restricted_developer", restricted)
    user = env.ref("gc_local_dev.developer")
    for key, title in (
        ("nexus", "Nexus-Schnittstellen übersichtlicher darstellen"),
        ("general", "Produktübergreifende Hinweise verständlicher formulieren"),
    ):
        xmlid = "requirement_ux_" + key
        if not env.ref("gc_local_dev." + xmlid, raise_if_not_found=False):
            product = env.ref("gc_requirements.product_" + key, raise_if_not_found=False)
            if product:
                remember(
                    xmlid,
                    env["gc.requirement"]
                    .with_user(user)
                    .create(
                        {
                            "name": title,
                            "description": "<p>Synthetisches UX-Beispiel ohne Funktionsbereich und ohne Ticketquelle.</p>",
                            "product_id": product.id,
                            "request_type": "improvement" if key == "general" else "feature",
                        }
                    ),
                )
    requirement = env.ref("gc_local_dev.requirement_1")
    assert requirement.with_user(user).get_authorized_sources(), "Demo needs a nonempty authorized snapshot"
    assert not requirement.with_user(restricted).get_authorized_sources(), (
        "Restricted demo must not read snapshots"
    )
    env.cr.commit()
    print("LOCAL_UX_DEMO_VERIFIED: linked snapshot, denied reader and available product examples")


def seed_planning_demo(env):
    """Add release fixtures once, preserving every existing interactive record."""
    if env.cr.dbname != "gc_requirements_dev":
        raise RuntimeError("Local development database required")
    module = env["ir.module.module"].search([("name", "=", "helpdesk")])
    if "ui-demo" not in module.with_context(lang="en_US").shortdesc.lower():
        return
    params = env["ir.config_parameter"]
    if params.get_param("gc_local_dev.planning_seeded"):
        return
    user = env.ref("gc_local_dev.developer")
    plans = [
        ("node", "GridCal Node 2027.1", "release", "planned"),
        ("operator", "GridCal Operator 2027.1", "release", "active"),
        ("core", "GridCal Core 2027.2", "release", "draft"),
        ("nexus", "GridCal Nexus 2026.4", "release", "done"),
        (None, "SCADA-Ausbau Q2 2027", "milestone", "planned"),
        ("general", "Übergreifende Dokumentation", "milestone", "cancelled"),
    ]
    for index, (product, title, kind, state) in enumerate(plans, 1):
        product_record = env.ref("gc_requirements.product_" + product) if product else False
        plan = (
            env["gc.requirement.milestone"]
            .with_user(user)
            .create(
                {
                    "name": title,
                    "kind": kind,
                    "product_id": product_record.id if product_record else False,
                    "version": "2027.1" if kind == "release" else False,
                    "planned_start": "2027-01-01",
                    "planned_date": "2027-06-30",
                    "description": "<p>Synthetische lokale Releaseplanung; keine Produktzusage.</p>",
                    "assigned_user_id": user.id,
                }
            )
        )
        env["ir.model.data"].create(
            {
                "module": "gc_local_dev",
                "name": "planning_%s" % index,
                "model": plan._name,
                "res_id": plan.id,
                "noupdate": True,
            }
        )
        for offset, req_state in enumerate(("planned", "implemented")):
            req_product = product_record or env.ref(
                "gc_requirements.product_" + ("node" if offset else "operator")
            )
            env["gc.requirement"].with_user(user).create(
                {
                    "name": "Planungsdemo: %s – %s" % (title, req_state),
                    "description": "<p>Eigenständiges synthetisches Planungsbeispiel.</p>",
                    "request_type": "feature" if offset else "improvement",
                    "product_id": req_product.id,
                    "milestone_id": plan.id,
                    "state": req_state,
                    "implemented_version": "DEMO-PUBLISHED" if req_state == "implemented" else False,
                }
            )
        if state == "done":
            env["gc.requirement.milestone.complete"].with_user(user).create(
                {
                    "milestone_id": plan.id,
                    "confirmed": True,
                }
            ).action_apply()
        else:
            plan.state = state
    params.set_param("gc_local_dev.planning_seeded", "True")
    env.cr.commit()
    print("LOCAL_PLANNING_DEMO_SEEDED: 6 plans, 12 requirements, published release with open work")


seed(env)  # noqa: F821 - Odoo shell supplies env
seed_ux_demo(env)  # noqa: F821
seed_planning_demo(env)  # noqa: F821
