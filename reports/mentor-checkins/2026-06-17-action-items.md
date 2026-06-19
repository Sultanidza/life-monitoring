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
- [x] **Update the `find-baseline-models-cv` skill.** The skill is config-driven
      (reads `PROJECT.md`, no hardcoded classes), already at its latest committed
      version. Updated its behavior the correct way — by adding the video-level
      families and selected baseline to `PROJECT.md` — then used it for the search.
- [x] **Use the skill to search for / apply a baseline suited to video.** Done.
      Verified shortlist produced; `reports/model-search/2026-06-17-video-level-baseline-shortlist.md`.
- [x] **Run the baseline on video (not just images).** Done. Ran VideoMAE on all 3
      real OBS videos; compared VideoMAE/TimeSformer/ViViT — VideoMAE selected.
      `reports/video-baseline/2026-06-17-video-baseline-report.md`.
- [x] **Produce a short descriptive analytics report.** Done, both levels:
      image-level IoU report (`reports/image-analysis/2026-06-17-image-iou-descriptive-report.md`,
      counts / average IoU / false-positive gallery) and the video-baseline report above.
- [x] **Fix the relationship overlay images** so their "playing" verdicts use the new
      IoU ≥ 0.26 rule. Done — overlays regenerated.
- [ ] **Send current CV** for review (job-search track).

### Mentor

- [ ] Review CV and send comments/clarifying questions.
- [ ] Send meeting materials before/on Friday; confirm follow-up (same time).

## Next steps (next sprint — validate the video baseline)

Everything above is **descriptive**, not yet **validated**: we have no ground
truth for *playing*, so we cannot yet say how well VideoMAE performs. The "top-1
playing-guitar rate" used to compare models only counts positive predictions — it
cannot tell genuine detection from over-prediction (false positives). Fixing that
is the next priority.

- [ ] **Define what counts as "playing"** (does tuning count? holding without
      strumming? short mid-song pauses?) — agree the rule with mentor.
- [ ] **Label the playing time-intervals on one video** (temporal labels, not
      boxes — just note start/end times, e.g. `0:30–2:15`). One 4-min video is
      enough to start (~250 windows).
- [ ] **Score VideoMAE against those labels:** precision, recall, F1, and
      total-playing-time error (precision directly exposes false positives).
- [ ] Use the result to tune the decision rule and the session parameters, and to
      decide whether a heavier model (temporal localization, tIoU) is justified.

## How to send

This file is committed to the repo, so the GitHub link above is the single source.
Paste the link in chat with the mentor, or copy this list into the message directly.
