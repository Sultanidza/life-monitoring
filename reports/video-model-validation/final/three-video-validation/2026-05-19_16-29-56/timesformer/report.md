# VideoMAE Validation Report

- Annotation: `/tmp/life-monitoring-annotation-splits/2026-05-19_16-29-56.json`
- Prediction timeline: `/home/arturka/Documents/Projects/life-monitoring/reports/video-model-validation/final/20260623-192301-comparison/2026-05-19_16-29-56_timesformer_timeline.json`
- Video duration: 258.08 seconds
- Label Studio timeline: frames 1–6194
- Ground-truth window rule: `playing` when at least 50% of the window overlaps playing
- Primary model rule: top-1 class equals `playing guitar`

## Ground-truth intervals

| Start | End | Label |
|---:|---:|---|
| 00:00.00 | 00:27.05 | not_playing |
| 00:27.05 | 03:30.08 | playing |
| 03:30.08 | 03:39.37 | ambiguous |
| 03:39.37 | 04:04.37 | playing |
| 04:04.37 | 04:18.08 | not_playing |

## Results

| Decision rule | Precision | Recall | F1 | Accuracy | TP | FP | FN | TN |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Top-1 playing guitar | 0.937 | 0.573 | 0.711 | 0.607 | 59 | 4 | 44 | 15 |
| P(guitar) ≥ 0.5 | 0.937 | 0.573 | 0.711 | 0.607 | 59 | 4 | 44 | 15 |

## Playing-time estimate

- Human-labeled playing time: **208.03 seconds**
- VideoMAE top-1 predicted playing time: **131.73 seconds**
- Error: **-76.30 seconds**

The predicted duration is the union of overlapping model windows, so overlapping windows are not double-counted.

## Incorrect top-1 windows

| Start | End | Error | Model top-1 | P(guitar) |
|---:|---:|---|---|---:|
| 00:00.00 | 00:02.53 | FP | playing guitar | 0.7316 |
| 00:02.00 | 00:04.53 | FP | playing guitar | 0.4823 |
| 00:26.00 | 00:28.53 | FN | stretching arm | 0.0018 |
| 00:28.00 | 00:30.53 | FN | stretching arm | 0.0008 |
| 00:30.00 | 00:32.53 | FN | stretching arm | 0.0025 |
| 00:32.00 | 00:34.53 | FN | stretching arm | 0.0010 |
| 00:34.00 | 00:36.53 | FN | stretching arm | 0.0006 |
| 00:36.00 | 00:38.53 | FN | stretching arm | 0.0008 |
| 00:38.00 | 00:40.53 | FN | stretching arm | 0.0012 |
| 00:40.00 | 00:42.53 | FN | stretching arm | 0.0009 |
| 00:42.00 | 00:44.53 | FN | stretching arm | 0.0006 |
| 00:44.00 | 00:46.53 | FN | stretching arm | 0.0007 |
| 00:46.00 | 00:48.53 | FN | stretching arm | 0.0008 |
| 00:48.00 | 00:50.53 | FN | stretching arm | 0.0022 |
| 00:50.00 | 00:52.53 | FN | stretching arm | 0.0006 |
| 00:52.00 | 00:54.53 | FN | stretching arm | 0.0008 |
| 00:54.00 | 00:56.53 | FN | stretching arm | 0.0006 |
| 00:56.00 | 00:58.53 | FN | stretching arm | 0.0003 |
| 00:58.00 | 01:00.53 | FN | stretching arm | 0.0004 |
| 01:00.00 | 01:02.53 | FN | stretching arm | 0.0010 |
| 01:02.00 | 01:04.53 | FN | stretching arm | 0.0004 |
| 01:04.00 | 01:06.53 | FN | stretching arm | 0.0006 |
| 01:06.00 | 01:08.53 | FN | stretching arm | 0.0005 |
| 01:08.00 | 01:10.53 | FN | stretching arm | 0.0005 |
| 01:10.00 | 01:12.53 | FN | stretching arm | 0.0002 |
| 01:12.00 | 01:14.53 | FN | stretching arm | 0.0003 |
| 01:14.00 | 01:16.53 | FN | stretching arm | 0.0227 |
| 01:16.00 | 01:18.53 | FN | moving furniture | 0.0004 |
| 01:18.00 | 01:20.53 | FN | plastering | 0.0001 |
| 01:20.00 | 01:22.53 | FN | robot dancing | 0.0001 |
| 01:22.00 | 01:24.53 | FN | contact juggling | 0.0176 |
| 01:38.00 | 01:40.53 | FN | playing bass guitar | 0.1653 |
| 01:40.00 | 01:42.53 | FN | playing bass guitar | 0.1285 |
| 01:50.00 | 01:52.53 | FN | plastering | 0.0009 |
| 01:52.00 | 01:54.53 | FN | busking | 0.1163 |
| 03:22.00 | 03:24.53 | FN | cleaning windows | 0.0003 |
| 03:24.00 | 03:26.53 | FN | cleaning windows | 0.0001 |
| 03:42.00 | 03:44.53 | FN | cleaning windows | 0.0164 |
| 03:44.00 | 03:46.53 | FN | cleaning windows | 0.0009 |
| 03:46.00 | 03:48.53 | FN | plastering | 0.0000 |
| 03:48.00 | 03:50.53 | FN | plastering | 0.0000 |
| 03:50.00 | 03:52.53 | FN | using remote controller (not gaming) | 0.0000 |
| 03:52.00 | 03:54.53 | FN | contact juggling | 0.0004 |
| 03:54.00 | 03:56.53 | FN | contact juggling | 0.0873 |
| 03:56.00 | 03:58.53 | FN | busking | 0.1618 |
| 03:58.00 | 04:00.53 | FN | busking | 0.2143 |
| 04:04.00 | 04:06.53 | FP | playing guitar | 0.6329 |
| 04:06.00 | 04:08.53 | FP | playing guitar | 0.4093 |

## Interpretation

- Precision measures how often a `playing` prediction is correct.
- Recall measures how much labeled playing the model detects.
- This is a first-video estimate. More labeled videos are required before treating it as general performance.
