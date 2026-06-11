#!/usr/bin/env python3
"""Insert a page into the matching docs.json navigation group.

Usage:
    python3 scripts/update_nav.py <target_path> <nav_group>

Example:
    python3 scripts/update_nav.py platform/new-page.mdx "Platform"

The page reference stored in docs.json is the target path without its
extension (Mintlify references pages without the .mdx/.md suffix).
The operation is idempotent: re-running with an already-present page
leaves docs.json unchanged.
"""
import json
import os
import sys

DOCS_JSON = "docs.json"


def page_ref_from_path(target_path: str) -> str:
    """Strip the extension to get the Mintlify page reference."""
    root, _ext = os.path.splitext(target_path)
    return root


def insert_page(docs: dict, nav_group: str, page_ref: str) -> bool:
    """Append page_ref to the matching group's pages. Returns True if changed."""
    groups = docs.get("navigation", {}).get("groups", [])
    for group in groups:
        if group.get("group") == nav_group:
            pages = group.setdefault("pages", [])
            if page_ref in pages:
                return False
            pages.append(page_ref)
            return True
    available = ", ".join(g.get("group", "?") for g in groups)
    raise SystemExit(
        f"Navigation group '{nav_group}' not found in {DOCS_JSON}. "
        f"Available groups: {available}"
    )


def main() -> None:
    if len(sys.argv) != 3:
        raise SystemExit("Usage: update_nav.py <target_path> <nav_group>")

    target_path, nav_group = sys.argv[1], sys.argv[2]
    page_ref = page_ref_from_path(target_path)

    with open(DOCS_JSON, "r", encoding="utf-8") as fh:
        docs = json.load(fh)

    changed = insert_page(docs, nav_group, page_ref)

    if not changed:
        print(f"No nav change: '{page_ref}' already in group '{nav_group}'.")
        return

    with open(DOCS_JSON, "w", encoding="utf-8") as fh:
        json.dump(docs, fh, indent=2, ensure_ascii=False)
        fh.write("\n")

    print(f"Added '{page_ref}' to group '{nav_group}' in {DOCS_JSON}.")


if __name__ == "__main__":
    main()
