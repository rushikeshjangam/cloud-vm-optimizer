"""Central AWS safety rules."""

from __future__ import annotations

REQUIRED_TAGS = {
    "Project": "cloud-vm-optimizer",
    "Owner": "college-demo",
    "Environment": "demo",
}


def has_required_tags(tags: list[dict[str, str]] | None) -> bool:
    actual = {tag.get("Key"): tag.get("Value") for tag in tags or []}
    return all(actual.get(key) == value for key, value in REQUIRED_TAGS.items())

