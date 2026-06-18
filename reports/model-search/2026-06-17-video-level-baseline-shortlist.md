# Video-Level Baseline Shortlist — 2026-06-17

Model discovery run via the `find-baseline-models-cv` skill, extended to the
**video level** per mentor guidance ("video models process sequential frames").
Constraints from `PROJECT.md`: targets `person` + `guitar`, PyTorch required,
code + checkpoints required, single-camera / single-user guitar-playing MVP,
prefer minimal labeling. Links verified against live sources on 2026-06-17.

Repo: https://github.com/Sultanidza/life-monitoring

## Two candidate families

The project is moving from image detection to a video-level "is the user playing
guitar?" signal. Two families fit, and they are complementary rather than
either/or:

- **A. Detection + tracking** — keep per-frame person/guitar detection, add
  temporal identity so the existing IoU-based "playing" decision aggregates
  robustly over time.
- **B. Video action recognition** — classify short clips directly as
  "playing guitar / not" with a video-native model.

## Family A — Detection + tracking

| Model/Repo | Family | person+guitar? | Source | PyTorch | Link | Why a good baseline |
|---|---|---|---|---|---|---|
| **BoxMOT** | Pluggable MOT: ByteTrack, BoT-SORT, OC-SORT, DeepOCSORT, BoostTrack, StrongSORT | Yes — detector-agnostic (tracks any boxes) | Repo + ReID checkpoints | Yes | https://github.com/mikel-brostrom/boxmot | Sits on top of the existing Grounding DINO / YOLO detections; no detector change. One API, swappable trackers. |
| **Ultralytics YOLO tracking** | YOLO11 + BoT-SORT/ByteTrack built-in | Yes — custom classes via config | Built-in + checkpoints | Yes | https://docs.ultralytics.com/modes/track | Zero-glue `model.track()` gives per-ID boxes across frames. BoT-SORT default, ByteTrack lightweight. |
| ByteTrack / BoT-SORT (standalone) | MOT algorithms | Yes | Repos | Yes | https://github.com/NirAharon/BoT-SORT | Underlying methods; use via BoxMOT rather than standalone. |

## Family B — Video action recognition

| Model/Repo | Family | Task | K400 "playing guitar"? | PyTorch | Link | Why a good baseline |
|---|---|---|---|---|---|---|
| **VideoMAE (K400-finetuned)** | Masked-autoencoder ViT | Clip classification | Yes — `playing_guitar` is a Kinetics-400 label | Yes (HF Transformers) | https://huggingface.co/MCG-NJU/videomae-base-finetuned-kinetics | Near-zero-shot start: already predicts "playing guitar". A few lines via `VideoMAEForVideoClassification`. Strong features for small-data fine-tune. |
| **InternVideo2** | Video foundation model | Classification + retrieval | K400-evaluated | Yes | https://github.com/OpenGVLab/InternVideo | 2024 SOTA features, best few-shot/zero-shot; heavier, check license (non-commercial). |
| **SlowFast / X3D** | 3D CNN | Clip classification | Yes (K400) | Yes (PyTorchVideo) | https://github.com/facebookresearch/pytorchvideo | X3D is lightweight — good for fixed-camera single-user; classic baselines. |
| **TimeSformer** | Space-time attention ViT | Clip classification | Yes (K400) | Yes (HF) | https://huggingface.co/facebook/timesformer-base-finetuned-k400 | Native HF class, easy inference; older repo. |

Docs reference: https://huggingface.co/docs/transformers/model_doc/videomae

## Recommendation

- **Best fit overall: VideoMAE (base, K400-finetuned).** "Playing guitar" is
  already a Kinetics-400 class, so this gives a working video-level signal today
  with essentially no labeling, and fine-tunes well on a small custom set later.
- **Best complement: BoxMOT** over the existing detector. Keeps the IoU-based
  person/guitar logic but adds temporal identity stability across frames —
  directly addressing the "video = sequential frames" point without discarding
  the IoU work.
- **For Friday:** present both. VideoMAE answers "is playing" directly; BoxMOT
  makes the detection -> IoU -> aggregate pipeline temporally robust. Complementary.

## Gaps / assumptions

- Assumption: `PROJECT.md` preferred families are all image detectors; the search
  was extended to video-native families per mentor guidance. Folded into
  `PROJECT.md`.
- Clip classifiers report *whether* a clip is "playing", not *when within a long
  video*. Exact intervals need temporal localization (ActionFormer / TriDet) and
  more labeling. A sliding-window classifier usually suffices for a fixed camera.
- License check needed before deployment: VideoMAE / InternVideo are often
  non-commercial research licenses.
- Tracking a *guitar* is unusual (near-static, heavily overlapping the person);
  tracking mainly helps the *person* identity, guitar may stay per-frame detection.

## Method note

The two background search agents could not verify links (sandboxed without
network access). Verification was re-run in the main session against live
sources (Hugging Face, GitHub, Ultralytics docs) on 2026-06-17.
