# VideoMAE Validation Report

- Annotation: `/tmp/life-monitoring-annotation-splits/2026-05-17_16-31-19.json`
- Prediction timeline: `/home/arturka/Documents/Projects/life-monitoring/reports/video-model-validation/final/20260623-192301-comparison/2026-05-17_16-31-19_timesformer_timeline.json`
- Video duration: 259.05 seconds
- Label Studio timeline: frames 1–6217
- Ground-truth window rule: `playing` when at least 50% of the window overlaps playing
- Primary model rule: top-1 class equals `playing guitar`

## Ground-truth intervals

| Start | End | Label |
|---:|---:|---|
| 00:00.00 | 00:20.21 | not_playing |
| 00:20.21 | 00:26.55 | playing |
| 00:26.55 | 00:29.63 | not_playing |
| 00:29.63 | 00:32.51 | not_playing |
| 00:32.51 | 01:34.39 | playing |
| 01:34.39 | 01:41.60 | ambiguous |
| 01:41.60 | 02:26.28 | playing |
| 02:26.28 | 04:19.05 | not_playing |

## Results

| Decision rule | Precision | Recall | F1 | Accuracy | TP | FP | FN | TN |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Top-1 playing guitar | 0.936 | 0.800 | 0.863 | 0.887 | 44 | 3 | 11 | 66 |
| P(guitar) ≥ 0.5 | 0.936 | 0.800 | 0.863 | 0.887 | 44 | 3 | 11 | 66 |

## Playing-time estimate

- Human-labeled playing time: **112.90 seconds**
- VideoMAE top-1 predicted playing time: **98.13 seconds**
- Error: **-14.76 seconds**

The predicted duration is the union of overlapping model windows, so overlapping windows are not double-counted.

## Incorrect top-1 windows

| Start | End | Error | Model top-1 | P(guitar) |
|---:|---:|---|---|---:|
| 00:20.00 | 00:22.53 | FN | contact juggling | 0.0000 |
| 00:22.00 | 00:24.53 | FN | playing ukulele | 0.0413 |
| 00:26.00 | 00:28.53 | FP | playing guitar | 0.8514 |
| 00:28.00 | 00:30.53 | FP | playing guitar | 0.8214 |
| 00:30.00 | 00:32.53 | FP | playing guitar | 0.8590 |
| 01:42.00 | 01:44.53 | FN | playing bass guitar | 0.3276 |
| 01:44.00 | 01:46.53 | FN | playing ukulele | 0.0254 |
| 01:46.00 | 01:48.53 | FN | playing ukulele | 0.1939 |
| 01:48.00 | 01:50.53 | FN | playing ukulele | 0.2296 |
| 01:50.00 | 01:52.53 | FN | playing ukulele | 0.0193 |
| 01:52.00 | 01:54.53 | FN | playing ukulele | 0.2915 |
| 02:14.00 | 02:16.53 | FN | archery | 0.1515 |
| 02:16.00 | 02:18.53 | FN | playing ukulele | 0.1288 |
| 02:20.00 | 02:22.53 | FN | playing ukulele | 0.3710 |

## Interpretation

- Precision measures how often a `playing` prediction is correct.
- Recall measures how much labeled playing the model detects.
- This is a first-video estimate. More labeled videos are required before treating it as general performance.
