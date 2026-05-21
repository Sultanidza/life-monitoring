#!/usr/bin/env python3
"""Build GT-vs-prediction overlay images for a validation run."""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from eval_grounding_dino_predictions import compute_iou, group_gt_annotations
from test_baseline_models import safe_stem_name


DEFAULT_RUN_DIR = "reports/model-validation/20260520-184645"
GT_COLOR = "#2563eb"
TP_COLOR = "#16a34a"
FP_COLOR = "#dc2626"
FN_COLOR = "#f59e0b"
LEGEND_BG = "#f8fafc"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build GT-vs-prediction overlays for each model in a validation run."
    )
    parser.add_argument(
        "--run-dir",
        default=DEFAULT_RUN_DIR,
        help=f"Validation run directory. Default: {DEFAULT_RUN_DIR}",
    )
    parser.add_argument(
        "--iou-threshold",
        type=float,
        default=0.5,
        help="IoU threshold used for TP/FP/FN matching. Default: 0.5",
    )
    return parser.parse_args()


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def coco_bbox_to_xyxy(bbox: list[float]) -> list[float]:
    x, y, width, height = bbox
    return [x, y, x + width, y + height]


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
                    "label": str(detection["label"]),
                }
            )
    for detections in grouped.values():
        detections.sort(key=lambda item: item["score"], reverse=True)
    return grouped


def text_box(draw: ImageDraw.ImageDraw, text: str, font) -> tuple[int, int]:
    try:
        x1, y1, x2, y2 = draw.textbbox((0, 0), text, font=font)
        return x2 - x1, y2 - y1
    except AttributeError:
        return draw.textsize(text, font=font)


def draw_tag(draw: ImageDraw.ImageDraw, x: float, y: float, text: str, color: str, font) -> None:
    width, height = text_box(draw, text, font)
    top = max(0, int(y) - height - 6)
    bottom = top + height + 4
    right = int(x) + width + 8
    draw.rectangle([int(x), top, right, bottom], fill=color)
    draw.text((int(x) + 4, top + 2), text, fill="white", font=font)


def draw_legend(draw: ImageDraw.ImageDraw, font) -> None:
    items = [
        ("GT", GT_COLOR),
        ("TP prediction", TP_COLOR),
        ("FP prediction", FP_COLOR),
        ("FN ground truth", FN_COLOR),
    ]
    x = 18
    y = 18
    line_h = 22
    box_w = 180
    box_h = line_h * len(items) + 14
    draw.rounded_rectangle([x - 10, y - 10, x - 10 + box_w, y - 10 + box_h], radius=10, fill=LEGEND_BG, outline="#cbd5e1")
    for idx, (label, color) in enumerate(items):
        row_y = y + idx * line_h
        draw.rectangle([x, row_y, x + 18, row_y + 12], fill=color)
        draw.text((x + 28, row_y - 2), label, fill="#0f172a", font=font)


def build_matches(
    image_id: int,
    categories: dict[int, str],
    gt_by_key: dict[tuple[int, int], list[dict]],
    pred_by_key: dict[tuple[int, int], list[dict]],
    iou_threshold: float,
) -> dict:
    matched_predictions = []
    false_predictions = []
    false_ground_truth = []

    for category_id, category_name in categories.items():
        gt_items = gt_by_key.get((image_id, category_id), [])
        pred_items = pred_by_key.get((image_id, category_id), [])
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
                matched_predictions.append(
                    {
                        "label": category_name,
                        "pred_box": prediction["bbox_xyxy"],
                        "gt_box": gt_items[best_gt_index]["bbox_xyxy"],
                        "score": prediction["score"],
                        "iou": best_iou,
                    }
                )
            else:
                false_predictions.append(
                    {
                        "label": category_name,
                        "pred_box": prediction["bbox_xyxy"],
                        "score": prediction["score"],
                    }
                )

        for gt_index, gt_item in enumerate(gt_items):
            if gt_index not in matched_gt_indices:
                false_ground_truth.append(
                    {
                        "label": category_name,
                        "gt_box": gt_item["bbox_xyxy"],
                    }
                )

    return {
        "tp": matched_predictions,
        "fp": false_predictions,
        "fn": false_ground_truth,
    }


def draw_overlay(
    image_path: Path,
    matches: dict,
    destination: Path,
) -> None:
    image = Image.open(image_path).convert("RGB")
    draw = ImageDraw.Draw(image)
    font = ImageFont.load_default()

    draw_legend(draw, font)

    for item in matches["tp"]:
        gx1, gy1, gx2, gy2 = item["gt_box"]
        px1, py1, px2, py2 = item["pred_box"]
        draw.rectangle([gx1, gy1, gx2, gy2], outline=GT_COLOR, width=2)
        draw.rectangle([px1, py1, px2, py2], outline=TP_COLOR, width=4)
        draw_tag(
            draw,
            px1,
            py1,
            f"TP {item['label']} {item['score']:.2f} IoU {item['iou']:.2f}",
            TP_COLOR,
            font,
        )

    for item in matches["fp"]:
        x1, y1, x2, y2 = item["pred_box"]
        draw.rectangle([x1, y1, x2, y2], outline=FP_COLOR, width=4)
        draw_tag(
            draw,
            x1,
            y1,
            f"FP {item['label']} {item['score']:.2f}",
            FP_COLOR,
            font,
        )

    for item in matches["fn"]:
        x1, y1, x2, y2 = item["gt_box"]
        draw.rectangle([x1, y1, x2, y2], outline=FN_COLOR, width=4)
        draw_tag(
            draw,
            x1,
            y1,
            f"FN {item['label']}",
            FN_COLOR,
            font,
        )

    destination.parent.mkdir(parents=True, exist_ok=True)
    image.save(destination)


def build_summary_line(model: str, image_id: int, file_name: str, matches: dict) -> str:
    return (
        f"- `{model}` image `{image_id}` `{Path(file_name).name}`: "
        f"TP={len(matches['tp'])} FP={len(matches['fp'])} FN={len(matches['fn'])}"
    )


def main() -> int:
    args = parse_args()
    project_root = Path(__file__).resolve().parents[1]
    run_dir = (project_root / args.run_dir).resolve()
    manifest = load_json(run_dir / "manifest.json")
    coco_data = load_json(Path(manifest["coco_file"]))
    gt_by_key = group_gt_annotations(coco_data)
    categories = {int(cat["id"]): str(cat["name"]) for cat in coco_data["categories"]}
    images = {int(img["id"]): img for img in coco_data["images"]}

    output_root = run_dir / "error-overlays"
    output_root.mkdir(parents=True, exist_ok=True)

    markdown_lines = [
        "# Model Error Overlays",
        "",
        f"IoU threshold: `{args.iou_threshold:.2f}`",
        "",
        "Legend:",
        "",
        "- `GT`: ground-truth box",
        "- `TP`: matched prediction",
        "- `FP`: prediction with no valid GT match",
        "- `FN`: ground-truth box the model missed",
        "",
    ]

    manifest_out = {
        "run_dir": str(run_dir),
        "iou_threshold": args.iou_threshold,
        "models": [],
    }

    for result in manifest["results"]:
        model_name = result["model"]
        predictions_data = load_json(Path(result["predictions_path"]))
        pred_by_key = group_predictions(predictions_data)
        pred_image_map = {
            int(item["image_id"]): item["resolved_path"]
            for item in predictions_data["predictions"]
        }
        model_output_dir = output_root / model_name
        model_output_dir.mkdir(parents=True, exist_ok=True)

        markdown_lines.extend([f"## {model_name}", ""])
        image_records = []

        for image_id, image in sorted(images.items()):
            matches = build_matches(
                image_id=image_id,
                categories=categories,
                gt_by_key=gt_by_key,
                pred_by_key=pred_by_key,
                iou_threshold=args.iou_threshold,
            )
            image_path = Path(pred_image_map[image_id])
            output_name = f"{safe_stem_name(image_path)}-overlay{image_path.suffix.lower()}"
            output_path = model_output_dir / output_name
            draw_overlay(image_path, matches, output_path)

            markdown_lines.append(build_summary_line(model_name, image_id, image["file_name"], matches))
            image_records.append(
                {
                    "image_id": image_id,
                    "file_name": image["file_name"],
                    "resolved_path": str(image_path),
                    "overlay_path": str(output_path),
                    "tp": len(matches["tp"]),
                    "fp": len(matches["fp"]),
                    "fn": len(matches["fn"]),
                }
            )

        markdown_lines.append("")
        manifest_out["models"].append(
            {
                "model": model_name,
                "output_dir": str(model_output_dir),
                "images": image_records,
            }
        )

    (output_root / "README.md").write_text("\n".join(markdown_lines) + "\n", encoding="utf-8")
    (output_root / "manifest.json").write_text(json.dumps(manifest_out, indent=2), encoding="utf-8")
    print(f"Saved error overlays to: {output_root}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
