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
- keep the product intentionally narrow: one camera, one user, one core metric
- detect `person`
- detect `guitar`
- test whether `musical instrument` is useful as a broader class
- aggregate practice/session duration from detections
- visualize activity as a 24-hour heatmap by instrument/session tags
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
- demonstrate end-to-end value with a minimal usable output, not only model metrics

Secondary goals:

- keep research notes, hypotheses, results, and context in-project
- make experiments reproducible with scripts
- prepare the project for later packaging and deployment

## MVP Scope

Current MVP scope:

- object detection, not segmentation or tracking
- image/frame-based evaluation first
- one-camera setup
- one-user setup
- classes:
  - `person`
  - `guitar`
  - `musical instrument`
- emphasis on `person` and `guitar` as the clearest initial targets
- aggregate detected activity into session-duration summaries
- generate a 24-hour heatmap or equivalent chart of instrument activity
- keep minimal UX simple, for example notifications plus compact visual reporting

Out of scope for now:

- full production deployment
- full COCO mAP reporting
- end-to-end video analytics beyond frame extraction
- broad lifestyle-event taxonomy beyond the current detection classes
- multi-user generalization as a first-class requirement
- broad robotics scope outside this CV MVP

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

## Product Constraints

Current product constraints:

- one camera
- one primary user
- one narrow activity domain
- one core downstream metric: time spent in sessions or practice activity
- short, concrete iterations with visible artifacts

Current preferred product output:

- detect `person` and instrument presence/interactions
- estimate or aggregate session duration
- visualize activity on a 24-hour timeline or heatmap
- optionally expose minimal notifications, such as Telegram, in later MVP stages

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
- prefer minimizing manual labeling cost
- use pretrained models, transfer learning, and small focused datasets before scaling labeling effort

Important path-resolution rule for Label Studio exports:

- if COCO `file_name` does not resolve directly:
  - take basename
  - URL-decode it
  - strip Label Studio hash prefix like `xxxxxxxx__`
  - search known image roots

## Data Strategy

Current data strategy:

- start with personal/source-local video and image data
- combine project data with open datasets where useful
- prefer narrow, realistic recording scenarios over broad uncontrolled coverage
- use augmentation aggressively for lighting, angle, and noise variation
- treat synthetic data as a valid supplement if real labeled data is scarce
- use weak supervision and semi-automatic labeling where it reduces annotation cost

Techniques explicitly aligned with project direction:

- pseudo-labeling with confidence thresholds
- active-learning style frame prioritization
- tracking-assisted label propagation between frames
- heuristic pre-labeling, such as motion/background-based proposals, when useful

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

Preferred iteration style:

- short sprints
- one instrument or one narrow setup at a time
- fixed camera/light/background when possible
- visible artifacts each cycle: dataset growth, detections, metrics, or visualization output

Data-centric loop to preserve:

1. label a small trusted set
2. run baseline inference
3. prelabel a larger set with the model
4. validate and correct labels
5. recompute metrics
6. track the numbers at each iteration

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

Planned tooling direction beyond current scripts:

- a simple session-duration aggregation step
- heatmap or chart generation for 24-hour activity summaries
- Dockerfile plus `docker-compose` support for reproducible startup

Repository context files that should be maintained:

- `PROJECT.md`
- `AGENTS.md`
- project-local skills under `.codex/skills/`

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

Pre-metrics baseline stage:

- several zero-shot detection models were tested visually
- Grounding DINO emerged as the strongest visual baseline
- the first comparison was based on roughly `30` images
- visual inspection alone was considered insufficient and was later replaced with explicit metrics

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
- narrow, concrete classes appear more useful than broad semantic classes for the current MVP
- a small manually trusted test set is necessary before scaling any video evaluation

## Test Set Strategy

Current agreed test-set strategy:

- start with about `30` manually labeled images for trustworthy evaluation
- then expand toward about `150` images
- use model prelabeling for the larger portion
- manually validate or correct prelabels before treating them as evaluation-quality data
- do not rely on visual judgment alone once metrics are available

Class note:

- one meeting summary referenced `person`, `guitar`, and `percussion` as manual labeling classes
- the current repo COCO evaluation export uses `person`, `guitar`, and `musical instrument`
- this class-definition mismatch should be treated as an open normalization issue for future evaluation work

## Working Hypotheses

Current hypotheses worth testing:

- `guitar` is a better MVP class than `musical instrument`
- open-vocabulary detection is a better fit than closed-set baselines for this project
- prompt wording may materially affect Grounding DINO quality
- data quality and class-definition clarity will improve results faster than swapping models again immediately
- a data-centric iteration loop will produce more value than model-family churn
- one-camera/one-user constraints may allow a useful MVP with much less data than a general detector would require
- a deployable demo with simple reporting may be more valuable than chasing a broader class taxonomy early

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
- plan for a dockerized local or VM deployment path
- keep open-source-friendly structure and startup simplicity where possible

## Near-Term Execution Priorities

Near-term priorities currently supported by the project context:

- keep improving the labeled test set
- increase scene diversity in collected images and videos
- continue extracting frames automatically from video at roughly `2` to `5` second intervals where useful
- use model-assisted prelabeling instead of scaling manual labeling linearly
- keep the current detection case focused before expanding to unrelated domains

## Project Memory Rules

Use this file to keep:

- project context
- model choices
- experiment conclusions
- hypotheses
- dataset and labeling decisions
- evaluation results worth preserving

Full meeting summaries are stored in:

- `docs/meeting-summaries/`

Do not use this file for:

- private personal notes
- raw meeting transcripts
- one-off shell output
- large generated artifacts
