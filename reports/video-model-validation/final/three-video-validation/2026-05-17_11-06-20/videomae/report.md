# VideoMAE Validation Report

- Annotation: `/tmp/life-monitoring-annotation-splits/2026-05-17_11-06-20.json`
- Prediction timeline: `/home/arturka/Documents/Projects/life-monitoring/reports/video-model-validation/final/20260623-192301-comparison/2026-05-17_11-06-20_videomae_timeline.json`
- Video duration: 253.07 seconds
- Label Studio timeline: frames 1–6083
- Ground-truth window rule: `playing` when at least 50% of the window overlaps playing
- Primary model rule: top-1 class equals `playing guitar`

## Ground-truth intervals

| Start | End | Label |
|---:|---:|---|
| 00:00.00 | 00:46.73 | not_playing |
| 00:46.73 | 01:54.51 | playing |
| 01:54.51 | 02:11.03 | ambiguous |
| 02:11.03 | 02:25.26 | playing |
| 02:25.26 | 02:40.15 | ambiguous |
| 02:40.15 | 03:41.57 | playing |
| 03:41.57 | 04:13.07 | not_playing |

## Results

| Decision rule | Precision | Recall | F1 | Accuracy | TP | FP | FN | TN |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Top-1 playing guitar | 0.964 | 0.768 | 0.855 | 0.832 | 53 | 2 | 16 | 36 |
| P(guitar) ≥ 0.5 | 0.964 | 0.768 | 0.855 | 0.832 | 53 | 2 | 16 | 36 |

## Playing-time estimate

- Human-labeled playing time: **143.43 seconds**
- VideoMAE top-1 predicted playing time: **120.40 seconds**
- Error: **-23.03 seconds**

The predicted duration is the union of overlapping model windows, so overlapping windows are not double-counted.

## Incorrect top-1 windows

| Start | End | Error | Model top-1 | P(guitar) |
|---:|---:|---|---|---:|
| 00:44.00 | 00:46.53 | FP | playing guitar | 0.2606 |
| 00:52.00 | 00:54.53 | FN | stretching arm | 0.0356 |
| 00:56.00 | 00:58.53 | FN | playing ukulele | 0.0936 |
| 01:08.00 | 01:10.53 | FN | playing bagpipes | 0.0737 |
| 01:14.00 | 01:16.53 | FN | playing ukulele | 0.1404 |
| 01:34.00 | 01:36.53 | FN | moving furniture | 0.0607 |
| 01:36.00 | 01:38.53 | FN | playing ukulele | 0.0487 |
| 01:50.00 | 01:52.53 | FN | playing ukulele | 0.1515 |
| 02:14.00 | 02:16.53 | FN | stretching arm | 0.0050 |
| 02:16.00 | 02:18.53 | FN | stretching arm | 0.0033 |
| 02:18.00 | 02:20.53 | FN | pull ups | 0.0023 |
| 02:20.00 | 02:22.53 | FN | pull ups | 0.0020 |
| 02:22.00 | 02:24.53 | FN | pull ups | 0.0013 |
| 02:52.00 | 02:54.53 | FN | opening bottle | 0.0061 |
| 02:54.00 | 02:56.53 | FN | playing bagpipes | 0.0133 |
| 03:10.00 | 03:12.53 | FN | playing ukulele | 0.1494 |
| 03:18.00 | 03:20.53 | FN | stretching arm | 0.0082 |
| 03:42.00 | 03:44.53 | FP | playing guitar | 0.3011 |

## Interpretation

- Precision measures how often a `playing` prediction is correct.
- Recall measures how much labeled playing the model detects.
- This is a first-video estimate. More labeled videos are required before treating it as general performance.
