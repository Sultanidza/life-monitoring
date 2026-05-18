# life-monitoring

Minimal project scaffold for `life-monitoring`.

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
- YOLO-World through a local official repo checkout and local config/checkpoint paths

By default, the script runs all models above except YOLOX and YOLO-World.

Results are saved under `reports/test-runs/<timestamp>/`.
Annotated image copies with detection boxes are saved under `reports/test-runs/<timestamp>/annotated/`.

To include every available model in one run:

```bash
python scripts/test_baseline_models.py \
  --source path/to/test-images \
  --models ultralytics detectron2 grounding-dino owlv2 florence2 yolox yolo-world \
  --yolox-exp-file path/to/YOLOX/exps/default/yolox_s.py \
  --yolox-checkpoint path/to/YOLOX/yolox_s.pth \
  --yolo-world-config path/to/YOLO-World/config.py \
  --yolo-world-checkpoint path/to/YOLO-World/weights.pth
```
