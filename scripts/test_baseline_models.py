#!/usr/bin/env python3
"""Run baseline detection smoke tests for person and instrument classes.

This script compares multiple closed-set and open-vocabulary detectors on the
same set of images and saves lightweight summaries plus annotated copies in
the project reports directory.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Iterable


IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}
DEFAULT_LABELS = ["person", "musical instrument", "guitar"]
DEFAULT_MODELS = ["ultralytics", "detectron2", "grounding-dino", "owlv2", "florence2"]
ANNOTATION_COLORS = [
    "#ff4d4f",
    "#1890ff",
    "#52c41a",
    "#faad14",
    "#722ed1",
    "#13c2c2",
]


@dataclass
class ModelRun:
    name: str
    metadata: dict
    images: list[dict]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Run selected detection baselines on a file or directory of test "
            "images and save comparable summaries."
        )
    )
    parser.add_argument(
        "--source",
        required=True,
        help="Path to an image file or a directory of images.",
    )
    parser.add_argument(
        "--models",
        nargs="+",
        choices=[
            "ultralytics",
            "detectron2",
            "yolox",
            "grounding-dino",
            "owlv2",
            "yolo-world",
            "florence2",
        ],
        default=DEFAULT_MODELS,
        help="Which models to run.",
    )
    parser.add_argument(
        "--labels",
        nargs="+",
        default=DEFAULT_LABELS,
        help="Grounding DINO target labels and report focus labels.",
    )
    parser.add_argument(
        "--output-dir",
        default=None,
        help="Directory to write results into. Defaults to reports/test-runs/<timestamp>/.",
    )
    parser.add_argument(
        "--ultralytics-model",
        default="yolov8n-oiv7.pt",
        help="Ultralytics checkpoint to load.",
    )
    parser.add_argument(
        "--ultralytics-conf",
        type=float,
        default=0.25,
        help="Confidence threshold for Ultralytics predictions.",
    )
    parser.add_argument(
        "--detectron2-config",
        default="COCO-Detection/faster_rcnn_R_50_FPN_3x.yaml",
        help="Detectron2 model zoo config path.",
    )
    parser.add_argument(
        "--detectron2-threshold",
        type=float,
        default=0.5,
        help="Score threshold for Detectron2 predictions.",
    )
    parser.add_argument(
        "--detectron2-device",
        default=None,
        help="Detectron2 device, such as cuda or cpu. Defaults to auto.",
    )
    parser.add_argument(
        "--grounding-dino-model",
        default="IDEA-Research/grounding-dino-base",
        help="Grounding DINO model id for Hugging Face Transformers.",
    )
    parser.add_argument(
        "--grounding-box-threshold",
        type=float,
        default=0.35,
        help="Grounding DINO box threshold.",
    )
    parser.add_argument(
        "--grounding-text-threshold",
        type=float,
        default=0.25,
        help="Grounding DINO text threshold.",
    )
    parser.add_argument(
        "--owlv2-model",
        default="google/owlv2-base-patch16-ensemble",
        help="OWLv2 model id for Hugging Face Transformers.",
    )
    parser.add_argument(
        "--owlv2-threshold",
        type=float,
        default=0.1,
        help="Score threshold for OWLv2 predictions.",
    )
    parser.add_argument(
        "--florence2-model",
        default="florence-community/Florence-2-base",
        help="Florence-2 model id for Hugging Face Transformers.",
    )
    parser.add_argument(
        "--florence2-max-new-tokens",
        type=int,
        default=256,
        help="Maximum generation length for Florence-2.",
    )
    parser.add_argument(
        "--yolox-exp-file",
        default=None,
        help="Path to a YOLOX experiment file, such as exps/default/yolox_s.py.",
    )
    parser.add_argument(
        "--yolox-exp-name",
        default=None,
        help="YOLOX experiment name, such as yolox-s. Used if --yolox-exp-file is omitted.",
    )
    parser.add_argument(
        "--yolox-checkpoint",
        default=None,
        help="Path to a local YOLOX checkpoint file.",
    )
    parser.add_argument(
        "--yolox-device",
        default=None,
        help="YOLOX device string, such as cuda or cpu. Defaults to auto.",
    )
    parser.add_argument(
        "--yolox-conf",
        type=float,
        default=0.25,
        help="Confidence threshold for YOLOX predictions.",
    )
    parser.add_argument(
        "--yolox-nms",
        type=float,
        default=0.45,
        help="NMS threshold for YOLOX predictions.",
    )
    parser.add_argument(
        "--yolox-test-size",
        type=int,
        nargs=2,
        default=[640, 640],
        metavar=("HEIGHT", "WIDTH"),
        help="YOLOX inference size as HEIGHT WIDTH.",
    )
    parser.add_argument(
        "--yolox-fuse",
        action="store_true",
        help="Fuse Conv and BatchNorm layers for YOLOX inference.",
    )
    parser.add_argument(
        "--yolo-world-config",
        default=None,
        help="Path to a local YOLO-World config file.",
    )
    parser.add_argument(
        "--yolo-world-checkpoint",
        default=None,
        help="Path to a local YOLO-World checkpoint file.",
    )
    parser.add_argument(
        "--yolo-world-device",
        default="cuda:0",
        help="Device string for YOLO-World, such as cuda:0 or cpu.",
    )
    parser.add_argument(
        "--yolo-world-threshold",
        type=float,
        default=0.1,
        help="Confidence threshold for YOLO-World predictions.",
    )
    parser.add_argument(
        "--yolo-world-topk",
        type=int,
        default=100,
        help="Maximum number of YOLO-World detections to keep per image.",
    )
    parser.add_argument(
        "--yolo-world-amp",
        action="store_true",
        help="Use AMP for YOLO-World inference.",
    )
    return parser.parse_args()


def build_output_dir(raw_output_dir: str | None) -> Path:
    if raw_output_dir:
        return Path(raw_output_dir).expanduser().resolve()

    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    return Path(__file__).resolve().parents[1] / "reports" / "test-runs" / timestamp


def collect_images(source: str) -> list[Path]:
    source_path = Path(source).expanduser().resolve()
    if not source_path.exists():
        raise FileNotFoundError(f"Source does not exist: {source_path}")

    if source_path.is_file():
        if source_path.suffix.lower() not in IMAGE_EXTENSIONS:
            raise ValueError(f"Unsupported image file: {source_path.name}")
        return [source_path]

    images = sorted(
        path
        for path in source_path.rglob("*")
        if path.is_file() and path.suffix.lower() in IMAGE_EXTENSIONS
    )
    if not images:
        raise ValueError(f"No supported images found under: {source_path}")
    return images


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def import_ultralytics():
    try:
        from ultralytics import YOLO
    except ImportError as exc:
        raise RuntimeError(
            "Ultralytics is not installed. Install it with: pip install ultralytics"
        ) from exc
    return YOLO


def import_grounding_dino():
    try:
        import torch
        from PIL import Image
        from transformers import AutoModelForZeroShotObjectDetection, AutoProcessor
    except ImportError as exc:
        raise RuntimeError(
            "Grounding DINO dependencies are missing. Install them with: "
            "pip install torch torchvision pillow transformers"
        ) from exc
    return torch, Image, AutoModelForZeroShotObjectDetection, AutoProcessor


def import_detectron2():
    try:
        import numpy as np
        import torch
        from PIL import Image
        from detectron2 import model_zoo
        from detectron2.config import get_cfg
        from detectron2.data import MetadataCatalog
        from detectron2.engine import DefaultPredictor
    except ImportError as exc:
        raise RuntimeError(
            "Detectron2 dependencies are missing. Install them with a "
            "Detectron2 build compatible with your PyTorch version."
        ) from exc
    return np, torch, Image, model_zoo, get_cfg, MetadataCatalog, DefaultPredictor


def import_owlv2():
    try:
        import torch
        from PIL import Image
        from transformers import Owlv2ForObjectDetection, Owlv2Processor
    except ImportError as exc:
        raise RuntimeError(
            "OWLv2 dependencies are missing. Install them with: "
            "pip install torch torchvision pillow transformers"
        ) from exc
    return torch, Image, Owlv2ForObjectDetection, Owlv2Processor


def import_florence2():
    try:
        import torch
        from PIL import Image
        from transformers import AutoProcessor, Florence2ForConditionalGeneration
    except ImportError as exc:
        raise RuntimeError(
            "Florence-2 dependencies are missing. Install them with: "
            "pip install torch torchvision pillow transformers"
        ) from exc
    return torch, Image, AutoProcessor, Florence2ForConditionalGeneration


def import_yolo_world():
    try:
        import torch
        from mmengine.config import Config
        from mmengine.dataset import Compose
        from mmengine.runner.amp import autocast
        from mmdet.apis import init_detector
        from mmdet.utils import get_test_pipeline_cfg
    except ImportError as exc:
        raise RuntimeError(
            "YOLO-World dependencies are missing. Install the official repo and its "
            "dependencies first, then make sure its environment is active."
        ) from exc
    return torch, Config, Compose, autocast, init_detector, get_test_pipeline_cfg


def import_yolox():
    try:
        import cv2
        import torch
        from yolox.data.data_augment import ValTransform
        from yolox.data.datasets import COCO_CLASSES
        from yolox.exp import get_exp
        from yolox.utils import fuse_model, postprocess
    except ImportError as exc:
        raise RuntimeError(
            "YOLOX dependencies are missing. Install the official repo and its "
            "dependencies first, then make sure its environment is active."
        ) from exc
    return cv2, torch, ValTransform, COCO_CLASSES, get_exp, fuse_model, postprocess


def import_pillow_draw():
    try:
        from PIL import Image, ImageDraw, ImageFont
    except ImportError as exc:
        raise RuntimeError(
            "Pillow is not installed. Install it with: pip install pillow"
        ) from exc
    return Image, ImageDraw, ImageFont


def normalize_prompt_label(label: str) -> str:
    lowered = label.strip().lower()
    for prefix in (
        "a photo of a ",
        "a photo of an ",
        "a photo of ",
        "photo of a ",
        "photo of an ",
        "photo of ",
    ):
        if lowered.startswith(prefix):
            lowered = lowered[len(prefix) :]
            break
    for prefix in ("a ", "an ", "the "):
        if lowered.startswith(prefix):
            return lowered[len(prefix) :]
    return lowered


def box_to_list(box: Iterable[float]) -> list[float]:
    return [round(float(value), 2) for value in box]


def safe_stem_name(path: Path) -> str:
    parent_bits = [part.replace(" ", "_") for part in path.parts[-3:-1]]
    stem = path.stem.replace(" ", "_")
    return "-".join(bit for bit in [*parent_bits, stem] if bit)


def color_for_label(label: str) -> str:
    return ANNOTATION_COLORS[sum(ord(char) for char in label) % len(ANNOTATION_COLORS)]


def draw_detections(
    image_path: Path,
    detections: list[dict],
    destination: Path,
) -> None:
    Image, ImageDraw, ImageFont = import_pillow_draw()

    image = Image.open(image_path).convert("RGB")
    draw = ImageDraw.Draw(image)
    font = ImageFont.load_default()

    for detection in detections:
        label = str(detection["label"])
        score = float(detection["score"])
        x1, y1, x2, y2 = detection["box"]
        color = color_for_label(label)

        draw.rectangle([x1, y1, x2, y2], outline=color, width=3)

        text = f"{label} {score:.2f}"
        try:
            text_x1, text_y1, text_x2, text_y2 = draw.textbbox((x1, y1), text, font=font)
            text_width = text_x2 - text_x1
            text_height = text_y2 - text_y1
        except AttributeError:
            text_width, text_height = draw.textsize(text, font=font)
        label_top = max(0, y1 - text_height - 6)
        label_bottom = label_top + text_height + 4
        label_right = x1 + text_width + 8

        draw.rectangle([x1, label_top, label_right, label_bottom], fill=color)
        draw.text((x1 + 4, label_top + 2), text, fill="white", font=font)

    destination.parent.mkdir(parents=True, exist_ok=True)
    image.save(destination)


def auto_device(torch_module) -> str:
    return "cuda" if torch_module.cuda.is_available() else "cpu"


def run_ultralytics(
    images: list[Path],
    checkpoint: str,
    confidence: float,
    annotated_dir: Path,
) -> ModelRun:
    YOLO = import_ultralytics()
    model = YOLO(checkpoint)
    image_results: list[dict] = []

    for image_path in images:
        predictions = model.predict(
            source=str(image_path),
            conf=confidence,
            verbose=False,
        )
        prediction = predictions[0]
        names = prediction.names
        detections: list[dict] = []

        if prediction.boxes is not None:
            classes = prediction.boxes.cls.tolist()
            scores = prediction.boxes.conf.tolist()
            boxes = prediction.boxes.xyxy.tolist()
            for cls_idx, score, box in zip(classes, scores, boxes):
                detections.append(
                    {
                        "label": str(names[int(cls_idx)]),
                        "score": round(float(score), 4),
                        "box": box_to_list(box),
                    }
                )

        annotated_path = annotated_dir / f"{safe_stem_name(image_path)}-annotated{image_path.suffix.lower()}"
        draw_detections(image_path, detections, annotated_path)

        image_results.append(
            {
                "image": str(image_path),
                "detections": detections,
                "annotated_image": str(annotated_path),
            }
        )

    return ModelRun(
        name="ultralytics",
        metadata={
            "checkpoint": checkpoint,
            "confidence": confidence,
        },
        images=image_results,
    )


def run_detectron2(
    images: list[Path],
    config_path: str,
    threshold: float,
    device: str | None,
    annotated_dir: Path,
) -> ModelRun:
    np, torch, Image, model_zoo, get_cfg, MetadataCatalog, DefaultPredictor = import_detectron2()

    resolved_device = device or auto_device(torch)
    cfg = get_cfg()
    cfg.merge_from_file(model_zoo.get_config_file(config_path))
    cfg.MODEL.WEIGHTS = model_zoo.get_checkpoint_url(config_path)
    cfg.MODEL.ROI_HEADS.SCORE_THRESH_TEST = threshold
    cfg.MODEL.DEVICE = resolved_device

    predictor = DefaultPredictor(cfg)
    metadata_name = cfg.DATASETS.TEST[0] if cfg.DATASETS.TEST else "__unused"
    metadata = MetadataCatalog.get(metadata_name)
    class_names = getattr(metadata, "thing_classes", None) or []
    image_results: list[dict] = []

    for image_path in images:
        image = np.array(Image.open(image_path).convert("RGB"))[:, :, ::-1]
        outputs = predictor(image)
        instances = outputs["instances"].to("cpu")
        detections: list[dict] = []

        if instances.has("pred_boxes"):
            boxes = instances.pred_boxes.tensor.tolist()
            scores = instances.scores.tolist() if instances.has("scores") else []
            classes = instances.pred_classes.tolist() if instances.has("pred_classes") else []
            for cls_idx, score, box in zip(classes, scores, boxes):
                label = class_names[int(cls_idx)] if int(cls_idx) < len(class_names) else str(cls_idx)
                detections.append(
                    {
                        "label": str(label),
                        "score": round(float(score), 4),
                        "box": box_to_list(box),
                    }
                )

        annotated_path = annotated_dir / f"{safe_stem_name(image_path)}-annotated{image_path.suffix.lower()}"
        draw_detections(image_path, detections, annotated_path)

        image_results.append(
            {
                "image": str(image_path),
                "detections": detections,
                "annotated_image": str(annotated_path),
            }
        )

    return ModelRun(
        name="detectron2",
        metadata={
            "config_path": config_path,
            "weights": cfg.MODEL.WEIGHTS,
            "threshold": threshold,
            "device": resolved_device,
        },
        images=image_results,
    )


def post_process_grounding_outputs(processor, outputs, input_ids, target_sizes, box_threshold, text_threshold):
    try:
        return processor.post_process_grounded_object_detection(
            outputs,
            input_ids,
            box_threshold=box_threshold,
            text_threshold=text_threshold,
            target_sizes=target_sizes,
        )
    except TypeError:
        return processor.post_process_grounded_object_detection(
            outputs,
            input_ids,
            threshold=box_threshold,
            text_threshold=text_threshold,
            target_sizes=target_sizes,
        )


def run_grounding_dino(
    images: list[Path],
    model_id: str,
    labels: list[str],
    box_threshold: float,
    text_threshold: float,
    annotated_dir: Path,
) -> ModelRun:
    torch, Image, AutoModelForZeroShotObjectDetection, AutoProcessor = import_grounding_dino()

    device = "cuda" if torch.cuda.is_available() else "cpu"
    prompt_labels = [f"a {label}" if not label.lower().startswith(("a ", "an ", "the ")) else label for label in labels]
    text_labels = [prompt_labels]

    processor = AutoProcessor.from_pretrained(model_id)
    model = AutoModelForZeroShotObjectDetection.from_pretrained(model_id).to(device)
    image_results: list[dict] = []

    for image_path in images:
        image = Image.open(image_path).convert("RGB")
        inputs = processor(images=image, text=text_labels, return_tensors="pt").to(device)
        with torch.no_grad():
            outputs = model(**inputs)

        processed = post_process_grounding_outputs(
            processor=processor,
            outputs=outputs,
            input_ids=inputs.input_ids,
            target_sizes=[image.size[::-1]],
            box_threshold=box_threshold,
            text_threshold=text_threshold,
        )[0]

        detections: list[dict] = []
        boxes = processed["boxes"].tolist() if hasattr(processed["boxes"], "tolist") else processed["boxes"]
        scores = processed["scores"].tolist() if hasattr(processed["scores"], "tolist") else processed["scores"]
        labels_out = processed["labels"]

        for label, score, box in zip(labels_out, scores, boxes):
            label_text = normalize_prompt_label(str(label))
            detections.append(
                {
                    "label": label_text,
                    "score": round(float(score), 4),
                    "box": box_to_list(box),
                }
            )

        annotated_path = annotated_dir / f"{safe_stem_name(image_path)}-annotated{image_path.suffix.lower()}"
        draw_detections(image_path, detections, annotated_path)

        image_results.append(
            {
                "image": str(image_path),
                "detections": detections,
                "annotated_image": str(annotated_path),
            }
        )

    return ModelRun(
        name="grounding-dino",
        metadata={
            "model_id": model_id,
            "device": device,
            "labels": labels,
            "box_threshold": box_threshold,
            "text_threshold": text_threshold,
        },
        images=image_results,
    )


def run_owlv2(
    images: list[Path],
    model_id: str,
    labels: list[str],
    threshold: float,
    annotated_dir: Path,
) -> ModelRun:
    torch, Image, Owlv2ForObjectDetection, Owlv2Processor = import_owlv2()

    device = "cuda" if torch.cuda.is_available() else "cpu"
    text_labels = [[f"a photo of a {label}" for label in labels]]
    processor = Owlv2Processor.from_pretrained(model_id)
    model = Owlv2ForObjectDetection.from_pretrained(model_id).to(device)
    image_results: list[dict] = []

    for image_path in images:
        image = Image.open(image_path).convert("RGB")
        inputs = processor(text=text_labels, images=image, return_tensors="pt").to(device)
        with torch.no_grad():
            outputs = model(**inputs)

        target_sizes = torch.tensor([(image.height, image.width)], device=device)
        processed = processor.post_process_grounded_object_detection(
            outputs=outputs,
            target_sizes=target_sizes,
            threshold=threshold,
            text_labels=text_labels,
        )[0]

        detections: list[dict] = []
        boxes = processed["boxes"].tolist() if hasattr(processed["boxes"], "tolist") else processed["boxes"]
        scores = processed["scores"].tolist() if hasattr(processed["scores"], "tolist") else processed["scores"]
        text_out = processed.get("text_labels", [])

        for label, score, box in zip(text_out, scores, boxes):
            detections.append(
                {
                    "label": normalize_prompt_label(str(label)),
                    "score": round(float(score), 4),
                    "box": box_to_list(box),
                }
            )

        annotated_path = annotated_dir / f"{safe_stem_name(image_path)}-annotated{image_path.suffix.lower()}"
        draw_detections(image_path, detections, annotated_path)

        image_results.append(
            {
                "image": str(image_path),
                "detections": detections,
                "annotated_image": str(annotated_path),
            }
        )

    return ModelRun(
        name="owlv2",
        metadata={
            "model_id": model_id,
            "device": device,
            "labels": labels,
            "threshold": threshold,
        },
        images=image_results,
    )


def extract_florence2_result(parsed_output: dict, task_prompt: str) -> tuple[list, list]:
    task_result = parsed_output.get(task_prompt, parsed_output)
    boxes = task_result.get("bboxes", [])
    labels = task_result.get("labels")
    if labels is None:
        labels = task_result.get("bboxes_labels", [])
    if labels is None:
        labels = []
    return boxes, labels


def run_florence2(
    images: list[Path],
    model_id: str,
    labels: list[str],
    max_new_tokens: int,
    annotated_dir: Path,
) -> ModelRun:
    torch, Image, AutoProcessor, Florence2ForConditionalGeneration = import_florence2()

    device = "cuda" if torch.cuda.is_available() else "cpu"
    task_prompt = "<OPEN_VOCABULARY_DETECTION>"
    text_input = " <and> ".join(labels)
    prompt = task_prompt + text_input
    processor = AutoProcessor.from_pretrained(model_id)
    model = Florence2ForConditionalGeneration.from_pretrained(model_id).to(device)
    image_results: list[dict] = []

    for image_path in images:
        image = Image.open(image_path).convert("RGB")
        inputs = processor(text=prompt, images=image, return_tensors="pt")
        inputs = {key: value.to(device) for key, value in inputs.items()}

        with torch.no_grad():
            generated_ids = model.generate(
                **inputs,
                max_new_tokens=max_new_tokens,
                do_sample=False,
                num_beams=3,
            )

        generated_text = processor.batch_decode(
            generated_ids,
            skip_special_tokens=False,
            clean_up_tokenization_spaces=False,
        )[0]
        parsed_output = processor.post_process_generation(
            generated_text,
            task=task_prompt,
            image_size=image.size,
        )
        boxes, labels_out = extract_florence2_result(parsed_output, task_prompt)

        detections: list[dict] = []
        for label, box in zip(labels_out, boxes):
            detections.append(
                {
                    "label": normalize_prompt_label(str(label)),
                    "score": 1.0,
                    "box": box_to_list(box),
                }
            )

        annotated_path = annotated_dir / f"{safe_stem_name(image_path)}-annotated{image_path.suffix.lower()}"
        draw_detections(image_path, detections, annotated_path)

        image_results.append(
            {
                "image": str(image_path),
                "detections": detections,
                "annotated_image": str(annotated_path),
                "raw_output": generated_text,
            }
        )

    return ModelRun(
        name="florence2",
        metadata={
            "model_id": model_id,
            "device": device,
            "labels": labels,
            "task_prompt": task_prompt,
            "max_new_tokens": max_new_tokens,
        },
        images=image_results,
    )


def run_yolox(
    images: list[Path],
    exp_file: str | None,
    exp_name: str | None,
    checkpoint_path: str | None,
    device: str | None,
    conf: float,
    nms: float,
    test_size: list[int],
    use_fuse: bool,
    annotated_dir: Path,
) -> ModelRun:
    if not checkpoint_path:
        raise RuntimeError("YOLOX requires --yolox-checkpoint.")
    if not exp_file and not exp_name:
        raise RuntimeError("YOLOX requires either --yolox-exp-file or --yolox-exp-name.")

    cv2, torch, ValTransform, COCO_CLASSES, get_exp, fuse_model, postprocess = import_yolox()

    resolved_device = device or auto_device(torch)
    exp = get_exp(exp_file, exp_name)
    exp.test_conf = conf
    exp.nmsthre = nms
    exp.test_size = tuple(test_size)

    model = exp.get_model()
    checkpoint = torch.load(checkpoint_path, map_location="cpu")
    state_dict = checkpoint["model"] if isinstance(checkpoint, dict) and "model" in checkpoint else checkpoint
    model.load_state_dict(state_dict)
    model.eval()
    model.to(resolved_device)
    if use_fuse:
        model = fuse_model(model)

    preproc = ValTransform(legacy=False)
    image_results: list[dict] = []

    for image_path in images:
        image = cv2.imread(str(image_path))
        if image is None:
            raise RuntimeError(f"Failed to read image for YOLOX: {image_path}")

        height, width = image.shape[:2]
        ratio = min(exp.test_size[0] / height, exp.test_size[1] / width)
        img_tensor, _ = preproc(image, None, exp.test_size)
        img_tensor = torch.from_numpy(img_tensor).unsqueeze(0).float()
        img_tensor = img_tensor.to(resolved_device)

        with torch.no_grad():
            outputs = model(img_tensor)
            outputs = postprocess(
                outputs,
                exp.num_classes,
                exp.test_conf,
                exp.nmsthre,
                class_agnostic=True,
            )[0]

        detections: list[dict] = []
        if outputs is not None:
            outputs = outputs.cpu()
            boxes = outputs[:, 0:4] / ratio
            scores = outputs[:, 4] * outputs[:, 5]
            classes = outputs[:, 6]
            for cls_idx, score, box in zip(classes.tolist(), scores.tolist(), boxes.tolist()):
                label = COCO_CLASSES[int(cls_idx)] if int(cls_idx) < len(COCO_CLASSES) else str(cls_idx)
                detections.append(
                    {
                        "label": str(label),
                        "score": round(float(score), 4),
                        "box": box_to_list(box),
                    }
                )

        annotated_path = annotated_dir / f"{safe_stem_name(image_path)}-annotated{image_path.suffix.lower()}"
        draw_detections(image_path, detections, annotated_path)

        image_results.append(
            {
                "image": str(image_path),
                "detections": detections,
                "annotated_image": str(annotated_path),
            }
        )

    return ModelRun(
        name="yolox",
        metadata={
            "exp_file": str(Path(exp_file).expanduser().resolve()) if exp_file else None,
            "exp_name": exp_name,
            "checkpoint_path": str(Path(checkpoint_path).expanduser().resolve()),
            "device": resolved_device,
            "conf": conf,
            "nms": nms,
            "test_size": list(test_size),
            "fuse": use_fuse,
        },
        images=image_results,
    )


def run_yolo_world(
    images: list[Path],
    config_path: str | None,
    checkpoint_path: str | None,
    labels: list[str],
    threshold: float,
    topk: int,
    device: str,
    use_amp: bool,
    annotated_dir: Path,
) -> ModelRun:
    if not config_path or not checkpoint_path:
        raise RuntimeError(
            "YOLO-World requires both --yolo-world-config and "
            "--yolo-world-checkpoint."
        )

    torch, Config, Compose, autocast, init_detector, get_test_pipeline_cfg = import_yolo_world()

    cfg = Config.fromfile(config_path)
    cfg.load_from = checkpoint_path
    model = init_detector(cfg, checkpoint=checkpoint_path, device=device)
    test_pipeline = Compose(get_test_pipeline_cfg(cfg=cfg))
    texts = [[label] for label in labels] + [[" "]]

    if hasattr(model, "reparameterize"):
        model.reparameterize(texts)

    image_results: list[dict] = []

    for image_path in images:
        data_info = dict(img_id=0, img_path=str(image_path), texts=texts)
        data_info = test_pipeline(data_info)
        data_batch = dict(
            inputs=data_info["inputs"].unsqueeze(0),
            data_samples=[data_info["data_samples"]],
        )

        with autocast(enabled=use_amp), torch.no_grad():
            output = model.test_step(data_batch)[0]

        pred_instances = output.pred_instances
        pred_instances = pred_instances[pred_instances.scores.float() > threshold]
        if len(pred_instances.scores) > topk:
            indices = pred_instances.scores.float().topk(topk)[1]
            pred_instances = pred_instances[indices]
        pred_instances = pred_instances.cpu().numpy()

        detections: list[dict] = []
        boxes = pred_instances["bboxes"]
        labels_idx = pred_instances["labels"]
        scores = pred_instances["scores"]

        for cls_idx, score, box in zip(labels_idx, scores, boxes):
            label_text = texts[int(cls_idx)][0]
            detections.append(
                {
                    "label": normalize_prompt_label(label_text),
                    "score": round(float(score), 4),
                    "box": box_to_list(box),
                }
            )

        annotated_path = annotated_dir / f"{safe_stem_name(image_path)}-annotated{image_path.suffix.lower()}"
        draw_detections(image_path, detections, annotated_path)

        image_results.append(
            {
                "image": str(image_path),
                "detections": detections,
                "annotated_image": str(annotated_path),
            }
        )

    return ModelRun(
        name="yolo-world",
        metadata={
            "config_path": str(Path(config_path).expanduser().resolve()),
            "checkpoint_path": str(Path(checkpoint_path).expanduser().resolve()),
            "device": device,
            "labels": labels,
            "threshold": threshold,
            "topk": topk,
            "amp": use_amp,
        },
        images=image_results,
    )


def summarize_run(run: ModelRun, focus_labels: list[str]) -> dict:
    normalized_focus = {normalize_prompt_label(label) for label in focus_labels}
    all_labels = Counter()
    focus_labels_count = Counter()
    images_with_focus = 0

    for image_entry in run.images:
        seen_focus = False
        for detection in image_entry["detections"]:
            label = normalize_prompt_label(detection["label"])
            all_labels[label] += 1
            if label in normalized_focus:
                focus_labels_count[label] += 1
                seen_focus = True
        if seen_focus:
            images_with_focus += 1

    return {
        "model": run.name,
        "metadata": run.metadata,
        "image_count": len(run.images),
        "total_detections": sum(all_labels.values()),
        "images_with_focus_labels": images_with_focus,
        "focus_label_counts": dict(focus_labels_count),
        "top_labels": all_labels.most_common(10),
    }


def write_json(path: Path, data: object) -> None:
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")


def build_markdown_summary(
    source: Path,
    labels: list[str],
    runs: list[ModelRun],
    summaries: list[dict],
) -> str:
    lines = [
        "# Baseline Model Test Run",
        "",
        f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "",
        f"Source: `{source}`",
        "",
        "## Focus Labels",
        "",
        ", ".join(f"`{label}`" for label in labels),
        "",
        "## Summary",
        "",
        "| Model | Images | Total detections | Images with focus labels | Top focus labels |",
        "|---|---:|---:|---:|---|",
    ]

    for summary in summaries:
        focus_bits = ", ".join(
            f"{label}: {count}" for label, count in summary["focus_label_counts"].items()
        ) or "none"
        lines.append(
            "| {model} | {image_count} | {total_detections} | {images_with_focus_labels} | {focus_bits} |".format(
                model=summary["model"],
                image_count=summary["image_count"],
                total_detections=summary["total_detections"],
                images_with_focus_labels=summary["images_with_focus_labels"],
                focus_bits=focus_bits,
            )
        )

    lines.extend(
        [
            "",
            "## Models",
            "",
        ]
    )

    for run, summary in zip(runs, summaries):
        lines.extend(
            [
                f"### {run.name}",
                "",
                f"- Metadata: `{json.dumps(run.metadata, sort_keys=True)}`",
                f"- Top labels: `{summary['top_labels']}`",
                f"- Annotated images: `{run.metadata['annotated_dir']}`",
                "",
            ]
        )

    return "\n".join(lines) + "\n"


def main() -> int:
    args = parse_args()
    source = Path(args.source).expanduser().resolve()
    images = collect_images(args.source)
    output_dir = build_output_dir(args.output_dir)
    ensure_dir(output_dir)

    runs: list[ModelRun] = []
    errors: list[dict] = []

    if "ultralytics" in args.models:
        try:
            ultralytics_annotated_dir = output_dir / "annotated" / "ultralytics"
            runs.append(
                run_ultralytics(
                    images=images,
                    checkpoint=args.ultralytics_model,
                    confidence=args.ultralytics_conf,
                    annotated_dir=ultralytics_annotated_dir,
                )
            )
            runs[-1].metadata["annotated_dir"] = str(ultralytics_annotated_dir)
        except Exception as exc:  # pragma: no cover - defensive CLI error path
            errors.append({"model": "ultralytics", "error": str(exc)})

    if "detectron2" in args.models:
        try:
            detectron2_annotated_dir = output_dir / "annotated" / "detectron2"
            runs.append(
                run_detectron2(
                    images=images,
                    config_path=args.detectron2_config,
                    threshold=args.detectron2_threshold,
                    device=args.detectron2_device,
                    annotated_dir=detectron2_annotated_dir,
                )
            )
            runs[-1].metadata["annotated_dir"] = str(detectron2_annotated_dir)
        except Exception as exc:  # pragma: no cover - defensive CLI error path
            errors.append({"model": "detectron2", "error": str(exc)})

    if "grounding-dino" in args.models:
        try:
            grounding_annotated_dir = output_dir / "annotated" / "grounding-dino"
            runs.append(
                run_grounding_dino(
                    images=images,
                    model_id=args.grounding_dino_model,
                    labels=args.labels,
                    box_threshold=args.grounding_box_threshold,
                    text_threshold=args.grounding_text_threshold,
                    annotated_dir=grounding_annotated_dir,
                )
            )
            runs[-1].metadata["annotated_dir"] = str(grounding_annotated_dir)
        except Exception as exc:  # pragma: no cover - defensive CLI error path
            errors.append({"model": "grounding-dino", "error": str(exc)})

    if "owlv2" in args.models:
        try:
            owlv2_annotated_dir = output_dir / "annotated" / "owlv2"
            runs.append(
                run_owlv2(
                    images=images,
                    model_id=args.owlv2_model,
                    labels=args.labels,
                    threshold=args.owlv2_threshold,
                    annotated_dir=owlv2_annotated_dir,
                )
            )
            runs[-1].metadata["annotated_dir"] = str(owlv2_annotated_dir)
        except Exception as exc:  # pragma: no cover - defensive CLI error path
            errors.append({"model": "owlv2", "error": str(exc)})

    if "yolox" in args.models:
        try:
            yolox_annotated_dir = output_dir / "annotated" / "yolox"
            runs.append(
                run_yolox(
                    images=images,
                    exp_file=args.yolox_exp_file,
                    exp_name=args.yolox_exp_name,
                    checkpoint_path=args.yolox_checkpoint,
                    device=args.yolox_device,
                    conf=args.yolox_conf,
                    nms=args.yolox_nms,
                    test_size=args.yolox_test_size,
                    use_fuse=args.yolox_fuse,
                    annotated_dir=yolox_annotated_dir,
                )
            )
            runs[-1].metadata["annotated_dir"] = str(yolox_annotated_dir)
        except Exception as exc:  # pragma: no cover - defensive CLI error path
            errors.append({"model": "yolox", "error": str(exc)})

    if "yolo-world" in args.models:
        try:
            yolo_world_annotated_dir = output_dir / "annotated" / "yolo-world"
            runs.append(
                run_yolo_world(
                    images=images,
                    config_path=args.yolo_world_config,
                    checkpoint_path=args.yolo_world_checkpoint,
                    labels=args.labels,
                    threshold=args.yolo_world_threshold,
                    topk=args.yolo_world_topk,
                    device=args.yolo_world_device,
                    use_amp=args.yolo_world_amp,
                    annotated_dir=yolo_world_annotated_dir,
                )
            )
            runs[-1].metadata["annotated_dir"] = str(yolo_world_annotated_dir)
        except Exception as exc:  # pragma: no cover - defensive CLI error path
            errors.append({"model": "yolo-world", "error": str(exc)})

    if "florence2" in args.models:
        try:
            florence2_annotated_dir = output_dir / "annotated" / "florence2"
            runs.append(
                run_florence2(
                    images=images,
                    model_id=args.florence2_model,
                    labels=args.labels,
                    max_new_tokens=args.florence2_max_new_tokens,
                    annotated_dir=florence2_annotated_dir,
                )
            )
            runs[-1].metadata["annotated_dir"] = str(florence2_annotated_dir)
        except Exception as exc:  # pragma: no cover - defensive CLI error path
            errors.append({"model": "florence2", "error": str(exc)})

    if not runs:
        print("No model runs completed successfully.", file=sys.stderr)
        if errors:
            print(json.dumps(errors, indent=2), file=sys.stderr)
        return 1

    summaries = [summarize_run(run, args.labels) for run in runs]

    manifest = {
        "date": datetime.now().isoformat(),
        "source": str(source),
        "images": [str(image) for image in images],
        "labels": args.labels,
        "models_requested": args.models,
        "successful_models": [run.name for run in runs],
        "errors": errors,
    }

    write_json(output_dir / "manifest.json", manifest)
    write_json(output_dir / "summary.json", summaries)
    for run in runs:
        write_json(output_dir / f"{run.name}.json", run.images)

    summary_md = build_markdown_summary(
        source=source,
        labels=args.labels,
        runs=runs,
        summaries=summaries,
    )
    (output_dir / "summary.md").write_text(summary_md, encoding="utf-8")

    print(f"Saved test run to: {output_dir}")
    if errors:
        print("Some model runs failed:")
        print(json.dumps(errors, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
