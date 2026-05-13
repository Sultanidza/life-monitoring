---
name: find-baseline-models-cv
description: Use this skill when you need to find baseline computer-vision detection models for person or musical-instrument classes, shortlist candidates from GitHub, Hugging Face, arXiv, and Papers with Code, prefer YOLO and Detectron2-family models, and filter for PyTorch-compatible implementations.
---

# Find Baseline Models CV

Use this skill for model discovery and baseline selection.

Do not use this skill for training, fine-tuning, benchmarking, or deployment work unless the user explicitly asks for those next steps.

## Target interpretation

Map user requests to standard detection targets before searching:

- `human` -> `person`
- `musical instruments` -> any instrument-detection model with explicit class coverage
- `guitar` -> guitar-specific or instrument models that explicitly include guitar

When the request includes musical instruments:

1. Prefer models that can detect multiple instruments.
2. If no credible multi-instrument baseline is available, narrow the search to guitar detection.

## Search order

Use sources in this order:

1. Papers with Code to identify task framing and common benchmark terms
2. arXiv for primary papers
3. GitHub for popular and maintained implementations
4. Hugging Face for checkpoints and model cards

## Selection rules

Prefer:

- YOLO-family detectors
- Detectron2-based detectors
- Repositories with clear training or inference instructions
- Implementations with explicit PyTorch compatibility
- Models with explicit support for `person`, `instrument`, or `guitar` classes

Down-rank or exclude:

- TensorFlow-only, Darknet-only, or framework-unclear implementations unless PyTorch compatibility is clearly documented
- Repositories with no recent maintenance signals, missing setup steps, or unclear licensing
- Papers or checkpoints without code unless the paper is necessary to establish a baseline family
- Models that do not clearly expose the target class set

## Required checks

For each candidate, verify:

- model family
- task type
- target classes
- framework compatibility, especially PyTorch
- code availability
- checkpoint availability if applicable
- evidence of practical usability

Treat "PyTorch-compatible" as satisfied only when at least one of the following is true:

- native PyTorch implementation
- Detectron2 implementation
- Ultralytics or other PyTorch YOLO implementation
- documented export or port to PyTorch with usable code

## Output format

Return a shortlist table with:

- model or repo name
- model family
- target classes
- source type: paper, repo, or checkpoint
- PyTorch compatibility
- links: GitHub, Hugging Face, arXiv, Papers with Code as available
- reason it is a good baseline

After the table, include:

1. the best baseline for `person` detection
2. the best baseline for musical-instrument detection if available
3. the best fallback baseline for `guitar` detection if multi-instrument coverage is weak or absent
4. any gaps or uncertainty about class coverage

## Search guidance

Use standard search phrases when needed:

- `person detection pytorch yolo`
- `musical instrument detection pytorch`
- `guitar detection pytorch`
- `detectron2 instrument detection`
- `papers with code object detection musical instrument`

If source coverage conflicts, prefer primary evidence in this order:

1. official repository documentation
2. model card
3. paper
4. third-party summaries
