# Baseline CV Models

Date: 2026-05-11

## Scope

Find baseline computer-vision detection models for:

- `person` detection
- musical-instrument detection
- fallback to `guitar` detection if multi-instrument coverage is weak

Constraints:

- prioritize YOLO and Detectron2 families
- filter for PyTorch compatibility
- use GitHub, Hugging Face, arXiv, and Papers with Code as primary discovery sources

## Task Mapping

- Closed-set baseline task: `Object Detection`
- Fallback task when class coverage is weak: `Open-Vocabulary Object Detection`

## Shortlist

| Baseline | GitHub stars | Exact checkpoint / model id | Exact target support | PyTorch | Notes |
|---|---:|---|---|---|---|
| Ultralytics YOLO | 57k | `yolo11n.pt` as the lightweight starting checkpoint; larger variants follow the same family | COCO path includes `person`. Open Images v7 path includes `Person`, `Musical instrument`, `Guitar`, `Piano`, `Violin`, `Cello`, `Drum`, `Flute`, `Harp`, `Harmonica`, `Musical keyboard`, `Oboe`, `Organ (Musical Instrument)`, `Saxophone`, `Trombone`, `Trumpet`, `Banjo`. | Yes | Best practical YOLO-family baseline. For instruments, the Open Images v7 class set is the important evidence. |
| Detectron2 Faster R-CNN R50-FPN 3x | 34.5k | Config: `COCO-Detection/faster_rcnn_R_50_FPN_3x.yaml` Checkpoint: `model_final_280758.pkl` | COCO 80 classes, including `person`; no strong built-in musical-instrument coverage surfaced from primary sources | Yes | Best canonical Detectron2-family baseline for `person`. |
| Grounding DINO | 10.1k | HF model id: `IDEA-Research/grounding-dino-base` Repo weights: `groundingdino_swint_ogc.pth` | Open-vocabulary prompts rather than fixed labels; usable with `person`, `musical instrument`, `guitar` | Yes | Best fallback when fixed-class instrument coverage is weak or inconsistent. |
| YOLOX | 10.5k | Official families include `YOLOX-s`, `YOLOX-m`, `YOLOX-l`, `YOLOX-x` | Standard object-detection baselines; good for `person`, but no strong official instrument-class evidence surfaced from primary sources | Yes | Strong YOLO-family research baseline, but weaker fit than Ultralytics for the instrument requirement. |

## Recommendations

- Best closed-set baseline: `Ultralytics YOLO + Open Images v7`
- Best fallback baseline: `Grounding DINO`
- Best Detectron2-family baseline for person detection: `Detectron2 Faster R-CNN R50-FPN 3x`

If one practical baseline should be tested first, use `Ultralytics YOLO + Open Images v7`.

If the instrument classes prove noisy or incomplete on real data, switch to `Grounding DINO` and query `guitar` directly.

## Install And Start

### Ultralytics

```bash
pip install ultralytics
```

```python
from ultralytics import YOLO

model = YOLO("yolo11n.pt")
```

```bash
yolo detect train data=open-images-v7.yaml model=yolo11n.pt imgsz=640
```

### Grounding DINO

```bash
git clone https://github.com/IDEA-Research/GroundingDINO
cd GroundingDINO
pip install -e .
mkdir weights
cd weights
wget -q https://github.com/IDEA-Research/GroundingDINO/releases/download/v0.1.0-alpha/groundingdino_swint_ogc.pth
```

```python
from transformers import pipeline

pipe = pipeline("zero-shot-object-detection", model="IDEA-Research/grounding-dino-base")
```

## Sources

- Ultralytics repo: <https://github.com/ultralytics/ultralytics>
- Ultralytics Open Images v7 docs: <https://github.com/ultralytics/ultralytics/blob/main/docs/en/datasets/detect/open-images-v7.md>
- Ultralytics COCO YAML: <https://raw.githubusercontent.com/ultralytics/ultralytics/main/ultralytics/cfg/datasets/coco.yaml>
- Ultralytics Open Images v7 YAML: <https://raw.githubusercontent.com/ultralytics/ultralytics/main/ultralytics/cfg/datasets/open-images-v7.yaml>
- Detectron2 repo: <https://github.com/facebookresearch/detectron2>
- Detectron2 model zoo: <https://github.com/facebookresearch/detectron2/blob/main/MODEL_ZOO.md?plain=1>
- YOLOX repo: <https://github.com/Megvii-BaseDetection/YOLOX>
- Grounding DINO repo: <https://github.com/IDEA-Research/GroundingDINO>
- Grounding DINO Hugging Face model: <https://huggingface.co/IDEA-Research/grounding-dino-base>
- Papers with Code object detection: <https://paperswithcode.com/task/object-detection>
- Papers with Code open-vocabulary object detection: <https://paperswithcode.com/task/open-vocabulary-object-detection>

## Notes

- The strongest evidence for multi-instrument coverage came from the Open Images v7 class list used by Ultralytics.
- No equally strong Detectron2-family instrument-specific baseline was surfaced in this pass.
- GitHub star counts and repository activity are time-sensitive and reflect a check made on 2026-05-11.
