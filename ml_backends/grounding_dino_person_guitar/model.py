import json
import logging
import os
from typing import Dict, List, Optional
from urllib.parse import parse_qs, unquote, urlparse

from PIL import Image
import torch
from label_studio_ml.model import LabelStudioMLBase
from label_studio_ml.response import ModelResponse
from transformers import AutoModelForZeroShotObjectDetection, AutoProcessor


LOGGER = logging.getLogger(__name__)

DEFAULT_MODEL_ID = "IDEA-Research/grounding-dino-base"
DEFAULT_PROMPT = "guitar. person."
DEFAULT_LABELS = ["guitar", "person"]
DEFAULT_CONFIG_PATH = os.path.join(os.path.dirname(__file__), "config.json")
DEFAULT_LOCAL_FILES_DOCUMENT_ROOT = os.path.realpath(
    os.path.join(os.path.dirname(__file__), "..", "..", "data")
)


def load_backend_config(config_path: str = DEFAULT_CONFIG_PATH) -> Dict:
    if not os.path.exists(config_path):
        return {}
    with open(config_path) as f:
        config = json.load(f)
    if not isinstance(config, dict):
        raise ValueError("config.json must contain a JSON object.")
    return config


def normalize_label(label: str) -> str:
    return str(label).strip().lower()


def to_ls_percent_bbox(
    bbox: List[float],
    width: int,
    height: int,
) -> Dict[str, float]:
    x, y, w, h = bbox
    return {
        "x": x * 100.0 / width,
        "y": y * 100.0 / height,
        "width": w * 100.0 / width,
        "height": h * 100.0 / height,
        "rotation": 0,
    }


def to_coco_bbox(box: List[float]) -> List[float]:
    x1, y1, x2, y2 = box
    return [
        round(float(x1), 2),
        round(float(y1), 2),
        round(float(x2 - x1), 2),
        round(float(y2 - y1), 2),
    ]


def post_process_outputs(
    processor,
    outputs,
    input_ids,
    target_sizes,
    box_threshold: float,
    text_threshold: float,
):
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


class GroundingDinoPersonGuitar(LabelStudioMLBase):
    """Minimal Label Studio ML backend for Grounding DINO image preannotation."""
    _shared_processor = None
    _shared_model = None
    _shared_model_id = None
    _shared_device = None

    def __init__(self, **kwargs):
        config = load_backend_config()
        config.update(kwargs)

        self.model_id = config.get("model_id", DEFAULT_MODEL_ID)
        self.prompt = config.get("prompt", DEFAULT_PROMPT)
        self.box_threshold = float(config.get("box_threshold", 0.35))
        self.text_threshold = float(config.get("text_threshold", 0.25))
        self.device = config.get("device") or (
            "cuda" if torch.cuda.is_available() else "cpu"
        )
        self.allowed_labels = [
            normalize_label(label)
            for label in config.get("labels", DEFAULT_LABELS)
        ]
        self.local_files_document_root = os.path.realpath(
            config.get(
                "local_files_document_root",
                os.getenv(
                    "LABEL_STUDIO_LOCAL_FILES_DOCUMENT_ROOT",
                    DEFAULT_LOCAL_FILES_DOCUMENT_ROOT,
                ),
            )
        )
        self.label_studio_url = config.get(
            "label_studio_url",
            os.getenv("LABEL_STUDIO_URL"),
        )

        project_id = config.pop("project_id", None)
        label_config = config.pop("label_config", None)
        super().__init__(project_id=project_id, label_config=label_config)

        LOGGER.info(
            "Initializing Grounding DINO backend: model_id=%s device=%s prompt=%s",
            self.model_id,
            self.device,
            self.prompt,
        )
        self.processor = None
        self.model = None

    def _resolve_local_files_path(self, image_ref: str) -> Optional[str]:
        parsed = urlparse(image_ref)
        if parsed.path != "/data/local-files/":
            return None

        relative_path = parse_qs(parsed.query).get("d", [None])[0]
        if not relative_path:
            return None

        relative_path = unquote(relative_path).lstrip("/")
        candidate = os.path.realpath(
            os.path.join(self.local_files_document_root, relative_path)
        )
        if os.path.commonpath([self.local_files_document_root, candidate]) != (
            self.local_files_document_root
        ):
            raise ValueError(
                f"Resolved path escapes local files root: {candidate}"
            )
        if not os.path.exists(candidate):
            raise FileNotFoundError(
                f"Resolved local file does not exist: {candidate}"
            )
        return candidate

    def _resolve_image_path(self, image_ref: str, task_id: Optional[int] = None) -> str:
        if os.path.exists(image_ref):
            return image_ref

        local_files_path = self._resolve_local_files_path(image_ref)
        if local_files_path is not None:
            return local_files_path

        return self.get_local_path(
            image_ref,
            project_dir=self.local_files_document_root,
            ls_host=self.label_studio_url,
            task_id=task_id,
        )

    def setup(self):
        self.set("model_version", f"grounding-dino:{self.model_id}")

    @property
    def model_version(self) -> str:
        return self.get("model_version") or (
            f"grounding-dino:{getattr(self, 'model_id', DEFAULT_MODEL_ID)}"
        )

    def _ensure_model_loaded(self):
        if (
            self.__class__._shared_model is not None
            and self.__class__._shared_processor is not None
            and self.__class__._shared_model_id == self.model_id
            and self.__class__._shared_device == self.device
        ):
            self.model = self.__class__._shared_model
            self.processor = self.__class__._shared_processor
            return

        LOGGER.info(
            "Loading Grounding DINO weights: model_id=%s device=%s",
            self.model_id,
            self.device,
        )
        processor = AutoProcessor.from_pretrained(self.model_id)
        model = (
            AutoModelForZeroShotObjectDetection.from_pretrained(self.model_id)
            .to(self.device)
            .eval()
        )

        self.__class__._shared_processor = processor
        self.__class__._shared_model = model
        self.__class__._shared_model_id = self.model_id
        self.__class__._shared_device = self.device
        self.processor = processor
        self.model = model

    def _get_rectanglelabels_schema(self) -> tuple[str, str, List[str]]:
        for from_name, schema in self.parsed_label_config.items():
            if schema.get("type") != "RectangleLabels":
                continue
            to_names = schema.get("to_name") or []
            if not to_names:
                continue
            configured_labels = [
                normalize_label(label)
                for label in schema.get("labels", [])
            ]
            return from_name, to_names[0], configured_labels
        raise ValueError(
            "No RectangleLabels control found in the Label Studio labeling config."
        )

    def _predict_image(self, image_path: str) -> List[dict]:
        self._ensure_model_loaded()
        image = Image.open(image_path).convert("RGB")
        width, height = image.size

        inputs = self.processor(
            images=image,
            text=self.prompt,
            return_tensors="pt",
        ).to(self.device)

        with torch.no_grad():
            outputs = self.model(**inputs)

        processed = post_process_outputs(
            processor=self.processor,
            outputs=outputs,
            input_ids=inputs.input_ids,
            target_sizes=[image.size[::-1]],
            box_threshold=self.box_threshold,
            text_threshold=self.text_threshold,
        )[0]

        boxes = (
            processed["boxes"].tolist()
            if hasattr(processed["boxes"], "tolist")
            else processed["boxes"]
        )
        scores = (
            processed["scores"].tolist()
            if hasattr(processed["scores"], "tolist")
            else processed["scores"]
        )
        labels = processed["labels"]

        detections = []
        for label, score, box in zip(labels, scores, boxes):
            normalized_label = normalize_label(str(label))
            if normalized_label not in self.allowed_labels:
                continue
            detections.append(
                {
                    "label": normalized_label,
                    "score": round(float(score), 4),
                    "bbox": to_coco_bbox(box),
                    "original_width": width,
                    "original_height": height,
                }
            )

        return detections

    def predict(
        self,
        tasks: List[Dict],
        context: Optional[Dict] = None,
        **kwargs,
    ) -> ModelResponse:
        from_name, to_name, configured_labels = self._get_rectanglelabels_schema()
        active_labels = (
            [label for label in self.allowed_labels if label in configured_labels]
            if configured_labels
            else list(self.allowed_labels)
        )

        predictions = []
        for task in tasks:
            image_ref = task["data"][to_name]
            image_path = self._resolve_image_path(
                image_ref,
                task_id=task.get("id"),
            )
            detections = self._predict_image(image_path)

            results = []
            for index, detection in enumerate(detections):
                if detection["label"] not in active_labels:
                    continue

                results.append(
                    {
                        "id": f"{task.get('id', 'task')}-{index}",
                        "from_name": from_name,
                        "to_name": to_name,
                        "type": "rectanglelabels",
                        "original_width": detection["original_width"],
                        "original_height": detection["original_height"],
                        "image_rotation": 0,
                        "score": detection["score"],
                        "value": {
                            **to_ls_percent_bbox(
                                detection["bbox"],
                                detection["original_width"],
                                detection["original_height"],
                            ),
                            "rectanglelabels": [detection["label"]],
                        },
                    }
                )

            avg_score = (
                sum(item["score"] for item in results) / len(results)
                if results
                else 0.0
            )
            predictions.append(
                {
                    "result": results,
                    "score": round(avg_score, 4),
                    "model_version": self.model_version,
                }
            )

        return ModelResponse(predictions=predictions)

    def fit(self, event, data, **kwargs):
        LOGGER.info("Ignoring fit event=%s for inference-only backend.", event)
        return {}
