#!/usr/bin/env python3
"""Resolve COCO image file_name entries against known local image roots."""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import unquote


LABEL_STUDIO_PREFIX = re.compile(r"^[0-9a-f]{8}__", re.IGNORECASE)
DEFAULT_COCO = "data/annotations/eval-webcamoid-obs-studio-2026-05-17-11-06-20/coco.json"
DEFAULT_ROOTS = [
    "data/frames/webcamoid",
    "data/frames/obs-studio-2026-05-17-11-06-20",
]


@dataclass
class ResolutionResult:
    file_name: str
    status: str
    matches: list[str]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Resolve COCO image paths against local dataset folders."
    )
    parser.add_argument(
        "--coco",
        default=DEFAULT_COCO,
        help=f"Path to COCO JSON. Default: {DEFAULT_COCO}",
    )
    parser.add_argument(
        "--image-roots",
        nargs="+",
        default=DEFAULT_ROOTS,
        help="Image root folders to search when direct resolution fails.",
    )
    return parser.parse_args()


def decode_candidate_name(file_name: str) -> str:
    basename = Path(file_name).name
    decoded = unquote(basename)
    return LABEL_STUDIO_PREFIX.sub("", decoded)


def direct_path_candidates(file_name: str) -> list[Path]:
    decoded = unquote(file_name)
    candidates = [Path(decoded).expanduser()]

    # Label Studio COCO exports can contain paths like
    # ../../home/user/project/data/frames/dataset/frame_000001.jpg.
    # Treat the embedded /home/... suffix as the intended absolute path.
    for marker in ("/home/", "/tmp/"):
        if marker in decoded and not decoded.startswith(marker):
            candidates.append(Path(decoded[decoded.index(marker) :]))

    return candidates


def collect_root_files(image_roots: list[Path]) -> dict[str, list[Path]]:
    by_name: dict[str, list[Path]] = {}
    for root in image_roots:
        if not root.exists():
            continue
        for path in root.rglob("*"):
            if not path.is_file():
                continue
            by_name.setdefault(path.name, []).append(path)
    return by_name


def resolve_one(file_name: str, image_roots: list[Path], by_name: dict[str, list[Path]]) -> ResolutionResult:
    direct_matches: list[Path] = []

    for direct_path in direct_path_candidates(file_name):
        if direct_path.exists():
            direct_matches.append(direct_path.resolve())

    if not direct_matches:
        for root in image_roots:
            candidate = root / file_name
            if candidate.exists():
                direct_matches.append(candidate.resolve())

    if len(direct_matches) == 1:
        return ResolutionResult(file_name=file_name, status="resolved", matches=[str(direct_matches[0])])
    if len(direct_matches) > 1:
        return ResolutionResult(
            file_name=file_name,
            status="ambiguous",
            matches=[str(path) for path in sorted(direct_matches)],
        )

    normalized_name = decode_candidate_name(file_name)
    fallback_matches = by_name.get(normalized_name, [])

    if len(fallback_matches) == 1:
        return ResolutionResult(
            file_name=file_name,
            status="resolved",
            matches=[str(fallback_matches[0].resolve())],
        )
    if len(fallback_matches) > 1:
        return ResolutionResult(
            file_name=file_name,
            status="ambiguous",
            matches=[str(path.resolve()) for path in sorted(fallback_matches)],
        )
    return ResolutionResult(file_name=file_name, status="unresolved", matches=[])


def main() -> int:
    args = parse_args()
    project_root = Path(__file__).resolve().parents[1]
    coco_path = (project_root / args.coco).resolve()
    image_roots = [(project_root / root).resolve() for root in args.image_roots]

    data = json.loads(coco_path.read_text(encoding="utf-8"))
    images = data.get("images", [])
    by_name = collect_root_files(image_roots)

    results = [
        resolve_one(image["file_name"], image_roots=image_roots, by_name=by_name)
        for image in images
    ]

    resolved = [result for result in results if result.status == "resolved"]
    unresolved = [result for result in results if result.status == "unresolved"]
    ambiguous = [result for result in results if result.status == "ambiguous"]

    print(f"COCO file: {coco_path}")
    print("Image roots:")
    for root in image_roots:
        print(f"  - {root}")
    print()
    print(f"Total images: {len(results)}")
    print(f"Resolved images: {len(resolved)}")
    print(f"Unresolved images: {len(unresolved)}")
    print(f"Ambiguous images: {len(ambiguous)}")

    if unresolved:
        print()
        print("Unresolved entries:")
        for result in unresolved:
            print(f"  - {result.file_name}")

    if ambiguous:
        print()
        print("Ambiguous entries:")
        for result in ambiguous:
            print(f"  - {result.file_name}")
            for match in result.matches:
                print(f"      {match}")

    return 1 if unresolved or ambiguous else 0


if __name__ == "__main__":
    raise SystemExit(main())
