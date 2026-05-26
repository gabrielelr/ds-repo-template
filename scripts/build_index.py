#!/usr/bin/env python3
"""
Build `index.toon` — single token-efficient aggregator dei metadata componenti.

Output: 4 sezioni
  - meta (totali, generatedAt)
  - components (tabular)
  - antiPatternsGlobal (tabular: scenario, components, count)
  - dependencyGraph (list: parent -> [nested components])

Escludes cartelle che iniziano con `_` (es. `_example`).

Usage:
  python scripts/build_index.py            # scrive index.toon in root
  python scripts/build_index.py --dry-run  # stampa, non scrive
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
COMPONENTS_DIR = REPO_ROOT / "components"
OUTPUT_FILE = REPO_ROOT / "index.toon"
TOON_ENCODER_PATH = REPO_ROOT / "skills" / "codebase-index" / "scripts"

sys.path.insert(0, str(TOON_ENCODER_PATH))
from index_codebase import TOONEncoder  # noqa: E402


def iter_component_metadata():
    if not COMPONENTS_DIR.is_dir():
        return
    for slug_dir in sorted(COMPONENTS_DIR.iterdir()):
        if not slug_dir.is_dir() or slug_dir.name.startswith("_"):
            continue
        meta_path = slug_dir / "docs" / "metadata.json"
        if not meta_path.is_file():
            continue
        try:
            with meta_path.open() as f:
                yield slug_dir.name, json.load(f)
        except json.JSONDecodeError as e:
            print(f"  ❌ {slug_dir.name}: metadata.json non valido ({e})", file=sys.stderr)


def build_index() -> dict:
    components_rows = []
    anti_patterns_by_scenario = {}
    dependency_graph = []
    full_count = scaffold_count = 0

    for slug, meta in iter_component_metadata():
        comp = meta.get("component") or {}
        status = meta.get("status", "unknown")
        if status == "full":
            full_count += 1
        elif status == "scaffold":
            scaffold_count += 1

        components_rows.append({
            "slug": meta.get("slug") or slug,
            "name": comp.get("name") or slug,
            "category": comp.get("category") or "",
            "type": comp.get("type") or "",
            "status": status,
            "lastUpdated": meta.get("lastUpdated") or "",
        })

        for ap in (meta.get("usage") or {}).get("antiPatterns") or []:
            scenario = ap.get("scenario") or ""
            if not scenario:
                continue
            anti_patterns_by_scenario.setdefault(scenario, []).append(slug)

        nested = (meta.get("composition") or {}).get("nestedComponents") or []
        if nested:
            dependency_graph.append({"parent": slug, "nests": nested})

    anti_patterns_global = [
        {
            "scenario": scenario,
            "components": ",".join(sorted(set(slugs))),
            "count": len(set(slugs)),
        }
        for scenario, slugs in sorted(anti_patterns_by_scenario.items())
    ]

    return {
        "meta": {
            "generatedAt": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
            "totalComponents": len(components_rows),
            "full": full_count,
            "scaffold": scaffold_count,
        },
        "components": components_rows,
        "antiPatternsGlobal": anti_patterns_global,
        "dependencyGraph": dependency_graph,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true", help="Stampa senza scrivere")
    args = parser.parse_args()

    print("🔍 Costruisco l'index dai metadata...")
    index = build_index()
    print(f"   {index['meta']['totalComponents']} componenti "
          f"({index['meta']['full']} full, {index['meta']['scaffold']} scaffold)")
    print(f"   {len(index['antiPatternsGlobal'])} antiPattern scenarios globali")
    print(f"   {len(index['dependencyGraph'])} componenti con nestedComponents")

    toon = TOONEncoder().encode(index)

    if args.dry_run:
        print("\n📄 Contenuto index.toon (dry-run):\n")
        print(toon)
        return

    OUTPUT_FILE.write_text(toon + "\n", encoding="utf-8")
    size_kb = OUTPUT_FILE.stat().st_size / 1024
    print(f"\n✅ Scritto {OUTPUT_FILE.relative_to(REPO_ROOT)} ({size_kb:.1f} KB)")


if __name__ == "__main__":
    main()
