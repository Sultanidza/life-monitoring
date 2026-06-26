# VideoMAE temporal-smoothing experiment

Stride is the time between consecutive window starts. These 2.5-second windows start every 2 seconds, so adjacent windows overlap by 0.5 seconds.

All rules were evaluated against the same three-video ground truth. Smoothing never crosses an ambiguous window.

## Updated metrics: selected smoothing rule

| Case | Precision | Recall | F1 | Accuracy | FP | FN |
|---|---:|---:|---:|---:|---:|---:|
| Raw VideoMAE | 0.941 | 0.841 | 0.888 | 0.864 | 12 | 36 |
| VideoMAE + selected smoothing | 0.941 | 0.912 | 0.926 | 0.907 | 13 | 20 |
| Change | 0.000 | +0.071 | +0.038 | +0.043 | +1 | -16 |

The selected rule fills up to two consecutive negative windows when both neighboring windows are positive.

## All tested rules

| Rule | Changed windows | Precision | Recall | F1 | Accuracy | FP | FN |
|---|---:|---:|---:|---:|---:|---:|---:|
| none | 0 | 0.941 | 0.841 | 0.888 | 0.864 | 12 | 36 |
| fill_1_negative | 13 | 0.940 | 0.894 | 0.916 | 0.895 | 13 | 24 |
| fill_up_to_2_negatives | 17 | 0.941 | 0.912 | 0.926 | 0.907 | 13 | 20 |
| remove_1_positive | 4 | 0.945 | 0.828 | 0.883 | 0.858 | 11 | 39 |
| fill_1_remove_1 | 13 | 0.940 | 0.894 | 0.916 | 0.895 | 13 | 24 |
| fill_2_remove_1 | 17 | 0.941 | 0.912 | 0.926 | 0.907 | 13 | 20 |

## Decision

Best tested rule by F1: **fill up to two consecutive negative windows when both neighboring windows are positive**.

This raises combined recall from **0.841** to **0.912**, F1 from **0.888** to **0.926**, and accuracy from **0.864** to **0.907**. Precision remains effectively unchanged: **0.941** before and **0.941** after. False negatives fall from 36 to 20; false positives rise from 12 to 13.

Per-video F1 changes: `0.855 → 0.948`, `0.956 → 0.956`, and `0.870 → 0.894`. The rule improves or preserves F1 on every labeled video.

A fill rule converts short negative gaps between positive windows to playing. A remove rule deletes short positive islands between negative windows.
