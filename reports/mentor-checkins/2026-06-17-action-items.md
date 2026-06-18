# Action Items — for mentor (follow-up: Friday)

Derived from the 2026-06-17 meeting summary (session `87af3ca0`). Status reflects
work completed as of this check-in. Repo: https://github.com/Sultanidza/life-monitoring

## Project context (restored)

- **Goal:** detect from video when the primary user is playing guitar; image/frame
  object detection is the foundation. Narrow MVP: one camera, one user, classes
  `person` and `guitar`.
- **Model baseline:** Grounding DINO is the chosen baseline (most balanced
  precision/recall; main failure mode is mirror reflections).
- **Current dataset:** 182 expanded frames; 129 have both a person and a guitar.

## Consolidated action items

### Mine (mentee)

- [x] **Switch person-with-guitar decision from center-distance to IoU.** Done.
      Pair selection and the "playing" decision now use person/guitar IoU.
- [x] **Build the IoU distribution and recommend a threshold.** Done.
      Otsu over the distribution recommends **IoU ≥ 0.26**; full threshold sweep
      produced (`build_iou_threshold_analysis.py`, histogram SVG + JSON).
- [x] **Push code to GitHub (centralize artifacts).** Done — scripts are on `main`.
      Note: `data/metrics/` outputs are gitignored, so IoU stats will be shared via
      the descriptive report below, not the raw files.
- [x] **Restore project context + send this action-item list.** Done (this doc).
- [ ] **Update the `find-baseline-models-cv` skill** to its latest version.
- [ ] **Use the skill to search for / apply a baseline suited to video.** Per mentor:
      video models process *sequential frames*, so search via the skill for a
      video-level baseline rather than assuming the image baseline transfers as-is.
- [ ] **Run the baseline on video (not just images).** In progress — currently only
      run on images; `data/raw-videos/` is empty, so this needs a sample clip or
      reuse of an existing OBS frame sequence.
- [ ] **Produce a short descriptive analytics report:** frames with/without
      person-with-guitar, average IoU, and false-positive examples where nearby
      objects caused a wrong pairing.
- [ ] **Fix the relationship overlay images** so their "playing" verdicts use the new
      IoU rule (currently still rendered with the old center-distance logic).
- [ ] **Send current CV** for review (job-search track).

### Mentor

- [ ] Review CV and send comments/clarifying questions.
- [ ] Send meeting materials before/on Friday; confirm follow-up (same time).

## How to send

This file is committed to the repo, so the GitHub link above is the single source.
Paste the link in chat with the mentor, or copy this list into the message directly.
