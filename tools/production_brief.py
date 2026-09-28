"""Print the exact editorial prompts for one playlist, audience and episode format."""
import argparse
import pathlib
import sys

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
    files = content_routing.profile_files(args.playlist, args.audience, args.kind)
    print(f"Production: {args.date}; playlist={args.playlist}; audience={args.audience}; format={args.kind}")
    for name in files:
        print(f"\n## {name}\n")
        print((ROOT / name).read_text(encoding="utf-8"))


if __name__ == "__main__":
    main()
