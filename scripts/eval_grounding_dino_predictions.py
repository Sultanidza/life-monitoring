#!/usr/bin/env python3
"""Evaluate Grounding DINO predictions against COCO ground truth."""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path


DEFAULT_COCO = (
    "data/annotations/eval-webcamoid-obs-studio-2026-05-17-11-06-20/coco.json"
)
DEFAULT_PREDICTIONS = "data/predictions/grounding_dino_predictions.json"
DEFAULT_OUTPUT = "data/metrics/grounding_dino_eval_iou050.json"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Evaluate Grounding DINO predictions with simple IoU-based diagnostics."
    )
    parser.add_argument(
        "--coco",
        default=DEFAULT_COCO,
        help=f"Path to COCO ground truth JSON. Default: {DEFAULT_COCO}",
    )
    parser.add_argument(
        "--predictions",
        default=DEFAULT_PREDICTIONS,
        help=f"Path to Grounding DINO predictions JSON. Default: {DEFAULT_PREDICTIONS}",
    )
    parser.add_argument(
        "--output",
        default=DEFAULT_OUTPUT,
        help=f"Path to metrics output JSON. Default: {DEFAULT_OUTPUT}",
    )
    parser.add_argument(
        "--iou-threshold",
        type=float,
        default=0.5,
        help="IoU threshold for matching. Default: 0.5",
    )
    return parser.parse_args()


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def coco_bbox_to_xyxy(bbox: list[float]) -> list[float]:
    x, y, width, height = bbox
    return [x, y, x + width, y + height]


def box_area_xyxy(box: list[float]) -> float:
    x1, y1, x2, y2 = box
    return max(0.0, x2 - x1) * max(0.0, y2 - y1)


def compute_iou(box_a: list[float], box_b: list[float]) -> float:
    ax1, ay1, ax2, ay2 = box_a
    bx1, by1, bx2, by2 = box_b

    inter_x1 = max(ax1, bx1)
    inter_y1 = max(ay1, by1)
    inter_x2 = min(ax2, bx2)
    inter_y2 = min(ay2, by2)

    inter_area = box_area_xyxy([inter_x1, inter_y1, inter_x2, inter_y2])
    if inter_area <= 0:
        return 0.0

    union = box_area_xyxy(box_a) + box_area_xyxy(box_b) - inter_area
    if union <= 0:
        return 0.0
    return inter_area / union


def safe_divide(numerator: float, denominator: float) -> float:
    if denominator == 0:
        return 0.0
    return numerator / denominator


def round_metric(value: float) -> float:
    return round(value, 4)


def build_category_info(coco_data: dict) -> dict[int, str]:
    return {
        int(category["id"]): str(category["name"])
        for category in coco_data.get("categories", [])
    }


def group_gt_annotations(coco_data: dict) -> dict[tuple[int, int], list[dict]]:
    grouped: dict[tuple[int, int], list[dict]] = defaultdict(list)
    for annotation in coco_data.get("annotations", []):
        key = (int(annotation["image_id"]), int(annotation["category_id"]))
        grouped[key].append(
            {
                "bbox_xyxy": coco_bbox_to_xyxy(annotation["bbox"]),
                "bbox_coco": annotation["bbox"],
            }
        )
    return grouped


def group_predictions(predictions_data: dict) -> dict[tuple[int, int], list[dict]]:
    grouped: dict[tuple[int, int], list[dict]] = defaultdict(list)
    for image_entry in predictions_data.get("predictions", []):
        image_id = int(image_entry["image_id"])
        for detection in image_entry.get("detections", []):
            category_id = int(detection["category_id"])
            grouped[(image_id, category_id)].append(
                {
                    "bbox_xyxy": coco_bbox_to_xyxy(detection["bbox"]),
                    "bbox_coco": detection["bbox"],
                    "score": float(detection["score"]),
                    "label": detection["label"],
                }
            )
    for detections in grouped.values():
        detections.sort(key=lambda item: item["score"], reverse=True)
    return grouped


def evaluate_category(
    image_ids: list[int],
    category_id: int,
    gt_by_key: dict[tuple[int, int], list[dict]],
    pred_by_key: dict[tuple[int, int], list[dict]],
    iou_threshold: float,
) -> dict:
    gt_count = 0
    pred_count = 0
    tp = 0
    fp = 0
    matched_ious: list[float] = []

    for image_id in image_ids:
        gt_items = gt_by_key.get((image_id, category_id), [])
        pred_items = pred_by_key.get((image_id, category_id), [])

        gt_count += len(gt_items)
        pred_count += len(pred_items)

        matched_gt_indices: set[int] = set()

        for prediction in pred_items:
            best_iou = 0.0
            best_gt_index: int | None = None

            for gt_index, gt_item in enumerate(gt_items):
                if gt_index in matched_gt_indices:
                    continue
                iou = compute_iou(prediction["bbox_xyxy"], gt_item["bbox_xyxy"])
                if iou > best_iou:
                    best_iou = iou
                    best_gt_index = gt_index

            if best_gt_index is not None and best_iou >= iou_threshold:
                matched_gt_indices.add(best_gt_index)
                tp += 1
                matched_ious.append(best_iou)
            else:
                fp += 1

    fn = gt_count - tp
    precision = safe_divide(tp, tp + fp)
    recall = safe_divide(tp, gt_count)
    mean_iou = safe_divide(sum(matched_ious), len(matched_ious))

    return {
        "gt_count": gt_count,
        "prediction_count": pred_count,
        "tp": tp,
        "fp": fp,
        "fn": fn,
        "precision": round_metric(precision),
        "recall": round_metric(recall),
        "mean_iou": round_metric(mean_iou),
        "matched_count": len(matched_ious),
    }


def build_overall_metrics(per_class: dict[int, dict]) -> dict:
    gt_count = sum(item["gt_count"] for item in per_class.values())
    prediction_count = sum(item["prediction_count"] for item in per_class.values())
    tp = sum(item["tp"] for item in per_class.values())
    fp = sum(item["fp"] for item in per_class.values())
    fn = sum(item["fn"] for item in per_class.values())

    matched_count = sum(item["matched_count"] for item in per_class.values())
    iou_sum = sum(item["mean_iou"] * item["matched_count"] for item in per_class.values())
    mean_iou = safe_divide(iou_sum, matched_count)

    return {
        "gt_count": gt_count,
        "prediction_count": prediction_count,
        "tp": tp,
        "fp": fp,
        "fn": fn,
        "precision": round_metric(safe_divide(tp, tp + fp)),
        "recall": round_metric(safe_divide(tp, gt_count)),
        "mean_iou": round_metric(mean_iou),
        "matched_count": matched_count,
    }


def print_report(categories: dict[int, str], per_class: dict[int, dict], overall: dict) -> None:
    print("Per-class metrics:")
    for category_id, name in sorted(categories.items()):
        metrics = per_class[category_id]
        print(
            f"  - {name} ({category_id}): "
            f"GT={metrics['gt_count']} "
            f"Pred={metrics['prediction_count']} "
            f"TP={metrics['tp']} FP={metrics['fp']} FN={metrics['fn']} "
            f"Precision={metrics['precision']:.4f} "
            f"Recall={metrics['recall']:.4f} "
            f"MeanIoU={metrics['mean_iou']:.4f}"
        )

    print("Overall:")
    print(
        f"  GT={overall['gt_count']} "
        f"Pred={overall['prediction_count']} "
        f"TP={overall['tp']} FP={overall['fp']} FN={overall['fn']} "
        f"Precision={overall['precision']:.4f} "
        f"Recall={overall['recall']:.4f} "
        f"MeanIoU={overall['mean_iou']:.4f}"
    )


def main() -> int:
    args = parse_args()
    project_root = Path(__file__).resolve().parents[1]
    coco_path = (project_root / args.coco).resolve()
    predictions_path = (project_root / args.predictions).resolve()
    output_path = (project_root / args.output).resolve()

    coco_data = load_json(coco_path)
    predictions_data = load_json(predictions_path)

    categories = build_category_info(coco_data)
    image_ids = [int(image["id"]) for image in coco_data.get("images", [])]
    gt_by_key = group_gt_annotations(coco_data)
    pred_by_key = group_predictions(predictions_data)

    per_class: dict[int, dict] = {}
    for category_id in sorted(categories):
        per_class[category_id] = evaluate_category(
            image_ids=image_ids,
            category_id=category_id,
            gt_by_key=gt_by_key,
            pred_by_key=pred_by_key,
            iou_threshold=args.iou_threshold,
        )

    overall = build_overall_metrics(per_class)

    output_payload = {
        "coco_file": str(coco_path),
        "predictions_file": str(predictions_path),
        "iou_threshold": args.iou_threshold,
        "categories": [
            {"id": category_id, "name": categories[category_id]}
            for category_id in sorted(categories)
        ],
        "per_class": {
            str(category_id): {
                "name": categories[category_id],
                **metrics,
            }
            for category_id, metrics in sorted(per_class.items())
        },
        "overall": overall,
    }

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(output_payload, indent=2), encoding="utf-8")

    print_report(categories, per_class, overall)
    print(f"Saved metrics to: {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
