# VideoMAE Validation Report

- Annotation: `/tmp/life-monitoring-annotation-splits/2026-05-17_16-31-19.json`
- Prediction timeline: `/home/arturka/Documents/Projects/life-monitoring/reports/video-model-validation/final/20260623-192301-comparison/2026-05-17_16-31-19_vivit_timeline.json`
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
| Top-1 playing guitar | 1.000 | 0.182 | 0.308 | 0.637 | 10 | 0 | 45 | 69 |
| P(guitar) ≥ 0.5 | 1.000 | 0.182 | 0.308 | 0.637 | 10 | 0 | 45 | 69 |

## Playing-time estimate

- Human-labeled playing time: **112.90 seconds**
- VideoMAE top-1 predicted playing time: **23.73 seconds**
- Error: **-89.16 seconds**

The predicted duration is the union of overlapping model windows, so overlapping windows are not double-counted.

## Incorrect top-1 windows

| Start | End | Error | Model top-1 | P(guitar) |
|---:|---:|---|---|---:|
| 00:20.00 | 00:22.53 | FN | LABEL_169 | 0.0000 |
| 00:22.00 | 00:24.53 | FN | LABEL_249 | 0.0046 |
| 00:24.00 | 00:26.53 | FN | LABEL_335 | 0.1801 |
| 00:32.00 | 00:34.53 | FN | LABEL_335 | 0.2363 |
| 00:34.00 | 00:36.53 | FN | LABEL_335 | 0.3655 |
| 00:36.00 | 00:38.53 | FN | LABEL_335 | 0.1849 |
| 00:38.00 | 00:40.53 | FN | LABEL_249 | 0.0026 |
| 00:40.00 | 00:42.53 | FN | LABEL_350 | 0.1714 |
| 00:46.00 | 00:48.53 | FN | LABEL_335 | 0.2807 |
| 00:48.00 | 00:50.53 | FN | LABEL_335 | 0.1990 |
| 00:50.00 | 00:52.53 | FN | LABEL_335 | 0.2771 |
| 00:54.00 | 00:56.53 | FN | LABEL_335 | 0.1632 |
| 00:56.00 | 00:58.53 | FN | LABEL_335 | 0.0108 |
| 00:58.00 | 01:00.53 | FN | LABEL_335 | 0.0635 |
| 01:00.00 | 01:02.53 | FN | LABEL_335 | 0.0835 |
| 01:02.00 | 01:04.53 | FN | LABEL_335 | 0.0100 |
| 01:04.00 | 01:06.53 | FN | LABEL_335 | 0.1649 |
| 01:06.00 | 01:08.53 | FN | LABEL_335 | 0.1435 |
| 01:08.00 | 01:10.53 | FN | LABEL_335 | 0.1672 |
| 01:12.00 | 01:14.53 | FN | LABEL_221 | 0.3450 |
| 01:16.00 | 01:18.53 | FN | LABEL_335 | 0.1019 |
| 01:18.00 | 01:20.53 | FN | LABEL_335 | 0.0051 |
| 01:20.00 | 01:22.53 | FN | LABEL_292 | 0.0031 |
| 01:22.00 | 01:24.53 | FN | LABEL_131 | 0.0177 |
| 01:24.00 | 01:26.53 | FN | LABEL_131 | 0.0545 |
| 01:26.00 | 01:28.53 | FN | LABEL_131 | 0.0074 |
| 01:28.00 | 01:30.53 | FN | LABEL_131 | 0.0091 |
| 01:30.00 | 01:32.53 | FN | LABEL_335 | 0.0053 |
| 01:42.00 | 01:44.53 | FN | LABEL_65 | 0.0001 |
| 01:46.00 | 01:48.53 | FN | LABEL_161 | 0.0003 |
| 01:48.00 | 01:50.53 | FN | LABEL_249 | 0.0605 |
| 01:50.00 | 01:52.53 | FN | LABEL_335 | 0.0815 |
| 01:52.00 | 01:54.53 | FN | LABEL_249 | 0.0562 |
| 01:56.00 | 01:58.53 | FN | LABEL_335 | 0.0122 |
| 01:58.00 | 02:00.53 | FN | LABEL_335 | 0.0032 |
| 02:00.00 | 02:02.53 | FN | LABEL_335 | 0.0017 |
| 02:02.00 | 02:04.53 | FN | LABEL_131 | 0.0006 |
| 02:04.00 | 02:06.53 | FN | LABEL_1 | 0.0004 |
| 02:06.00 | 02:08.53 | FN | LABEL_335 | 0.0033 |
| 02:08.00 | 02:10.53 | FN | LABEL_335 | 0.0294 |
| 02:10.00 | 02:12.53 | FN | LABEL_335 | 0.0026 |
| 02:12.00 | 02:14.53 | FN | LABEL_96 | 0.0017 |
| 02:14.00 | 02:16.53 | FN | LABEL_44 | 0.0000 |
| 02:16.00 | 02:18.53 | FN | LABEL_129 | 0.0003 |
| 02:18.00 | 02:20.53 | FN | LABEL_221 | 0.0485 |

## Interpretation

- Precision measures how often a `playing` prediction is correct.
- Recall measures how much labeled playing the model detects.
- This is a first-video estimate. More labeled videos are required before treating it as general performance.
