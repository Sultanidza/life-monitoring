#!/usr/bin/env python3
"""Run VideoMAE (Kinetics-400) over real videos to detect 'playing guitar'.

This is the first video-level baseline pass. VideoMAE fine-tuned on Kinetics-400
already has a 'playing guitar' class, so this gives a near-zero-shot temporal
signal: slide a 16-frame window across each video, classify each clip, and record
when 'playing guitar' is predicted. Outputs a per-window timeline (JSON + CSV), a
summary, and an SVG timeline per video, plus an aggregate summary across videos.
"""

from __future__ import annotations

import argparse
import csv
import datetime as dt
import html
import json
from pathlib import Path

import cv2
import numpy as np
import torch
from transformers import VideoMAEForVideoClassification, VideoMAEImageProcessor


DEFAULT_MODEL = "MCG-NJU/videomae-base-finetuned-kinetics"
DEFAULT_OUTPUT_ROOT = "reports/video-baseline"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="VideoMAE playing-guitar detection on video.")
    parser.add_argument("--video", action="append", required=True, help="Video path (repeatable).")
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--output-root", default=DEFAULT_OUTPUT_ROOT)
    parser.add_argument("--target-fps", type=float, default=6.0, help="Decimated sampling fps.")
    parser.add_argument("--window-stride-sec", type=float, default=2.0, help="Seconds between windows.")
    parser.add_argument("--batch-size", type=int, default=8)
    parser.add_argument("--play-threshold", type=float, default=0.5,
                        help="Min playing-guitar probability to flag a window as playing.")
    return parser.parse_args()


def patch_attention_biases(model: VideoMAEForVideoClassification, model_name: str) -> int:
    """Remap VideoMAE's original q_bias/v_bias to the query.bias/value.bias that
    newer transformers expect. Without this, these biases load as zeros and
    silently degrade predictions. Key bias stays zero (VideoMAE has none)."""
    from huggingface_hub import hf_hub_download
    from safetensors.torch import load_file

    checkpoint = load_file(hf_hub_download(model_name, "model.safetensors"))
    remap: dict[str, torch.Tensor] = {}
    for key, tensor in checkpoint.items():
        if key.endswith(".q_bias"):
            remap[key[: -len("q_bias")] + "query.bias"] = tensor
        elif key.endswith(".v_bias"):
            remap[key[: -len("v_bias")] + "value.bias"] = tensor

    params = dict(model.named_parameters())
    applied = 0
    with torch.no_grad():
        for key, tensor in remap.items():
            target = params.get(key)
            if target is not None and target.shape == tensor.shape:
                target.copy_(tensor.to(target.device, target.dtype))
                applied += 1
    return applied


def find_guitar_label(id2label: dict[int, str]) -> tuple[int, str]:
    lowered = {i: str(name).lower() for i, name in id2label.items()}
    for i, name in lowered.items():
        if name == "playing guitar":
            return i, id2label[i]
    for i, name in lowered.items():
        if "guitar" in name:
            return i, id2label[i]
    raise ValueError("No 'guitar' class found in the model label set.")


def decode_decimated(video_path: Path, target_fps: float) -> tuple[list[np.ndarray], float]:
    """Read the video and keep ~target_fps frames, resized to 224, as RGB arrays."""
    capture = cv2.VideoCapture(str(video_path))
    if not capture.isOpened():
        raise RuntimeError(f"Could not open video: {video_path}")
    src_fps = capture.get(cv2.CAP_PROP_FPS) or 30.0
    step = max(1, round(src_fps / target_fps))
    frames: list[np.ndarray] = []
    index = 0
    while True:
        ok, frame = capture.read()
        if not ok:
            break
        if index % step == 0:
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frames.append(cv2.resize(rgb, (224, 224)))
        index += 1
    capture.release()
    effective_fps = src_fps / step
    return frames, effective_fps


def run_video(
    video_path: Path,
    model: VideoMAEForVideoClassification,
    processor: VideoMAEImageProcessor,
    device: torch.device,
    guitar_id: int,
    id2label: dict[int, str],
    args: argparse.Namespace,
    clip_len: int,
) -> dict:
    frames, eff_fps = decode_decimated(video_path, args.target_fps)
    stride = max(1, round(args.window_stride_sec * eff_fps))
    starts = list(range(0, max(0, len(frames) - clip_len) + 1, stride))

    rows: list[dict] = []
    softmax = torch.nn.Softmax(dim=-1)

    for batch_start in range(0, len(starts), args.batch_size):
        batch_starts = starts[batch_start : batch_start + args.batch_size]
        clips = [[frames[s + k] for k in range(clip_len)] for s in batch_starts]
        inputs = processor(clips, return_tensors="pt").to(device)
        with torch.no_grad():
            logits = model(**inputs).logits
        probs = softmax(logits)
        top = torch.topk(probs, k=5, dim=-1)
        for row_i, s in enumerate(batch_starts):
            guitar_prob = float(probs[row_i, guitar_id])
            top_ids = top.indices[row_i].tolist()
            top_label = id2label[top_ids[0]]
            guitar_rank = top_ids.index(guitar_id) + 1 if guitar_id in top_ids else None
            rows.append(
                {
                    "window_index": batch_start + row_i,
                    "start_sec": round(s / eff_fps, 2),
                    "end_sec": round((s + clip_len) / eff_fps, 2),
                    "top1_label": top_label,
                    "top1_prob": round(float(top.values[row_i, 0]), 4),
                    "playing_guitar_prob": round(guitar_prob, 4),
                    "playing_guitar_rank": guitar_rank,
                    "is_playing": bool(guitar_prob >= args.play_threshold),
                }
            )

    total = len(rows)
    playing = sum(1 for r in rows if r["is_playing"])
    mean_guitar = sum(r["playing_guitar_prob"] for r in rows) / total if total else 0.0
    summary = {
        "video": str(video_path),
        "effective_fps": round(eff_fps, 3),
        "clip_len_frames": clip_len,
        "clip_span_sec": round(clip_len / eff_fps, 2),
        "window_stride_sec": args.window_stride_sec,
        "decimated_frames": len(frames),
        "windows": total,
        "playing_windows": playing,
        "playing_rate": round(playing / total, 4) if total else 0.0,
        "mean_playing_guitar_prob": round(mean_guitar, 4),
        "play_threshold": args.play_threshold,
    }
    return {"summary": summary, "rows": rows}


def write_csv(path: Path, rows: list[dict]) -> None:
    fields = [
        "window_index", "start_sec", "end_sec", "top1_label", "top1_prob",
        "playing_guitar_prob", "playing_guitar_rank", "is_playing",
    ]
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def render_timeline_svg(result: dict, title: str) -> str:
    rows = result["rows"]
    summary = result["summary"]
    left, right, top, bottom = 70, 24, 96, 54
    track_h = 150
    col_w = max(2, min(8, round(1100 / max(1, len(rows)))))
    width = left + right + len(rows) * col_w
    height = top + track_h + bottom
    baseline = top + track_h

    svg = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="#f7f5ef" />',
        f'<text x="{left}" y="42" font-family="Arial, sans-serif" font-size="22" font-weight="700" fill="#1f2933">{html.escape(title)}</text>',
        f'<text x="{left}" y="68" font-family="Arial, sans-serif" font-size="13" fill="#52606d">'
        f'playing-guitar rate {summary["playing_rate"]*100:.1f}% • mean prob {summary["mean_playing_guitar_prob"]:.3f} • '
        f'{summary["windows"]} windows • clip {summary["clip_span_sec"]}s</text>',
        f'<line x1="{left}" y1="{baseline}" x2="{width-right}" y2="{baseline}" stroke="#9aa5b1" stroke-width="1" />',
        f'<line x1="{left}" y1="{top}" x2="{left}" y2="{baseline}" stroke="#9aa5b1" stroke-width="1" />',
    ]
    for idx, r in enumerate(rows):
        x = left + idx * col_w
        bar_h = round(r["playing_guitar_prob"] * track_h)
        y = baseline - bar_h
        fill = "#5aa676" if r["is_playing"] else "#c0ccda"
        svg.append(f'<rect x="{x}" y="{y}" width="{max(1, col_w-1)}" height="{bar_h}" fill="{fill}" />')
    # threshold line
    thr_y = baseline - round(summary["play_threshold"] * track_h)
    svg.append(f'<line x1="{left}" y1="{thr_y}" x2="{width-right}" y2="{thr_y}" stroke="#bf4a3f" stroke-width="1" stroke-dasharray="5 4" />')
    svg.append(f'<text x="{width-right}" y="{thr_y-4}" text-anchor="end" font-family="Arial, sans-serif" font-size="10" fill="#bf4a3f">threshold {summary["play_threshold"]:.2f}</text>')
    svg.append(f'<text x="{left}" y="{height-22}" font-family="Arial, sans-serif" font-size="11" fill="#52606d">x: time across video • y: P(playing guitar) • green = above threshold</text>')
    svg.append("</svg>")
    return "\n".join(svg)


def main() -> int:
    args = parse_args()
    project_root = Path(__file__).resolve().parents[1]
    stamp = dt.datetime.now().strftime("%Y%m%d-%H%M%S")
    out_dir = (project_root / args.output_root / stamp).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Loading {args.model} on {device} ...")
    processor = VideoMAEImageProcessor.from_pretrained(args.model)
    model = VideoMAEForVideoClassification.from_pretrained(args.model)
    applied = patch_attention_biases(model, args.model)
    print(f"Patched {applied} attention bias tensors (query/value).")
    model = model.to(device).eval()
    id2label = {int(i): v for i, v in model.config.id2label.items()}
    clip_len = int(getattr(model.config, "num_frames", 16))
    guitar_id, guitar_label = find_guitar_label(id2label)
    print(f"Guitar class: id={guitar_id} label='{guitar_label}' | clip_len={clip_len}")

    aggregate = []
    for raw in args.video:
        video_path = Path(raw).expanduser().resolve()
        print(f"\nProcessing: {video_path.name}")
        result = run_video(video_path, model, processor, device, guitar_id, id2label, args, clip_len)
        stem = video_path.stem.replace(" ", "_")
        (out_dir / f"{stem}_timeline.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
        write_csv(out_dir / f"{stem}_timeline.csv", result["rows"])
        (out_dir / f"{stem}_timeline.svg").write_text(
            render_timeline_svg(result, f"Playing-guitar timeline — {video_path.name}"), encoding="utf-8"
        )
        s = result["summary"]
        aggregate.append(s)
        print(f"  windows={s['windows']} playing={s['playing_windows']} "
              f"rate={s['playing_rate']*100:.1f}% mean_prob={s['mean_playing_guitar_prob']:.3f}")

    overall = {
        "model": args.model,
        "guitar_label": guitar_label,
        "generated": stamp,
        "videos": aggregate,
        "total_windows": sum(s["windows"] for s in aggregate),
        "total_playing_windows": sum(s["playing_windows"] for s in aggregate),
    }
    (out_dir / "summary.json").write_text(json.dumps(overall, indent=2), encoding="utf-8")
    print(f"\nSaved outputs to: {out_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
