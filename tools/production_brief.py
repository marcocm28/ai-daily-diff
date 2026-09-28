"""Print the exact editorial prompts for one playlist, audience and episode format."""
import argparse
import pathlib
import sys
import json

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
import content_routing


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("date")
    parser.add_argument("--playlist", required=True, choices=sorted(content_routing.PROFILES))
    parser.add_argument("--audience", required=True, choices=sorted(content_routing.AUDIENCES))
    parser.add_argument("--kind", required=True, choices=["daily", "method", "deep"])
    args = parser.parse_args()
    suffix = "" if args.kind == "daily" else f".{args.kind}"
    selected_path = ROOT / "data/inbox" / f"{args.date}{suffix}.selected.json"
    selection = json.loads(selected_path.read_text(encoding="utf-8")) if selected_path.exists() else None
    print(content_routing.production_brief(args.date, args.playlist, args.audience, args.kind, selection), end="")


if __name__ == "__main__":
    main()
