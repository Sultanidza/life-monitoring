# Video action-model comparison — playing guitar

Sampled @ 15.0 fps, 2.5s windows, 2.0s stride. Metric: top-1 == 'playing guitar' (K400 idx 232).

## Per model, per video

| Model | Video | Clip frames | Windows | Top-1 guitar rate | Mean P(guitar) |
|---|---|---|---|---|---|
| videomae | 2026-05-17 11-06-20.mkv | 16 | 126 | 44.4% | 0.184 |
| timesformer | 2026-05-17 11-06-20.mkv | 8 | 126 | 19.8% | 0.106 |
| vivit | 2026-05-17 11-06-20.mkv | 32 | 126 | 5.6% | 0.043 |
| videomae | 2026-05-17 16-31-19.mkv | 16 | 129 | 45.7% | 0.202 |
| timesformer | 2026-05-17 16-31-19.mkv | 8 | 129 | 37.2% | 0.283 |
| vivit | 2026-05-17 16-31-19.mkv | 32 | 129 | 8.5% | 0.072 |
| videomae | 2026-05-19 16-29-56.mkv | 16 | 128 | 69.5% | 0.303 |
| timesformer | 2026-05-19 16-29-56.mkv | 8 | 128 | 48.4% | 0.397 |
| vivit | 2026-05-19 16-29-56.mkv | 32 | 128 | 45.3% | 0.387 |

## Aggregated per model

| Model | Total windows | Top-1 guitar windows | Top-1 guitar rate | Mean P(guitar) |
|---|---|---|---|---|
| videomae | 383 | 204 | 53.3% | 0.230 |
| timesformer | 383 | 135 | 35.2% | 0.263 |
| vivit | 383 | 76 | 19.8% | 0.168 |
