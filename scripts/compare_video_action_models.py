#!/usr/bin/env python3
"""Compare HF video action-recognition baselines on real videos (playing guitar).

Runs several Kinetics-400 clip classifiers over the same time windows and reports,
per model and video, how often "playing guitar" (Kinetics index 232) is the top-1
prediction and its mean probability. Models sample their own frame count from a
shared fixed-duration window so the comparison is temporally fair.

Tier-1 (runnable via transformers): VideoMAE, TimeSformer, ViViT.
"""

from __future__ import annotations

import argparse
import csv
import datetime as dt
import json
from pathlib import Path

import cv2
import numpy as np
import torch
from transformers import AutoConfig, AutoModelForVideoClassification, AutoImageProcessor


def load_processor(repo: str):
    """AutoImageProcessor works for VideoMAE/TimeSformer; ViViT needs its own class
    because its preprocessor_config.json lacks the auto-resolution key."""
    try:
        return AutoImageProcessor.from_pretrained(repo)
    except ValueError:
        from transformers import VivitImageProcessor
        return VivitImageProcessor.from_pretrained(repo)


# Canonical Kinetics-400 index for "playing guitar" (VideoMAE & TimeSformer agree).
GUITAR_INDEX = 232

MODELS = [
    {"key": "videomae", "repo": "MCG-NJU/videomae-base-finetuned-kinetics", "patch_bias": True},
    {"key": "timesformer", "repo": "facebook/timesformer-base-finetuned-k400", "patch_bias": False},
    {"key": "vivit", "repo": "google/vivit-b-16x2-kinetics400", "patch_bias": False},
]

DEFAULT_OUTPUT_ROOT = "reports/video-baseline"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Compare video action models on guitar playing.")
    parser.add_argument("--video", action="append", required=True)
    parser.add_argument("--output-root", default=DEFAULT_OUTPUT_ROOT)
    parser.add_argument("--sample-fps", type=float, default=15.0)
    parser.add_argument("--window-span-sec", type=float, default=2.5)
    parser.add_argument("--window-stride-sec", type=float, default=2.0)
    parser.add_argument("--batch-size", type=int, default=8)
    parser.add_argument("--models", nargs="+", choices=[spec["key"] for spec in MODELS], default=[spec["key"] for spec in MODELS])
    return parser.parse_args()


def patch_attention_biases(model, repo: str) -> int:
    from huggingface_hub import hf_hub_download
    from safetensors.torch import load_file

    checkpoint = load_file(hf_hub_download(repo, "model.safetensors"))
    remap = {}
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


def guitar_index_for(repo: str) -> int:
    cfg = AutoConfig.from_pretrained(repo)
    id2label = {int(i): str(v) for i, v in cfg.id2label.items()}
    for i, name in id2label.items():
        if name.lower() == "playing guitar":
            return i
    return GUITAR_INDEX  # placeholder labels (e.g. ViViT) -> canonical index


def decode_decimated(video_path: Path, sample_fps: float) -> tuple[list[np.ndarray], float]:
    capture = cv2.VideoCapture(str(video_path))
    if not capture.isOpened():
        raise RuntimeError(f"Could not open video: {video_path}")
    src_fps = capture.get(cv2.CAP_PROP_FPS) or 30.0
    step = max(1, round(src_fps / sample_fps))
    frames, index = [], 0
    while True:
        ok, frame = capture.read()
        if not ok:
            break
        if index % step == 0:
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frames.append(cv2.resize(rgb, (224, 224)))
        index += 1
    capture.release()
    return frames, src_fps / step


def run_model_on_frames(repo: str, patch_bias: bool, frames: list[np.ndarray],
                        eff_fps: float, args: argparse.Namespace, device: torch.device) -> dict:
    processor = load_processor(repo)
    model = AutoModelForVideoClassification.from_pretrained(repo)
    if patch_bias:
        patch_attention_biases(model, repo)
    model = model.to(device).eval()
    clip_len = int(getattr(model.config, "num_frames", 16))
    guitar_id = guitar_index_for(repo)

    window_frames = max(clip_len, round(args.window_span_sec * eff_fps))
    stride = max(1, round(args.window_stride_sec * eff_fps))
    starts = list(range(0, max(0, len(frames) - window_frames) + 1, stride))
    sample_offsets = np.linspace(0, window_frames - 1, clip_len).round().astype(int)
    softmax = torch.nn.Softmax(dim=-1)

    id2label = {int(i): str(v) for i, v in model.config.id2label.items()}
    top1_guitar, guitar_probs, rows = 0, [], []
    for batch_start in range(0, len(starts), args.batch_size):
        batch = starts[batch_start: batch_start + args.batch_size]
        clips = [[frames[s + off] for off in sample_offsets] for s in batch]
        inputs = processor(clips, return_tensors="pt").to(device)
        with torch.no_grad():
            probs = softmax(model(**inputs).logits)
        top1 = probs.argmax(dim=-1)
        for row in range(len(batch)):
            start_frame = batch[row]
            guitar_prob = float(probs[row, guitar_id])
            top1_id = int(top1[row])
            is_guitar = top1_id == guitar_id
            guitar_probs.append(guitar_prob)
            if is_guitar:
                top1_guitar += 1
            top1_label = id2label.get(top1_id, f"LABEL_{top1_id}")
            if top1_id == GUITAR_INDEX and top1_label.startswith("LABEL_"):
                top1_label = "playing guitar"
            rows.append({"window_index": batch_start + row, "start_sec": round(start_frame / eff_fps, 4), "end_sec": round((start_frame + window_frames) / eff_fps, 4), "top1_id": top1_id, "top1_label": top1_label, "top1_prob": round(float(probs[row, top1_id]), 6), "playing_guitar_prob": round(guitar_prob, 6), "is_playing": is_guitar})

    del model
    if device.type == "cuda":
        torch.cuda.empty_cache()

    total = len(starts)
    return {
        "summary": {
        "repo": repo,
        "clip_len": clip_len,
        "clip_span_sec": round(clip_len and window_frames / eff_fps, 2),
        "windows": total,
        "top1_playing_guitar": top1_guitar,
        "top1_guitar_rate": round(top1_guitar / total, 4) if total else 0.0,
        "mean_playing_guitar_prob": round(sum(guitar_probs) / total, 4) if total else 0.0,
    },
        "rows": rows,
    }


def main() -> int:
    args = parse_args()
    project_root = Path(__file__).resolve().parents[1]
    stamp = dt.datetime.now().strftime("%Y%m%d-%H%M%S")
    out_dir = (project_root / args.output_root / f"{stamp}-comparison").resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    results = []
    for raw in args.video:
        video_path = Path(raw).expanduser().resolve()
        print(f"\nDecoding {video_path.name} ...")
        frames, eff_fps = decode_decimated(video_path, args.sample_fps)
        print(f"  {len(frames)} frames @ {eff_fps:.1f} fps")
        for spec in [item for item in MODELS if item["key"] in args.models]:
            print(f"  running {spec['key']} ...")
            result = run_model_on_frames(spec["repo"], spec["patch_bias"], frames, eff_fps, args, device)
            res = result["summary"]
            res.update({"model": spec["key"], "video": video_path.name})
            results.append(res)
            stem = video_path.stem.replace(" ", "_")
            (out_dir / f"{stem}_{spec['key']}_timeline.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
            with (out_dir / f"{stem}_{spec['key']}_timeline.csv").open("w", newline="", encoding="utf-8") as handle:
                writer = csv.DictWriter(handle, fieldnames=list(result["rows"][0].keys()))
                writer.writeheader()
                writer.writerows(result["rows"])
            print(f"    top1 guitar {res['top1_guitar_rate']*100:5.1f}%  " f"mean prob {res['mean_playing_guitar_prob']:.3f}  ({res['windows']} windows)")

    (out_dir / "comparison.json").write_text(json.dumps(results, indent=2), encoding="utf-8")

    # Build a comparison table aggregated across videos, per model.
    lines = ["# Video action-model comparison — playing guitar\n",
             f"Sampled @ {args.sample_fps} fps, {args.window_span_sec}s windows, "
             f"{args.window_stride_sec}s stride. Metric: top-1 == 'playing guitar' (K400 idx 232).\n",
             "## Per model, per video\n",
             "| Model | Video | Clip frames | Windows | Top-1 guitar rate | Mean P(guitar) |",
             "|---|---|---|---|---|---|"]
    for r in results:
        lines.append(f"| {r['model']} | {r['video']} | {r['clip_len']} | {r['windows']} | "
                     f"{r['top1_guitar_rate']*100:.1f}% | {r['mean_playing_guitar_prob']:.3f} |")
    lines.append("\n## Aggregated per model\n")
    lines.append("| Model | Total windows | Top-1 guitar windows | Top-1 guitar rate | Mean P(guitar) |")
    lines.append("|---|---|---|---|---|")
    for spec in [item for item in MODELS if item["key"] in args.models]:
        rows = [r for r in results if r["model"] == spec["key"]]
        w = sum(r["windows"] for r in rows)
        g = sum(r["top1_playing_guitar"] for r in rows)
        mp = sum(r["mean_playing_guitar_prob"] * r["windows"] for r in rows) / w if w else 0.0
        lines.append(f"| {spec['key']} | {w} | {g} | {g/w*100:.1f}% | {mp:.3f} |")
    (out_dir / "comparison.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"\nSaved comparison to: {out_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
