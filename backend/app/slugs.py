"""Readable post addresses: "Geneva Hosts Data Talks" -> "geneva-hosts-data-talks"."""

import re
import unicodedata
from collections.abc import Callable

MAX_LENGTH = 80


def slugify(text: str) -> str:
    ascii_text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()
    slug = re.sub(r"[^a-z0-9]+", "-", ascii_text.lower()).strip("-")
    return slug[:MAX_LENGTH].rstrip("-") or "post"


def unique_slug(title: str, is_taken: Callable[[str], bool]) -> str:
    """slugify(title), adding -2, -3, ... if that address is already used."""
    base = slugify(title)
    if base.isdigit():
        base = f"post-{base}"  # plain numbers are reserved for old /posts/<id> links
    slug, n = base, 2
    while is_taken(slug):
        slug, n = f"{base}-{n}", n + 1
    return slug
