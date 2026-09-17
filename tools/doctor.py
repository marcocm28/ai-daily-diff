"""Read-only local prerequisite check; never prints credentials or installs software."""
from __future__ import annotations

import importlib.metadata
import importlib.util
import pathlib
import shutil
import sys


def main() -> int:
    root = pathlib.Path(__file__).resolve().parent.parent
    missing = []
    print(f"Python {sys.version.split()[0]} (CI: 3.12)")
    for line in (root / "requirements.txt").read_text(encoding="utf-8").splitlines():
        if not line or line.startswith("#"):
            continue
        name, required = line.split("==", 1)
        try:
            installed = importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError:
            installed = "MISSING"
        print(f"{name}: {installed} (required {required})")
        if installed != required:
            missing.append(name)
    for command in ("git", "bash", "codex", "ffmpeg"):
        found = shutil.which(command)
        if command == "bash" and not found and shutil.which("git"):
            bundled = pathlib.Path(shutil.which("git")).parent.parent / "bin/bash.exe"
            found = str(bundled) if bundled.exists() else None
        print(f"{command}: {found or 'MISSING'}")
        if not found:
            missing.append(command)
    # Start the driver only when explicitly running this diagnostic. No browser launched.
    if importlib.util.find_spec("playwright"):
        try:
            from playwright.sync_api import sync_playwright
            with sync_playwright() as playwright:
                path = pathlib.Path(playwright.chromium.executable_path)
                present = path.is_file()
                print(f"Chromium: {'installed' if present else 'MISSING'} ({path})")
                if not present:
                    missing.append("chromium")
        except Exception as exc:
            print(f"Chromium check unavailable: {type(exc).__name__}: {exc}")
            missing.append("chromium-check")
    if missing:
        print("Needs attention: " + ", ".join(missing))
        return 1
    print("Local prerequisites OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
