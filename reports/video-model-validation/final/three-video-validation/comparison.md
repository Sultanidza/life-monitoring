# Three-video validated action-model comparison

Ground truth: three Label Studio timelines. Model input: video frames only. Evaluation uses identical 2.5-second windows with a 2-second stride. Windows touching `ambiguous` intervals are excluded.

## Combined metrics (micro-averaged)

| Model | Precision | Recall | F1 | Accuracy | TP | FP | FN | TN | Excluded |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| VideoMAE | 0.941 | 0.841 | 0.888 | 0.864 | 191 | 12 | 36 | 114 | 30 |
| TimeSformer | 0.947 | 0.555 | 0.700 | 0.694 | 126 | 7 | 101 | 119 | 30 |
| ViViT | 0.986 | 0.317 | 0.480 | 0.558 | 72 | 1 | 155 | 125 | 30 |

## Per-video F1

| Video | VideoMAE | TimeSformer | ViViT |
|---|---:|---:|---:|
| 2026-05-17_11-06-20 | 0.855 | 0.500 | 0.160 |
| 2026-05-17_16-31-19 | 0.956 | 0.863 | 0.308 |
| 2026-05-19_16-29-56 | 0.870 | 0.711 | 0.700 |

## Decision

VideoMAE remains the baseline. It has the best combined F1 and wins on every labeled video. Its main remaining weakness is false negatives rather than false positives.

Duration totals are retained in `combined-metrics.json`, but classification metrics are primary because ambiguous intervals are deliberately excluded from window scoring.
