import datetime as dt
import json
import pathlib
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'src'))
from episode_identity import episode_key
import author
import content_routing


@pytest.mark.parametrize('identity', ['../2026-09-28', '2026-09-29-topic', '2026-09-28-../topic',
                                     '2026-09-28/second', '2026-09-28-Uppercase'])
def test_identity_rejects_wrong_date_and_unsafe_paths(identity):
    with pytest.raises(ValueError):
        episode_key({'date': '2026-09-28', 'episode_id': identity})


def test_extra_scaffold_preserves_same_day_archive_and_requires_current_prompts(tmp_path, monkeypatch):
    inbox = tmp_path / 'inbox'; inbox.mkdir()
    episodes = tmp_path / 'episodes'; episodes.mkdir()
    legacy = episodes / '2026-09-28.json'; legacy.write_text('published immutable bytes')
    monkeypatch.setattr(author, 'INBOX', inbox)
    monkeypatch.setattr(author, 'EPISODES', episodes)
    key = '2026-09-28-codex-mcp'
    (inbox / f'{key}.selected.json').write_text(json.dumps({'selected': [
        {'title': 'MCP feature', 'url': 'https://example.org/feature', 'source': 'primary'}]}))
    path = author.run(dt.date(2026, 9, 28), playlist='agents', audience='builder', episode_id=key)
    draft = json.loads(path.read_text())
    assert path.stem == episode_key(draft) == key
    assert legacy.read_text() == 'published immutable bytes'
    assert draft['production_prompts'] == content_routing.profile_files('agents', 'builder', 'daily')
    assert any('approved' in error for error in content_routing.episode_problems(draft))
    with pytest.raises(SystemExit):
        author.run(dt.date(2026, 9, 28), playlist='agents', audience='builder', episode_id=key)
