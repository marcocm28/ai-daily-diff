"""Brand assets, shared by every renderer.

Images are inlined as data URIs rather than referenced by path, because the deck is rendered
from a temporary directory and relative paths would break. It also means slides.pdf and the
video frames are self-contained.

Vendor logos (assets/logos/vendors/<slug>.png) are optional and used strictly as identifiers —
never as the subject of a slide or thumbnail, never next to a judgement about that vendor. See
prompts/title.md and PROJECT_INSTRUCTIONS.md §8.4. When a vendor logo is absent, the item falls
back to a monospace text chip, which is why a missing file is never an error.
"""
from __future__ import annotations

import base64
import functools
import mimetypes
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent

# Carried in brief.md and the YouTube description. The current track needs no attribution
# (confirmed 2026-09-03), so this line is a courtesy, not an obligation — but keeping it here,
# in one place, means the brief and the YouTube description can never disagree. If the track is
# ever swapped for a Creative Commons one, this line stops being optional.
# License of record: assets/music/CREDITS.md.
MUSIC_CREDIT = "Music: \"Nebula\" by The Grey Room / Density & Time, from the YouTube Audio Library."
LOGOS = ROOT / "assets" / "logos"
CHANNEL_LOGO = LOGOS / "channel" / "aidailydiff-logo.png"
VENDOR_DIR = LOGOS / "vendors"


@functools.lru_cache(maxsize=64)
def data_uri(path: pathlib.Path) -> str | None:
    """Returns a data: URI for the file, or None if it isn't there."""
    if not path.exists():
        return None
    mime = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
    return f"data:{mime};base64," + base64.b64encode(path.read_bytes()).decode("ascii")


def channel_logo() -> str | None:
    return data_uri(CHANNEL_LOGO)


def vendor_logo(slug: str | None) -> str | None:
    """assets/logos/vendors/<slug>.png (or .svg), if we have the official asset for it."""
    if not slug:
        return None
    for ext in (".png", ".svg", ".webp"):
        uri = data_uri(VENDOR_DIR / f"{slug}{ext}")
        if uri:
            return uri
    return None


def decorate(items: list[dict]) -> list[dict]:
    """Adds org_logo_uri to each item, leaving the text fallback to the template."""
    return [{**item, "org_logo_uri": vendor_logo(item.get("org"))} for item in items]
