#!/usr/bin/env python3
"""Dependency-free syntax/packaging checks. Does not certify an Odoo install."""

import ast
import csv
from pathlib import Path
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
ADDON = ROOT / "addons/gc_requirements"


def main():
    python_files = (
        list((ROOT / "addons").rglob("*.py"))
        + list((ROOT / "scripts").glob("*.py"))
        + list((ROOT / "tests").rglob("*.py"))
    )
    for path in python_files:
        compile(path.read_text(), str(path), "exec")
    manifest = ast.literal_eval((ADDON / "__manifest__.py").read_text())
    contract_manifest = ast.literal_eval((ROOT / "tests/contract_addons/helpdesk/manifest.py.in").read_text())
    assert "synthetic" in contract_manifest["name"].lower()
    assert not list((ROOT / "tests").rglob("__manifest__.py")), (
        "Test contracts must not shadow Enterprise modules during addon discovery"
    )
    assert manifest["version"].startswith("18.0.")
    assert manifest["application"] and manifest["installable"]
    assert set(manifest["depends"]) == {"base", "mail", "helpdesk"}
    loaded = set(manifest["data"])
    assets = {name for bundle in manifest.get("assets", {}).values() for name in bundle}
    for name in assets:
        assert (ADDON.parent / name).is_file(), name
    for name in loaded:
        assert (ADDON / name).is_file(), name
    xml_files = list(ADDON.rglob("*.xml"))
    for path in xml_files:
        root = ET.parse(path).getroot()
        if path.is_relative_to(ADDON / "static"):
            assert root.tag == "templates", path
            assert "gc_requirements/" + str(path.relative_to(ADDON)) in assets, path
            continue
        assert root.tag == "odoo", path
        assert not root.findall(".//tree"), "Odoo 18 needs <list>"
        assert str(path.relative_to(ADDON)) in loaded, "Unloaded XML: %s" % path
    for name in ("initial_products.xml", "sequence.xml"):
        assert ET.parse(ADDON / "data" / name).getroot().get("noupdate") == "1"
    with (ADDON / "security/ir.model.access.csv").open() as handle:
        access = list(csv.DictReader(handle))
    assert not any(row["model_id:id"] == "model_gc_requirement_ticket_source" for row in access), (
        "Raw snapshots must have no generic ACL"
    )
    assert all(row["group_id:id"].startswith("gc_requirements.") for row in access)
    assert all(row["perm_unlink"] == "0" for row in access if row["model_id:id"] == "model_gc_requirement")
    print(
        "PASS: %s Python files, %s XML files, manifest/data/ACL packaging"
        % (len(python_files), len(xml_files))
    )


if __name__ == "__main__":
    main()
