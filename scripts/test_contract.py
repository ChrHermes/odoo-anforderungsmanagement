#!/usr/bin/env python3
"""Reproducible Community ORM contract suite. NOT Enterprise acceptance."""

import argparse
import ast
import io
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tarfile

ROOT = Path(__file__).resolve().parents[1]
COMPOSE = ["docker", "compose", "-p", "gc-requirements-contract", "-f", str(ROOT / "compose.test.yaml")]
ODOO = [
    "--addons-path=/usr/lib/python3/dist-packages/odoo/addons,/mnt/extra-addons,/test-contracts",
    "--db_host=db",
    "--db_user=odoo",
    "--db_password=isolated-test-only",
    "-d",
    "gc_requirements_contract",
]
LOGS = ROOT / ".local/test-results"


def run(args, name, input_text=None, require_tests=False, marker=None):
    print("RUN:", name, flush=True)
    result = subprocess.run(
        args, cwd=ROOT, input=input_text, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT
    )
    LOGS.mkdir(parents=True, exist_ok=True)
    (LOGS / (name + ".log")).write_text(result.stdout)
    summaries = re.findall(r".*(?:tests.result|PERFORMANCE:|CONTRACT_UPGRADE_).*", result.stdout)
    for line in summaries:
        print(line, flush=True)
    valid_summary = re.search(r"0 failed, 0 error\(s\) of ([1-9]\d*) tests", result.stdout)
    if result.returncode or (require_tests and not valid_summary) or (marker and marker not in result.stdout):
        print(result.stdout[-16000:], file=sys.stderr)
        raise RuntimeError("Failed %s; see %s" % (name, LOGS / (name + ".log")))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--keep", action="store_true", help="Keep ONLY the synthetic contract containers/data for inspection"
    )
    parser.add_argument(
        "--baseline-ref", help="Also install a previous Git candidate before testing upgrade to this checkout"
    )
    options = parser.parse_args()
    if options.baseline_ref:
        previous = subprocess.run(
            ["git", "show", options.baseline_ref + ":addons/gc_requirements/__manifest__.py"],
            cwd=ROOT,
            check=True,
            text=True,
            stdout=subprocess.PIPE,
        ).stdout
        old_version = ast.literal_eval(previous)["version"].split(".")[:2]
        new_version = ast.literal_eval((ROOT / "addons/gc_requirements/__manifest__.py").read_text())[
            "version"
        ].split(".")[:2]
        if old_version != new_version:
            parser.error(
                "--baseline-ref requires the same Odoo major; this driver does not migrate core databases"
            )
    run([sys.executable, "scripts/check_static.py"], "static")
    # Keep a Helpdesk-named test addon OUT of versioned Odoo discovery paths.
    # Only this ignored runtime directory receives an actual manifest.
    contract_template = ROOT / "tests/contract_addons/helpdesk"
    generated_contract = ROOT / ".local/contract-addons/helpdesk"
    generated_contract.mkdir(parents=True, exist_ok=True)
    for filename in ("__init__.py", "models.py", "security.xml"):
        shutil.copyfile(contract_template / filename, generated_contract / filename)
    shutil.copyfile(contract_template / "manifest.py.in", generated_contract / "__manifest__.py")
    # This fixed project is exclusively disposable synthetic test state.
    run(COMPOSE + ["down", "--volumes", "--remove-orphans"], "clean-contract")
    try:
        run(COMPOSE + ["up", "-d", "db"], "start-contract")
        run(COMPOSE + ["run", "--rm", "odoo"], "install", require_tests=True)
        if options.baseline_ref:
            archive = subprocess.run(
                ["git", "archive", options.baseline_ref, "addons"],
                cwd=ROOT,
                check=True,
                stdout=subprocess.PIPE,
            )
            baseline = ROOT / ".local/baseline"
            if baseline.exists():
                shutil.rmtree(baseline)
            baseline.mkdir(parents=True)
            with tarfile.open(fileobj=io.BytesIO(archive.stdout)) as files:
                files.extractall(baseline, filter="data")
            run(COMPOSE + ["down", "--volumes", "--remove-orphans"], "clean-baseline")
            run(COMPOSE + ["up", "-d", "db"], "start-baseline")
            run(
                COMPOSE + ["run", "--rm", "-v", str(baseline / "addons") + ":/mnt/extra-addons:ro", "odoo"],
                "baseline-install",
                require_tests=True,
            )
        audit = (ROOT / "scripts/migration_audit.py").read_text()
        fixture = (ROOT / "scripts/contract_upgrade_fixture.py").read_text()
        shell = COMPOSE + ["run", "--rm", "-T", "odoo", "odoo", "shell"] + ODOO + ["--no-http"]
        prepare_shell = shell
        if options.baseline_ref:
            # Before -u, registry code MUST match the installed old schema.
            # Loading today's fields against yesterday's DB can access missing columns.
            prepare_shell = (
                COMPOSE
                + [
                    "run",
                    "--rm",
                    "-T",
                    "-v",
                    str(baseline / "addons") + ":/mnt/extra-addons:ro",
                    "odoo",
                    "odoo",
                    "shell",
                ]
                + ODOO
                + ["--no-http"]
            )
        run(
            prepare_shell,
            "prepare-upgrade",
            audit + "\npreservation_verify = verify\n" + fixture + "\nprepare(env, capture)\n",
            marker="CONTRACT_UPGRADE_PREPARED",
        )
        upgrade = (
            COMPOSE
            + ["run", "--rm", "odoo", "odoo"]
            + ODOO
            + [
                "-u",
                "gc_requirements",
                "--test-enable",
                "--test-tags",
                "/gc_requirements",
                "--stop-after-init",
                "--without-demo=all",
                "--http-port=0",
            ]
        )
        run(upgrade, "upgrade", require_tests=True)
        run(
            shell,
            "verify-upgrade",
            audit + "\npreservation_verify = verify\n" + fixture + "\nverify(env, preservation_verify)\n",
            marker="CONTRACT_UPGRADE_VERIFIED",
        )
        print(
            "PASS: fresh install + tests + edited-data upgrade + tests + preservation checks (synthetic Helpdesk only)",
            flush=True,
        )
    finally:
        if not options.keep:
            run(COMPOSE + ["down", "--volumes", "--remove-orphans"], "cleanup")


if __name__ == "__main__":
    main()
