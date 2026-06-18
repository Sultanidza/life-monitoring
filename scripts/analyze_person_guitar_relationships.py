#!/usr/bin/env python3
"""Analyze person/guitar spatial relationships from detection predictions."""

from __future__ import annotations

import argparse
import csv
import json
import math
from pathlib import Path


DEFAULT_PREDICTIONS = "data/predictions/grounding_dino_expanded_2026_05_29_predictions.json"
DEFAULT_JSON = "data/metrics/person_guitar_relationships_expanded_2026_05_29.json"
DEFAULT_CSV = "data/metrics/person_guitar_relationships_expanded_2026_05_29.csv"

# Data-driven default from the person/guitar IoU distribution (Otsu's method).
# See scripts/build_iou_threshold_analysis.py for how this is derived.
DEFAULT_IOU_THRESHOLD = 0.26


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Compute frame-level person/guitar relationship features."
    )
    parser.add_argument("--predictions", default=DEFAULT_PREDICTIONS)
    parser.add_argument("--output-json", default=DEFAULT_JSON)
    parser.add_argument("--output-csv", default=DEFAULT_CSV)
    parser.add_argument("--person-label", default="person")
    parser.add_argument("--guitar-label", default="guitar")
    parser.add_argument(
        "--iou-threshold",
        type=float,
        default=DEFAULT_IOU_THRESHOLD,
        help=(
            "Minimum person/guitar IoU to count a frame as person-with-guitar. "
            f"Default {DEFAULT_IOU_THRESHOLD} (Otsu over the IoU distribution)."
        ),
    )
    return parser.parse_args()


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def coco_to_xyxy(box: list[float]) -> list[float]:
    x, y, width, height = box
    return [float(x), float(y), float(x + width), float(y + height)]


def area(box: list[float]) -> float:
    x1, y1, x2, y2 = box
    return max(0.0, x2 - x1) * max(0.0, y2 - y1)


def intersection(box_a: list[float], box_b: list[float]) -> float:
    ax1, ay1, ax2, ay2 = box_a
    bx1, by1, bx2, by2 = box_b
    return area([max(ax1, bx1), max(ay1, by1), min(ax2, bx2), min(ay2, by2)])


def safe_divide(numerator: float, denominator: float) -> float:
    return numerator / denominator if denominator else 0.0


def center(box: list[float]) -> tuple[float, float]:
    x1, y1, x2, y2 = box
    return ((x1 + x2) / 2.0, (y1 + y2) / 2.0)


def point_inside(point: tuple[float, float], box: list[float]) -> bool:
    x, y = point
    x1, y1, x2, y2 = box
    return x1 <= x <= x2 and y1 <= y <= y2


def diagonal(box: list[float]) -> float:
    x1, y1, x2, y2 = box
    return math.hypot(x2 - x1, y2 - y1)


def pair_features(person: dict, guitar: dict) -> dict:
    person_box = coco_to_xyxy(person["bbox"])
    guitar_box = coco_to_xyxy(guitar["bbox"])
    person_area = area(person_box)
    guitar_area = area(guitar_box)
    inter = intersection(person_box, guitar_box)
    union = person_area + guitar_area - inter
    person_center = center(person_box)
    guitar_center = center(guitar_box)
    center_distance = math.hypot(
        person_center[0] - guitar_center[0],
        person_center[1] - guitar_center[1],
    )
    center_distance_person_diag = safe_divide(center_distance, diagonal(person_box))
    guitar_center_in_person = point_inside(guitar_center, person_box)
    person_center_in_guitar = point_inside(person_center, guitar_box)
    guitar_intersection_over_guitar = safe_divide(inter, guitar_area)
    intersection_over_person = safe_divide(inter, person_area)

    return {
        "person_score": float(person.get("score", 0.0)),
        "guitar_score": float(guitar.get("score", 0.0)),
        "pair_score": round(float(person.get("score", 0.0)) * float(guitar.get("score", 0.0)), 6),
        "pair_iou": round(safe_divide(inter, union), 6),
        "guitar_center_in_person": guitar_center_in_person,
        "person_center_in_guitar": person_center_in_guitar,
        "guitar_intersection_over_guitar": round(guitar_intersection_over_guitar, 6),
        "intersection_over_person": round(intersection_over_person, 6),
        "center_distance_px": round(center_distance, 3),
        "center_distance_person_diag": round(center_distance_person_diag, 6),
        "guitar_area_over_person_area": round(safe_divide(guitar_area, person_area), 6),
    }


def choose_best_pair(persons: list[dict], guitars: list[dict]) -> dict | None:
    best: dict | None = None
    for person in persons:
        for guitar in guitars:
            features = pair_features(person, guitar)
            # Rank by intersection-over-union first (the decision signal),
            # then by joint detection confidence as a tie-breaker.
            ranking = (
                features["pair_iou"],
                features["pair_score"],
            )
            candidate = {"ranking": ranking, **features}
            if best is None or candidate["ranking"] > best["ranking"]:
                best = candidate
    if best is None:
        return None
    best.pop("ranking")
    return best


def playing_candidate(features: dict | None, iou_threshold: float) -> bool:
    if not features:
        return False
    return features["pair_iou"] >= iou_threshold


def build_rows(
    predictions_data: dict, person_label: str, guitar_label: str, iou_threshold: float
) -> list[dict]:
    rows = []
    for image in predictions_data.get("predictions", []):
        detections = image.get("detections", [])
        persons = [d for d in detections if str(d.get("label", "")).lower() == person_label]
        guitars = [d for d in detections if str(d.get("label", "")).lower() == guitar_label]
        best = choose_best_pair(persons, guitars)
        row = {
            "image_id": int(image["image_id"]),
            "file_name": image["file_name"],
            "resolved_path": image.get("resolved_path", ""),
            "person_count": len(persons),
            "guitar_count": len(guitars),
            "both_detected": bool(persons and guitars),
            "playing_candidate": playing_candidate(best, iou_threshold),
        }
        if best:
            row.update(best)
        else:
            row.update(
                {
                    "person_score": 0.0,
                    "guitar_score": 0.0,
                    "pair_score": 0.0,
                    "pair_iou": 0.0,
                    "guitar_center_in_person": False,
                    "person_center_in_guitar": False,
                    "guitar_intersection_over_guitar": 0.0,
                    "intersection_over_person": 0.0,
                    "center_distance_px": 0.0,
                    "center_distance_person_diag": 0.0,
                    "guitar_area_over_person_area": 0.0,
                }
            )
        rows.append(row)
    return rows


def summarize(rows: list[dict]) -> dict:
    total = len(rows)
    both = sum(1 for row in rows if row["both_detected"])
    candidates = sum(1 for row in rows if row["playing_candidate"])
    person_only = sum(1 for row in rows if row["person_count"] > 0 and row["guitar_count"] == 0)
    guitar_only = sum(1 for row in rows if row["guitar_count"] > 0 and row["person_count"] == 0)
    absent = sum(1 for row in rows if row["guitar_count"] == 0 and row["person_count"] == 0)
    return {
        "total_images": total,
        "both_detected": both,
        "playing_candidates": candidates,
        "person_only": person_only,
        "guitar_only": guitar_only,
        "neither_detected": absent,
        "playing_candidate_rate": round(safe_divide(candidates, total), 4),
        "both_detected_rate": round(safe_divide(both, total), 4),
    }


def write_csv(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = [
        "image_id",
        "file_name",
        "resolved_path",
        "person_count",
        "guitar_count",
        "both_detected",
        "playing_candidate",
        "person_score",
        "guitar_score",
        "pair_score",
        "pair_iou",
        "guitar_center_in_person",
        "person_center_in_guitar",
        "guitar_intersection_over_guitar",
        "intersection_over_person",
        "center_distance_px",
        "center_distance_person_diag",
        "guitar_area_over_person_area",
    ]
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    args = parse_args()
    project_root = Path(__file__).resolve().parents[1]
    predictions_path = (project_root / args.predictions).resolve()
    output_json = (project_root / args.output_json).resolve()
    output_csv = (project_root / args.output_csv).resolve()

    predictions_data = load_json(predictions_path)
    rows = build_rows(
        predictions_data=predictions_data,
        person_label=args.person_label.lower(),
        guitar_label=args.guitar_label.lower(),
        iou_threshold=args.iou_threshold,
    )
    summary = summarize(rows)

    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_text(
        json.dumps(
            {
                "predictions_file": str(predictions_path),
                "iou_threshold": args.iou_threshold,
                "heuristic": (
                    f"playing_candidate if the best person/guitar pair has IoU >= {args.iou_threshold} "
                    "(threshold derived from the IoU distribution via Otsu's method)"
                ),
                "summary": summary,
                "frames": rows,
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    write_csv(output_csv, rows)

    print("Relationship summary:")
    for key, value in summary.items():
        print(f"  {key}: {value}")
    print(f"Saved JSON to: {output_json}")
    print(f"Saved CSV to: {output_csv}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
