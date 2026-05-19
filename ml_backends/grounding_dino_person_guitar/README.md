# Grounding DINO Label Studio Backend

Minimal Label Studio ML backend for image preannotation with Grounding DINO.

Current scope:

- input: image tasks
- output: `RectangleLabels`
- labels: `guitar`, `person`
- prompt: `guitar. person.`
- no training loop
- local file root: `/home/arturka/Documents/Projects/life-monitoring/data`

## Files

- `model.py`: backend model class
- `_wsgi.py`: backend entrypoint
- `config.json`: model settings
- `requirements.txt`: backend dependencies

## Intended Label Studio Config

This backend expects a project config with:

- `from_name = label`
- `to_name = image`
- `type = rectanglelabels`

The backend reads the actual `from_name` / `to_name` from Label Studio at runtime, but it only supports `RectangleLabels`.

## Install

Use the project `.venv` or another dedicated environment:

```bash
source /home/arturka/Documents/Projects/life-monitoring/.venv/bin/activate
pip install -r /home/arturka/Documents/Projects/life-monitoring/ml_backends/grounding_dino_person_guitar/requirements.txt
```

## Run

```bash
source /home/arturka/Documents/Projects/life-monitoring/.venv/bin/activate
python /home/arturka/Documents/Projects/life-monitoring/ml_backends/grounding_dino_person_guitar/_wsgi.py --port 9090
```

Then connect it in Label Studio as an ML backend at:

```text
http://localhost:9090
```

## Notes

- If Label Studio serves local files, make sure the backend can access those image paths.
- The backend lazy-loads Grounding DINO on the first prediction request and then reuses it.
- Local file tasks from Label Studio like `/data/local-files/?d=...` are resolved against `local_files_document_root`.
- Predictions are filtered to `guitar` and `person` only.
