#!/usr/bin/env python3
"""Render a simple SVG heatmap for evaluation metrics."""

from __future__ import annotations

import argparse
import html
import json
from pathlib import Path


DEFAULT_INPUT = "data/metrics/grounding_dino_eval_iou050.json"
DEFAULT_OUTPUT = "data/metrics/grounding_dino_eval_iou050_heatmap.svg"

PERCENT_COLUMNS = [
    ("precision", "Precision"),
    ("recall", "Recall"),
    ("mean_iou", "Mean IoU"),
]

COUNT_COLUMNS = [
    ("gt_count", "GT"),
    ("prediction_count", "Pred"),
    ("tp", "TP"),
    ("fp", "FP"),
    ("fn", "FN"),
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build a compact SVG heatmap from evaluation metrics."
    )
    parser.add_argument(
        "--input",
        default=DEFAULT_INPUT,
        help=f"Metrics JSON path. Default: {DEFAULT_INPUT}",
    )
    parser.add_argument(
        "--output",
        default=DEFAULT_OUTPUT,
        help=f"SVG output path. Default: {DEFAULT_OUTPUT}",
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
    return interpolate_color((248, 216, 206), (90, 166, 118), value)


def ratio_fill(value: float, invert: bool = False) -> str:
    score = 1.0 - value if invert else value
    return interpolate_color((241, 244, 248), (82, 132, 193), score)


def build_rows(metrics: dict) -> list[dict]:
    categories = {int(item["id"]): item["name"] for item in metrics["categories"]}
    rows: list[dict] = []

    for category_id in sorted(categories):
        item = metrics["per_class"][str(category_id)]
        row = {
            "label": categories[category_id],
            **item,
        }
        row["tp_rate"] = item["tp"] / item["gt_count"] if item["gt_count"] else 0.0
        row["fp_rate"] = (
            item["fp"] / item["prediction_count"] if item["prediction_count"] else 0.0
        )
        row["fn_rate"] = item["fn"] / item["gt_count"] if item["gt_count"] else 0.0
        rows.append(row)

    overall = dict(metrics["overall"])
    overall["label"] = "overall"
    overall["tp_rate"] = (
        overall["tp"] / overall["gt_count"] if overall["gt_count"] else 0.0
    )
    overall["fp_rate"] = (
        overall["fp"] / overall["prediction_count"] if overall["prediction_count"] else 0.0
    )
    overall["fn_rate"] = (
        overall["fn"] / overall["gt_count"] if overall["gt_count"] else 0.0
    )
    rows.append(overall)
    return rows


def render_svg(metrics: dict) -> str:
    rows = build_rows(metrics)

    default_title = "Detection Metrics Heatmap"
    default_subtitle = (
        f"{len(rows) - 1} classes • IoU threshold {metrics['iou_threshold']:.2f} • "
        f"{Path(metrics['predictions_file']).name}"
    )
    title = metrics.get("title", default_title)
    subtitle = metrics.get("subtitle", default_subtitle)

    left_col_width = 190
    cell_width = 94
    cell_height = 60
    top_pad = 92
    table_x = 32
    table_y = 116

    metric_columns = [
        ("precision", "Precision", "percent"),
        ("recall", "Recall", "percent"),
        ("mean_iou", "Mean IoU", "percent"),
        ("gt_count", "GT", "count"),
        ("prediction_count", "Pred", "count"),
        ("tp", "TP", "count"),
        ("fp", "FP", "count_bad"),
        ("fn", "FN", "count_bad"),
    ]

    width = table_x * 2 + left_col_width + len(metric_columns) * cell_width
    height = table_y + (len(rows) + 1) * cell_height + 100

    svg: list[str] = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="#f7f5ef" />',
        f'<text x="{table_x}" y="46" font-family="Arial, sans-serif" font-size="28" font-weight="700" fill="#1f2933">{html.escape(title)}</text>',
        f'<text x="{table_x}" y="74" font-family="Arial, sans-serif" font-size="14" fill="#52606d">{html.escape(subtitle)}</text>',
    ]

    header_y = table_y
    svg.append(
        f'<rect x="{table_x}" y="{header_y}" width="{left_col_width}" height="{cell_height}" fill="#dbe2ea" rx="10" />'
    )
    svg.append(
        f'<text x="{table_x + 16}" y="{header_y + 36}" font-family="Arial, sans-serif" font-size="16" font-weight="700" fill="#1f2933">Class</text>'
    )

    for index, (_, label, _) in enumerate(metric_columns):
        x = table_x + left_col_width + index * cell_width
        svg.append(
            f'<rect x="{x}" y="{header_y}" width="{cell_width}" height="{cell_height}" fill="#dbe2ea" rx="10" />'
        )
        svg.append(
            f'<text x="{x + cell_width / 2}" y="{header_y + 22}" text-anchor="middle" font-family="Arial, sans-serif" font-size="13" font-weight="700" fill="#1f2933">{html.escape(label)}</text>'
        )
        if label in {"FP", "FN"}:
            hint = "lower better"
        elif label in {"GT", "Pred", "TP"}:
            hint = "count"
        else:
            hint = "higher better"
        svg.append(
            f'<text x="{x + cell_width / 2}" y="{header_y + 42}" text-anchor="middle" font-family="Arial, sans-serif" font-size="10" fill="#52606d">{html.escape(hint)}</text>'
        )

    for row_index, row in enumerate(rows, start=1):
        y = table_y + row_index * cell_height
        svg.append(
            f'<rect x="{table_x}" y="{y}" width="{left_col_width}" height="{cell_height}" fill="#ffffff" stroke="#d9e2ec" rx="10" />'
        )
        svg.append(
            f'<text x="{table_x + 16}" y="{y + 28}" font-family="Arial, sans-serif" font-size="16" font-weight="700" fill="#102a43">{html.escape(str(row["label"]))}</text>'
        )
        svg.append(
            f'<text x="{table_x + 16}" y="{y + 46}" font-family="Arial, sans-serif" font-size="11" fill="#52606d">TP rate {row["tp_rate"]:.2f} • FP rate {row["fp_rate"]:.2f} • FN rate {row["fn_rate"]:.2f}</text>'
        )

        for col_index, (key, _, kind) in enumerate(metric_columns):
            x = table_x + left_col_width + col_index * cell_width
            value = row[key]
            if kind == "percent":
                fill = percent_fill(float(value))
                main_text = f"{float(value):.3f}"
            elif kind == "count_bad":
                denominator = row["prediction_count"] if key == "fp" else row["gt_count"]
                ratio = float(value) / denominator if denominator else 0.0
                fill = ratio_fill(ratio, invert=True)
                main_text = str(value)
            else:
                ratio = row["tp_rate"] if key == "tp" else 0.0
                fill = ratio_fill(ratio)
                main_text = str(value)

            svg.append(
                f'<rect x="{x}" y="{y}" width="{cell_width}" height="{cell_height}" fill="{fill}" stroke="#ffffff" rx="10" />'
            )
            svg.append(
                f'<text x="{x + cell_width / 2}" y="{y + 28}" text-anchor="middle" font-family="Arial, sans-serif" font-size="18" font-weight="700" fill="#102a43">{html.escape(main_text)}</text>'
            )

            if key == "fp":
                detail = f"{row['fp_rate']:.2f}"
            elif key == "fn":
                detail = f"{row['fn_rate']:.2f}"
            elif key == "tp":
                detail = f"{row['tp_rate']:.2f}"
            elif key in {"gt_count", "prediction_count"}:
                detail = "count"
            else:
                detail = f"{float(value) * 100:.1f}%"
            svg.append(
                f'<text x="{x + cell_width / 2}" y="{y + 47}" text-anchor="middle" font-family="Arial, sans-serif" font-size="10" fill="#243b53">{html.escape(detail)}</text>'
            )

    footer_y = height - 34
    svg.append(
        f'<text x="{table_x}" y="{footer_y}" font-family="Arial, sans-serif" font-size="12" fill="#52606d">Source: {html.escape(Path(metrics["coco_file"]).name)} vs {html.escape(Path(metrics["predictions_file"]).name)}</text>'
    )
    svg.append("</svg>")
    return "\n".join(svg)


def main() -> int:
    args = parse_args()
    project_root = Path(__file__).resolve().parents[1]
    input_path = (project_root / args.input).resolve()
    output_path = (project_root / args.output).resolve()

    metrics = load_json(input_path)
    svg = render_svg(metrics)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(svg, encoding="utf-8")

    print(f"Saved heatmap to: {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
