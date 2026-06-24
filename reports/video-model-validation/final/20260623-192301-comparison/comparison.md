# Video action-model comparison — playing guitar

Sampled @ 15.0 fps, 2.5s windows, 2.0s stride. Metric: top-1 == 'playing guitar' (K400 idx 232).

## Per model, per video

| Model | Video | Clip frames | Windows | Top-1 guitar rate | Mean P(guitar) |
|---|---|---|---|---|---|
| videomae | 2026-05-17_11-06-20.mp4 | 16 | 126 | 45.2% | 0.184 |
| timesformer | 2026-05-17_11-06-20.mp4 | 8 | 126 | 19.8% | 0.106 |
| vivit | 2026-05-17_11-06-20.mp4 | 32 | 126 | 5.6% | 0.043 |
| videomae | 2026-05-17_16-31-19.mp4 | 16 | 129 | 45.7% | 0.204 |
| timesformer | 2026-05-17_16-31-19.mp4 | 8 | 129 | 37.2% | 0.283 |
| vivit | 2026-05-17_16-31-19.mp4 | 32 | 129 | 7.8% | 0.072 |
| videomae | 2026-05-19_16-29-56.mp4 | 16 | 128 | 71.9% | 0.308 |
| timesformer | 2026-05-19_16-29-56.mp4 | 8 | 128 | 50.0% | 0.400 |
| vivit | 2026-05-19_16-29-56.mp4 | 32 | 128 | 46.1% | 0.389 |

## Aggregated per model

| Model | Total windows | Top-1 guitar windows | Top-1 guitar rate | Mean P(guitar) |
|---|---|---|---|---|
| videomae | 383 | 208 | 54.3% | 0.232 |
| timesformer | 383 | 137 | 35.8% | 0.264 |
| vivit | 383 | 76 | 19.8% | 0.168 |
