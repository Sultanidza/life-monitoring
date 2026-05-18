# Project Config

This file stores project-specific goals and preferences that local Codex skills can read.

## Baseline Model Search

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
