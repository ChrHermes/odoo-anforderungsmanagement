"""Check and neutralize only the local UI database; no production entry point."""

import json
from pathlib import Path

from odoo.tools import config


def verify_local(env):
    if env.cr.dbname != "gc_requirements_dev":
        raise RuntimeError("Local development database required")
    assert config["dbfilter"] == "^gc_requirements_dev$"
    assert config["max_cron_threads"] == 0
    assert config["smtp_server"] == "127.0.0.1" and config["smtp_port"] == 1
    assert not config["list_db"]
    params = env["ir.config_parameter"]
    assert params.get_param("gc_local_dev.seeded") == "True", (
        "Seed incomplete; inspect seed.log or reset local data"
    )
    env["ir.cron"].search([]).write({"active": False})
    env["ir.mail_server"].search([]).write({"active": False})
    assert not env["ir.cron"].search_count([])
    assert not env["ir.mail_server"].search_count([])
    assert not env["mail.mail"].search_count([("state", "=", "sent")])
    user = env.ref("gc_local_dev.developer")
    assert not user.share and user.has_group("gc_requirements.group_config")
    requirements = env["gc.requirement"].with_user(user)
    assert requirements.with_context(active_test=False).search_count([]) >= 8
    requirement = env.ref("gc_local_dev.requirement_1").with_user(user)
    assert requirement.get_authorized_sources()
    assert env.ref("gc_requirements.menu_root").with_user(user).name == "Anforderungen"
    modules = env["ir.module.module"].search_read(
        [("name", "in", ["gc_requirements", "gc_local_dev", "helpdesk", "web_enterprise"])],
        ["name", "state", "installed_version"],
    )
    assert all(row["state"] == "installed" for row in modules if row["name"] != "web_enterprise")
    # Persist synthetic-state edits only; no arbitrary sudo/RPC surface added.
    env.cr.commit()
    print("LOCAL_DEV_VERIFIED", json.dumps(modules))
    Path("/var/lib/odoo/local-dev-verified.txt").write_text("local UI database verified\n")


verify_local(env)  # noqa: F821 - Odoo shell supplies env
