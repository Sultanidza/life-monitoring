#!/usr/bin/env python3
"""Extract frames from one video or a directory of videos at a fixed interval."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


VIDEO_EXTENSIONS = {
    ".mp4",
    ".mov",
    ".avi",
    ".mkv",
    ".webm",
    ".m4v",
    ".mpeg",
    ".mpg",
}


@dataclass
class ExtractionResult:
    video: str
    output_dir: str
    duration_seconds: float | None
    interval_seconds: float
    frame_count: int
    pattern: str


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Extract frames from a video or directory of videos every N seconds "
            "using ffmpeg."
        )
    )
    parser.add_argument(
        "--source",
        required=True,
        help="Path to a video file or a directory containing videos.",
    )
    parser.add_argument(
        "--interval",
        type=float,
        default=2.0,
        help="Frame extraction interval in seconds. Default: 2.0",
    )
    parser.add_argument(
        "--output-dir",
        default=None,
        help=(
            "Directory to save extracted frame folders into. Defaults to "
            "data/frames/."
        ),
    )
    parser.add_argument(
        "--metadata-dir",
        default=None,
        help=(
            "Directory to save run metadata into. Defaults to "
            "reports/frame-extraction/<timestamp>/."
        ),
    )
    parser.add_argument(
        "--image-format",
        choices=["jpg", "png"],
        default="jpg",
        help="Image format for extracted frames. Default: jpg",
    )
    parser.add_argument(
        "--jpg-quality",
        type=int,
        default=2,
        help="JPEG quality for ffmpeg, where lower is better. Default: 2",
    )
    parser.add_argument(
        "--recursive",
        action="store_true",
        help="Search for videos recursively when --source is a directory.",
    )
    return parser.parse_args()


def build_output_dir(raw_output_dir: str | None) -> Path:
    if raw_output_dir:
        return Path(raw_output_dir).expanduser().resolve()

    return Path(__file__).resolve().parents[1] / "data" / "frames"


def build_metadata_dir(raw_metadata_dir: str | None) -> Path:
    if raw_metadata_dir:
        return Path(raw_metadata_dir).expanduser().resolve()

    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    return Path(__file__).resolve().parents[1] / "reports" / "frame-extraction" / timestamp


def ensure_ffmpeg_tools() -> None:
    for tool in ("ffmpeg", "ffprobe"):
        try:
            subprocess.run(
                [tool, "-version"],
                check=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
        except (FileNotFoundError, subprocess.CalledProcessError) as exc:
            raise RuntimeError(f"{tool} is required but was not found in PATH.") from exc


def slugify(text: str) -> str:
    return re.sub(r"[^A-Za-z0-9]+", "-", text).strip("-").lower()


def dataset_name_for_video(video_path: Path) -> str:
    parent_slug = slugify(video_path.parent.name)
    stem_slug = slugify(video_path.stem)

    if parent_slug == "obs-studio":
        return f"obs-studio-{stem_slug}"
    if parent_slug and parent_slug not in {"videos", "video"}:
        return f"{parent_slug}-{stem_slug}"
    return stem_slug


def collect_videos(source: str, recursive: bool) -> list[Path]:
    source_path = Path(source).expanduser().resolve()
    if not source_path.exists():
        raise FileNotFoundError(f"Source does not exist: {source_path}")

    if source_path.is_file():
        if source_path.suffix.lower() not in VIDEO_EXTENSIONS:
            raise ValueError(f"Unsupported video file: {source_path.name}")
        return [source_path]

    iterator = source_path.rglob("*") if recursive else source_path.glob("*")
    videos = sorted(
        path
        for path in iterator
        if path.is_file() and path.suffix.lower() in VIDEO_EXTENSIONS
    )
    if not videos:
        raise ValueError(f"No supported video files found under: {source_path}")
    return videos


def probe_duration(video_path: Path) -> float | None:
    command = [
        "ffprobe",
        "-v",
        "error",
        "-show_entries",
        "format=duration",
        "-of",
        "default=noprint_wrappers=1:nokey=1",
        str(video_path),
    ]
    result = subprocess.run(command, capture_output=True, text=True, check=True)
    value = result.stdout.strip()
    if not value or value == "N/A":
        return None
    return round(float(value), 3)


def build_ffmpeg_command(
    video_path: Path,
    output_pattern: Path,
    interval: float,
    image_format: str,
    jpg_quality: int,
) -> list[str]:
    command = [
        "ffmpeg",
        "-hide_banner",
        "-loglevel",
        "error",
        "-n",
        "-i",
        str(video_path),
        "-vf",
        f"fps=1/{interval}",
        "-vsync",
        "vfr",
    ]
    if image_format == "jpg":
        command.extend(["-q:v", str(jpg_quality)])
    command.extend(["-start_number", "1", str(output_pattern)])
    return command


def extract_frames_for_video(
    video_path: Path,
    destination_root: Path,
    interval: float,
    image_format: str,
    jpg_quality: int,
) -> ExtractionResult:
    video_output_dir = destination_root / dataset_name_for_video(video_path)
    video_output_dir.mkdir(parents=True, exist_ok=True)

    output_pattern = video_output_dir / f"frame_%06d.{image_format}"
    command = build_ffmpeg_command(
        video_path=video_path,
        output_pattern=output_pattern,
        interval=interval,
        image_format=image_format,
        jpg_quality=jpg_quality,
    )
    subprocess.run(command, check=True)

    extracted_frames = sorted(video_output_dir.glob(f"frame_*.{image_format}"))
    return ExtractionResult(
        video=str(video_path),
        output_dir=str(video_output_dir),
        duration_seconds=probe_duration(video_path),
        interval_seconds=interval,
        frame_count=len(extracted_frames),
        pattern=str(output_pattern),
    )


def write_manifest(output_dir: Path, results: list[ExtractionResult]) -> None:
    manifest = {
        "date": datetime.now().isoformat(),
        "video_count": len(results),
        "results": [result.__dict__ for result in results],
    }
    (output_dir / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")


def write_summary(output_dir: Path, source: str, interval: float, results: list[ExtractionResult]) -> None:
    total_frames = sum(result.frame_count for result in results)
    lines = [
        "# Frame Extraction Run",
        "",
        f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "",
        f"Source: `{Path(source).expanduser().resolve()}`",
        "",
        f"Interval: `{interval}` seconds",
        "",
        f"Videos processed: `{len(results)}`",
        "",
        f"Frames extracted: `{total_frames}`",
        "",
        "| Video | Duration (s) | Frames | Output |",
        "|---|---:|---:|---|",
    ]

    for result in results:
        duration = "unknown" if result.duration_seconds is None else str(result.duration_seconds)
        lines.append(
            f"| `{Path(result.video).name}` | {duration} | {result.frame_count} | `{result.output_dir}` |"
        )

    (output_dir / "summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    args = parse_args()
    if args.interval <= 0:
        print("--interval must be greater than 0.", file=sys.stderr)
        return 1
    if not 2 <= args.jpg_quality <= 31:
        print("--jpg-quality must be between 2 and 31.", file=sys.stderr)
        return 1

    ensure_ffmpeg_tools()
    output_dir = build_output_dir(args.output_dir)
    metadata_dir = build_metadata_dir(args.metadata_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    metadata_dir.mkdir(parents=True, exist_ok=True)

    videos = collect_videos(args.source, args.recursive)
    results: list[ExtractionResult] = []

    for video_path in videos:
        results.append(
            extract_frames_for_video(
                video_path=video_path,
                destination_root=output_dir,
                interval=args.interval,
                image_format=args.image_format,
                jpg_quality=args.jpg_quality,
            )
        )

    write_manifest(metadata_dir, results)
    write_summary(metadata_dir, args.source, args.interval, results)

    print(f"Saved extracted frames to: {output_dir}")
    print(f"Saved extraction metadata to: {metadata_dir}")
    print(f"Processed {len(results)} video(s).")
    print(f"Extracted {sum(result.frame_count for result in results)} frame(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
