#!/usr/bin/env python3
"""Study the person/guitar IoU distribution and recommend a decision threshold.

This replaces center-distance reasoning with intersection-over-union (IoU)
between the best person box and the best guitar box in each frame, builds the
IoU distribution across the dataset, and recommends a threshold for deciding
"person with guitar". The recommendation uses Otsu's method, which splits a
1-D distribution into two classes without needing playing/not-playing labels.
"""

from __future__ import annotations

import argparse
import html
import json
from pathlib import Path


DEFAULT_PREDICTIONS = "data/predictions/grounding_dino_expanded_2026_05_29_predictions.json"
DEFAULT_JSON = "data/metrics/person_guitar_iou_threshold_expanded_2026_05_29.json"
DEFAULT_SVG = "data/metrics/person_guitar_iou_distribution_expanded_2026_05_29.svg"

SWEEP_THRESHOLDS = [0.0, 0.05, 0.10, 0.15, 0.20, 0.25, 0.30, 0.40, 0.50]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build the person/guitar IoU distribution and recommend a threshold."
    )
    parser.add_argument("--predictions", default=DEFAULT_PREDICTIONS)
    parser.add_argument("--output-json", default=DEFAULT_JSON)
    parser.add_argument("--output-svg", default=DEFAULT_SVG)
    parser.add_argument("--person-label", default="person")
    parser.add_argument("--guitar-label", default="guitar")
    parser.add_argument("--bins", type=int, default=20)
    return parser.parse_args()


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def coco_to_xyxy(box: list[float]) -> list[float]:
    x, y, width, height = box
    return [float(x), float(y), float(x + width), float(y + height)]


def area(box: list[float]) -> float:
    x1, y1, x2, y2 = box
    return max(0.0, x2 - x1) * max(0.0, y2 - y1)


def iou(box_a: list[float], box_b: list[float]) -> float:
    ax1, ay1, ax2, ay2 = box_a
    bx1, by1, bx2, by2 = box_b
    inter = area([max(ax1, bx1), max(ay1, by1), min(ax2, bx2), min(ay2, by2)])
    union = area(box_a) + area(box_b) - inter
    return inter / union if union else 0.0


def best_pair_iou(detections: list[dict], person_label: str, guitar_label: str) -> float | None:
    persons = [coco_to_xyxy(d["bbox"]) for d in detections if str(d.get("label", "")).lower() == person_label]
    guitars = [coco_to_xyxy(d["bbox"]) for d in detections if str(d.get("label", "")).lower() == guitar_label]
    if not persons or not guitars:
        return None
    return max(iou(p, g) for p in persons for g in guitars)


def percentile(values: list[float], pct: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    if len(ordered) == 1:
        return ordered[0]
    rank = pct / 100.0 * (len(ordered) - 1)
    low = int(rank)
    high = min(low + 1, len(ordered) - 1)
    frac = rank - low
    return ordered[low] + (ordered[high] - ordered[low]) * frac


def histogram(values: list[float], bins: int, hi: float) -> list[dict]:
    hi = hi if hi > 0 else 1.0
    counts = [0] * bins
    for value in values:
        index = min(bins - 1, int(value / hi * bins))
        counts[index] += 1
    edges = [round(i * hi / bins, 4) for i in range(bins + 1)]
    return [
        {"lo": edges[i], "hi": edges[i + 1], "count": counts[i]}
        for i in range(bins)
    ]


def otsu_threshold(values: list[float], bins: int, hi: float) -> float:
    """Pick the IoU that maximizes between-class variance over the histogram."""
    hi = hi if hi > 0 else 1.0
    counts = [0] * bins
    for value in values:
        index = min(bins - 1, int(value / hi * bins))
        counts[index] += 1
    centers = [(i + 0.5) * hi / bins for i in range(bins)]
    total = sum(counts)
    if total == 0:
        return 0.0
    sum_all = sum(centers[i] * counts[i] for i in range(bins))
    weight_bg = 0.0
    sum_bg = 0.0
    best_variance = -1.0
    best_threshold = 0.0
    for i in range(bins):
        weight_bg += counts[i]
        if weight_bg == 0:
            continue
        weight_fg = total - weight_bg
        if weight_fg == 0:
            break
        sum_bg += centers[i] * counts[i]
        mean_bg = sum_bg / weight_bg
        mean_fg = (sum_all - sum_bg) / weight_fg
        variance = weight_bg * weight_fg * (mean_bg - mean_fg) ** 2
        if variance > best_variance:
            best_variance = variance
            best_threshold = (i + 1) * hi / bins
    return round(best_threshold, 4)


def build_analysis(data: dict, person_label: str, guitar_label: str, bins: int) -> dict:
    total_frames = 0
    both_detected: list[float] = []  # best-pair IoU for frames with person AND guitar
    for image in data.get("predictions", []):
        total_frames += 1
        value = best_pair_iou(image.get("detections", []), person_label, guitar_label)
        if value is not None:
            both_detected.append(value)

    positives = [v for v in both_detected if v > 0.0]
    zeros = len(both_detected) - len(positives)
    hi = max(both_detected) if both_detected else 1.0
    recommended = otsu_threshold(both_detected, bins, hi)

    sweep = []
    for threshold in SWEEP_THRESHOLDS:
        qualifying = sum(1 for v in both_detected if v >= threshold)
        sweep.append(
            {
                "iou_threshold": threshold,
                "frames_person_with_guitar": qualifying,
                "share_of_all_frames": round(qualifying / total_frames, 4) if total_frames else 0.0,
                "share_of_both_detected": round(qualifying / len(both_detected), 4) if both_detected else 0.0,
            }
        )

    def stat(fn):
        return round(fn, 4)

    distribution = {
        "count_both_detected": len(both_detected),
        "count_iou_zero": zeros,
        "count_iou_positive": len(positives),
        "min": stat(min(both_detected)) if both_detected else 0.0,
        "max": stat(max(both_detected)) if both_detected else 0.0,
        "mean": stat(sum(both_detected) / len(both_detected)) if both_detected else 0.0,
        "median": stat(percentile(both_detected, 50)),
        "p25": stat(percentile(both_detected, 25)),
        "p75": stat(percentile(both_detected, 75)),
        "p90": stat(percentile(both_detected, 90)),
        "histogram": histogram(both_detected, bins, hi),
    }

    return {
        "predictions_file": "",  # filled by caller
        "method": (
            "IoU between best person box and best guitar box per frame. "
            "Recommended threshold from Otsu's method over the IoU distribution "
            "(no playing/not-playing labels required)."
        ),
        "total_frames": total_frames,
        "recommended_iou_threshold": recommended,
        "distribution": distribution,
        "threshold_sweep": sweep,
    }


def render_svg(analysis: dict) -> str:
    dist = analysis["distribution"]
    bins = dist["histogram"]
    recommended = analysis["recommended_iou_threshold"]

    left_pad = 64
    right_pad = 32
    top_pad = 110
    bottom_pad = 70
    bar_width = 46
    bar_gap = 8
    plot_height = 280

    width = left_pad + right_pad + len(bins) * (bar_width + bar_gap)
    height = top_pad + plot_height + bottom_pad
    max_count = max((b["count"] for b in bins), default=1) or 1

    hi = bins[-1]["hi"] if bins else 1.0
    title = "Person/Guitar IoU Distribution"
    subtitle = (
        f"{dist['count_both_detected']} frames with person+guitar • "
        f"IoU=0 in {dist['count_iou_zero']} • "
        f"mean {dist['mean']:.3f} • median {dist['median']:.3f} • "
        f"recommended threshold {recommended:.3f} (Otsu)"
    )

    svg: list[str] = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="#f7f5ef" />',
        f'<text x="{left_pad}" y="46" font-family="Arial, sans-serif" font-size="26" font-weight="700" fill="#1f2933">{html.escape(title)}</text>',
        f'<text x="{left_pad}" y="74" font-family="Arial, sans-serif" font-size="13" fill="#52606d">{html.escape(subtitle)}</text>',
    ]

    baseline = top_pad + plot_height
    svg.append(
        f'<line x1="{left_pad}" y1="{baseline}" x2="{width - right_pad}" y2="{baseline}" stroke="#9aa5b1" stroke-width="1" />'
    )

    for index, b in enumerate(bins):
        x = left_pad + index * (bar_width + bar_gap)
        bar_h = round(b["count"] / max_count * plot_height)
        y = baseline - bar_h
        in_class = b["lo"] >= recommended
        fill = "#5aa676" if in_class else "#c0ccda"
        svg.append(
            f'<rect x="{x}" y="{y}" width="{bar_width}" height="{bar_h}" fill="{fill}" rx="4" />'
        )
        if b["count"]:
            svg.append(
                f'<text x="{x + bar_width / 2}" y="{y - 6}" text-anchor="middle" font-family="Arial, sans-serif" font-size="11" fill="#243b53">{b["count"]}</text>'
            )
        svg.append(
            f'<text x="{x + bar_width / 2}" y="{baseline + 18}" text-anchor="middle" font-family="Arial, sans-serif" font-size="10" fill="#52606d">{b["lo"]:.2f}</text>'
        )

    # recommended threshold marker
    if hi > 0:
        plot_span = len(bins) * (bar_width + bar_gap) - bar_gap
        marker_x = left_pad + recommended / hi * plot_span
        svg.append(
            f'<line x1="{marker_x:.1f}" y1="{top_pad - 6}" x2="{marker_x:.1f}" y2="{baseline}" stroke="#bf4a3f" stroke-width="2" stroke-dasharray="5 4" />'
        )
        svg.append(
            f'<text x="{marker_x:.1f}" y="{top_pad - 12}" text-anchor="middle" font-family="Arial, sans-serif" font-size="11" font-weight="700" fill="#bf4a3f">threshold {recommended:.2f}</text>'
        )

    svg.append(
        f'<text x="{left_pad}" y="{height - 22}" font-family="Arial, sans-serif" font-size="11" fill="#52606d">x: person/guitar IoU (bin lower edge) • y: frame count • green bars = counted as person-with-guitar</text>'
    )
    svg.append("</svg>")
    return "\n".join(svg)


def main() -> int:
    args = parse_args()
    project_root = Path(__file__).resolve().parents[1]
    predictions_path = (project_root / args.predictions).resolve()
    output_json = (project_root / args.output_json).resolve()
    output_svg = (project_root / args.output_svg).resolve()

    data = load_json(predictions_path)
    analysis = build_analysis(
        data=data,
        person_label=args.person_label.lower(),
        guitar_label=args.guitar_label.lower(),
        bins=args.bins,
    )
    analysis["predictions_file"] = str(predictions_path)

    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps(analysis, indent=2), encoding="utf-8")
    output_svg.write_text(render_svg(analysis), encoding="utf-8")

    dist = analysis["distribution"]
    print("Person/guitar IoU distribution:")
    print(f"  frames with person+guitar: {dist['count_both_detected']}")
    print(f"  IoU == 0 (co-present, no overlap): {dist['count_iou_zero']}")
    print(f"  mean {dist['mean']} | median {dist['median']} | p25 {dist['p25']} | p75 {dist['p75']}")
    print(f"  recommended IoU threshold (Otsu): {analysis['recommended_iou_threshold']}")
    print("  threshold sweep:")
    for row in analysis["threshold_sweep"]:
        print(
            f"    IoU>={row['iou_threshold']:.2f}: {row['frames_person_with_guitar']} frames "
            f"({row['share_of_all_frames'] * 100:.1f}% of all)"
        )
    print(f"Saved JSON to: {output_json}")
    print(f"Saved SVG to: {output_svg}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
