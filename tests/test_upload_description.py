import pathlib
import sys

import pytest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "src"))
import upload


def episode(**extras):
    return {"date": "2026-09-25", "title": "Model feature explained",
            "items": [{"source_url": "https://example.org/release"}], **extras}


def test_authored_opening_replaces_brief_and_keeps_publication_identity(tmp_path):
    (tmp_path / "brief.md").write_text("INTERNAL BRIEF BODY", encoding="utf-8")
    result = upload.build_description(episode(youtube_description="Model X: a useful new feature."), tmp_path)
    assert result.startswith("Model X: a useful new feature.")
    assert "INTERNAL BRIEF BODY" not in result
    assert "AI Daily Diff episode: 2026-09-25" in result.splitlines()
    assert "https://example.org/release" in result
    assert upload.brand.MUSIC_CREDIT in result
    assert "00:00 Front page" not in result


def test_legacy_long_brief_cannot_truncate_links_credits_or_exceed_limit(tmp_path):
    (tmp_path / "brief.md").write_text("<>" * 6000, encoding="utf-8")
    result = upload.build_description(episode(), tmp_path)
    assert len(result) <= 4900
    assert "<" not in result and ">" not in result
    assert "AI Daily Diff episode: 2026-09-25" in result.splitlines()
    assert "https://example.org/release" in result
    assert upload.brand.MUSIC_CREDIT in result


@pytest.mark.parametrize("bad", ["", "   ", 123, "x" * 2501])
def test_invalid_authored_description_is_rejected(tmp_path, bad):
    with pytest.raises(ValueError, match="youtube_description"):
        upload.build_description(episode(youtube_description=bad), tmp_path)
