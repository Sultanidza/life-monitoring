# VideoMAE Validation Report

- Annotation: `/tmp/life-monitoring-annotation-splits/2026-05-19_16-29-56.json`
- Prediction timeline: `/home/arturka/Documents/Projects/life-monitoring/reports/video-model-validation/final/20260623-192301-comparison/2026-05-19_16-29-56_vivit_timeline.json`
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
| Top-1 playing guitar | 0.982 | 0.544 | 0.700 | 0.607 | 56 | 1 | 47 | 18 |
| P(guitar) ≥ 0.5 | 0.982 | 0.544 | 0.700 | 0.607 | 56 | 1 | 47 | 18 |

## Playing-time estimate

- Human-labeled playing time: **208.03 seconds**
- VideoMAE top-1 predicted playing time: **122.27 seconds**
- Error: **-85.77 seconds**

The predicted duration is the union of overlapping model windows, so overlapping windows are not double-counted.

## Incorrect top-1 windows

| Start | End | Error | Model top-1 | P(guitar) |
|---:|---:|---|---|---:|
| 00:26.00 | 00:28.53 | FN | LABEL_333 | 0.0000 |
| 00:28.00 | 00:30.53 | FN | LABEL_333 | 0.0000 |
| 00:30.00 | 00:32.53 | FN | LABEL_333 | 0.0004 |
| 00:32.00 | 00:34.53 | FN | LABEL_327 | 0.0027 |
| 00:34.00 | 00:36.53 | FN | LABEL_327 | 0.0008 |
| 00:36.00 | 00:38.53 | FN | LABEL_327 | 0.0002 |
| 00:38.00 | 00:40.53 | FN | LABEL_327 | 0.0001 |
| 00:40.00 | 00:42.53 | FN | LABEL_327 | 0.0006 |
| 00:42.00 | 00:44.53 | FN | LABEL_327 | 0.0015 |
| 00:44.00 | 00:46.53 | FN | LABEL_327 | 0.0005 |
| 00:46.00 | 00:48.53 | FN | LABEL_327 | 0.0004 |
| 00:48.00 | 00:50.53 | FN | LABEL_327 | 0.0005 |
| 00:50.00 | 00:52.53 | FN | LABEL_333 | 0.0028 |
| 00:52.00 | 00:54.53 | FN | LABEL_335 | 0.0050 |
| 00:54.00 | 00:56.53 | FN | LABEL_333 | 0.0015 |
| 00:56.00 | 00:58.53 | FN | LABEL_327 | 0.0002 |
| 00:58.00 | 01:00.53 | FN | LABEL_333 | 0.0014 |
| 01:00.00 | 01:02.53 | FN | LABEL_333 | 0.0006 |
| 01:02.00 | 01:04.53 | FN | LABEL_333 | 0.0018 |
| 01:04.00 | 01:06.53 | FN | LABEL_333 | 0.0006 |
| 01:06.00 | 01:08.53 | FN | LABEL_333 | 0.0009 |
| 01:08.00 | 01:10.53 | FN | LABEL_333 | 0.0003 |
| 01:10.00 | 01:12.53 | FN | LABEL_333 | 0.0003 |
| 01:12.00 | 01:14.53 | FN | LABEL_333 | 0.0012 |
| 01:14.00 | 01:16.53 | FN | LABEL_327 | 0.0006 |
| 01:16.00 | 01:18.53 | FN | LABEL_327 | 0.0001 |
| 01:18.00 | 01:20.53 | FN | LABEL_216 | 0.0000 |
| 01:20.00 | 01:22.53 | FN | LABEL_216 | 0.0000 |
| 01:22.00 | 01:24.53 | FN | LABEL_169 | 0.0043 |
| 01:38.00 | 01:40.53 | FN | LABEL_65 | 0.0109 |
| 01:40.00 | 01:42.53 | FN | LABEL_129 | 0.0141 |
| 01:50.00 | 01:52.53 | FN | LABEL_216 | 0.0063 |
| 02:54.00 | 02:56.53 | FN | LABEL_335 | 0.2521 |
| 02:56.00 | 02:58.53 | FN | LABEL_221 | 0.2251 |
| 03:20.00 | 03:22.53 | FN | LABEL_335 | 0.0586 |
| 03:22.00 | 03:24.53 | FN | LABEL_216 | 0.0000 |
| 03:24.00 | 03:26.53 | FN | LABEL_216 | 0.0000 |
| 03:42.00 | 03:44.53 | FN | LABEL_216 | 0.0009 |
| 03:44.00 | 03:46.53 | FN | LABEL_169 | 0.0001 |
| 03:46.00 | 03:48.53 | FN | LABEL_169 | 0.0000 |
| 03:48.00 | 03:50.53 | FN | LABEL_65 | 0.0000 |
| 03:50.00 | 03:52.53 | FN | LABEL_216 | 0.0000 |
| 03:52.00 | 03:54.53 | FN | LABEL_328 | 0.0000 |
| 03:54.00 | 03:56.53 | FN | LABEL_249 | 0.0173 |
| 03:56.00 | 03:58.53 | FN | LABEL_335 | 0.0219 |
| 03:58.00 | 04:00.53 | FN | LABEL_249 | 0.0517 |
| 04:02.00 | 04:04.53 | FN | LABEL_335 | 0.4043 |
| 04:04.00 | 04:06.53 | FP | playing guitar | 0.6550 |

## Interpretation

- Precision measures how often a `playing` prediction is correct.
- Recall measures how much labeled playing the model detects.
- This is a first-video estimate. More labeled videos are required before treating it as general performance.
