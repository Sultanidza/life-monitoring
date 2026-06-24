# VideoMAE Validation Report

- Annotation: `/tmp/life-monitoring-annotation-splits/2026-05-17_11-06-20.json`
- Prediction timeline: `/home/arturka/Documents/Projects/life-monitoring/reports/video-model-validation/final/20260623-192301-comparison/2026-05-17_11-06-20_vivit_timeline.json`
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
| Top-1 playing guitar | 1.000 | 0.087 | 0.160 | 0.411 | 6 | 0 | 63 | 38 |
| P(guitar) ≥ 0.5 | 1.000 | 0.087 | 0.160 | 0.411 | 6 | 0 | 63 | 38 |

## Playing-time estimate

- Human-labeled playing time: **143.43 seconds**
- VideoMAE top-1 predicted playing time: **17.20 seconds**
- Error: **-126.23 seconds**

The predicted duration is the union of overlapping model windows, so overlapping windows are not double-counted.

## Incorrect top-1 windows

| Start | End | Error | Model top-1 | P(guitar) |
|---:|---:|---|---|---:|
| 00:48.00 | 00:50.53 | FN | LABEL_335 | 0.2411 |
| 00:50.00 | 00:52.53 | FN | LABEL_41 | 0.1871 |
| 00:52.00 | 00:54.53 | FN | LABEL_347 | 0.0000 |
| 00:54.00 | 00:56.53 | FN | LABEL_65 | 0.0000 |
| 00:56.00 | 00:58.53 | FN | LABEL_169 | 0.0003 |
| 00:58.00 | 01:00.53 | FN | LABEL_41 | 0.0045 |
| 01:04.00 | 01:06.53 | FN | LABEL_335 | 0.0149 |
| 01:06.00 | 01:08.53 | FN | LABEL_347 | 0.0000 |
| 01:08.00 | 01:10.53 | FN | LABEL_347 | 0.0000 |
| 01:10.00 | 01:12.53 | FN | LABEL_219 | 0.0000 |
| 01:12.00 | 01:14.53 | FN | LABEL_347 | 0.1068 |
| 01:14.00 | 01:16.53 | FN | LABEL_249 | 0.0005 |
| 01:16.00 | 01:18.53 | FN | LABEL_41 | 0.1035 |
| 01:20.00 | 01:22.53 | FN | LABEL_200 | 0.0043 |
| 01:22.00 | 01:24.53 | FN | LABEL_169 | 0.0000 |
| 01:24.00 | 01:26.53 | FN | LABEL_258 | 0.0000 |
| 01:26.00 | 01:28.53 | FN | LABEL_328 | 0.0000 |
| 01:28.00 | 01:30.53 | FN | LABEL_65 | 0.0004 |
| 01:30.00 | 01:32.53 | FN | LABEL_5 | 0.0003 |
| 01:32.00 | 01:34.53 | FN | LABEL_200 | 0.0004 |
| 01:34.00 | 01:36.53 | FN | LABEL_200 | 0.0015 |
| 01:36.00 | 01:38.53 | FN | LABEL_220 | 0.0000 |
| 01:38.00 | 01:40.53 | FN | LABEL_41 | 0.0034 |
| 01:40.00 | 01:42.53 | FN | LABEL_41 | 0.1055 |
| 01:42.00 | 01:44.53 | FN | LABEL_41 | 0.1300 |
| 01:46.00 | 01:48.53 | FN | LABEL_335 | 0.0959 |
| 01:48.00 | 01:50.53 | FN | LABEL_41 | 0.0361 |
| 01:50.00 | 01:52.53 | FN | LABEL_328 | 0.0000 |
| 02:12.00 | 02:14.53 | FN | LABEL_216 | 0.0003 |
| 02:14.00 | 02:16.53 | FN | LABEL_200 | 0.0001 |
| 02:16.00 | 02:18.53 | FN | LABEL_338 | 0.0000 |
| 02:18.00 | 02:20.53 | FN | LABEL_65 | 0.0000 |
| 02:20.00 | 02:22.53 | FN | LABEL_255 | 0.0000 |
| 02:22.00 | 02:24.53 | FN | LABEL_198 | 0.0000 |
| 02:42.00 | 02:44.53 | FN | LABEL_338 | 0.0000 |
| 02:44.00 | 02:46.53 | FN | LABEL_41 | 0.0343 |
| 02:46.00 | 02:48.53 | FN | LABEL_41 | 0.2773 |
| 02:50.00 | 02:52.53 | FN | LABEL_203 | 0.0206 |
| 02:52.00 | 02:54.53 | FN | LABEL_219 | 0.0000 |
| 02:54.00 | 02:56.53 | FN | LABEL_338 | 0.0001 |
| 02:56.00 | 02:58.53 | FN | LABEL_41 | 0.0209 |
| 02:58.00 | 03:00.53 | FN | LABEL_335 | 0.1009 |
| 03:00.00 | 03:02.53 | FN | LABEL_221 | 0.1347 |
| 03:02.00 | 03:04.53 | FN | LABEL_335 | 0.1620 |
| 03:04.00 | 03:06.53 | FN | LABEL_328 | 0.0241 |
| 03:06.00 | 03:08.53 | FN | LABEL_258 | 0.0000 |
| 03:08.00 | 03:10.53 | FN | LABEL_65 | 0.0063 |
| 03:10.00 | 03:12.53 | FN | LABEL_203 | 0.0012 |
| 03:12.00 | 03:14.53 | FN | LABEL_169 | 0.0001 |
| 03:14.00 | 03:16.53 | FN | LABEL_41 | 0.2418 |
| 03:16.00 | 03:18.53 | FN | LABEL_41 | 0.0161 |
| 03:18.00 | 03:20.53 | FN | LABEL_328 | 0.0000 |
| 03:20.00 | 03:22.53 | FN | LABEL_328 | 0.0002 |
| 03:22.00 | 03:24.53 | FN | LABEL_249 | 0.0003 |
| 03:24.00 | 03:26.53 | FN | LABEL_249 | 0.0005 |
| 03:26.00 | 03:28.53 | FN | LABEL_333 | 0.0002 |
| 03:28.00 | 03:30.53 | FN | LABEL_345 | 0.0001 |
| 03:30.00 | 03:32.53 | FN | LABEL_217 | 0.0001 |
| 03:32.00 | 03:34.53 | FN | LABEL_382 | 0.0001 |
| 03:34.00 | 03:36.53 | FN | LABEL_41 | 0.0644 |
| 03:36.00 | 03:38.53 | FN | LABEL_249 | 0.0056 |
| 03:38.00 | 03:40.53 | FN | LABEL_41 | 0.1624 |
| 03:40.00 | 03:42.53 | FN | LABEL_41 | 0.0180 |

## Interpretation

- Precision measures how often a `playing` prediction is correct.
- Recall measures how much labeled playing the model detects.
- This is a first-video estimate. More labeled videos are required before treating it as general performance.
