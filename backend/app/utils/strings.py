from __future__ import annotations

import re
from typing import Iterable


def normalize_column_name(name: str) -> str:
    """Convert arbitrary column names to snake_case ASCII identifiers."""
    if not name:
        return "column"
    # Replace non-word characters with spaces
    cleaned = re.sub(r"[^0-9A-Za-z]+", " ", name)
    cleaned = cleaned.strip().lower()
    if not cleaned:
        return "column"
    # Collapse spaces to single underscore
    parts = re.split(r"\s+", cleaned)
    identifier = "_".join(filter(None, parts))
    identifier = re.sub(r"_+", "_", identifier)
    if identifier[0].isdigit():
        identifier = f"col_{identifier}"
    return identifier


def ensure_unique_names(names: Iterable[str]) -> list[str]:
    """Ensure column names are unique by appending suffixes when needed."""
    seen: dict[str, int] = {}
    unique: list[str] = []
    for name in names:
        base = name
        count = seen.get(base, 0)
        if count:
            new_name = f"{base}_{count}"
        else:
            new_name = base
        seen[base] = count + 1
        unique.append(new_name)
    return unique


__all__ = ["normalize_column_name", "ensure_unique_names"]
