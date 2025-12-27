#!/usr/bin/env python3
"""
Convert Wappalyzer JSON output to a CycloneDX SBOM (JSON) focusing on JavaScript tech.

Usage:
    python wappalyzer_to_sbom.py wappalyzer.json sbom.json
"""

import json
import sys
import uuid
from datetime import datetime
from pathlib import Path

# Categories that should be treated as JavaScript technologies.
JS_CATEGORY_SLUGS = {
    "javascript-framework",
    "javascript-library",
    "javascript-graphics",
    "programming-language",
    "web-frameworks",
}

JS_CATEGORY_NAMES = {
    "JavaScript Frameworks",
    "JavaScript Libraries",
    "JavaScript Graphics",
    "Programming Languages",
    "Web Frameworks",
}


def is_js_tech(tech: dict) -> bool:
    """Return True if a Wappalyzer technology looks JavaScript-related."""
    categories = tech.get("Categories", [])
    for cat in categories:
        if cat in JS_CATEGORY_NAMES:
            return True
    return False


def build_component_from_tech(name: str, tech: dict, target_url: str) -> dict:
    """Convert a Wappalyzer technology entry into a CycloneDX component."""
    #name = tech.get("name") or "unknown-tech"
    version = None
    if ":" in name:
        name, version = name.split(":", 1)
        version = version.strip()
    website = tech.get("Website")

    component = {
        "type": "library",
        "name": name,
        "bomRef": f"{target_url}::{name}",
    }

    if version:
        component["version"] = str(version)

    if tech.get("CPE"):
        component["cpe"] = tech["CPE"]

    if tech.get("Description"):
        component["description"] = tech["Description"]

    if website:
        component["externalReferences"] = [
            {
                "type": "website",
                "url": website,
            }
        ]

    # You *could* guess a purl from slug (e.g., npm package), but that’s risky.
    # Uncomment and customize if you have a mapping:
    # slug = tech.get("slug")
    # if slug:
    #     component["purl"] = f"pkg:npm/{slug}" + (f"@{version}" if version else "")

    return component


def build_bom(wappalyzer_data) -> dict:
    """Build a minimal CycloneDX 1.4 SBOM from Wappalyzer JSON data."""
    # Normalize: Wappalyzer may return an object or a list of targets
    if isinstance(wappalyzer_data, list):
        targets = wappalyzer_data
    else:
        targets = [wappalyzer_data]

    components = []
    main_components = []

    for target in targets:
        url = target.get("url", "unknown-target")

        # Treat each scanned target as an application component
        app_component = {
            "type": "application",
            "name": url,
            "bomRef": url,
        }
        main_components.append(app_component)

        for tech in target.get("technologies", {}).items():
            name, tech = tech
            #if not is_js_tech(tech):
            #    print(f"Skipping non-JavaScript tech: {name}", file=sys.stderr)
            #    continue
            components.append(build_component_from_tech(name, tech, url))

    bom = {
        "bomFormat": "CycloneDX",
        "specVersion": "1.4",
        "serialNumber": f"urn:uuid:{uuid.uuid4()}",
        "version": 1,
        "metadata": {
            "timestamp": datetime.utcnow().isoformat(timespec="seconds") + "Z",
            "tools": [
                {
                    "vendor": "Wappalyzer",
                    "name": "Wappalyzer technology detection",
                },
                {
                    "vendor": "Custom",
                    "name": "wappalyzer_to_sbom.py converter",
                },
            ],
        },
        "components": components,
    }

    # If there is exactly one main application, put it in metadata.component
    # If more than one, put them into metadata.components
    if len(main_components) == 1:
        bom["metadata"]["component"] = main_components[0]
    elif main_components:
        bom["metadata"]["components"] = main_components

    return bom


def main():
    if len(sys.argv) != 3:
        print("Usage: python wappalyzer_to_sbom.py <wappalyzer.json> <sbom.json>", file=sys.stderr)
        sys.exit(1)

    input_path = Path(sys.argv[1])
    output_path = Path(sys.argv[2])

    try:
        with input_path.open("r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        print(f"Error reading {input_path}: {e}", file=sys.stderr)
        sys.exit(1)

    if not data.get("data", {}).get("technologies"):
        print(f"No technologies found in {input_path}", file=sys.stderr)
        sys.exit(1)
    bom = build_bom(data["data"])

    try:
        with output_path.open("w", encoding="utf-8") as f:
            json.dump(bom, f, indent=2)
    except Exception as e:
        print(f"Error writing {output_path}: {e}", file=sys.stderr)
        sys.exit(1)

    print(f"SBOM written to {output_path.resolve()}")


if __name__ == "__main__":
    main()
