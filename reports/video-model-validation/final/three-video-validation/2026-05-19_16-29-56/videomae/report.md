# VideoMAE Validation Report

- Annotation: `/tmp/life-monitoring-annotation-splits/2026-05-19_16-29-56.json`
- Prediction timeline: `/home/arturka/Documents/Projects/life-monitoring/reports/video-model-validation/final/20260623-192301-comparison/2026-05-19_16-29-56_videomae_timeline.json`
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
| Top-1 playing guitar | 0.933 | 0.816 | 0.870 | 0.795 | 84 | 6 | 19 | 13 |
| P(guitar) ≥ 0.5 | 0.933 | 0.816 | 0.870 | 0.795 | 84 | 6 | 19 | 13 |

## Playing-time estimate

- Human-labeled playing time: **208.03 seconds**
- VideoMAE top-1 predicted playing time: **190.40 seconds**
- Error: **-17.63 seconds**

The predicted duration is the union of overlapping model windows, so overlapping windows are not double-counted.

## Incorrect top-1 windows

| Start | End | Error | Model top-1 | P(guitar) |
|---:|---:|---|---|---:|
| 00:00.00 | 00:02.53 | FP | playing guitar | 0.4241 |
| 00:02.00 | 00:04.53 | FP | playing guitar | 0.5248 |
| 00:22.00 | 00:24.53 | FP | playing guitar | 0.3565 |
| 00:28.00 | 00:30.53 | FN | archery | 0.0228 |
| 00:30.00 | 00:32.53 | FN | archery | 0.0286 |
| 00:32.00 | 00:34.53 | FN | spray painting | 0.0160 |
| 00:36.00 | 00:38.53 | FN | headbanging | 0.1132 |
| 00:44.00 | 00:46.53 | FN | headbanging | 0.0558 |
| 00:52.00 | 00:54.53 | FN | headbanging | 0.0301 |
| 01:00.00 | 01:02.53 | FN | stretching arm | 0.0438 |
| 01:02.00 | 01:04.53 | FN | shaking head | 0.0738 |
| 01:04.00 | 01:06.53 | FN | headbanging | 0.0899 |
| 01:06.00 | 01:08.53 | FN | headbanging | 0.0344 |
| 01:08.00 | 01:10.53 | FN | headbanging | 0.0648 |
| 01:10.00 | 01:12.53 | FN | playing cello | 0.0401 |
| 01:12.00 | 01:14.53 | FN | headbanging | 0.0103 |
| 01:14.00 | 01:16.53 | FN | playing cello | 0.0778 |
| 01:20.00 | 01:22.53 | FN | plastering | 0.2267 |
| 03:24.00 | 03:26.53 | FN | plastering | 0.0951 |
| 03:48.00 | 03:50.53 | FN | plastering | 0.0374 |
| 03:50.00 | 03:52.53 | FN | juggling balls | 0.0161 |
| 03:52.00 | 03:54.53 | FN | contact juggling | 0.0228 |
| 04:04.00 | 04:06.53 | FP | playing guitar | 0.3679 |
| 04:06.00 | 04:08.53 | FP | playing guitar | 0.3150 |
| 04:08.00 | 04:10.53 | FP | playing guitar | 0.2437 |

## Interpretation

- Precision measures how often a `playing` prediction is correct.
- Recall measures how much labeled playing the model detects.
- This is a first-video estimate. More labeled videos are required before treating it as general performance.
