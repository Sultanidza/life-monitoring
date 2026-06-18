#!/usr/bin/env python3
"""Build the image-level IoU descriptive report (person-with-guitar).

Turns the per-frame person/guitar IoU analysis into a short, readable report:
frame counts (with/without person-with-guitar), average IoU, the IoU distribution,
and a curated gallery of example frames — confident positives, near-object
false-positive risks, borderline cases, and near-misses. Selected overlay images
are copied into the report folder so they are committable/shareable (the source
overlays live under the gitignored data/metrics/).
"""

from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path


DEFAULT_RELATIONSHIPS = "data/metrics/person_guitar_relationships_expanded_2026_05_29.json"
DEFAULT_THRESHOLD = "data/metrics/person_guitar_iou_threshold_expanded_2026_05_29.json"
DEFAULT_MANIFEST = "data/metrics/person_guitar_relationship_overlays_expanded_2026_05_29/manifest.json"
DEFAULT_OUTPUT = "reports/image-analysis/2026-06-17-image-iou-descriptive-report.md"
DEFAULT_GALLERY = "reports/image-analysis/2026-06-17-gallery"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build the image-level IoU descriptive report.")
    parser.add_argument("--relationships", default=DEFAULT_RELATIONSHIPS)
    parser.add_argument("--threshold", default=DEFAULT_THRESHOLD)
    parser.add_argument("--manifest", default=DEFAULT_MANIFEST)
    parser.add_argument("--output", default=DEFAULT_OUTPUT)
    parser.add_argument("--gallery", default=DEFAULT_GALLERY)
    parser.add_argument("--iou-threshold", type=float, default=0.26)
    return parser.parse_args()


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def histogram_ascii(histogram: list[dict], threshold: float) -> list[str]:
    rows = []
    peak = max((b["count"] for b in histogram), default=1) or 1
    for b in histogram:
        if b["count"] == 0:
            continue
        bar = "#" * round(b["count"] / peak * 40)
        mark = "  <- threshold" if b["lo"] <= threshold < b["hi"] else ""
        rows.append(f"{b['lo']:.2f}-{b['hi']:.2f} | {b['count']:>3} | {bar}{mark}")
    return rows


def pick(frames: list[dict], predicate, key, count: int, reverse: bool = False) -> list[dict]:
    chosen = [f for f in frames if predicate(f)]
    chosen.sort(key=key, reverse=reverse)
    return chosen[:count]


def main() -> int:
    args = parse_args()
    root = Path(__file__).resolve().parents[1]
    rel = load(root / args.relationships)
    thr = load(root / args.threshold)
    manifest = load(root / args.manifest)
    overlay_by_id = {int(o["image_id"]): o for o in manifest["overlays"]}

    frames = rel["frames"]
    summary = rel["summary"]
    dist = thr["distribution"]
    t = args.iou_threshold

    gallery_dir = (root / args.gallery).resolve()
    gallery_dir.mkdir(parents=True, exist_ok=True)
    output_path = (root / args.output).resolve()

    def gallery_entry(frame: dict, tag: str) -> str | None:
        overlay = overlay_by_id.get(int(frame["image_id"]))
        if not overlay:
            return None
        src = Path(overlay["overlay_path"])
        if not src.exists():
            return None
        dst_name = f"{tag}-id{int(frame['image_id']):04d}.jpg"
        shutil.copyfile(src, gallery_dir / dst_name)
        rel_path = f"{Path(args.gallery).name}/{dst_name}"
        return (
            f"- **{tag}** (image {frame['image_id']}): IoU `{frame['pair_iou']:.3f}`, "
            f"guitar-overlap-covered `{frame['guitar_intersection_over_guitar']:.2f}`, "
            f"guitar-center-in-person `{frame['guitar_center_in_person']}`, "
            f"persons `{frame['person_count']}` guitars `{frame['guitar_count']}`\n"
            f"  \n  ![{tag}-{frame['image_id']}]({rel_path})"
        )

    # Example selection (descriptive, no playing/not-playing ground truth).
    both = [f for f in frames if f["both_detected"]]
    confident = pick(both, lambda f: f["playing_candidate"] and f["guitar_center_in_person"],
                     key=lambda f: f["pair_iou"], count=2, reverse=True)
    # Near-object risk: scene has more than one person/guitar, so the chosen pair
    # could be coincidental. Weakest overlap first.
    near_object_fp = pick(
        both,
        lambda f: f["playing_candidate"] and (f["person_count"] > 1 or f["guitar_count"] > 1),
        key=lambda f: f["pair_iou"], count=3)
    borderline_pos = pick(both, lambda f: t <= f["pair_iou"] < t + 0.06,
                          key=lambda f: f["pair_iou"], count=2)
    near_miss = pick(both, lambda f: t - 0.08 <= f["pair_iou"] < t,
                     key=lambda f: f["pair_iou"], count=2, reverse=True)

    lines: list[str] = [
        "# Image-Level IoU Descriptive Report — person with guitar (2026-06-17)",
        "",
        "Descriptive analytics of per-frame person/guitar detections (Grounding DINO).",
        "A frame counts as **person-with-guitar** when the best person and guitar boxes",
        f"overlap with **IoU >= {t:.2f}** (threshold from the IoU distribution via Otsu).",
        "Repo: https://github.com/Sultanidza/life-monitoring",
        "",
        "## Frame counts",
        "",
        f"- Total frames: **{summary['total_images']}**",
        f"- Person AND guitar detected: **{summary['both_detected']}** "
        f"({summary['both_detected_rate']*100:.1f}%)",
        f"- **Person-with-guitar (IoU >= {t:.2f}): {summary['playing_candidates']}** "
        f"({summary['playing_candidate_rate']*100:.1f}% of all frames)",
        f"- Person only: {summary['person_only']}  |  guitar only: {summary['guitar_only']}  |  "
        f"neither: {summary['neither_detected']}",
        f"- Both detected but **not overlapping (IoU = 0)**: {dist['count_iou_zero']} "
        "(co-present but apart — e.g. guitar on a stand)",
        "",
        "## Average IoU (person vs guitar, frames with both)",
        "",
        f"- Mean: **{dist['mean']:.3f}**  |  Median: **{dist['median']:.3f}**",
        f"- p25 / p75: {dist['p25']:.3f} / {dist['p75']:.3f}  |  range {dist['min']:.3f}-{dist['max']:.3f}",
        f"- Recommended threshold (Otsu): **{thr['recommended_iou_threshold']:.3f}**",
        "",
        "### IoU distribution",
        "",
        "```",
        "IoU range   | cnt | histogram",
        *histogram_ascii(dist["histogram"], t),
        "```",
        "",
        "### Threshold sweep (frames counted as person-with-guitar)",
        "",
        "| IoU threshold | frames | share of all |",
        "|---|---|---|",
    ]
    for row in thr["threshold_sweep"]:
        lines.append(f"| {row['iou_threshold']:.2f} | {row['frames_person_with_guitar']} | "
                     f"{row['share_of_all_frames']*100:.1f}% |")

    lines += [
        "",
        "## Decision rule",
        "",
        f"`person-with-guitar` = best person/guitar pair has IoU >= {t:.2f}. This replaced an",
        "earlier center-distance heuristic; IoU directly measures box overlap, which is what",
        "'holding a guitar' looks like. The threshold is **descriptive** (from the distribution",
        "shape), not yet validated against hand-labeled playing/not-playing frames.",
        "",
        "## Example frames",
        "",
        "Blue = chosen person, green = chosen guitar, panel shows the IoU verdict.",
        "",
        "### Confident person-with-guitar (high overlap, guitar centered on person)",
        "",
        *[e for f in confident if (e := gallery_entry(f, "confident"))],
        "",
        "### Near-object false-positive risk (multiple people/guitars in frame)",
        "",
        "Note: at IoU >= threshold, the guitar center is inside the person box in **all** 86",
        "person-with-guitar frames, so peripheral overlaps do not pass. The remaining risk is",
        "**multi-object scenes** — more than one person or guitar present — where the chosen",
        "pair could be coincidental rather than the person actually playing.",
        "",
        *[e for f in near_object_fp if (e := gallery_entry(f, "near-object-fp"))],
        "",
        "### Borderline (just above the threshold)",
        "",
        *[e for f in borderline_pos if (e := gallery_entry(f, "borderline"))],
        "",
        "### Near-miss (just below the threshold — counted as NOT playing)",
        "",
        *[e for f in near_miss if (e := gallery_entry(f, "near-miss"))],
        "",
        "## Caveats / next steps",
        "",
        "- Rates are **descriptive**, not measured accuracy — no playing/not-playing labels yet.",
        "- A small hand-labeled subset would turn the threshold into a validated precision/recall.",
        "- Mirror reflections remain a known hard case for the underlying detector.",
        "",
    ]

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(lines), encoding="utf-8")
    n_gallery = len(list(gallery_dir.glob("*.jpg")))
    print(f"Saved report to: {output_path}")
    print(f"Copied {n_gallery} gallery images to: {gallery_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
