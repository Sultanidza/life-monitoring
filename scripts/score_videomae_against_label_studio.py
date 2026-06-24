#!/usr/bin/env python3
"""Score a VideoMAE window timeline against Label Studio timeline labels."""

from __future__ import annotations

import argparse
import csv
import datetime as dt
import json
import subprocess
from pathlib import Path
from typing import Any


VALID_LABELS = {"playing", "not_playing", "ambiguous"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Compare VideoMAE playing/not-playing windows with Label Studio ground truth."
    )
    parser.add_argument("--annotations", required=True, help="Label Studio JSON export.")
    parser.add_argument("--timeline", required=True, help="VideoMAE timeline JSON.")
    parser.add_argument("--video", help="Video file used to obtain exact duration.")
    parser.add_argument(
        "--output-dir",
        help="Output directory (default: reports/video-validation/<timestamp>).",
    )
    parser.add_argument(
        "--decision-rule",
        choices=("top1", "threshold"),
        default="top1",
        help="Model decision: top-1 label is playing guitar, or saved is_playing threshold.",
    )
    parser.add_argument(
        "--ground-truth-overlap",
        type=float,
        default=0.5,
        help="Minimum fraction of a window covered by playing to label it playing.",
    )
    return parser.parse_args()


def video_duration(path: Path) -> float:
    result = subprocess.run(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "default=noprint_wrappers=1:nokey=1",
            str(path),
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    return float(result.stdout.strip())


def load_label_studio(path: Path, duration: float) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    tasks = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(tasks, list) or len(tasks) != 1:
        raise ValueError(f"Expected exactly one Label Studio task, found {len(tasks)}.")
    task = tasks[0]
    annotations = [a for a in task.get("annotations", []) if not a.get("was_cancelled")]
    if len(annotations) != 1:
        raise ValueError(f"Expected exactly one completed annotation, found {len(annotations)}.")

    raw_intervals: list[dict[str, Any]] = []
    for result in annotations[0].get("result", []):
        if result.get("type") != "timelinelabels":
            continue
        labels = result.get("value", {}).get("timelinelabels", [])
        ranges = result.get("value", {}).get("ranges", [])
        if len(labels) != 1:
            raise ValueError(f"Timeline result must have one label: {result}")
        label = labels[0]
        if label not in VALID_LABELS:
            raise ValueError(f"Unsupported label {label!r}; expected {sorted(VALID_LABELS)}.")
        for item in ranges:
            raw_intervals.append(
                {"start_frame": float(item["start"]), "end_frame": float(item["end"]), "label": label}
            )

    if not raw_intervals:
        raise ValueError("No timeline label intervals found.")
    raw_intervals.sort(key=lambda row: (row["start_frame"], row["end_frame"]))
    timeline_start = min(row["start_frame"] for row in raw_intervals)
    timeline_end = max(row["end_frame"] for row in raw_intervals)
    timeline_span = timeline_end - timeline_start
    if timeline_span <= 0:
        raise ValueError("Invalid Label Studio timeline span.")

    intervals = []
    for row in raw_intervals:
        start_sec = (row["start_frame"] - timeline_start) / timeline_span * duration
        end_sec = (row["end_frame"] - timeline_start) / timeline_span * duration
        intervals.append(
            {
                **row,
                "start_sec": start_sec,
                "end_sec": end_sec,
            }
        )

    tolerance = 1e-9
    for previous, current in zip(intervals, intervals[1:]):
        if current["start_frame"] < previous["end_frame"] - tolerance:
            raise ValueError(f"Overlapping ground-truth intervals: {previous} and {current}")
        if current["start_frame"] > previous["end_frame"] + tolerance:
            raise ValueError(f"Gap between ground-truth intervals: {previous} and {current}")

    metadata = {
        "task_id": task.get("id"),
        "video": task.get("data", {}).get("video"),
        "timeline_start_frame": timeline_start,
        "timeline_end_frame": timeline_end,
        "timeline_span_frames": timeline_span,
        "seconds_per_timeline_frame": duration / timeline_span,
    }
    return intervals, metadata


def overlap(start_a: float, end_a: float, start_b: float, end_b: float) -> float:
    return max(0.0, min(end_a, end_b) - max(start_a, start_b))


def ground_truth_for_window(
    start: float,
    end: float,
    intervals: list[dict[str, Any]],
    playing_threshold: float,
) -> tuple[str, dict[str, float]]:
    window_duration = end - start
    overlaps = {label: 0.0 for label in VALID_LABELS}
    for interval in intervals:
        overlaps[interval["label"]] += overlap(start, end, interval["start_sec"], interval["end_sec"])

    if overlaps["ambiguous"] > 0:
        return "ambiguous", overlaps
    playing_fraction = overlaps["playing"] / window_duration
    label = "playing" if playing_fraction >= playing_threshold else "not_playing"
    return label, overlaps


def model_prediction(row: dict[str, Any], decision_rule: str) -> str:
    if decision_rule == "top1":
        return "playing" if str(row.get("top1_label", "")).lower() == "playing guitar" else "not_playing"
    return "playing" if bool(row.get("is_playing")) else "not_playing"


def safe_div(numerator: float, denominator: float) -> float:
    return numerator / denominator if denominator else 0.0


def union_duration(intervals: list[tuple[float, float]], limit: float) -> float:
    clipped = sorted((max(0.0, start), min(limit, end)) for start, end in intervals if end > 0 and start < limit)
    if not clipped:
        return 0.0
    total = 0.0
    current_start, current_end = clipped[0]
    for start, end in clipped[1:]:
        if start <= current_end:
            current_end = max(current_end, end)
        else:
            total += current_end - current_start
            current_start, current_end = start, end
    return total + current_end - current_start


def evaluate(
    rows: list[dict[str, Any]],
    intervals: list[dict[str, Any]],
    decision_rule: str,
    gt_overlap: float,
    duration: float,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    scored = []
    counts = {"tp": 0, "fp": 0, "fn": 0, "tn": 0, "excluded": 0}
    predicted_playing_intervals = []

    for row in rows:
        start = float(row["start_sec"])
        end = min(float(row["end_sec"]), duration)
        gt, overlaps = ground_truth_for_window(start, end, intervals, gt_overlap)
        prediction = model_prediction(row, decision_rule)
        if prediction == "playing":
            predicted_playing_intervals.append((start, end))

        if gt == "ambiguous":
            outcome = "excluded"
        elif gt == "playing" and prediction == "playing":
            outcome = "tp"
        elif gt == "not_playing" and prediction == "playing":
            outcome = "fp"
        elif gt == "playing" and prediction == "not_playing":
            outcome = "fn"
        else:
            outcome = "tn"
        counts[outcome] += 1

        scored.append(
            {
                "window_index": row["window_index"],
                "start_sec": start,
                "end_sec": end,
                "ground_truth": gt,
                "prediction": prediction,
                "outcome": outcome,
                "playing_overlap_sec": round(overlaps["playing"], 4),
                "not_playing_overlap_sec": round(overlaps["not_playing"], 4),
                "ambiguous_overlap_sec": round(overlaps["ambiguous"], 4),
                "top1_label": row.get("top1_label"),
                "top1_prob": row.get("top1_prob"),
                "playing_guitar_prob": row.get("playing_guitar_prob"),
            }
        )

    tp, fp, fn, tn = counts["tp"], counts["fp"], counts["fn"], counts["tn"]
    evaluated = tp + fp + fn + tn
    precision = safe_div(tp, tp + fp)
    recall = safe_div(tp, tp + fn)
    metrics = {
        **counts,
        "evaluated_windows": evaluated,
        "total_windows": len(scored),
        "precision": precision,
        "recall": recall,
        "f1": safe_div(2 * precision * recall, precision + recall),
        "accuracy": safe_div(tp + tn, evaluated),
        "specificity": safe_div(tn, tn + fp),
        "ground_truth_playing_sec": sum(
            interval["end_sec"] - interval["start_sec"]
            for interval in intervals
            if interval["label"] == "playing"
        ),
        "predicted_playing_sec": union_duration(predicted_playing_intervals, duration),
    }
    metrics["playing_duration_error_sec"] = (
        metrics["predicted_playing_sec"] - metrics["ground_truth_playing_sec"]
    )
    metrics["playing_duration_absolute_error_sec"] = abs(metrics["playing_duration_error_sec"])
    return scored, metrics


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def format_seconds(value: float) -> str:
    minutes, seconds = divmod(value, 60)
    return f"{int(minutes):02d}:{seconds:05.2f}"


def build_report(
    annotation_path: Path,
    timeline_path: Path,
    duration: float,
    intervals: list[dict[str, Any]],
    metadata: dict[str, Any],
    results: dict[str, dict[str, Any]],
) -> str:
    primary = results["top1"]
    mistakes = [row for row in primary["windows"] if row["outcome"] in {"fp", "fn"}]
    lines = [
        "# VideoMAE Validation Report",
        "",
        f"- Annotation: `{annotation_path}`",
        f"- Prediction timeline: `{timeline_path}`",
        f"- Video duration: {duration:.2f} seconds",
        f"- Label Studio timeline: frames {metadata['timeline_start_frame']:g}–{metadata['timeline_end_frame']:g}",
        "- Ground-truth window rule: `playing` when at least 50% of the window overlaps playing",
        "- Primary model rule: top-1 class equals `playing guitar`",
        "",
        "## Ground-truth intervals",
        "",
        "| Start | End | Label |",
        "|---:|---:|---|",
    ]
    for interval in intervals:
        lines.append(
            f"| {format_seconds(interval['start_sec'])} | {format_seconds(interval['end_sec'])} "
            f"| {interval['label']} |"
        )

    lines.extend(
        [
            "",
            "## Results",
            "",
            "| Decision rule | Precision | Recall | F1 | Accuracy | TP | FP | FN | TN |",
            "|---|---:|---:|---:|---:|---:|---:|---:|---:|",
        ]
    )
    for key, label in (("top1", "Top-1 playing guitar"), ("threshold", "P(guitar) ≥ 0.5")):
        metrics = results[key]["metrics"]
        lines.append(
            f"| {label} | {metrics['precision']:.3f} | {metrics['recall']:.3f} "
            f"| {metrics['f1']:.3f} | {metrics['accuracy']:.3f} | {metrics['tp']} "
            f"| {metrics['fp']} | {metrics['fn']} | {metrics['tn']} |"
        )

    lines.extend(
        [
            "",
            "## Playing-time estimate",
            "",
            f"- Human-labeled playing time: **{primary['metrics']['ground_truth_playing_sec']:.2f} seconds**",
            f"- VideoMAE top-1 predicted playing time: **{primary['metrics']['predicted_playing_sec']:.2f} seconds**",
            f"- Error: **{primary['metrics']['playing_duration_error_sec']:+.2f} seconds**",
            "",
            "The predicted duration is the union of overlapping model windows, so overlapping windows are not double-counted.",
            "",
            "## Incorrect top-1 windows",
            "",
        ]
    )
    if mistakes:
        lines.extend(
            [
                "| Start | End | Error | Model top-1 | P(guitar) |",
                "|---:|---:|---|---|---:|",
            ]
        )
        for row in mistakes:
            lines.append(
                f"| {format_seconds(row['start_sec'])} | {format_seconds(row['end_sec'])} "
                f"| {row['outcome'].upper()} | {row['top1_label']} | "
                f"{float(row['playing_guitar_prob']):.4f} |"
            )
    else:
        lines.append("No false-positive or false-negative windows.")

    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "- Precision measures how often a `playing` prediction is correct.",
            "- Recall measures how much labeled playing the model detects.",
            "- This is a first-video estimate. More labeled videos are required before treating it as general performance.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    args = parse_args()
    project_root = Path(__file__).resolve().parents[1]
    annotation_path = Path(args.annotations).expanduser().resolve()
    timeline_path = Path(args.timeline).expanduser().resolve()
    timeline = json.loads(timeline_path.read_text(encoding="utf-8"))

    if args.video:
        duration = video_duration(Path(args.video).expanduser().resolve())
    else:
        duration = max(float(row["end_sec"]) for row in timeline["rows"])

    intervals, metadata = load_label_studio(annotation_path, duration)
    results = {}
    for rule in ("top1", "threshold"):
        windows, metrics = evaluate(
            timeline["rows"], intervals, rule, args.ground_truth_overlap, duration
        )
        results[rule] = {"metrics": metrics, "windows": windows}

    stamp = dt.datetime.now().strftime("%Y%m%d-%H%M%S")
    output_dir = (
        Path(args.output_dir).expanduser().resolve()
        if args.output_dir
        else project_root / "reports" / "video-validation" / stamp
    )
    output_dir.mkdir(parents=True, exist_ok=True)

    for rule, result in results.items():
        write_csv(output_dir / f"windows-{rule}.csv", result["windows"])
    payload = {
        "annotation": str(annotation_path),
        "timeline": str(timeline_path),
        "video_duration_sec": duration,
        "label_studio": metadata,
        "ground_truth_intervals": intervals,
        "ground_truth_window_overlap_threshold": args.ground_truth_overlap,
        "results": {rule: result["metrics"] for rule, result in results.items()},
    }
    (output_dir / "metrics.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")
    (output_dir / "report.md").write_text(
        build_report(annotation_path, timeline_path, duration, intervals, metadata, results),
        encoding="utf-8",
    )

    primary = results[args.decision_rule]["metrics"]
    print(f"Saved validation artifacts to {output_dir}")
    print(
        f"{args.decision_rule}: precision={primary['precision']:.3f} "
        f"recall={primary['recall']:.3f} f1={primary['f1']:.3f} "
        f"accuracy={primary['accuracy']:.3f}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
