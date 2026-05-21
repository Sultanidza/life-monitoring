#!/usr/bin/env python3
"""Run all configured detectors on the active COCO eval set and score them."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from datetime import datetime
from pathlib import Path

from build_metrics_heatmap import render_svg
from eval_grounding_dino_predictions import (
    build_category_info,
    build_overall_metrics,
    evaluate_category,
    group_gt_annotations,
)
from resolve_coco_image_paths import collect_root_files, resolve_one
from test_baseline_models import (
    ModelRun,
    normalize_prompt_label,
    run_detectron2,
    run_florence2,
    run_grounding_dino,
    run_owlv2,
    run_ultralytics,
    run_yolox,
)


DEFAULT_COCO = "data/annotations/eval-webcamoid-obs-studio-2026-05-17-11-06-20/coco.json"
DEFAULT_IMAGE_ROOTS = [
    "data/frames/webcamoid",
    "data/frames/obs-studio-2026-05-17-11-06-20",
]
DEFAULT_MODELS = [
    "ultralytics",
    "detectron2",
    "grounding-dino",
    "owlv2",
    "florence2",
    "yolox",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run multi-model validation on the active COCO evaluation set."
    )
    parser.add_argument("--coco", default=DEFAULT_COCO)
    parser.add_argument("--image-roots", nargs="+", default=DEFAULT_IMAGE_ROOTS)
    parser.add_argument("--models", nargs="+", choices=DEFAULT_MODELS, default=DEFAULT_MODELS)
    parser.add_argument(
        "--output-dir",
        default=None,
        help="Directory to store predictions, metrics, heatmaps, and summary outputs.",
    )
    parser.add_argument("--iou-threshold", type=float, default=0.5)
    parser.add_argument("--ultralytics-model", default="yolov8n-oiv7.pt")
    parser.add_argument("--ultralytics-conf", type=float, default=0.25)
    parser.add_argument(
        "--detectron2-config",
        default="COCO-Detection/faster_rcnn_R_50_FPN_3x.yaml",
    )
    parser.add_argument("--detectron2-threshold", type=float, default=0.5)
    parser.add_argument("--grounding-dino-model", default="IDEA-Research/grounding-dino-base")
    parser.add_argument("--grounding-box-threshold", type=float, default=0.35)
    parser.add_argument("--grounding-text-threshold", type=float, default=0.25)
    parser.add_argument("--owlv2-model", default="google/owlv2-base-patch16-ensemble")
    parser.add_argument("--owlv2-threshold", type=float, default=0.1)
    parser.add_argument("--florence2-model", default="florence-community/Florence-2-base")
    parser.add_argument("--florence2-max-new-tokens", type=int, default=256)
    parser.add_argument(
        "--yolox-exp-file",
        default="external/YOLOX/exps/default/yolox_s.py",
    )
    parser.add_argument(
        "--yolox-checkpoint",
        default="models/yolox/yolox_s.pth",
    )
    parser.add_argument("--yolox-conf", type=float, default=0.25)
    parser.add_argument("--yolox-nms", type=float, default=0.45)
    parser.add_argument("--yolox-test-size", type=int, nargs=2, default=[640, 640])
    parser.add_argument("--yolox-fuse", action="store_true")
    return parser.parse_args()


def project_path(raw_path: str) -> Path:
    path = Path(raw_path).expanduser()
    if path.is_absolute():
        return path.resolve()
    return (Path(__file__).resolve().parents[1] / path).resolve()


def build_output_dir(raw_output_dir: str | None) -> Path:
    if raw_output_dir:
        return project_path(raw_output_dir)
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    return (
        Path(__file__).resolve().parents[1]
        / "reports"
        / "model-validation"
        / timestamp
    )


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")


def resolve_images(coco_data: dict, image_roots: list[Path]) -> list[dict]:
    by_name = collect_root_files(image_roots)
    resolved = []
    for image in coco_data.get("images", []):
        result = resolve_one(image["file_name"], image_roots=image_roots, by_name=by_name)
        if result.status != "resolved":
            raise RuntimeError(
                f"Image could not be resolved uniquely: {image['file_name']} ({result.status})"
            )
        resolved.append(
            {
                "image_id": int(image["id"]),
                "file_name": image["file_name"],
                "resolved_path": str(Path(result.matches[0]).resolve()),
            }
        )
    return resolved


def coco_bbox_from_xyxy(box: list[float]) -> list[float]:
    x1, y1, x2, y2 = box
    return [
        round(float(x1), 2),
        round(float(y1), 2),
        round(float(x2 - x1), 2),
        round(float(y2 - y1), 2),
    ]


def category_name_to_id(coco_data: dict) -> dict[str, int]:
    return {
        str(category["name"]).strip().lower(): int(category["id"])
        for category in coco_data.get("categories", [])
    }


def build_model_predictions(
    run: ModelRun,
    resolved_images: list[dict],
    category_map: dict[str, int],
) -> dict:
    path_to_image = {entry["resolved_path"]: entry for entry in resolved_images}
    predictions = []
    counts: Counter = Counter()

    for image_entry in run.images:
        resolved_path = str(Path(image_entry["image"]).resolve())
        resolved_meta = path_to_image.get(resolved_path)
        if resolved_meta is None:
            raise RuntimeError(f"Run image not found in resolved COCO set: {resolved_path}")

        detections = []
        for detection in image_entry["detections"]:
            normalized_label = normalize_prompt_label(str(detection["label"]))
            if normalized_label not in category_map:
                continue
            counts[normalized_label] += 1
            detections.append(
                {
                    "label": normalized_label,
                    "category_id": category_map[normalized_label],
                    "bbox": coco_bbox_from_xyxy(detection["box"]),
                    "score": round(float(detection["score"]), 4),
                }
            )

        predictions.append(
            {
                "image_id": resolved_meta["image_id"],
                "file_name": resolved_meta["file_name"],
                "resolved_path": resolved_meta["resolved_path"],
                "detections": detections,
            }
        )

    return {
        "model": run.name,
        "metadata": run.metadata,
        "predictions": predictions,
        "class_prediction_counts": dict(counts),
    }


def group_predictions(predictions_data: dict) -> dict[tuple[int, int], list[dict]]:
    grouped: dict[tuple[int, int], list[dict]] = {}
    for image_entry in predictions_data.get("predictions", []):
        image_id = int(image_entry["image_id"])
        for detection in image_entry.get("detections", []):
            key = (image_id, int(detection["category_id"]))
            grouped.setdefault(key, []).append(
                {
                    "bbox_xyxy": [
                        detection["bbox"][0],
                        detection["bbox"][1],
                        detection["bbox"][0] + detection["bbox"][2],
                        detection["bbox"][1] + detection["bbox"][3],
                    ],
                    "bbox_coco": detection["bbox"],
                    "score": float(detection["score"]),
                    "label": detection["label"],
                }
            )
    for detections in grouped.values():
        detections.sort(key=lambda item: item["score"], reverse=True)
    return grouped


def evaluate_predictions(
    coco_data: dict,
    predictions_data: dict,
    iou_threshold: float,
    coco_file: Path,
) -> dict:
    categories = build_category_info(coco_data)
    image_ids = [int(image["id"]) for image in coco_data.get("images", [])]
    gt_by_key = group_gt_annotations(coco_data)
    pred_by_key = group_predictions(predictions_data)

    per_class: dict[int, dict] = {}
    for category_id in sorted(categories):
        metrics = evaluate_category(
            image_ids=image_ids,
            category_id=category_id,
            gt_by_key=gt_by_key,
            pred_by_key=pred_by_key,
            iou_threshold=iou_threshold,
        )
        metrics["name"] = categories[category_id]
        per_class[category_id] = metrics

    overall = build_overall_metrics(per_class)
    return {
        "title": f"{predictions_data['model']} Metrics Heatmap",
        "subtitle": (
            f"{len(image_ids)} labeled images • IoU threshold {iou_threshold:.2f} • "
            f"{predictions_data['model']}"
        ),
        "model": predictions_data["model"],
        "coco_file": str(coco_file),
        "predictions_file": "",
        "iou_threshold": iou_threshold,
        "categories": [
            {"id": category_id, "name": categories[category_id]}
            for category_id in sorted(categories)
        ],
        "per_class": {
            str(category_id): per_class[category_id]
            for category_id in sorted(per_class)
        },
        "overall": overall,
    }


def build_markdown_summary(results: list[dict]) -> str:
    lines = [
        "# Model Validation Summary",
        "",
        "| Model | Precision | Recall | Mean IoU | GT | Pred | TP | FP | FN |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for result in results:
        overall = result["metrics"]["overall"]
        lines.append(
            "| {model} | {precision:.4f} | {recall:.4f} | {mean_iou:.4f} | {gt} | {pred} | {tp} | {fp} | {fn} |".format(
                model=result["model"],
                precision=overall["precision"],
                recall=overall["recall"],
                mean_iou=overall["mean_iou"],
                gt=overall["gt_count"],
                pred=overall["prediction_count"],
                tp=overall["tp"],
                fp=overall["fp"],
                fn=overall["fn"],
            )
        )
    return "\n".join(lines) + "\n"


def main(args: argparse.Namespace) -> int:
    project_root = Path(__file__).resolve().parents[1]
    coco_path = project_path(args.coco)
    image_roots = [project_path(root) for root in args.image_roots]
    output_dir = build_output_dir(args.output_dir)
    predictions_dir = output_dir / "predictions"
    metrics_dir = output_dir / "metrics"
    annotated_dir = output_dir / "annotated"
    output_dir.mkdir(parents=True, exist_ok=True)
    predictions_dir.mkdir(parents=True, exist_ok=True)
    metrics_dir.mkdir(parents=True, exist_ok=True)
    annotated_dir.mkdir(parents=True, exist_ok=True)

    coco_data = load_json(coco_path)
    labels = [str(category["name"]) for category in coco_data.get("categories", [])]
    resolved_images = resolve_images(coco_data, image_roots)
    image_paths = [Path(entry["resolved_path"]) for entry in resolved_images]
    category_map = category_name_to_id(coco_data)

    model_runners = {
        "ultralytics": lambda: run_ultralytics(
            image_paths,
            checkpoint=args.ultralytics_model,
            confidence=args.ultralytics_conf,
            annotated_dir=annotated_dir / "ultralytics",
        ),
        "detectron2": lambda: run_detectron2(
            image_paths,
            config_path=args.detectron2_config,
            threshold=args.detectron2_threshold,
            device=None,
            annotated_dir=annotated_dir / "detectron2",
        ),
        "grounding-dino": lambda: run_grounding_dino(
            image_paths,
            model_id=args.grounding_dino_model,
            labels=labels,
            box_threshold=args.grounding_box_threshold,
            text_threshold=args.grounding_text_threshold,
            annotated_dir=annotated_dir / "grounding-dino",
        ),
        "owlv2": lambda: run_owlv2(
            image_paths,
            model_id=args.owlv2_model,
            labels=labels,
            threshold=args.owlv2_threshold,
            annotated_dir=annotated_dir / "owlv2",
        ),
        "florence2": lambda: run_florence2(
            image_paths,
            model_id=args.florence2_model,
            labels=labels,
            max_new_tokens=args.florence2_max_new_tokens,
            annotated_dir=annotated_dir / "florence2",
        ),
        "yolox": lambda: run_yolox(
            image_paths,
            exp_file=str(project_path(args.yolox_exp_file)),
            exp_name=None,
            checkpoint_path=str(project_path(args.yolox_checkpoint)),
            device=None,
            conf=args.yolox_conf,
            nms=args.yolox_nms,
            test_size=args.yolox_test_size,
            use_fuse=args.yolox_fuse,
            annotated_dir=annotated_dir / "yolox",
        ),
    }

    results = []
    for model_name in args.models:
        print(f"Running {model_name} on {len(image_paths)} images...")
        run = model_runners[model_name]()

        predictions_data = build_model_predictions(
            run=run,
            resolved_images=resolved_images,
            category_map=category_map,
        )
        predictions_path = predictions_dir / f"{model_name}_predictions.json"
        write_json(predictions_path, predictions_data)

        metrics = evaluate_predictions(
            coco_data=coco_data,
            predictions_data=predictions_data,
            iou_threshold=args.iou_threshold,
            coco_file=coco_path,
        )
        metrics["predictions_file"] = str(predictions_path)
        metrics_path = metrics_dir / f"{model_name}_eval_iou{int(args.iou_threshold * 100):03d}.json"
        write_json(metrics_path, metrics)

        heatmap_path = metrics_dir / f"{model_name}_eval_iou{int(args.iou_threshold * 100):03d}_heatmap.svg"
        heatmap_path.write_text(render_svg(metrics), encoding="utf-8")

        results.append(
            {
                "model": model_name,
                "predictions_path": str(predictions_path),
                "metrics_path": str(metrics_path),
                "heatmap_path": str(heatmap_path),
                "metrics": metrics,
            }
        )

    summary_path = output_dir / "summary.md"
    summary_path.write_text(build_markdown_summary(results), encoding="utf-8")
    manifest = {
        "coco_file": str(coco_path),
        "image_roots": [str(root) for root in image_roots],
        "labels": labels,
        "models": args.models,
        "results": results,
    }
    write_json(output_dir / "manifest.json", manifest)

    print(f"Saved model validation outputs to: {output_dir}")
    return 0


if __name__ == "__main__":
    args = parse_args()
    raise SystemExit(main(args))
