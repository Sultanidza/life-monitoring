#!/usr/bin/env python3
"""Build visual overlays for person/guitar relationship distances."""

from __future__ import annotations

import argparse
import json
import math
import re
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


DEFAULT_PREDICTIONS = "data/predictions/grounding_dino_expanded_2026_05_29_predictions.json"
DEFAULT_OUTPUT_DIR = "data/metrics/person_guitar_relationship_overlays_expanded_2026_05_29"

# Data-driven default from the person/guitar IoU distribution (Otsu's method).
# Keep in sync with scripts/analyze_person_guitar_relationships.py.
DEFAULT_IOU_THRESHOLD = 0.26

PERSON_COLOR = "#2563eb"
GUITAR_COLOR = "#16a34a"
PAIR_COLOR = "#dc2626"
OTHER_COLOR = "#94a3b8"
PANEL_BG = "#f8fafc"
TEXT_COLOR = "#0f172a"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Draw person/guitar pair distances on prediction images."
    )
    parser.add_argument("--predictions", default=DEFAULT_PREDICTIONS)
    parser.add_argument("--output-dir", default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--person-label", default="person")
    parser.add_argument("--guitar-label", default="guitar")
    parser.add_argument("--iou-threshold", type=float, default=DEFAULT_IOU_THRESHOLD)
    return parser.parse_args()


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def safe_stem(value: str) -> str:
    stem = Path(value).stem
    stem = re.sub(r"[^A-Za-z0-9_.-]+", "_", stem)
    return stem.strip("._") or "image"


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


def diagonal(box: list[float]) -> float:
    x1, y1, x2, y2 = box
    return math.hypot(x2 - x1, y2 - y1)


def point_inside(point: tuple[float, float], box: list[float]) -> bool:
    x, y = point
    x1, y1, x2, y2 = box
    return x1 <= x <= x2 and y1 <= y <= y2


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

    return {
        "person": person,
        "guitar": guitar,
        "person_box": person_box,
        "guitar_box": guitar_box,
        "person_center": person_center,
        "guitar_center": guitar_center,
        "person_score": float(person.get("score", 0.0)),
        "guitar_score": float(guitar.get("score", 0.0)),
        "pair_score": float(person.get("score", 0.0)) * float(guitar.get("score", 0.0)),
        "pair_iou": safe_divide(inter, union),
        "guitar_center_in_person": point_inside(guitar_center, person_box),
        "person_center_in_guitar": point_inside(person_center, guitar_box),
        "guitar_intersection_over_guitar": safe_divide(inter, guitar_area),
        "intersection_over_person": safe_divide(inter, person_area),
        "center_distance_px": center_distance,
        "center_distance_person_diag": safe_divide(center_distance, diagonal(person_box)),
        "guitar_area_over_person_area": safe_divide(guitar_area, person_area),
    }


def choose_best_pair(persons: list[dict], guitars: list[dict]) -> dict | None:
    best: dict | None = None
    for person in persons:
        for guitar in guitars:
            features = pair_features(person, guitar)
            # Rank by IoU first (the decision signal), then joint confidence.
            ranking = (features["pair_iou"], features["pair_score"])
            candidate = {"ranking": ranking, **features}
            if best is None or candidate["ranking"] > best["ranking"]:
                best = candidate
    return best


def playing_candidate(features: dict | None, iou_threshold: float) -> bool:
    if not features:
        return False
    return features["pair_iou"] >= iou_threshold


def text_size(draw: ImageDraw.ImageDraw, text: str, font) -> tuple[int, int]:
    x1, y1, x2, y2 = draw.textbbox((0, 0), text, font=font)
    return x2 - x1, y2 - y1


def draw_label(
    draw: ImageDraw.ImageDraw,
    xy: tuple[float, float],
    text: str,
    color: str,
    font,
) -> None:
    x, y = xy
    width, height = text_size(draw, text, font)
    x = int(max(0, min(x, 1900 - width - 10)))
    y = int(max(0, y - height - 8))
    draw.rectangle([x, y, x + width + 8, y + height + 5], fill=color)
    draw.text((x + 4, y + 2), text, fill="white", font=font)


def draw_box(
    draw: ImageDraw.ImageDraw,
    box: list[float],
    color: str,
    width: int,
    label: str,
    font,
) -> None:
    x1, y1, x2, y2 = box
    draw.rectangle([x1, y1, x2, y2], outline=color, width=width)
    draw_label(draw, (x1, y1), label, color, font)


def draw_center(draw: ImageDraw.ImageDraw, point: tuple[float, float], color: str) -> None:
    x, y = point
    radius = 7
    draw.ellipse([x - radius, y - radius, x + radius, y + radius], fill=color, outline="white", width=2)


def draw_panel(draw: ImageDraw.ImageDraw, lines: list[str], font) -> None:
    x = 18
    y = 18
    widths = [text_size(draw, line, font)[0] for line in lines]
    line_h = 19
    panel_w = max(widths) + 28
    panel_h = line_h * len(lines) + 20
    draw.rounded_rectangle(
        [x, y, x + panel_w, y + panel_h],
        radius=8,
        fill=PANEL_BG,
        outline="#cbd5e1",
        width=2,
    )
    for index, line in enumerate(lines):
        draw.text((x + 14, y + 10 + index * line_h), line, fill=TEXT_COLOR, font=font)


def draw_overlay(
    image_entry: dict, output_path: Path, person_label: str, guitar_label: str, iou_threshold: float
) -> dict:
    image = Image.open(image_entry["resolved_path"]).convert("RGB")
    draw = ImageDraw.Draw(image)
    font = ImageFont.load_default()

    detections = image_entry.get("detections", [])
    persons = [d for d in detections if str(d.get("label", "")).lower() == person_label]
    guitars = [d for d in detections if str(d.get("label", "")).lower() == guitar_label]
    best = choose_best_pair(persons, guitars)

    chosen_person = best["person"] if best else None
    chosen_guitar = best["guitar"] if best else None

    for detection in detections:
        label = str(detection.get("label", "")).lower()
        box = coco_to_xyxy(detection["bbox"])
        score = float(detection.get("score", 0.0))
        if detection is chosen_person or detection is chosen_guitar:
            continue
        if label == person_label:
            draw_box(draw, box, OTHER_COLOR, 2, f"other person {score:.2f}", font)
        elif label == guitar_label:
            draw_box(draw, box, OTHER_COLOR, 2, f"other guitar {score:.2f}", font)

    if best:
        draw_box(
            draw,
            best["person_box"],
            PERSON_COLOR,
            5,
            f"chosen person {best['person_score']:.2f}",
            font,
        )
        draw_box(
            draw,
            best["guitar_box"],
            GUITAR_COLOR,
            5,
            f"chosen guitar {best['guitar_score']:.2f}",
            font,
        )
        draw.line([best["person_center"], best["guitar_center"]], fill=PAIR_COLOR, width=5)
        draw_center(draw, best["person_center"], PERSON_COLOR)
        draw_center(draw, best["guitar_center"], GUITAR_COLOR)

    candidate = playing_candidate(best, iou_threshold)
    lines = [
        f"image_id: {image_entry['image_id']}",
        f"persons: {len(persons)}  guitars: {len(guitars)}",
        f"person-with-guitar: {candidate}  (IoU >= {iou_threshold:.2f})",
    ]
    if best:
        lines.extend(
            [
                f"pair IoU: {best['pair_iou']:.3f}",
                f"guitar overlap covered: {best['guitar_intersection_over_guitar']:.3f}",
                f"center distance: {best['center_distance_px']:.1f}px",
            ]
        )
    else:
        lines.append("chosen pair: none")
    draw_panel(draw, lines, font)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    image.save(output_path)

    return {
        "image_id": int(image_entry["image_id"]),
        "file_name": image_entry["file_name"],
        "resolved_path": image_entry["resolved_path"],
        "overlay_path": str(output_path),
        "person_count": len(persons),
        "guitar_count": len(guitars),
        "playing_candidate": candidate,
        "center_distance_px": round(best["center_distance_px"], 3) if best else None,
        "center_distance_person_diag": round(best["center_distance_person_diag"], 6) if best else None,
        "pair_iou": round(best["pair_iou"], 6) if best else None,
        "guitar_intersection_over_guitar": round(best["guitar_intersection_over_guitar"], 6) if best else None,
    }


def main() -> int:
    args = parse_args()
    project_root = Path(__file__).resolve().parents[1]
    predictions_path = (project_root / args.predictions).resolve()
    output_dir = (project_root / args.output_dir).resolve()

    predictions_data = load_json(predictions_path)
    outputs = []
    for image_entry in predictions_data.get("predictions", []):
        image_id = int(image_entry["image_id"])
        output_name = f"{image_id:04d}-{safe_stem(image_entry['file_name'])}-relationship.jpg"
        outputs.append(
            draw_overlay(
                image_entry=image_entry,
                output_path=output_dir / output_name,
                person_label=args.person_label.lower(),
                guitar_label=args.guitar_label.lower(),
                iou_threshold=args.iou_threshold,
            )
        )

    manifest = {
        "predictions_file": str(predictions_path),
        "output_dir": str(output_dir),
        "iou_threshold": args.iou_threshold,
        "heuristic": (
            f"person-with-guitar if the best person/guitar pair has IoU >= {args.iou_threshold} "
            "(threshold from the IoU distribution via Otsu's method)"
        ),
        "overlays": outputs,
    }
    (output_dir / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    index_lines = [
        "# Person/Guitar Relationship Overlays",
        "",
        f"Predictions: `{predictions_path}`",
        "",
        "Colors:",
        "",
        "- Blue: chosen person box and center",
        "- Green: chosen guitar box and center",
        "- Red: distance line between chosen centers",
        "- Gray: other detected person/guitar boxes not used for the distance",
        "",
        "Files:",
        "",
    ]
    for item in outputs:
        index_lines.append(
            f"- `{Path(item['overlay_path']).name}`: "
            f"person_with_guitar={item['playing_candidate']} "
            f"pair_iou={item['pair_iou']}"
        )
    (output_dir / "index.md").write_text("\n".join(index_lines) + "\n", encoding="utf-8")

    print(f"Saved {len(outputs)} overlays to: {output_dir}")
    print(f"Saved manifest to: {output_dir / 'manifest.json'}")
    print(f"Saved index to: {output_dir / 'index.md'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
