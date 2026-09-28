"""Editorial coverage and persistent topic queues; candidate data is not publication approval."""
import datetime as dt
import hashlib
import json
import pathlib

from radar import canonical_url

SCOPES = {"openai", "anthropic", "google", "repositories", "architectures"}
TOPICS = {"models", "repositories", "architectures", "agents", "guides"}
AUDIENCES = {"everyday", "professional", "builder"}
STATES = {"candidate", "source_verified", "editorial_ready", "queued", "published", "deferred", "rejected"}


def episode_problems(episode):
    if not isinstance(episode.get("date", ""), str) or episode.get("date", "") < "2026-09-28":
        return []
    errors = []
    for field, allowed in (("topics", TOPICS), ("audiences", AUDIENCES)):
        value = episode.get(field)
        if not isinstance(value, list) or not value or any(not isinstance(x, str) or x not in allowed for x in value):
            errors.append(f"{field} requires a nonempty list of supported values")
    audiences = episode.get("audiences")
    if not isinstance(audiences, list) or episode.get("primary_audience") not in audiences:
        errors.append("primary_audience must belong to audiences")
    coverage = episode.get("coverage_review")
    if not isinstance(coverage, dict):
        return errors + ["coverage_review required for new episodes"]
    for scope in sorted(SCOPES):
        review = coverage.get(scope, {})
        if not isinstance(review, dict) or review.get("status") != "checked":
            errors.append(f"coverage_review.{scope} has not been checked")
            continue
        if review.get("decision") not in {"included", "deferred", "rejected", "no_qualifying_news"}:
            errors.append(f"coverage_review.{scope} requires a decision")
        if not isinstance(review.get("reason"), str) or not review["reason"].strip():
            errors.append(f"coverage_review.{scope} requires a reason")
        sources = review.get("sources")
        if not isinstance(sources, list) or not sources:
            errors.append(f"coverage_review.{scope} requires sources")
        else:
            for source in sources:
                try:
                    canonical_url(source)
                except (ValueError, TypeError, AttributeError):
                    errors.append(f"coverage_review.{scope} has an invalid source")
    return errors


def reconcile_queues(folder, episodes, receipts, channel_id):
    """Advance only an explicitly linked episode item, using a verified public receipt."""
    for path in pathlib.Path(folder).glob("*.json"):
        data = json.loads(path.read_text(encoding="utf-8"))
        changed = False
        for entry in data.get("entries", []):
            date = entry.get("episode_date")
            episode = episodes.get(date, {})
            if not any(item.get("id") == entry.get("item_id") and item.get("source_url") == entry.get("url")
                       for item in episode.get("items", [])):
                continue
            receipt = receipts.get(date, {})
            if receipt.get("channel_id") == channel_id and receipt.get("actual_privacy") == "public" and receipt.get("video_id"):
                update = {"state": "published", "publication_url": receipt["url"], "review_required": False}
            elif episode.get("publication", {}).get("ready"):
                update = {"state": "queued"}
            else:
                continue
            if any(entry.get(key) != value for key, value in update.items()):
                entry.update(update)
                changed = True
        if changed:
            path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def topic_for(candidate):
    explicit = candidate.get("topic")
    if isinstance(explicit, str) and explicit in TOPICS:
        return explicit
    if candidate.get("kind") == "research":
        return "architectures"
    if candidate.get("kind") in {"vendor_release", "model_weights", "pricing", "deprecation"}:
        return "models"
    if str(candidate.get("source", "")).startswith(("search:", "github:")):
        return "repositories"
    return "agents"


def update_queues(candidates, folder, date):
    """Merge discovery leads without discarding human review or pretending a push date is a release."""
    folder = pathlib.Path(folder)
    folder.mkdir(parents=True, exist_ok=True)
    buckets = {}
    for topic in sorted(TOPICS):
        path = folder / f"{topic}.json"
        data = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {"topic": topic, "entries": []}
        buckets[topic] = {entry["id"]: entry for entry in data["entries"]}
    for candidate in candidates:
        try:
            url = canonical_url(candidate["url"])
        except (KeyError, ValueError, TypeError, AttributeError):
            continue
        topic = topic_for(candidate)
        ident = hashlib.sha256(url.encode()).hexdigest()[:16]
        existing = buckets[topic].get(ident)
        if existing:
            existing["last_seen"] = date.isoformat()
            continue
        buckets[topic][ident] = {"id": ident, "title": candidate.get("title", ""), "url": url,
            "discovered_at": date.isoformat(), "last_seen": date.isoformat(),
            "reported_date": candidate.get("published_at"), "event_date": None,
            "state": "candidate", "suggested_format": candidate.get("suggested_format", "daily"),
            "source": candidate.get("source", ""), "review_required": True,
            "reason": "Verify actual novelty, source, audience and archive before production."}
    for topic, entries in buckets.items():
        (folder / f"{topic}.json").write_text(json.dumps({"topic": topic, "updated_at": date.isoformat(),
            "entries": list(entries.values())}, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
