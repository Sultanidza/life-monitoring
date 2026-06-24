# life-monitoring

Computer-vision MVP for detecting when the primary user is playing guitar.

Primary project goal:

- detect guitar playing from video
- evaluate image-level object detection and video-level action recognition

Current selected baselines:

- image detection: Grounding DINO for `person` and `guitar`
- video action recognition: VideoMAE with top-1 `playing guitar`

Validated VideoMAE metrics across three labeled videos and 353 scored windows:

- precision: `0.9409`
- recall: `0.8414`
- F1: `0.8884`
- accuracy: `0.8640`

With the selected temporal smoothing rule:

- precision: `0.9409`
- recall: `0.9119`
- F1: `0.9262`
- accuracy: `0.9065`

See `reports/video-model-validation/final/three-video-validation/comparison.md`.

## Structure

- `data/` for local dataset assets kept out of git
- `PROJECT.md` for project-specific goals and preferences used by local skills
- `src/` for application code
- `.codex/skills/` for project-local Codex skills
- `scripts/test_baseline_models.py` for quick detector smoke tests
- `scripts/extract_video_frames.py` for turning videos into still-image datasets
- `scripts/resolve_coco_image_paths.py` for checking COCO filename alignment against local images
- `scripts/run_grounding_dino_coco.py` for exporting Grounding DINO predictions on COCO-labeled images
- `scripts/eval_grounding_dino_predictions.py` for simple IoU/precision/recall diagnostics
- `scripts/build_metrics_heatmap.py` for rendering an SVG heatmap from saved evaluation metrics
- `scripts/run_coco_model_validation.py` for multi-model validation on a COCO-labeled set
- `scripts/build_model_comparison_visuals.py` for overall/per-class model comparison visuals
- `scripts/build_model_error_overlays.py` for GT-vs-prediction overlay images
- `scripts/compare_video_action_models.py` for VideoMAE/TimeSformer/ViViT inference
- `scripts/score_videomae_against_label_studio.py` for temporal ground-truth scoring
- `reports/` for saved research notes and test runs

## Extract Video Frames

Extract one frame every 2 seconds from a video or a directory of videos:

```bash
python scripts/extract_video_frames.py --source path/to/video-or-folder --interval 2
```

By default:

- frames are saved under `data/frames/<dataset-name>/`
- run metadata is saved under `reports/frame-extraction/<timestamp>/`

Use `--recursive` if `--source` is a directory and the videos are nested in subfolders.

## Annotations

Store dataset labels under `data/annotations/<dataset-name>/`, for example:

- `data/annotations/eval-webcamoid-obs-studio-2026-05-17-11-06-20/coco.json`

Video annotations are Label Studio timeline exports using `playing`, `not_playing`, and `ambiguous`. Windows touching `ambiguous` intervals are excluded from scoring.

## Metrics And Reports

Use:

- `data/metrics/` for the active single-model evaluation artifacts
- `reports/model-validation/<timestamp>/` for image-model comparison runs
- `reports/video-model-validation/final/` for the validated video-model comparison

## Test Baselines

Run the baseline smoke test on a file or directory of images:

```bash
python scripts/test_baseline_models.py --source path/to/test-images
```

The script compares:

- `yolov8n-oiv7.pt` through Ultralytics
- `COCO-Detection/faster_rcnn_R_50_FPN_3x.yaml` through Detectron2 model zoo
- `IDEA-Research/grounding-dino-base` through Transformers
- `google/owlv2-base-patch16-ensemble` through Transformers
- `florence-community/Florence-2-base` through Transformers
- YOLOX through a local official repo environment plus local experiment/checkpoint paths

By default, the script runs all models above except YOLOX.

Results are saved under `reports/test-runs/<timestamp>/`.
Annotated image copies with detection boxes are saved under `reports/test-runs/<timestamp>/annotated/`.

To include every available model in one run:

```bash
python scripts/test_baseline_models.py \
  --source path/to/test-images \
  --models ultralytics detectron2 grounding-dino owlv2 florence2 yolox \
  --yolox-exp-file path/to/YOLOX/exps/default/yolox_s.py \
  --yolox-checkpoint path/to/YOLOX/yolox_s.pth
```

## Current Benchmark Read

On the latest 30-image, 67-box validation set, Grounding DINO is the strongest overall model and the most balanced across precision and recall. It still misses some hard cases, especially mirror reflections, but it remains the best current baseline for this project.

Use:

- `data/metrics/` for the active single-model Grounding DINO evaluation
- `reports/model-validation/<timestamp>/` for multi-model comparisons, heatmaps, and GT-vs-prediction overlays
- `reports/video-model-validation/final/three-video-validation/` for the validated three-video action-model comparison
