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


def _attachment_bytes(attachment):
    if "raw" in attachment._fields:
        value = attachment.raw
        return value.content if hasattr(value, "content") else value or b""
    return base64.b64decode(attachment.datas or b"")


def capture(env, user_ids, *, excluded_security_models=()):
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
                    hashlib.sha256(_attachment_bytes(attachment)).hexdigest(),
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
    if "milestone_id" in requirements._fields:
        result["requirement_planning"] = _inventory(requirements, ["milestone_id", "worktimes_url"])
        milestones = admin["gc.requirement.milestone"].search([], order="id")
        result["milestones"] = _inventory(
            milestones,
            [
                "reference",
                "name",
                "kind",
                "product_id",
                "version",
                "description",
                "planned_start",
                "planned_date",
                "completed_on",
                "state",
                "assigned_user_id",
                "active",
                "requirement_ids",
            ],
        )
        planning_messages = admin["mail.message"].search([("model", "=", "gc.requirement.milestone")])
        messages |= planning_messages
        result["planning_messages"] = _inventory(
            planning_messages, ["body", "author_id", "subtype_id", "res_id"]
        )
        result["planning_followers"] = _inventory(
            admin["mail.followers"].search([("res_model", "=", "gc.requirement.milestone")]),
            ["res_id", "partner_id", "subtype_ids"],
        )
        result["planning_activities"] = _inventory(
            admin["mail.activity"].search([("res_model", "=", "gc.requirement.milestone")]),
            ["res_id", "activity_type_id", "user_id", "summary", "note", "date_deadline"],
        )
        sequence_ms = admin.ref("gc_requirements.sequence_milestone")
        result["planning_sequence"] = {
            "id": sequence_ms.id,
            "prefix": sequence_ms.prefix,
            "padding": sequence_ms.padding,
            "code": sequence_ms.code,
            "next": sequence_ms.number_next_actual,
        }
    tracking = messages.tracking_value_ids
    if "color_hex" in admin["gc.requirement.product"]._fields:
        result["product_colors"] = _inventory(admin["gc.requirement.product"].search([]), ["color_hex"])
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
    protected_models = protected_models.filtered(lambda model: model.model not in excluded_security_models)
    # Canonical policy definitions survive upstream model/field renames. Grouped
    # policies are split per group; any real semantic difference still fails.
    policies = []
    if "ir.access" in admin.registry.models:
        for policy in admin["ir.access"].search(
            [
                (
                    "model_id",
                    "in",
                    protected_models.ids,
                )
            ]
        ):
            policies.append(
                {
                    "model": policy.model_id.model,
                    "group": policy.group_id.id,
                    "kind": "permission" if policy.group_id else "restriction",
                    "operation": policy.operation,
                    "domain": policy.domain or "",
                    "active": policy.active,
                }
            )
    else:
        for policy in admin["ir.model.access"].search(
            [
                (
                    "model_id",
                    "in",
                    protected_models.ids,
                )
            ]
        ):
            policies.append(
                {
                    "model": policy.model_id.model,
                    "group": policy.group_id.id,
                    "kind": "permission",
                    "operation": "".join(
                        letter
                        for letter, name in (
                            ("c", "perm_create"),
                            ("r", "perm_read"),
                            ("u", "perm_write"),
                            ("d", "perm_unlink"),
                        )
                        if policy[name]
                    ),
                    "domain": "",
                    "active": policy.active,
                }
            )
        for policy in admin["ir.rule"].search(
            [
                (
                    "model_id",
                    "in",
                    protected_models.ids,
                )
            ]
        ):
            for group_id in policy.groups.ids or [False]:
                policies.append(
                    {
                        "model": policy.model_id.model,
                        "group": group_id,
                        "kind": "permission" if group_id else "restriction",
                        "operation": "".join(
                            letter
                            for letter, name in (
                                ("c", "perm_create"),
                                ("r", "perm_read"),
                                ("u", "perm_write"),
                                ("d", "perm_unlink"),
                            )
                            if policy[name]
                        ),
                        "domain": policy.domain_force or "",
                        "active": policy.active,
                    }
                )
    result["security"] = sorted(_digest(policy) for policy in policies)
    for name, target in list(result["xmlids"].items()):
        if target[0] in {"ir.access", "ir.model.access", "ir.rule"}:
            # Core migration can change storage model/row IDs, not our XML IDs.
            result["xmlids"][name] = ["access_policy", name, target[2]]
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


def verify(env, baseline, *, allowed_new_product_ids=(), allowed_new_security_models=()):
    """Fail on any preservation/access difference; never modify or repair data."""
    current = capture(
        env,
        [int(value) for value in baseline["permissions"]],
        excluded_security_models=allowed_new_security_models,
    )
    differences = []
    for section, expected in baseline.items():
        if section in ("sequence", "planning_sequence"):
            if current[section]["next"] < expected["next"]:
                differences.append(section + ": counter moved backwards")
            expected = {key: value for key, value in expected.items() if key != "next"}
            actual = {key: value for key, value in current[section].items() if key != "next"}
        elif section == "xmlids":
            actual = {key: current[section].get(key) for key in expected}
        elif section in ("products", "product_colors") and allowed_new_product_ids:
            # Explicitly enumerated additive master data is allowed for a reviewed
            # addon upgrade. Every pre-existing record/hash must still match.
            additions = set(current[section]) - set(expected)
            if not additions.issubset({str(value) for value in allowed_new_product_ids}):
                differences.append(section + ": unexpected new products")
            actual = {key: current[section].get(key) for key in expected}
        else:
            actual = current.get(section)
        if actual != expected:
            differences.append(section)
    if differences:
        raise ValueError("Preservation audit failed: %s" % ", ".join(differences))
    return True
