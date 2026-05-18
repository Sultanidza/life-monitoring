#!/usr/bin/env python3
"""Run Grounding DINO on COCO-labeled images and save predictions as JSON."""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont
import torch
from transformers import AutoModelForZeroShotObjectDetection, AutoProcessor

from resolve_coco_image_paths import collect_root_files, resolve_one


DEFAULT_COCO = (
    "data/annotations/eval-webcamoid-obs-studio-2026-05-17-11-06-20/coco.json"
)
DEFAULT_IMAGE_ROOTS = [
    "data/frames/webcamoid",
    "data/frames/obs-studio-2026-05-17-11-06-20",
]
DEFAULT_OUTPUT = "data/predictions/grounding_dino_predictions.json"
DEFAULT_ANNOTATED_DIR = "data/predictions/grounding_dino_annotated"
DEFAULT_PROMPT = "guitar. musical instrument. person."
DEFAULT_MODEL_ID = "IDEA-Research/grounding-dino-base"
ANNOTATION_COLORS = {
    "guitar": "#ff4d4f",
    "musical instrument": "#1890ff",
    "person": "#52c41a",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run Grounding DINO on COCO images and export predictions."
    )
    parser.add_argument(
        "--coco",
        default=DEFAULT_COCO,
        help=f"Path to COCO ground truth JSON. Default: {DEFAULT_COCO}",
    )
    parser.add_argument(
        "--image-roots",
        nargs="+",
        default=DEFAULT_IMAGE_ROOTS,
        help="Image root folders used by the resolver.",
    )
    parser.add_argument(
        "--output",
        default=DEFAULT_OUTPUT,
        help=f"Path to output predictions JSON. Default: {DEFAULT_OUTPUT}",
    )
    parser.add_argument(
        "--model-id",
        default=DEFAULT_MODEL_ID,
        help=f"Grounding DINO model id. Default: {DEFAULT_MODEL_ID}",
    )
    parser.add_argument(
        "--annotated-dir",
        default=DEFAULT_ANNOTATED_DIR,
        help=f"Directory to save annotated images. Default: {DEFAULT_ANNOTATED_DIR}",
    )
    parser.add_argument(
        "--prompt",
        default=DEFAULT_PROMPT,
        help='Text prompt. Default: "guitar. musical instrument. person."',
    )
    parser.add_argument(
        "--box-threshold",
        type=float,
        default=0.35,
        help="Grounding DINO box threshold. Default: 0.35",
    )
    parser.add_argument(
        "--text-threshold",
        type=float,
        default=0.25,
        help="Grounding DINO text threshold. Default: 0.25",
    )
    parser.add_argument(
        "--device",
        default=None,
        help="Torch device, such as cuda or cpu. Defaults to auto.",
    )
    return parser.parse_args()


def choose_device(requested_device: str | None) -> str:
    if requested_device:
        return requested_device
    return "cuda" if torch.cuda.is_available() else "cpu"


def load_coco(coco_path: Path) -> dict:
    return json.loads(coco_path.read_text(encoding="utf-8"))


def build_category_map(coco_data: dict) -> dict[str, int]:
    category_map: dict[str, int] = {}
    for category in coco_data.get("categories", []):
        category_map[str(category["name"]).strip().lower()] = int(category["id"])
    return category_map


def resolve_images(coco_data: dict, image_roots: list[Path]) -> list[dict]:
    by_name = collect_root_files(image_roots)
    resolved_images: list[dict] = []

    for image in coco_data.get("images", []):
        result = resolve_one(
            image["file_name"],
            image_roots=image_roots,
            by_name=by_name,
        )
        if result.status != "resolved":
            raise RuntimeError(
                f"Image could not be resolved uniquely: {image['file_name']} ({result.status})"
            )
        resolved_images.append(
            {
                "image_id": int(image["id"]),
                "file_name": image["file_name"],
                "resolved_path": result.matches[0],
            }
        )
    return resolved_images


def to_coco_bbox(box: list[float]) -> list[float]:
    x1, y1, x2, y2 = box
    return [
        round(float(x1), 2),
        round(float(y1), 2),
        round(float(x2 - x1), 2),
        round(float(y2 - y1), 2),
    ]


def color_for_label(label: str) -> str:
    return ANNOTATION_COLORS.get(label, "#faad14")


def normalize_label(label: str) -> str:
    return str(label).strip().lower()


def safe_output_name(file_name: str, image_id: int) -> str:
    basename = Path(file_name).name.replace("%20", "_").replace("/", "_")
    return f"{image_id:04d}-{basename}"


def draw_detections(
    image_path: Path,
    detections: list[dict],
    destination: Path,
) -> None:
    image = Image.open(image_path).convert("RGB")
    draw = ImageDraw.Draw(image)
    font = ImageFont.load_default()

    for detection in detections:
        label = detection["label"]
        score = detection["score"]
        x, y, width, height = detection["bbox"]
        x2 = x + width
        y2 = y + height
        color = color_for_label(label)

        draw.rectangle([x, y, x2, y2], outline=color, width=3)

        text = f"{label} {score:.2f}"
        try:
            text_x1, text_y1, text_x2, text_y2 = draw.textbbox((x, y), text, font=font)
            text_width = text_x2 - text_x1
            text_height = text_y2 - text_y1
        except AttributeError:
            text_width, text_height = draw.textsize(text, font=font)

        label_top = max(0, y - text_height - 6)
        label_bottom = label_top + text_height + 4
        label_right = x + text_width + 8

        draw.rectangle([x, label_top, label_right, label_bottom], fill=color)
        draw.text((x + 4, label_top + 2), text, fill="white", font=font)

    destination.parent.mkdir(parents=True, exist_ok=True)
    image.save(destination)


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


def run_inference(
    resolved_images: list[dict],
    category_map: dict[str, int],
    model_id: str,
    prompt: str,
    box_threshold: float,
    text_threshold: float,
    device: str,
    annotated_dir: Path,
) -> tuple[list[dict], Counter]:
    processor = AutoProcessor.from_pretrained(model_id)
    model = AutoModelForZeroShotObjectDetection.from_pretrained(model_id).to(device)
    counts: Counter = Counter()
    predictions: list[dict] = []

    for image_entry in resolved_images:
        image_path = Path(image_entry["resolved_path"])
        image = Image.open(image_path).convert("RGB")
        inputs = processor(images=image, text=prompt, return_tensors="pt").to(device)

        with torch.no_grad():
            outputs = model(**inputs)

        processed = post_process_outputs(
            processor=processor,
            outputs=outputs,
            input_ids=inputs.input_ids,
            target_sizes=[image.size[::-1]],
            box_threshold=box_threshold,
            text_threshold=text_threshold,
        )[0]

        detections = []
        boxes = processed["boxes"].tolist() if hasattr(processed["boxes"], "tolist") else processed["boxes"]
        scores = processed["scores"].tolist() if hasattr(processed["scores"], "tolist") else processed["scores"]
        labels = processed["labels"]

        for label, score, box in zip(labels, scores, boxes):
            normalized_label = normalize_label(str(label))
            if normalized_label not in category_map:
                continue
            counts[normalized_label] += 1
            detections.append(
                {
                    "label": normalized_label,
                    "category_id": category_map[normalized_label],
                    "bbox": to_coco_bbox(box),
                    "score": round(float(score), 4),
                }
            )

        annotated_path = annotated_dir / safe_output_name(
            image_entry["file_name"],
            image_entry["image_id"],
        )
        draw_detections(image_path, detections, annotated_path)

        predictions.append(
            {
                "image_id": image_entry["image_id"],
                "file_name": image_entry["file_name"],
                "resolved_path": image_entry["resolved_path"],
                "annotated_image": str(annotated_path),
                "detections": detections,
            }
        )

    return predictions, counts


def main() -> int:
    args = parse_args()
    project_root = Path(__file__).resolve().parents[1]
    coco_path = (project_root / args.coco).resolve()
    output_path = (project_root / args.output).resolve()
    annotated_dir = (project_root / args.annotated_dir).resolve()
    image_roots = [(project_root / root).resolve() for root in args.image_roots]

    coco_data = load_coco(coco_path)
    category_map = build_category_map(coco_data)
    resolved_images = resolve_images(coco_data, image_roots)

    predictions, counts = run_inference(
        resolved_images=resolved_images,
        category_map=category_map,
        model_id=args.model_id,
        prompt=args.prompt,
        box_threshold=args.box_threshold,
        text_threshold=args.text_threshold,
        device=choose_device(args.device),
        annotated_dir=annotated_dir,
    )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    annotated_dir.mkdir(parents=True, exist_ok=True)
    output_payload = {
        "coco_file": str(coco_path),
        "image_roots": [str(root) for root in image_roots],
        "model_id": args.model_id,
        "prompt": args.prompt,
        "box_threshold": args.box_threshold,
        "text_threshold": args.text_threshold,
        "annotated_dir": str(annotated_dir),
        "predictions": predictions,
    }
    output_path.write_text(json.dumps(output_payload, indent=2), encoding="utf-8")

    print(f"Saved predictions to: {output_path}")
    print(f"Images processed: {len(predictions)}")
    print("Predictions per class:")
    for label, category_id in sorted(category_map.items(), key=lambda item: item[1]):
        print(f"  - {label} ({category_id}): {counts.get(label, 0)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
