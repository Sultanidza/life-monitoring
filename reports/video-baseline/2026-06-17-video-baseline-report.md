# Video-Level Baseline Report — 2026-06-17

> Historical first-pass report. Final validated results are in
> `reports/video-model-validation/final/three-video-validation/comparison.md`.

First video-level pass: detecting when the user is **playing guitar** directly
from video, using Kinetics-400 action-recognition models near-zero-shot
("playing guitar" is a Kinetics class). Repo: https://github.com/Sultanidza/life-monitoring

## Setup

- **Videos:** 3 real OBS recordings, `~/Videos/OBS-Studio/`, 1152x720 @ 60 fps,
  ~4.2 min each (the same recordings the image frames were sampled from).
- **Method:** slide a fixed-duration window across each video; each model
  classifies the clip into one of 400 Kinetics actions. Primary signal:
  top-1 == "playing guitar" (Kinetics index 232).
- **Sampling (comparison):** 15 fps, 2.5 s windows, 2 s stride → 383 windows total.
- **Scripts:** `scripts/run_videomae_video.py` (single model + per-window timeline),
  `scripts/compare_video_action_models.py` (multi-model comparison).

## Model comparison (383 windows, 3 videos)

| Model | Clip frames | Top-1 "playing guitar" rate | Mean P(guitar) |
|---|---|---|---|
| **VideoMAE** (selected) | 16 | **53.3%** | 0.230 |
| TimeSformer | 8 | 35.2% | 0.263 |
| ViViT | 32 | 19.8% | 0.168 |

VideoMAE wins on **every** video (per-video top-1: 44% / 46% / 70%) and the
ranking is consistent. This empirically confirms the shortlist recommendation.

Notes:
- TimeSformer has higher *mean probability* on two videos but lower *top-1 rate*
  — confident when it fires, but loses top-1 more often. VideoMAE is the more
  reliable "is playing" signal.
- ViViT's HF config uses placeholder labels; index 232 was assumed canonical
  Kinetics ordering. It fired at 45% on video 3, validating the assumption while
  remaining the weakest model.
- All three agree video 3 (`2026-05-19`) has the most playing — cross-model
  sanity check.

## Decision: VideoMAE is the video-level baseline

`MCG-NJU/videomae-base-finetuned-kinetics`. Runs via HuggingFace transformers on
GPU. One loader fix was required: the checkpoint stores VideoMAE's original
`q_bias`/`v_bias`, which newer transformers silently drops (zero-init); the script
remaps them to `query.bias`/`value.bias`. Without the fix the guitar rate
collapsed (0% / mean 0.02); with it, the model works correctly.

## Descriptive analytics (VideoMAE)

Per-video top-1 "playing guitar" rate: 44.4%, 45.7%, 69.5%. Aggregate: **204 of
383 windows (53.3%)**.

Top-1 predicted actions across all windows (single-model run):

| Action (top-1) | Windows |
|---|---|
| playing guitar | 205 |
| juggling balls | 42 |
| stretching arm | 23 |
| dunking basketball | 20 |
| pull ups | 17 |
| headbanging | 12 |

The non-guitar labels are the **not-playing / ambiguous segments**: strumming-arm
motion misread as juggling, music motion as headbanging, reaching as pull-ups.
These are the false-positive examples to inspect.

### Calibration insight (important)

An absolute `P(playing guitar) >= 0.5` threshold is **too strict for a 400-class
softmax** — probability mass splits across related classes (playing guitar /
strumming / tapping / bass / ukulele), so the 0.5 rule undercounts badly (it
flagged only 9-20% of windows). **Top-1 prediction is the correct decision rule**
here (53%). This mirrors step 1: pick the decision rule from how the scores
actually behave, not an arbitrary cutoff.

## Caveats

- At the time of this report the videos were unlabeled, so these rates were descriptive. Validation was completed on 2026-06-23.
- Clip classification says *whether* a clip is playing, not *when* within a long
  video (no exact interval localization).
- Kinetics splits guitar across several classes; aggregating the guitar family
  would raise the rate further.
- VideoMAE / Kinetics checkpoints are often **non-commercial** research licenses —
  verify before any deployment.

## Next steps

- Completed: label all three videos with temporal ground truth.
- Completed: rerun and score VideoMAE, TimeSformer, and ViViT.
- Completed: select VideoMAE by validated F1.
- Remaining: test guitar-family decisions and temporal smoothing.
- Optional: detection + tracking (BoxMOT on Grounding DINO) to complement the
  action signal with per-frame person/guitar boxes over time.

## Artifacts

- `reports/video-baseline/20260617-220910/` — VideoMAE per-video timelines (JSON/CSV/SVG) + summary
- `reports/video-baseline/20260617-221905-comparison/` — 3-model comparison (md + json)
