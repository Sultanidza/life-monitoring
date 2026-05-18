---
name: find-baseline-models-cv
description: Use this skill when you need to find baseline computer-vision models for a project-defined task, shortlist candidates from GitHub, Hugging Face, arXiv, and Papers with Code, prefer the project's requested model families, and filter for the project's required framework compatibility.
---

# Find Baseline Models CV

Use this skill for model discovery and baseline selection.

Do not use this skill for training, fine-tuning, benchmarking, or deployment work unless the user explicitly asks for those next steps.

## Project configuration

Before searching, read `/home/arturka/Documents/Projects/life-monitoring/PROJECT.md` if it exists.

Treat `PROJECT.md` as the source of truth for:

- task type
- target classes
- aliases or class normalization rules
- fallback rules
- preferred model families
- required frameworks
- source priority
- output requirements

If `PROJECT.md` is missing or incomplete, use reasonable defaults and say which assumptions were applied.

## Target interpretation

Map user requests and project targets to standard benchmark or repository terms before searching.

When `PROJECT.md` defines aliases, use them.

When `PROJECT.md` defines fallback rules, apply them in the search and explain when they were needed.

## Search order

Use the source order from `PROJECT.md` if specified.

Otherwise use:

1. Papers with Code to identify task framing and common benchmark terms
2. arXiv for primary papers
3. GitHub for popular and maintained implementations
4. Hugging Face for checkpoints and model cards

## Selection rules

Prefer:

- model families preferred by `PROJECT.md`
- Repositories with clear training or inference instructions
- Implementations compatible with the frameworks required by `PROJECT.md`
- Models with explicit support for the configured target classes

Down-rank or exclude:

- Implementations that do not satisfy the required framework constraints
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

When `PROJECT.md` requires PyTorch compatibility, treat that as satisfied only when at least one of the following is true:

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

1. the best baseline per configured target or target group
2. the best fallback baseline if the configured fallback rules were triggered
3. any gaps or uncertainty about class coverage
4. any assumptions applied because `PROJECT.md` was incomplete

## Search guidance

Generate search phrases dynamically from the configured task and targets.

Typical patterns:

- `{target} {task_type} pytorch`
- `{preferred_family} {target} {task_type}`
- `papers with code {task_type} {target}`
- `{target} huggingface object detection`

If source coverage conflicts, prefer primary evidence in this order:

1. official repository documentation
2. model card
3. paper
4. third-party summaries
