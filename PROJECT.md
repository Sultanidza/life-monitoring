# Project

This file is the canonical project memory for `life-monitoring`.

Store here:

- project goals
- scope decisions
- dataset context
- model findings
- evaluation results
- working hypotheses
- workflow and deployment constraints

Do not store personal notes here.

## Overview

`life-monitoring` is a computer-vision MVP focused on lifestyle and musical-activity monitoring from images and video frames.

Current product direction inferred from the linked project discussions and the implemented repo workflow:

- build an MVP around object detection
- detect `person`
- detect `guitar`
- test whether `musical instrument` is useful as a broader class
- evaluate models with clear IoU and precision/recall diagnostics
- keep the process data-centric
- keep the pipeline portable enough for Docker or `docker-compose`

## Project Goals

Primary goals:

- create a reusable dataset from local videos and screenshots
- label images in a format suitable for objective evaluation
- compare baseline detection models on project data
- inspect prediction failures visually, not only numerically
- converge on a practical baseline for the MVP

Secondary goals:

- keep research notes, hypotheses, results, and context in-project
- make experiments reproducible with scripts
- prepare the project for later packaging and deployment

## MVP Scope

Current MVP scope:

- object detection, not segmentation or tracking
- image/frame-based evaluation first
- classes:
  - `person`
  - `guitar`
  - `musical instrument`
- emphasis on `person` and `guitar` as the clearest initial targets

Out of scope for now:

- full production deployment
- full COCO mAP reporting
- end-to-end video analytics beyond frame extraction
- broad lifestyle-event taxonomy beyond the current detection classes

## Detection Task

```yaml
task_type: object detection

targets:
  - person
  - guitar
  - musical instrument

aliases:
  human: person
  musical instruments: musical instrument

fallback_rules:
  - if_no_multi_instrument_model: use_guitar
  - if_broad_instrument_class_is_noisy: prioritize_guitar_for_evaluation
```

## Model Search Preferences

```yaml
preferred_families:
  - yolo
  - detectron2
  - grounding-dino
  - owlv2

required_frameworks:
  - pytorch

source_priority:
  - paperswithcode
  - arxiv
  - github
  - huggingface

output:
  require_checkpoints: true
  shortlist_size: 5
```

## Current Datasets

Current frame/image roots:

- `data/frames/webcamoid`
- `data/frames/obs-studio-2026-05-17-11-06-20`
- `data/frames/obs-studio-2026-05-17-16-31-19`

Current mixed evaluation annotation set:

- `data/annotations/eval-webcamoid-obs-studio-2026-05-17-11-06-20/coco.json`

That COCO set currently contains:

- `30` images
- `52` annotations
- `3` categories

Category mapping in the current COCO export:

- `0` -> `guitar`
- `1` -> `musical instrument`
- `2` -> `person`

Current labeled export mixes:

- `27` images from `webcamoid`
- `3` images from `obs-studio-2026-05-17-11-06-20`

## Data And Annotation Decisions

Current decisions:

- COCO is the evaluation source of truth
- Label Studio is acceptable for labeling as long as exports are normalized through the resolver
- raw datasets stay under `data/`
- reports and run metadata stay under `reports/`
- keep source datasets separated by folder rather than flattening everything immediately

Important path-resolution rule for Label Studio exports:

- if COCO `file_name` does not resolve directly:
  - take basename
  - URL-decode it
  - strip Label Studio hash prefix like `xxxxxxxx__`
  - search known image roots

## Current Workflow

Current project workflow:

1. extract frames from local videos
2. organize frames under `data/frames/<dataset-name>/`
3. label images in Label Studio
4. export COCO annotations
5. resolve image paths
6. run model inference on labeled images
7. save predictions to `data/predictions/`
8. compute IoU/precision/recall diagnostics
9. inspect false positives, false negatives, and class confusion visually
10. refine data, prompts, and class definitions before making larger model changes

## Implemented Tooling

Current project scripts:

- `scripts/extract_video_frames.py`
- `scripts/test_baseline_models.py`
- `scripts/resolve_coco_image_paths.py`
- `scripts/run_grounding_dino_coco.py`
- `scripts/eval_grounding_dino_predictions.py`

Current environment/tooling assumptions:

- use `.venv/` as the single project virtual environment
- Label Studio is installed in `.venv`
- local file serving for Label Studio should point at the project `data/` root
- `ffmpeg` is available for frame extraction

## Baseline Model Context

Project baseline search and testing so far identified:

- a closed-set baseline path with Ultralytics YOLO
- a closed-set framework baseline path with Detectron2
- open-vocabulary candidates including:
  - Grounding DINO
  - OWLv2
  - Florence-2
  - YOLO-World

Current practical conclusion from project testing:

- Grounding DINO is the strongest current baseline on project data

## Current Results

Grounding DINO COCO inference output:

- `data/predictions/grounding_dino_predictions.json`
- annotated images in `data/predictions/grounding_dino_annotated/`

Current evaluation output:

- `data/metrics/grounding_dino_eval_iou050.json`

Current Grounding DINO metrics at IoU `0.5`:

- `guitar`
  - GT: `22`
  - Pred: `24`
  - TP: `20`
  - FP: `4`
  - FN: `2`
  - Precision: `0.8333`
  - Recall: `0.9091`
  - Mean IoU: `0.8593`
- `musical instrument`
  - GT: `7`
  - Pred: `18`
  - TP: `0`
  - FP: `18`
  - FN: `7`
  - Precision: `0.0000`
  - Recall: `0.0000`
  - Mean IoU: `0.0000`
- `person`
  - GT: `23`
  - Pred: `37`
  - TP: `23`
  - FP: `14`
  - FN: `0`
  - Precision: `0.6216`
  - Recall: `1.0000`
  - Mean IoU: `0.9640`

Overall current totals:

- GT: `52`
- Pred: `79`
- TP: `43`
- FP: `36`
- FN: `9`
- Precision: `0.5443`
- Recall: `0.8269`
- Mean IoU: `0.9153`

## Current Findings

Current findings from the project data:

- `person` works well in recall
- `guitar` is already usable as an evaluation class
- `musical instrument` is currently a poor class for evaluation with Grounding DINO in this setup
- broad instrument labeling appears noisier than concrete `guitar` labeling
- visual inspection is necessary because aggregate metrics alone hide class-confusion patterns

## Working Hypotheses

Current hypotheses worth testing:

- `guitar` is a better MVP class than `musical instrument`
- open-vocabulary detection is a better fit than closed-set baselines for this project
- prompt wording may materially affect Grounding DINO quality
- data quality and class-definition clarity will improve results faster than swapping models again immediately
- a data-centric iteration loop will produce more value than model-family churn

## Evaluation Priorities

Current evaluation priorities:

- IoU-based matching
- precision
- recall
- false positives
- false negatives
- per-class diagnostics
- visual error inspection

Current evaluation policy:

- default IoU threshold: `0.5`
- greedy score-sorted matching
- one GT box can match at most one prediction
- delay full COCO mAP until class definitions and data alignment are more stable

## Deployment Direction

Current deployment expectations:

- keep paths and scripts reproducible
- avoid environment-specific assumptions where possible
- preserve a path toward Docker or `docker-compose`
- prefer simple, scriptable workflows over manual one-offs

## Project Memory Rules

Use this file to keep:

- project context
- model choices
- experiment conclusions
- hypotheses
- dataset and labeling decisions
- evaluation results worth preserving

Do not use this file for:

- private personal notes
- raw meeting transcripts
- one-off shell output
- large generated artifacts
