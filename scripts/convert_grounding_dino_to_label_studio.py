#!/usr/bin/env python3

import argparse
import json
from pathlib import Path
from urllib.parse import quote

from PIL import Image


PROJECT_ROOT = Path("/home/arturka/Documents/Projects/life-monitoring")
DEFAULT_INPUT = PROJECT_ROOT / "data/predictions/grounding_dino_predictions.json"
DEFAULT_OUTPUT = PROJECT_ROOT / "data/predictions/label_studio_predictions.json"
ALLOWED_LABELS = {"guitar", "person"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Convert Grounding DINO predictions into Label Studio pre-annotation JSON."
    )
    parser.add_argument(
        "--input",
        default=str(DEFAULT_INPUT),
        help="Path to grounding_dino_predictions.json",
    )
    parser.add_argument(
        "--output",
        default=str(DEFAULT_OUTPUT),
        help="Path to write label_studio_predictions.json",
    )
    parser.add_argument(
        "--model-version",
        default="grounding-dino",
        help="Value to store in Label Studio predictions[].model_version",
    )
    parser.add_argument(
        "--use-local-files-urls",
        action="store_true",
        help=(
            "Emit Label Studio local-files URLs like "
            "/data/local-files/?d=... instead of absolute file paths."
        ),
    )
    parser.add_argument(
        "--local-files-root",
        default=str(PROJECT_ROOT / "data"),
        help="Root directory used with --use-local-files-urls.",
    )
    return parser.parse_args()


def coco_bbox_to_percent(bbox: list[float], width: int, height: int) -> dict[str, float]:
    x, y, w, h = bbox
    return {
        "x": x * 100.0 / width,
        "y": y * 100.0 / height,
        "width": w * 100.0 / width,
        "height": h * 100.0 / height,
        "rotation": 0,
    }


def build_image_ref(
    resolved_path: Path,
    use_local_files_urls: bool,
    local_files_root: Path,
) -> str:
    if not use_local_files_urls:
        return str(resolved_path)

    relative_path = resolved_path.relative_to(local_files_root)
    return "/data/local-files/?d=" + quote(str(relative_path))


def main() -> None:
    args = parse_args()
    input_path = Path(args.input).expanduser().resolve()
    output_path = Path(args.output).expanduser().resolve()
    local_files_root = Path(args.local_files_root).expanduser().resolve()

    with input_path.open() as f:
        payload = json.load(f)

    predictions = payload.get("predictions", [])
    tasks = []

    for image_prediction in predictions:
        resolved_path = Path(image_prediction["resolved_path"])
        with Image.open(resolved_path) as image:
            original_width, original_height = image.size

        results = []
        for index, detection in enumerate(image_prediction.get("detections", [])):
            label = detection["label"]
            if label not in ALLOWED_LABELS:
                continue

            results.append(
                {
                    "id": f"{image_prediction['image_id']}-{index}",
                    "from_name": "label",
                    "to_name": "image",
                    "type": "rectanglelabels",
                    "original_width": original_width,
                    "original_height": original_height,
                    "image_rotation": 0,
                    "score": detection["score"],
                    "value": {
                        **coco_bbox_to_percent(
                            detection["bbox"],
                            original_width,
                            original_height,
                        ),
                        "rectanglelabels": [label],
                    },
                }
            )

        tasks.append(
            {
                "data": {
                    "image": build_image_ref(
                        resolved_path,
                        args.use_local_files_urls,
                        local_files_root,
                    )
                },
                "predictions": [
                    {
                        "model_version": args.model_version,
                        "result": results,
                    }
                ],
            }
        )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w") as f:
        json.dump(tasks, f, indent=2)

    print(f"Saved Label Studio predictions to: {output_path}")
    print(f"Tasks written: {len(tasks)}")


if __name__ == "__main__":
    main()
