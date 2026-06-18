# Meeting Summary - 2026-05-20T12:59:23.372645+00:00

- Session ID: `9965e839-d06d-49f7-b1d5-452497c079cb`
- Status: `summarized`
- Started: 2026-05-20T12:59:23.372645+00:00
- Ended: 2026-05-20T13:52:50.060426+00:00
- Audio: `/home/arturka/Documents/Projects/VSCode_projects/meeting-copilot-mvp/backend/data/recordings/9965e839-d06d-49f7-b1d5-452497c079cb-2f16009aee0c4f01b45b24ba061b477c.wav`

## Short Summary

Mentor review of the first computer-vision pipeline: 30 labeled images, Grounding DINO baseline, video frame extraction, Label Studio pre-annotation, and next steps. The main direction is to compare multiple baselines objectively, clean the person/guitar dataset, add IoU analytics, and move from still images toward video-level reporting.

## Detailed Summary

Arthur presented the first working version of the project pipeline. He labeled 30 images, ran one baseline model, collected more video data, extracted frames roughly every five seconds, and connected model predictions into Label Studio for pre-annotation. The pipeline exists, but the evaluation is still too narrow because only one model was evaluated and the annotation rules are not fully settled.

The mentor pushed the workflow toward a more rigorous baseline process. Instead of choosing Grounding DINO visually, Arthur should run several candidate models and compare them with per-class and overall metrics. For many models/classes, heatmaps are preferred over bar charts because they are easier to scan. The comparison should explain both which model is best overall and whether any model fails specifically on person or guitar.

The dataset discussion centered on simplifying the label space. For the current iteration, the project should focus on person and guitar. The broad 'musical instruments' class can be removed because it makes the metrics harder to interpret. The mirror/reflection case remains an annotation decision: the practical goal is to detect whether Arthur is playing, so the team needs a consistent rule for whether reflections count as separate objects.

The downstream analytics plan is the most important technical next step. The output model boxes need to be converted into a product-level report: frames where the person is playing, not playing, or absent. The mentor recommended computing IoU between person and guitar boxes, plotting train/val/test distributions, and choosing a threshold empirically rather than guessing. This prepares the project to move from static images into video analysis and eventually tracking.

Organizationally, the mentor also recommended better documentation: a README or markdown report should explain the project story, baseline choice, metrics, dataset-centric loop, and next experiments. Arthur also mentioned converting his academic CV into a shorter resume for review.

## Cleaned Notes

Project state after this meeting:
- Data: 30 labeled seed images plus additional video-derived frames.
- Current model: Grounding DINO tested first, but not enough for final baseline choice.
- Annotation scope: person and guitar for now; remove broad musical-instrument class.
- Evaluation: compare models with per-class and overall metrics, preferably heatmaps.
- Next analytical layer: IoU distributions and threshold selection for playing/not-playing detection.
- Product output: aggregate frame-level detections into an interpretable report.

## Action Items

- Run several baseline models, not only Grounding DINO, on the labeled image set.
- Collect per-class and overall metrics for each candidate model.
- Build comparison visualizations, especially heatmaps for model/class/metric scanning.
- Clean the Label Studio annotations and keep the current label set focused on person and guitar.
- Make a consistent annotation decision for mirror/reflection cases.
- Rerun the pipeline after annotation cleanup and compare metric changes.
- Write an IoU script for person/guitar boxes per frame.
- Plot IoU distributions across train/validation/test and propose threshold candidates.
- Create an aggregator that converts detections into a final report: playing / not playing / absent.
- Run the model on extracted video frames and test whether simple bbox tracking is enough.
- Draft README/markdown documentation with baseline choice, metrics, and dataset-centric workflow.
- Convert the CV into a concise resume and send it for mentor review.

## Action Items By Person

### Arthur

- Run multiple baseline models and collect per-class/overall metrics; priority high.
- Create heatmap-style visualizations for model comparison; priority high.
- Clean Label Studio annotations and settle person/guitar label rules; priority high.
- Rerun metrics after annotation cleanup; priority high.
- Implement IoU analytics and distribution plots; priority high.
- Build report aggregator for playing/not playing/absent frame counts; priority medium.
- Move the pipeline from images to video frames and test basic bbox tracking; priority medium.
- Document the project in README/markdown; priority medium.
- Prepare a shorter resume from the academic CV; priority medium.

### Mentor

- Review next visual report and help choose baseline/model comparison criteria.
- Clarify annotation rule for mirror/reflection if Arthur cannot decide consistently.
- Optionally help arrange English mock interview practice.

## Tasks

- Multi-model baseline comparison
- Annotation cleanup
- IoU threshold analysis
- Video-frame experiment
- README/report draft
- Resume review

## Tasks By Person

### Arthur

- Run baseline comparison and visualizations.
- Clean annotations and rerun metrics.
- Build IoU and report aggregation scripts.
- Prepare README/report and resume draft.

### Mentor

- Review visual report and advise on annotation/model decisions.

## Decisions

- Current dataset iteration should use two classes: person and guitar.
- Grounding DINO alone is not enough; baseline selection should compare multiple models objectively.
- Use heatmaps for scalable per-class/model metric comparison.
- Use a data-centric loop: baseline pre-annotation, manual correction, metric review, then repeat or fine-tune if needed.
- Choose the playing/not-playing threshold empirically from IoU distributions.

## Open Questions

- Should a person reflected in a mirror be labeled as a separate object or ignored/merged for this task?
- Which exact models should be included in the baseline comparison?
- What frame extraction interval is best for the video experiments: five seconds, denser sampling, or adaptive sampling?
- What IoU threshold should define person+guitar interaction after distributions are plotted?
- Is bbox-level tracking sufficient, or will skeleton/finger tracking be necessary later?
- Who owns the final README/report updates if Arthur does not complete them?

## Ideas

- Heatmaps make model/class weaknesses visible faster than bar charts when comparing many baselines.
- The project report should tell the whole story: baseline, data correction, metrics, then video-level signal extraction.
- Start with bbox-level tracking before escalating to skeleton or finger tracking.

## Follow Ups

- Next mentor session should review the visual baseline comparison and corrected annotations.
- Resume/CV review after Arthur prepares a shorter version.
