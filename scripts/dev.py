#!/usr/bin/env python3
"""Manage ONLY the persistent local Odoo 18 UI stack, never the contract stack."""

import argparse
import ast
import json
import os
from pathlib import Path
import secrets
import shutil
import subprocess
import sys
import time
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
LOCAL = ROOT / ".local/dev"
PROJECT = "gc-requirements-dev"
DATABASE = "gc_requirements_dev"
BRANCH = "codex/initial-mvp"
CONFIG = "--config=/etc/odoo/dev.conf"
COMPOSE = [
    "docker",
    "compose",
    "--project-directory",
    str(ROOT),
    "-p",
    PROJECT,
    "-f",
    str(ROOT / "compose.dev.yml"),
]
DEMO_LABEL = "EINGESCHRÄNKTE UI-DEMO · synthetisches Helpdesk · keine Enterprise-Abnahme"
ENTERPRISE_LABEL = "LOKALE ENTWICKLUNG · Enterprise-Quellen · ausschließlich synthetische Daten"


def execute(args, *, input_text=None, log=None):
    environment = os.environ.copy()
    environment["GC_ENTERPRISE_PATH"] = settings().get("enterprise_path") or str(LOCAL / "empty-enterprise")
    if log:
        target = LOCAL / "logs" / (log + ".log")
        target.parent.mkdir(parents=True, exist_ok=True)
        print("Odoo:", log, "→", target.relative_to(ROOT), flush=True)
        with target.open("w") as output:
            result = subprocess.run(
                args, cwd=ROOT, env=environment, input=input_text, text=True, stdout=output, stderr=output
            )
        if result.returncode:
            raise RuntimeError("Fehlgeschlagen: %s (Exit %s). Siehe %s" % (log, result.returncode, target))
    else:
        subprocess.run(args, cwd=ROOT, env=environment, input=input_text, text=True, check=True)


def settings():
    path = LOCAL / "settings.json"
    return json.loads(path.read_text()) if path.exists() else {}


def branch_guard():
    branch = subprocess.check_output(["git", "branch", "--show-current"], cwd=ROOT, text=True).strip()
    if branch != BRANCH:
        raise RuntimeError("Nur auf dem autorisierten Development-Branch %s ausführen." % BRANCH)


def private_file(path, content):
    path.write_text(content)
    # Docker's non-root Odoo user must read the individual bind-mounted files.
    # The containing host directory is 0700; no secrets are versioned.
    path.chmod(0o644)


def prepare(mode=None, enterprise_path=None):
    previous = settings()
    supplied = enterprise_path or os.environ.get("GC_ENTERPRISE_PATH")
    selected = mode or ("enterprise" if supplied else previous.get("mode", "demo"))
    path = str(Path(supplied).expanduser().resolve()) if supplied else previous.get("enterprise_path", "")
    if previous and (selected != previous["mode"] or path != previous.get("enterprise_path", "")):
        raise RuntimeError(
            "Modus/Pfadwechsel benötigt zuerst 'reset --yes' im bisherigen Modus. Keine DB-Konvertierung."
        )
    if selected == "enterprise":
        if not path:
            raise RuntimeError("Enterprise benötigt --enterprise-path mit lizenzierten Odoo-18-Quellen.")
        manifest = Path(path) / "helpdesk/__manifest__.py"
        if not manifest.is_file() or not (Path(path) / "web_enterprise/__manifest__.py").is_file():
            raise RuntimeError(
                "Enterprise-Pfad muss helpdesk und web_enterprise enthalten; kein synthetischer Fallback."
            )
        values = ast.literal_eval(manifest.read_text())
        version = str(values.get("version", "1.0"))
        # Official addons also use short native versions such as 1.0.
        explicit_major = int(version.split(".")[0])
        if (explicit_major >= 10 and explicit_major != 18) or values.get("license") != "OEEL-1":
            raise RuntimeError(
                "Erwartet wird das offizielle lizenzierte Odoo-18-Enterprise-Helpdesk (OEEL-1)."
            )
    elif path:
        raise RuntimeError("Enterprise-Pfad kann nicht im Demomodus verwendet werden.")
    LOCAL.mkdir(parents=True, exist_ok=True)
    LOCAL.chmod(0o700)
    (LOCAL / "empty-enterprise").mkdir(exist_ok=True)
    info = {"mode": selected, "enterprise_path": path, "database": DATABASE, "project": PROJECT}
    private_file(LOCAL / "settings.json", json.dumps(info, indent=2) + "\n")
    credential_file = LOCAL / "credentials.json"
    if not credential_file.exists():
        credentials = {
            "login": "entwicklung@example.invalid",
            "password": secrets.token_urlsafe(24),
            "admin_password": secrets.token_urlsafe(32),
            "database_password": secrets.token_urlsafe(32),
            "master_password": secrets.token_urlsafe(32),
        }
        private_file(credential_file, json.dumps(credentials, indent=2) + "\n")
    credentials = json.loads(credential_file.read_text())
    private_file(LOCAL / "postgres-password", credentials["database_password"] + "\n")
    addons = LOCAL / "addons"
    addons.mkdir(exist_ok=True)
    helper = addons / "gc_local_dev"
    shutil.copytree(ROOT / "dev/templates/gc_local_dev", helper, dirs_exist_ok=True)
    shutil.copyfile(helper / "manifest.py.in", helper / "__manifest__.py")
    label = DEMO_LABEL if selected == "demo" else ENTERPRISE_LABEL
    for file in (helper / "views.xml", helper / "static/src/banner.xml"):
        file.write_text(file.read_text().replace("__MODE_LABEL__", label))
    if selected == "demo":
        contract = ROOT / "tests/contract_addons/helpdesk"
        synthetic = addons / "helpdesk"
        synthetic.mkdir(exist_ok=True)
        for filename in ("__init__.py", "models.py", "security.xml"):
            shutil.copyfile(contract / filename, synthetic / filename)
        values = ast.literal_eval((contract / "manifest.py.in").read_text())
        values["name"] = "EINGESCHRÄNKTE UI-DEMO: synthetisches Helpdesk (kein Enterprise)"
        values["data"] = ["security.xml", "local_views.xml"]
        (synthetic / "__manifest__.py").write_text(repr(values) + "\n")
        shutil.copyfile(ROOT / "dev/templates/helpdesk_views.xml", synthetic / "local_views.xml")
    elif (addons / "helpdesk").exists():
        raise RuntimeError("Synthetischer Helpdesk-Pfad im Enterprise-Modus gefunden; Start verweigert.")
    addon_paths = ["/mnt/extra-addons", "/mnt/local-addons", "/usr/lib/python3/dist-packages/odoo/addons"]
    if selected == "enterprise":
        addon_paths.insert(0, "/mnt/enterprise")
    config = {
        "addons_path": ",".join(addon_paths),
        "data_dir": "/var/lib/odoo",
        "db_host": "db",
        "db_port": "5432",
        "db_user": "odoo",
        "db_password": credentials["database_password"],
        "db_name": DATABASE,
        "dbfilter": "^" + DATABASE + "$",
        "list_db": "False",
        "admin_passwd": credentials["master_password"],
        "http_interface": "0.0.0.0",
        "http_port": "8069",
        "proxy_mode": "False",
        "workers": "0",
        "max_cron_threads": "0",
        "smtp_server": "127.0.0.1",
        "smtp_port": "1",
        "smtp_ssl": "False",
        "limit_time_real": "180",
    }
    private_file(LOCAL / "odoo.conf", "[options]\n" + "".join("%s = %s\n" % item for item in config.items()))
    print(label, flush=True)


def require_prepared():
    info = settings()
    if info.get("database") != DATABASE or info.get("project") != PROJECT:
        raise RuntimeError(
            "Zuerst 'python3 scripts/dev.py start' ausführen; unbekannte Umgebung wird nicht bedient."
        )


def database_exists():
    environment = os.environ.copy()
    environment["GC_ENTERPRISE_PATH"] = settings().get("enterprise_path") or str(LOCAL / "empty-enterprise")
    result = subprocess.check_output(
        COMPOSE
        + [
            "exec",
            "-T",
            "db",
            "psql",
            "-U",
            "odoo",
            "-d",
            "postgres",
            "-Atc",
            "SELECT 1 FROM pg_database WHERE datname = '%s'" % DATABASE,
        ],
        cwd=ROOT,
        env=environment,
        text=True,
    )
    return result.strip() == "1"


def shell_script(filename, log):
    execute(
        COMPOSE + ["run", "--rm", "-T", "odoo", "shell", CONFIG, "--no-http"],
        input_text=(ROOT / "scripts" / filename).read_text(),
        log=log,
    )


def wait_web():
    deadline = time.monotonic() + 180
    while time.monotonic() < deadline:
        try:
            with urllib.request.urlopen("http://127.0.0.1:8069/web/login", timeout=5) as response:
                if response.status == 200:
                    print("Bereit: http://localhost:8069/local-dev", flush=True)
                    print("Zugang anzeigen: python3 scripts/dev.py credentials", flush=True)
                    return
        except OSError:
            pass
        time.sleep(2)
    raise RuntimeError("Weboberfläche nach 180s nicht erreichbar. Siehe 'python3 scripts/dev.py logs'.")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "command",
        choices=["start", "stop", "update", "reset", "logs", "status", "credentials", "test", "verify"],
    )
    parser.add_argument("--mode", choices=["demo", "enterprise"])
    parser.add_argument("--enterprise-path", help="Lizenzierter lokaler Odoo-18-Enterprise-Addonpfad")
    parser.add_argument(
        "--yes",
        action="store_true",
        help="Nur für reset: lokale Dev-DB UND Filestore unwiderruflich entfernen",
    )
    options = parser.parse_args()
    if options.command in ("start", "update", "reset"):
        branch_guard()
    if options.command == "start":
        prepare(options.mode, options.enterprise_path)
        execute(COMPOSE + ["up", "-d", "--wait", "db"])
        if not database_exists():
            modules = "gc_requirements,gc_local_dev"
            if settings()["mode"] == "enterprise":
                modules += ",web_enterprise"
            execute(
                COMPOSE
                + [
                    "run",
                    "--rm",
                    "-T",
                    "odoo",
                    CONFIG,
                    "-i",
                    modules,
                    "--stop-after-init",
                    "--without-demo=all",
                    "--load-language=de_DE",
                    "--no-http",
                ],
                log="install",
            )
        shell_script("dev_seed.py", "seed")
        shell_script("dev_verify.py", "verify-start")
        execute(COMPOSE + ["up", "-d", "--wait", "web"])
        wait_web()
    elif options.command == "test":
        # Existing isolated suite has its OWN project, database, mounts and cleanup.
        execute([sys.executable, str(ROOT / "scripts/test_contract.py")])
    else:
        require_prepared()
        if options.mode or options.enterprise_path:
            parser.error("Modus/Pfad nur beim ersten start wählen; Wechsel erst nach reset.")
        if options.command == "stop":
            execute(COMPOSE + ["stop"])
        elif options.command == "update":
            prepare()
            execute(COMPOSE + ["up", "-d", "--wait", "db"])
            execute(COMPOSE + ["stop", "odoo"])
            execute(
                COMPOSE
                + [
                    "run",
                    "--rm",
                    "-T",
                    "odoo",
                    CONFIG,
                    "-u",
                    "gc_requirements,gc_local_dev",
                    "--stop-after-init",
                    "--without-demo=all",
                    "--no-http",
                ],
                log="update",
            )
            shell_script("dev_verify.py", "verify-update")
            # Recreate the proxy so Nginx resolves the current Odoo container IP.
            execute(COMPOSE + ["up", "-d", "--wait", "--force-recreate", "web"])
            wait_web()
        elif options.command == "reset":
            if not options.yes:
                parser.error(
                    "reset benötigt --yes; löscht ausschließlich %s DB/Filestore. Danach start." % PROJECT
                )
            execute(COMPOSE + ["down", "--volumes", "--remove-orphans"])
            # Keep credentials and logs; release mode/path only after successful teardown.
            (LOCAL / "settings.json").unlink()
            synthetic = LOCAL / "addons/helpdesk"
            if synthetic.exists():
                shutil.rmtree(synthetic)
            print("Nur lokale Development-Daten entfernt. Neuer Start installiert und seedet erneut.")
        elif options.command == "logs":
            execute(COMPOSE + ["logs", "-f", "--tail=100", "odoo"])
        elif options.command == "status":
            execute(COMPOSE + ["ps"])
        elif options.command == "credentials":
            credentials = json.loads((LOCAL / "credentials.json").read_text())
            print(
                "http://localhost:8069/local-dev\nLogin: %s\nPasswort: %s"
                % (credentials["login"], credentials["password"])
            )
        elif options.command == "verify":
            shell_script("dev_verify.py", "verify")
            wait_web()


if __name__ == "__main__":
    try:
        main()
    except (RuntimeError, subprocess.CalledProcessError) as error:
        print("FEHLER:", error, file=sys.stderr)
        sys.exit(1)
