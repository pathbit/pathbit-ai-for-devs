#!/usr/bin/env python3
"""Copy the article 0005 application into a fresh directory for later labs."""

from argparse import ArgumentParser
from pathlib import Path
from shutil import copy2, copytree

ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "0005_sdd_do_vibe_coding_a_engenharia_deterministica"


def prepare(destination: Path) -> None:
    destination = destination.resolve()
    if destination == ROOT or ROOT in destination.parents:
        raise ValueError("Choose a destination outside the repository.")
    destination.mkdir(parents=True, exist_ok=True)
    if any(destination.iterdir()):
        raise ValueError(f"Destination must be empty: {destination}")
    for folder in ("src", "tests"):
        copytree(APP / folder, destination / folder)
    for name in ("package.json", "package-lock.json"):
        copy2(APP / name, destination / name)
    (destination / ".pathbit-aggregator-lab").touch()
    (destination / ".gitignore").write_text(
        "node_modules/\n.env\n.env.*\ndata/\n.pathbit-aggregator-lab\n", encoding="utf-8"
    )


def main() -> None:
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("destination", type=Path)
    args = parser.parse_args()
    try:
        prepare(args.destination)
    except (OSError, ValueError) as exc:
        parser.error(str(exc))
    print(args.destination.resolve())


if __name__ == "__main__":
    main()
