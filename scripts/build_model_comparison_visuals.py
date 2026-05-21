#!/usr/bin/env python3
"""Build comparison visuals from a multi-model validation run."""

from __future__ import annotations

import argparse
import html
import json
import os
from pathlib import Path

from eval_grounding_dino_predictions import compute_iou, group_gt_annotations
from test_baseline_models import safe_stem_name


DEFAULT_RUN_DIR = "reports/model-validation/20260520-184645"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build comparison visuals for a model-validation run."
    )
    parser.add_argument(
        "--run-dir",
        default=DEFAULT_RUN_DIR,
        help=f"Validation run directory. Default: {DEFAULT_RUN_DIR}",
    )
    parser.add_argument(
        "--top-images",
        type=int,
        default=8,
        help="How many hard images to include in the gallery. Default: 8",
    )
    return parser.parse_args()


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def clamp01(value: float) -> float:
    return max(0.0, min(1.0, value))


def interpolate_color(low: tuple[int, int, int], high: tuple[int, int, int], t: float) -> str:
    t = clamp01(t)
    r = round(low[0] + (high[0] - low[0]) * t)
    g = round(low[1] + (high[1] - low[1]) * t)
    b = round(low[2] + (high[2] - low[2]) * t)
    return f"rgb({r},{g},{b})"


def percent_fill(value: float) -> str:
    return interpolate_color((247, 215, 203), (79, 163, 118), value)


def inverse_fill(value: float) -> str:
    return interpolate_color((237, 243, 248), (198, 78, 54), value)


def overall_heatmap_svg(results: list[dict]) -> str:
    columns = [
        ("precision", "Precision", "good"),
        ("recall", "Recall", "good"),
        ("mean_iou", "Mean IoU", "good"),
        ("tp", "TP", "count"),
        ("fp", "FP", "bad"),
        ("fn", "FN", "bad"),
    ]
    left_w = 180
    cell_w = 98
    cell_h = 56
    x0 = 32
    y0 = 112
    width = x0 * 2 + left_w + len(columns) * cell_w
    height = y0 + (len(results) + 1) * cell_h + 80

    lines = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="#f7f5ef"/>',
        f'<text x="{x0}" y="46" font-family="Arial, sans-serif" font-size="28" font-weight="700" fill="#1f2933">Overall Model Comparison</text>',
        f'<text x="{x0}" y="74" font-family="Arial, sans-serif" font-size="14" fill="#52606d">Rows are models, columns are overall metrics on the updated 30-image COCO set.</text>',
    ]

    lines.append(f'<rect x="{x0}" y="{y0}" width="{left_w}" height="{cell_h}" fill="#dbe2ea" rx="10"/>')
    lines.append(f'<text x="{x0 + 16}" y="{y0 + 34}" font-family="Arial, sans-serif" font-size="16" font-weight="700" fill="#1f2933">Model</text>')
    for i, (_, label, _) in enumerate(columns):
        x = x0 + left_w + i * cell_w
        lines.append(f'<rect x="{x}" y="{y0}" width="{cell_w}" height="{cell_h}" fill="#dbe2ea" rx="10"/>')
        lines.append(f'<text x="{x + cell_w/2}" y="{y0 + 33}" text-anchor="middle" font-family="Arial, sans-serif" font-size="14" font-weight="700" fill="#1f2933">{html.escape(label)}</text>')

    for row_idx, result in enumerate(results, start=1):
        y = y0 + row_idx * cell_h
        metrics = result["metrics"]["overall"]
        lines.append(f'<rect x="{x0}" y="{y}" width="{left_w}" height="{cell_h}" fill="#ffffff" stroke="#d9e2ec" rx="10"/>')
        lines.append(f'<text x="{x0 + 16}" y="{y + 33}" font-family="Arial, sans-serif" font-size="16" font-weight="700" fill="#102a43">{html.escape(result["model"])}</text>')
        for i, (key, _, kind) in enumerate(columns):
            x = x0 + left_w + i * cell_w
            value = metrics[key]
            if kind == "good":
                fill = percent_fill(float(value))
                display = f"{float(value):.3f}"
            elif kind == "bad":
                denom = metrics["prediction_count"] if key == "fp" else metrics["gt_count"]
                ratio = float(value) / denom if denom else 0.0
                fill = inverse_fill(ratio)
                display = str(value)
            else:
                fill = percent_fill(metrics["tp"] / metrics["gt_count"] if metrics["gt_count"] else 0.0)
                display = str(value)
            lines.append(f'<rect x="{x}" y="{y}" width="{cell_w}" height="{cell_h}" fill="{fill}" stroke="#ffffff" rx="10"/>')
            lines.append(f'<text x="{x + cell_w/2}" y="{y + 31}" text-anchor="middle" font-family="Arial, sans-serif" font-size="18" font-weight="700" fill="#102a43">{html.escape(display)}</text>')

    lines.append("</svg>")
    return "\n".join(lines)


def per_class_heatmap_svg(results: list[dict]) -> str:
    classes = []
    for result in results:
        for category in result["metrics"]["categories"]:
            if category["name"] not in classes:
                classes.append(category["name"])
    columns = []
    for class_name in classes:
        columns.extend(
            [
                (class_name, "precision", f"{class_name} P"),
                (class_name, "recall", f"{class_name} R"),
                (class_name, "mean_iou", f"{class_name} IoU"),
            ]
        )

    left_w = 180
    cell_w = 90
    cell_h = 56
    x0 = 32
    y0 = 112
    width = x0 * 2 + left_w + len(columns) * cell_w
    height = y0 + (len(results) + 1) * cell_h + 80

    lines = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="#f7f5ef"/>',
        f'<text x="{x0}" y="46" font-family="Arial, sans-serif" font-size="28" font-weight="700" fill="#1f2933">Per-Class Model Comparison</text>',
        f'<text x="{x0}" y="74" font-family="Arial, sans-serif" font-size="14" fill="#52606d">Per-class precision, recall, and mean IoU across all evaluated models.</text>',
    ]

    lines.append(f'<rect x="{x0}" y="{y0}" width="{left_w}" height="{cell_h}" fill="#dbe2ea" rx="10"/>')
    lines.append(f'<text x="{x0 + 16}" y="{y0 + 34}" font-family="Arial, sans-serif" font-size="16" font-weight="700" fill="#1f2933">Model</text>')
    for i, (_, _, label) in enumerate(columns):
        x = x0 + left_w + i * cell_w
        lines.append(f'<rect x="{x}" y="{y0}" width="{cell_w}" height="{cell_h}" fill="#dbe2ea" rx="10"/>')
        lines.append(f'<text x="{x + cell_w/2}" y="{y0 + 33}" text-anchor="middle" font-family="Arial, sans-serif" font-size="13" font-weight="700" fill="#1f2933">{html.escape(label)}</text>')

    for row_idx, result in enumerate(results, start=1):
        y = y0 + row_idx * cell_h
        per_class = result["metrics"]["per_class"]
        name_to_id = {c["name"]: str(c["id"]) for c in result["metrics"]["categories"]}
        lines.append(f'<rect x="{x0}" y="{y}" width="{left_w}" height="{cell_h}" fill="#ffffff" stroke="#d9e2ec" rx="10"/>')
        lines.append(f'<text x="{x0 + 16}" y="{y + 33}" font-family="Arial, sans-serif" font-size="16" font-weight="700" fill="#102a43">{html.escape(result["model"])}</text>')
        for i, (class_name, key, _) in enumerate(columns):
            x = x0 + left_w + i * cell_w
            metrics = per_class[name_to_id[class_name]]
            value = float(metrics[key])
            fill = percent_fill(value)
            lines.append(f'<rect x="{x}" y="{y}" width="{cell_w}" height="{cell_h}" fill="{fill}" stroke="#ffffff" rx="10"/>')
            lines.append(f'<text x="{x + cell_w/2}" y="{y + 31}" text-anchor="middle" font-family="Arial, sans-serif" font-size="16" font-weight="700" fill="#102a43">{value:.3f}</text>')

    lines.append("</svg>")
    return "\n".join(lines)


def precision_recall_scatter_svg(results: list[dict]) -> str:
    width = 900
    height = 620
    left = 90
    right = 40
    top = 70
    bottom = 80
    plot_w = width - left - right
    plot_h = height - top - bottom

    def px_x(v: float) -> float:
        return left + plot_w * v

    def px_y(v: float) -> float:
        return top + plot_h * (1.0 - v)

    colors = ["#ff6b6b", "#2f80ed", "#27ae60", "#f2994a", "#9b51e0", "#219ebc"]

    lines = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="#f7f5ef"/>',
        f'<text x="{left}" y="38" font-family="Arial, sans-serif" font-size="28" font-weight="700" fill="#1f2933">Precision vs Recall</text>',
        f'<text x="{left}" y="58" font-family="Arial, sans-serif" font-size="14" fill="#52606d">Point size tracks mean IoU. Upper-right is better balanced.</text>',
        f'<rect x="{left}" y="{top}" width="{plot_w}" height="{plot_h}" fill="#ffffff" stroke="#d9e2ec"/>',
    ]

    for tick in range(0, 11):
        frac = tick / 10
        x = px_x(frac)
        y = px_y(frac)
        lines.append(f'<line x1="{x}" y1="{top}" x2="{x}" y2="{top + plot_h}" stroke="#ecf0f3" />')
        lines.append(f'<line x1="{left}" y1="{y}" x2="{left + plot_w}" y2="{y}" stroke="#ecf0f3" />')
        lines.append(f'<text x="{x}" y="{top + plot_h + 24}" text-anchor="middle" font-family="Arial, sans-serif" font-size="12" fill="#52606d">{frac:.1f}</text>')
        lines.append(f'<text x="{left - 16}" y="{y + 4}" text-anchor="end" font-family="Arial, sans-serif" font-size="12" fill="#52606d">{frac:.1f}</text>')

    lines.append(f'<text x="{left + plot_w/2}" y="{height - 24}" text-anchor="middle" font-family="Arial, sans-serif" font-size="16" fill="#1f2933">Recall</text>')
    lines.append(f'<text x="28" y="{top + plot_h/2}" transform="rotate(-90 28 {top + plot_h/2})" text-anchor="middle" font-family="Arial, sans-serif" font-size="16" fill="#1f2933">Precision</text>')

    for idx, result in enumerate(results):
        overall = result["metrics"]["overall"]
        x = px_x(float(overall["recall"]))
        y = px_y(float(overall["precision"]))
        r = 8 + float(overall["mean_iou"]) * 18
        color = colors[idx % len(colors)]
        lines.append(f'<circle cx="{x}" cy="{y}" r="{r}" fill="{color}" fill-opacity="0.75" stroke="#102a43" stroke-width="2"/>')
        lines.append(f'<text x="{x}" y="{y - r - 8}" text-anchor="middle" font-family="Arial, sans-serif" font-size="13" font-weight="700" fill="#102a43">{html.escape(result["model"])}</text>')

    lines.append("</svg>")
    return "\n".join(lines)


def coco_bbox_to_xyxy(bbox: list[float]) -> list[float]:
    x, y, w, h = bbox
    return [x, y, x + w, y + h]


def evaluate_image_errors(coco_data: dict, predictions_data: dict, iou_threshold: float = 0.5) -> dict[int, dict]:
    gt_by_key = group_gt_annotations(coco_data)
    per_image: dict[int, dict] = {}
    categories = {int(cat["id"]): cat["name"] for cat in coco_data["categories"]}

    pred_by_key: dict[tuple[int, int], list[dict]] = {}
    for image_entry in predictions_data["predictions"]:
        for det in image_entry["detections"]:
            key = (int(image_entry["image_id"]), int(det["category_id"]))
            pred_by_key.setdefault(key, []).append(
                {
                    "bbox_xyxy": coco_bbox_to_xyxy(det["bbox"]),
                    "score": float(det["score"]),
                }
            )
    for dets in pred_by_key.values():
        dets.sort(key=lambda x: x["score"], reverse=True)

    for image in coco_data["images"]:
        image_id = int(image["id"])
        fp = 0
        fn = 0
        tp = 0
        details = []
        for category_id, category_name in categories.items():
            gt_items = gt_by_key.get((image_id, category_id), [])
            pred_items = pred_by_key.get((image_id, category_id), [])
            matched_gt = set()
            local_tp = 0
            local_fp = 0
            for pred in pred_items:
                best_iou = 0.0
                best_idx = None
                for idx, gt in enumerate(gt_items):
                    if idx in matched_gt:
                        continue
                    iou = compute_iou(pred["bbox_xyxy"], gt["bbox_xyxy"])
                    if iou > best_iou:
                        best_iou = iou
                        best_idx = idx
                if best_idx is not None and best_iou >= iou_threshold:
                    matched_gt.add(best_idx)
                    local_tp += 1
                else:
                    local_fp += 1
            local_fn = len(gt_items) - local_tp
            tp += local_tp
            fp += local_fp
            fn += local_fn
            details.append(
                {
                    "category": category_name,
                    "tp": local_tp,
                    "fp": local_fp,
                    "fn": local_fn,
                }
            )
        per_image[image_id] = {"tp": tp, "fp": fp, "fn": fn, "details": details}
    return per_image


def build_hard_gallery(run_dir: Path, comparisons_dir: Path, manifest: dict, top_images: int) -> str:
    coco_data = load_json(Path(manifest["coco_file"]))
    image_map = {int(img["id"]): img for img in coco_data["images"]}
    aggregate: dict[int, dict] = {}
    per_model_image_errors = {}

    for result in manifest["results"]:
        predictions_data = load_json(Path(result["predictions_path"]))
        image_errors = evaluate_image_errors(coco_data, predictions_data)
        per_model_image_errors[result["model"]] = image_errors
        for image_id, errors in image_errors.items():
            item = aggregate.setdefault(image_id, {"score": 0, "models_with_error": 0})
            score = errors["fp"] + errors["fn"]
            item["score"] += score
            if score > 0:
                item["models_with_error"] += 1

    ranked = sorted(
        aggregate.items(),
        key=lambda kv: (kv[1]["models_with_error"], kv[1]["score"]),
        reverse=True,
    )[:top_images]

    lines = [
        "<!doctype html>",
        "<html><head><meta charset='utf-8'>",
        "<title>Hard Image Gallery</title>",
        "<style>",
        "body{font-family:Arial,sans-serif;background:#f7f5ef;color:#1f2933;margin:24px;}",
        ".card{background:#fff;border:1px solid #d9e2ec;border-radius:12px;padding:16px;margin-bottom:22px;}",
        ".grid{display:grid;grid-template-columns:repeat(3,minmax(260px,1fr));gap:14px;}",
        "img{max-width:100%;border:1px solid #d9e2ec;border-radius:8px;display:block;}",
        ".meta{font-size:13px;color:#52606d;margin:6px 0 12px;}",
        ".model{font-size:14px;font-weight:700;margin:8px 0 4px;}",
        "a{color:#0b69a3;text-decoration:none;} a:hover{text-decoration:underline;}",
        "</style></head><body>",
        "<h1>Hard Image Gallery</h1>",
        "<p>Images ranked by aggregate FP+FN across models. Use this page to compare annotated outputs on the hardest cases.</p>",
    ]

    for image_id, score_info in ranked:
        image = image_map[image_id]
        resolved_path = None
        for result in manifest["results"]:
            preds = load_json(Path(result["predictions_path"]))
            for pred in preds["predictions"]:
                if int(pred["image_id"]) == image_id:
                    resolved_path = pred["resolved_path"]
                    break
            if resolved_path:
                break
        lines.append("<div class='card'>")
        lines.append(f"<h2>{html.escape(Path(image['file_name']).name)}</h2>")
        original_rel = os.path.relpath(Path(resolved_path).resolve(), comparisons_dir)
        lines.append(f"<div class='meta'>Image ID {image_id} • aggregate score {score_info['score']} • models with error {score_info['models_with_error']} • <a href='{html.escape(original_rel)}'>original image</a></div>")
        lines.append("<div class='grid'>")
        for result in manifest["results"]:
            model = result["model"]
            err = per_model_image_errors[model][image_id]
            suffix = Path(resolved_path)
            annotated = run_dir / "annotated" / model / f"{safe_stem_name(suffix)}-annotated{suffix.suffix.lower()}"
            annotated_href = os.path.relpath(annotated.resolve(), comparisons_dir)
            lines.append("<div>")
            lines.append(f"<div class='model'>{html.escape(model)}</div>")
            lines.append(f"<div class='meta'>TP {err['tp']} • FP {err['fp']} • FN {err['fn']}</div>")
            lines.append(f"<a href='{html.escape(annotated_href)}'><img src='{html.escape(annotated_href)}' alt='{html.escape(model)} annotated output'></a>")
            lines.append("</div>")
        lines.append("</div></div>")
    lines.append("</body></html>")
    return "\n".join(lines)


def main() -> int:
    args = parse_args()
    project_root = Path(__file__).resolve().parents[1]
    run_dir = (project_root / args.run_dir).resolve()
    manifest = load_json(run_dir / "manifest.json")
    comparisons_dir = run_dir / "comparisons"
    comparisons_dir.mkdir(parents=True, exist_ok=True)

    results = manifest["results"]

    (comparisons_dir / "overall_model_comparison_heatmap.svg").write_text(
        overall_heatmap_svg(results),
        encoding="utf-8",
    )
    (comparisons_dir / "per_class_model_comparison_heatmap.svg").write_text(
        per_class_heatmap_svg(results),
        encoding="utf-8",
    )
    (comparisons_dir / "precision_recall_scatter.svg").write_text(
        precision_recall_scatter_svg(results),
        encoding="utf-8",
    )
    (comparisons_dir / "hard_image_gallery.html").write_text(
        build_hard_gallery(run_dir, comparisons_dir, manifest, args.top_images),
        encoding="utf-8",
    )

    summary = {
        "run_dir": str(run_dir),
        "generated": [
            "overall_model_comparison_heatmap.svg",
            "per_class_model_comparison_heatmap.svg",
            "precision_recall_scatter.svg",
            "hard_image_gallery.html",
        ],
    }
    (comparisons_dir / "manifest.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(f"Saved comparison visuals to: {comparisons_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
