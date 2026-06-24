# AGENTS

This file gives project-specific guidance for agents working in `life-monitoring`.

## Project purpose

This project is used for:

- detecting when the primary user is playing guitar at image and video level
- collecting image datasets from local videos
- labeling images
- running detection model experiments
- comparing predictions against COCO-style image ground truth
- comparing video predictions against Label Studio temporal ground truth

## Important paths

- `PROJECT.md`: project-specific goals and preferences used by local skills
- `.codex/skills/`: project-local Codex skills
- `data/frames/`: image datasets
- `data/annotations/`: dataset annotations
- `data/predictions/`: saved model predictions
- `data/metrics/`: active single-model evaluation outputs
- `data/raw-videos/`: optional local video storage
- `reports/`: research notes and run metadata
- `scripts/`: reusable project scripts

## Data layout

Keep reusable dataset assets under `data/`, not `reports/`.

Preferred pattern:

- `data/frames/<dataset-name>/`
- `data/annotations/<dataset-name>/coco.json`
- `data/predictions/<model-or-run>.json`
- `data/metrics/<active-single-model>.json`
- `reports/model-validation/<timestamp>/...` for image-model comparison bundles
- `reports/video-model-validation/final/` for validated video-model artifacts

Current datasets include:

- `data/frames/webcamoid`
- `data/frames/obs-studio-2026-05-17-11-06-20`
- `data/frames/obs-studio-2026-05-17-16-31-19`
- three MP4 recordings under `data/raw-videos/labeling/`
- one three-task Label Studio export under `data/annotations/video-playing/`

## Environment

Use the project virtual environment:

- `.venv/`

Do not recreate or use a second virtual environment such as `env/`.

## Current model workflow

1. Extract frames from videos with `scripts/extract_video_frames.py`
2. Label images and export COCO annotations
3. Resolve COCO image paths with `scripts/resolve_coco_image_paths.py`
4. Run Grounding DINO predictions with `scripts/run_grounding_dino_coco.py`
5. Evaluate predictions with `scripts/eval_grounding_dino_predictions.py`
6. For broader comparisons, use `scripts/run_coco_model_validation.py`
7. Use `scripts/build_model_error_overlays.py` when image-level TP/FP/FN inspection is needed

Video workflow:

1. Label `playing`, `not_playing`, and `ambiguous` temporal intervals.
2. Run `scripts/compare_video_action_models.py` with identical windows.
3. Score timelines with `scripts/score_videomae_against_label_studio.py`.
4. Exclude windows touching `ambiguous`.
5. Aggregate confusion counts before computing combined metrics.

## Annotation and evaluation notes

- COCO is the preferred format for evaluation work.
- Label Studio timeline JSON is the source of truth for video evaluation.
- `playing` means visible intentional guitar playing.
- Pauses up to 2 seconds inside continuous playing remain `playing`.
- Off-camera audio-only playing is `ambiguous`; current models are visual-only.
- Use the category mapping defined in the exported COCO file as the source of truth.
- The current benchmark treats mirror reflections as legitimate visible instances when they are labeled.
- Keep the reporting split consistent:
  - `data/metrics/` for the current active single-model evaluation
  - `reports/model-validation/` for timestamped multi-model comparisons
- When matching Label Studio exports to local files, account for:
  - URL-decoded filenames
  - Label Studio hash prefixes like `xxxxxxxx__filename`

## Current benchmark conclusion

- Grounding DINO is the best balanced current model on project data.
- Reflection-heavy images are a major failure mode and should be inspected with GT-vs-prediction overlays, not metrics alone.
- YOLOX and Detectron2 are useful closed-set baselines for `person`, but they are not competitive zero-shot `guitar` detectors in the current setup.
- VideoMAE is the selected video baseline: precision `0.9409`, recall `0.8414`, F1 `0.8884`, accuracy `0.8640` across 353 scored windows.
- TimeSformer and ViViT have lower combined F1: `0.7000` and `0.4800`.

## Skill usage

The local skill `find-baseline-models-cv` is config-driven.

When using it:

1. Read `PROJECT.md`
2. Use the configured targets, fallback rules, model family preferences, and framework constraints
3. Avoid hardcoding project classes in the skill itself

## Practical rules

- Prefer updating scripts over one-off manual steps when the workflow is repeatable.
- Keep file and dataset names consistent and lowercase with hyphens when possible.
- Keep reports as metadata and notes, not as the main storage for datasets.
- Do not move or rename dataset files casually if annotations or predictions already reference them.
