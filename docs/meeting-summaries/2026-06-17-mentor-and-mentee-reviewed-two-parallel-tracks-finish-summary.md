# Meeting Summary - 2026-06-17T13:06:39.140587+00:00

- Session ID: `87af3ca0-659b-42f5-9bec-181b727f5b4f`
- Status: `summarized`
- Started: 2026-06-17T13:06:39.140587+00:00
- Ended: 2026-06-17T13:18:14.816178+00:00
- Audio: `/home/arturka/Documents/Projects/VSCode_projects/meeting-copilot-mvp/backend/data/recordings/87af3ca0-659b-42f5-9bec-181b727f5b4f-4bb9a56446e34fbeb1362229c0f9712d.wav`

## Title

Mentor project & job-search checkin

## Short Summary

Mentor and mentee reviewed two parallel tracks: finish the machine-vision project and support the mentee's job search. They agreed next steps: mentee to restore project context, update and run the baseline (including on video), compute IoU statistics and produce a descriptive report; mentor will review CV and send meeting materials for a follow-up on Friday (same time).

## Detailed Summary

The meeting covered two parallel tracks: finishing the ongoing machine-vision project and supporting the mentee's job search (CV/LinkedIn). The mentee confirmed interest in both. The mentor requested the mentee's current CV for review and feedback. They discussed LinkedIn strategy: treat it as a social feed to show learning progress and project updates rather than switching account types for different engineering roles. On the project side, the mentor asked for the current project state and which action items from the previous meeting were completed. The mentee said they had minimal time in the past two weeks due to interview preparation, but that a baseline model for images exists and some local statistics (center-distance-based) were computed; however the baseline has not been run on video yet. The mentor emphasized the need to restore context before the next session — review meeting recordings and project flog/logs — and to come prepared with specific questions. Concrete technical guidance: compute intersection-over-union (IoU) between detected objects (not just center distances), build IoU distributions across the dataset to determine an optimal IoU threshold, and prepare descriptive analytics (e.g., on how many frames contain a person-with-guitar vs not, average IoU, false positives when objects are near each other). The mentor requested that the mentee (a) update the skill, (b) use that skill to retrieve the baseline, (c) attempt to run the baseline on video frames (if it fails they will debug together), and (d) share the skill/validation output for the baseline. The mentor offered to send something during the week and they scheduled a follow-up meeting on Friday at the same time. The mentor also flagged that they want an action-item list from the mentee derived from the meeting recordings and logs before the next meeting. They noted uncertainty about whether some local statistics were present in the GitHub repo and asked the mentee to clarify and centralize artifacts.

## Action Items

- [Mentee] Send current CV to mentor for review
- [Mentee] Restore project context: review meeting recordings and project flog/logs, and list outstanding action items
- [Mentee] Prepare and send a concise list of specific questions for the next meeting
- [Mentee] Update the 'skill' (project code/component) to the latest version in repo or working directory
- [Mentee] Use the updated skill to retrieve/apply the baseline and run the baseline on video data (not just images)
- [Mentee] Compute IoU (intersection-over-union) between detected objects across the dataset and build the IoU distribution
- [Mentee] Produce a descriptive analytics report on frames: counts of frames with/without person-with-guitar, average IoU, false positives/negatives and examples
- [Mentee] Share skill/validation artifacts and where statistics/results are stored (GitHub link or shared folder)
- [Mentee] Send the consolidated action-item list (derived from recordings and flog) to mentor before the Friday meeting
- [Mentor] Review the mentee's CV and provide comments and clarifying questions
- [Mentor] Send meeting materials / any necessary files before or on Friday (confirming follow-up meeting)
- [Either] If baseline cannot be run on video, debug together during follow-up meeting

## Action Items By Person

### Mentee

- Task: Send current CV to mentor for review; Context: mentor requested to review and comment on CV for job-search track; Due: Friday; Priority: high
- Task: Restore project context by reviewing meeting recordings and project flog/logs; Context: recover last meeting details and action items so next session is efficient; Due: Friday; Priority: high
- Task: Prepare and send a concise list of specific technical and process questions; Context: come to next meeting with targeted questions about baseline, labeling, and video processing; Due: Friday; Priority: high
- Task: Update the project 'skill' to latest changes; Context: skill is used to find/apply baseline for validation; Due: Friday; Priority: high
- Task: Use updated skill to retrieve/apply baseline and attempt to run baseline on video data (not only images); Context: currently baseline was run on images only; Due: Friday (attempt before meeting); Priority: high
- Task: Compute IoU (intersection-over-union) between detected objects across the dataset and build the IoU distribution; Context: mentor advised IoU rather than center distances to choose thresholds; Due: Friday; Priority: high
- Task: Produce a descriptive analytics report (counts of frames with/without person-with-guitar, average IoU, examples of false positives/negatives); Context: deliver a short report to discuss at the follow-up meeting; Due: Friday; Priority: high
- Task: Share skill/validation artifacts and the location of statistics/results (GitHub link or shared folder); Context: mentor needs access to artifacts to review and comment; Due: Friday; Priority: high
- Task: Consolidate and send the action-item list derived from recordings and flog to mentor; Context: mentor asked for a single action-item list for clarity; Due: Before the Friday meeting; Priority: high

### Mentor

- Task: Review the mentee's CV and provide comments and clarifying questions; Context: support job-search track and improve CV for machine-engineering roles; Due: After mentee sends CV (by Friday); Priority: high
- Task: Send meeting materials and confirm the follow-up meeting on Friday (same time); Context: mentor said 'я передашу на этой неделе, давай на пятницу'; Due: Friday; Priority: high

## Project State

- Baseline model exists and has been run on images (mentee believes baseline is built).
- No full baseline run on video yet; video processing was not attempted.
- Mentee computed some preliminary statistics based on center distances (not IoU).
- Some meeting recordings exist and there is a project flog/log that should contain prior decisions and action items; these need to be reviewed.
- Unclear whether current statistics and small analyses are committed to GitHub; location of artifacts is not fully centralized.

## Changed Since Last Meeting

- Minimal progress in the last two weeks due to mentee's interview preparation.
- Mentee reports having updated the skill at some point and computed center-distance statistics, but did not complete the video baseline or IoU analysis.

## Blockers

- Time constraints: mentee had limited availability the last two weeks.
- Loss of context: mentor suggested the mentee needs to rehydrate the project context from recordings and flog.
- Artifact location uncertainty: unclear whether stats/analyses are in GitHub or only local, making review harder.
- Technical uncertainty: mentee hasn't worked with video pipelines previously; running baseline on sequential frames may require environment/configuration adjustments.

## Mentor Feedback

- Send your current CV so I can comment and ask clarifying questions—LinkedIn should be used as a social feed to show learning and project progress rather than trying to switch account type for different roles.
- For detections use IoU rather than center distance to determine whether a person-with-guitar is detected; compute IoU distribution across dataset to pick an optimal threshold.
- Produce descriptive analytics after re-running/cleaning the model outputs: counts of frames with/without person-with-guitar, average IoU, and examples of false positives where nearby objects caused misclassification.
- Restore project context from the recordings and flog before the next meeting and prepare targeted questions—this will make the next session much more efficient.
- Update the skill and attempt to run the baseline on video; if it fails, bring errors/logs to the next meeting for live debugging.

## Before Next Meeting

- High priority: Send current CV to mentor so they can review before or at the next meeting (success = mentee's CV received by mentor).
- High priority: Restore project context from meeting recordings and flog, then produce and send a consolidated action-item list (success = action-item list received).
- High priority: Update the skill, use it to retrieve/apply the baseline, and attempt to run the baseline on video frames (success = baseline runs on at least a sample video or logs showing failure).
- High priority: Compute IoU for detections across dataset and build IoU distribution; prepare suggested IoU threshold candidates (success = IoU distribution plot or table).
- High priority: Produce a short descriptive analytics report with frame counts, average IoU, and representative failure cases (success = report PDF/markdown/CSV shared).
- Medium priority: Centralize artifacts (code, logs, analytics) in an accessible location (GitHub link or shared folder) and share the link with mentor.

## Artifacts To Prepare

- Current CV (file) to send to mentor
- List of meeting recording links and project flog/log file(s) references
- Updated skill code (GitHub link or zipped folder) and instructions to run it
- Baseline run scripts and logs for both image and video attempts
- IoU distribution data and visualization (plot PNG or Jupyter notebook), plus table of IoU summary statistics (CSV)
- Descriptive analytics report: counts of frames with/without person-with-guitar, average IoU, common false-positive examples (PDF/markdown/CSV)
- Consolidated action-item list derived from recordings (text/markdown)

## Questions For Next Meeting

- Can you confirm which exact meeting recording(s) and flog entries I should review first (provide links/paths)?
- Where would you like me to upload the updated skill and analytics (specific GitHub repo/path or shared folder)?
- What materials will you send on Friday (meeting invite, baseline code, or other reference files)?
- If I can't get the baseline to run on video before Friday, can we allocate time in the meeting for live debugging and what environment/access will you need?
- Do you have a recommended IoU threshold range to consider for 'person playing guitar', or should I purely derive it from the distribution?
- Which dataset split and annotation specification should I use for the IoU analysis (train/val/test and box format)?

## Decisions

- Two parallel tracks confirmed: finish the project and pursue job-search (machine-engineering).
- Follow-up meeting scheduled for Friday at the same time as this session.
- Focus for next meeting: mentee will restore context, update skill, run baseline on video, compute IoU distributions, and bring descriptive analytics and specific questions.

## Open Questions

- Exactly which meeting recordings and flog/log files should the mentee prioritize to restore context (which file paths or links)?
- Where are the existing statistics and short analyses stored (local machine vs GitHub)? The mentor and mentee were unsure if current statistics are present in the GitHub repo.
- What specifically will the mentor 'передашу' on Friday (meeting invite, reference files, baseline code, or other artifacts)?
- If the baseline cannot run on video before Friday, who will lead debugging and what environment/access is required?
- Which dataset splits and annotation formats should be used for the IoU analysis (train/val/test; box vs mask annotations)?
- Is there a required file layout or GitHub path where the mentee must upload the updated skill and analytics (mentor did not specify a path)?
- What is the target/acceptable IoU threshold definition for 'person playing guitar' vs false positive—mentor requested distribution analysis but did not specify threshold criteria.
