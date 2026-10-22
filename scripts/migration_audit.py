"""Read-only Odoo-shell preservation audit; never a database migration engine.

Run only on an authorized isolated copy. Inventories contain IDs and hashes,
not ticket/customer text. Keep them outside Git and treat them as private data.
"""

import base64
import hashlib
import json


def _digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, default=str).encode()).hexdigest()


def _inventory(records, fields):
    result = {}
    for row in records.read(fields):
        normalized = {}
        for name in fields:
            value = row[name]
            field = records._fields[name]
            if field.type == "many2one":
                value = value[0] if value else False
            elif field.type in ("many2many", "one2many"):
                value = sorted(value)
            normalized[name] = value
        result[str(row["id"])] = _digest(normalized)
    return result


def capture(env, user_ids):
    """Capture all app records, including archived originals, in canonical form.

    Elevated reads are confined to this administrator CLI script. Public addon
    methods still run without sudo for each explicitly supplied test identity.
    """
    if not user_ids:
        raise ValueError("Supply approved test identities, including allowed and denied ticket readers")
    admin = env(su=True, context=dict(env.context, active_test=False, lang="en_US"))
    requirements = admin["gc.requirement"].search([], order="id")
    sources = admin["gc.requirement.ticket.source"].search([], order="id")
    messages = admin["mail.message"].search(
        [("model", "=", "gc.requirement"), ("res_id", "in", requirements.ids)]
    )
    messages |= admin["mail.message"].search(
        [
            ("model", "=", "helpdesk.ticket"),
            ("res_id", "in", sources.ticket_id.ids),
            ("subtype_id", "=", admin.ref("mail.mt_note").id),
        ]
    )
    attachments = (
        admin["ir.attachment"].search(
            [("res_model", "=", "gc.requirement"), ("res_id", "in", requirements.ids)]
        )
        | messages.attachment_ids
    )
    result = {
        "format": 1,
        "requirements": _inventory(
            requirements,
            [
                "name",
                "reference",
                "description",
                "request_type",
                "state",
                "priority",
                "product_id",
                "category_id",
                "assigned_user_id",
                "creator_user_id",
                "active",
                "affected_version",
                "implemented_version",
                "implementation_note",
                "development_url",
                "implemented_on",
                "decision_reason",
                "manual_customer_ids",
                "merged_into_id",
            ],
        ),
        "products": _inventory(
            admin["gc.requirement.product"].search([]), ["name", "active", "sequence", "description"]
        ),
        "categories": _inventory(
            admin["gc.requirement.category"].search([]),
            ["name", "active", "sequence", "product_id", "parent_id"],
        ),
        "sources": _inventory(
            sources,
            [
                "requirement_id",
                "ticket_id",
                "description_snapshot",
                "captured_at",
                "captured_by_id",
                "origin_requirement_id",
            ],
        ),
        "linked_tickets": _inventory(
            sources.ticket_id,
            ["name", "description", "partner_id", "team_id", "stage_id", "priority", "active"],
        ),
        "messages": _inventory(
            messages,
            [
                "model",
                "res_id",
                "body",
                "subject",
                "author_id",
                "date",
                "message_type",
                "subtype_id",
                "attachment_ids",
            ],
        ),
        "attachments": {
            str(attachment.id): _digest(
                [
                    attachment.res_model,
                    attachment.res_id,
                    attachment.name,
                    attachment.mimetype,
                    hashlib.sha256(base64.b64decode(attachment.datas or b"")).hexdigest(),
                ]
            )
            for attachment in attachments
        },
        "followers": _inventory(
            admin["mail.followers"].search(
                [("res_model", "=", "gc.requirement"), ("res_id", "in", requirements.ids)]
            ),
            ["res_model", "res_id", "partner_id", "subtype_ids"],
        ),
        "activities": _inventory(
            admin["mail.activity"].search(
                [("res_model", "=", "gc.requirement"), ("res_id", "in", requirements.ids)]
            ),
            ["res_id", "activity_type_id", "user_id", "summary", "note", "date_deadline"],
        ),
        "xmlids": {
            row.name: [row.model, row.res_id, row.noupdate]
            for row in admin["ir.model.data"].search([("module", "=", "gc_requirements")])
        },
        "permissions": {},
    }
    tracking = messages.tracking_value_ids
    result["tracking"] = _inventory(
        tracking,
        sorted(
            name
            for name, field in tracking._fields.items()
            if field.store and name not in {"id", "create_uid", "create_date", "write_uid", "write_date"}
        ),
    )
    protected_models = admin["ir.model"].search(
        ["|", ("model", "like", "gc.requirement%"), ("model", "=", "helpdesk.ticket")]
    )
    result["acls"] = _inventory(
        admin["ir.model.access"].search([("model_id", "in", protected_models.ids)]),
        ["model_id", "group_id", "active", "perm_read", "perm_write", "perm_create", "perm_unlink"],
    )
    rules = admin["ir.rule"].search([("model_id", "in", protected_models.ids)])
    rule_groups = "group_ids" if "group_ids" in rules._fields else "groups"
    definitions = _inventory(
        rules, ["model_id", "active", "domain_force", "perm_read", "perm_write", "perm_create", "perm_unlink"]
    )
    result["rules"] = {
        str(rule.id): [definitions[str(rule.id)], sorted(rule[rule_groups].ids)] for rule in rules
    }
    # Normalize the upstream group-field rename only in this offline tool.
    group_users_field = "all_user_ids" if "all_user_ids" in admin["res.groups"]._fields else "users"
    result["membership"] = {
        xmlid: sorted(admin.ref(xmlid)[group_users_field].ids)
        for xmlid in ("gc_requirements.group_user", "gc_requirements.group_config")
    }
    for user_id in sorted(set(user_ids)):
        user = env["res.users"].browse(user_id).exists()
        if not user:
            raise ValueError("Missing test identity: %s" % user_id)
        records = env["gc.requirement"].with_user(user).with_context(active_test=False)
        visible = records.search([]).ids if records.has_access("read") else []
        authorized = {
            str(record.id): sorted(row["ticket_id"] for row in record.get_authorized_sources())
            for record in records.browse(visible)
        }
        result["permissions"][str(user_id)] = {
            "requirements": visible,
            "sources": authorized,
            "raw_read": env["gc.requirement.ticket.source"].with_user(user).has_access("read"),
        }
    sequence = admin.ref("gc_requirements.sequence_requirement")
    result["sequence"] = {
        "id": sequence.id,
        "code": sequence.code,
        "prefix": sequence.prefix,
        "padding": sequence.padding,
        "next": sequence.number_next_actual,
    }
    return result


def verify(env, baseline):
    """Fail on any preservation/access difference; never modify or repair data."""
    current = capture(env, [int(value) for value in baseline["permissions"]])
    differences = []
    for section, expected in baseline.items():
        if section == "sequence":
            if current[section]["next"] < expected["next"]:
                differences.append("sequence: counter moved backwards")
            expected = {key: value for key, value in expected.items() if key != "next"}
            actual = {key: value for key, value in current[section].items() if key != "next"}
        else:
            actual = current[section]
        if actual != expected:
            differences.append(section)
    if differences:
        raise ValueError("Preservation audit failed: %s" % ", ".join(differences))
    return True
