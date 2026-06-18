# Mentor project & job-search checkin

_Meeting_

Jun 17, 2026 · 13:06 · summarized · 10 captured items

## Overview

_Mentor and mentee reviewed two parallel tracks: finish the machine-vision project and support the mentee's job search. They agreed next steps: mentee to restore project context, update and run the baseline (including on video), compute IoU statistics and produce a descriptive report; mentor will review CV and send meeting materials for a follow-up on Friday (same time)._

The meeting covered two parallel tracks: finishing the ongoing machine-vision project and supporting the mentee's job search (CV/LinkedIn). The mentee confirmed interest in both. The mentor requested the mentee's current CV for review and feedback. They discussed LinkedIn strategy: treat it as a social feed to show learning progress and project updates rather than switching account types for different engineering roles. On the project side, the mentor asked for the current project state and which action items from the previous meeting were completed. The mentee said they had minimal time in the past two weeks due to interview preparation, but that a baseline model for images exists and some local statistics (center-distance-based) were computed; however the baseline has not been run on video yet. The mentor emphasized the need to restore context before the next session — review meeting recordings and project flog/logs — and to come prepared with specific questions. Concrete technical guidance: compute intersection-over-union (IoU) between detected objects (not just center distances), build IoU distributions across the dataset to determine an optimal IoU threshold, and prepare descriptive analytics (e.g., on how many frames contain a person-with-guitar vs not, average IoU, false positives when objects are near each other). The mentor requested that the mentee (a) update the skill, (b) use that skill to retrieve the baseline, (c) attempt to run the baseline on video frames (if it fails they will debug together), and (d) share the skill/validation output for the baseline. The mentor offered to send something during the week and they scheduled a follow-up meeting on Friday at the same time. The mentor also flagged that they want an action-item list from the mentee derived from the meeting recordings and logs before the next meeting. They noted uncertainty about whether some local statistics were present in the GitHub repo and asked the mentee to clarify and centralize artifacts.

## Mentor Review

_Project-focused_

### Project State

- Baseline model exists and has been run on images (mentee believes baseline is built).
- No full baseline run on video yet; video processing was not attempted.
- Mentee computed some preliminary statistics based on center distances (not IoU).
- Some meeting recordings exist and there is a project flog/log that should contain prior decisions and action items; these need to be reviewed.
- Unclear whether current statistics and small analyses are committed to GitHub; location of artifacts is not fully centralized.

### Changed Since Last Meeting

- Minimal progress in the last two weeks due to mentee's interview preparation.
- Mentee reports having updated the skill at some point and computed center-distance statistics, but did not complete the video baseline or IoU analysis.

### Blockers

- Time constraints: mentee had limited availability the last two weeks.
- Loss of context: mentor suggested the mentee needs to rehydrate the project context from recordings and flog.
- Artifact location uncertainty: unclear whether stats/analyses are in GitHub or only local, making review harder.
- Technical uncertainty: mentee hasn't worked with video pipelines previously; running baseline on sequential frames may require environment/configuration adjustments.

### Mentor Feedback

- Send your current CV so I can comment and ask clarifying questions—LinkedIn should be used as a social feed to show learning and project progress rather than trying to switch account type for different roles.
- For detections use IoU rather than center distance to determine whether a person-with-guitar is detected; compute IoU distribution across dataset to pick an optimal threshold.
- Produce descriptive analytics after re-running/cleaning the model outputs: counts of frames with/without person-with-guitar, average IoU, and examples of false positives where nearby objects caused misclassification.
- Restore project context from the recordings and flog before the next meeting and prepare targeted questions—this will make the next session much more efficient.
- Update the skill and attempt to run the baseline on video; if it fails, bring errors/logs to the next meeting for live debugging.

### Before Next Meeting

- High priority: Send current CV to mentor so they can review before or at the next meeting (success = mentee's CV received by mentor).
- High priority: Restore project context from meeting recordings and flog, then produce and send a consolidated action-item list (success = action-item list received).
- High priority: Update the skill, use it to retrieve/apply the baseline, and attempt to run the baseline on video frames (success = baseline runs on at least a sample video or logs showing failure).
- High priority: Compute IoU for detections across dataset and build IoU distribution; prepare suggested IoU threshold candidates (success = IoU distribution plot or table).
- High priority: Produce a short descriptive analytics report with frame counts, average IoU, and representative failure cases (success = report PDF/markdown/CSV shared).
- Medium priority: Centralize artifacts (code, logs, analytics) in an accessible location (GitHub link or shared folder) and share the link with mentor.

### Artifacts To Prepare

- Current CV (file) to send to mentor
- List of meeting recording links and project flog/log file(s) references
- Updated skill code (GitHub link or zipped folder) and instructions to run it
- Baseline run scripts and logs for both image and video attempts
- IoU distribution data and visualization (plot PNG or Jupyter notebook), plus table of IoU summary statistics (CSV)
- Descriptive analytics report: counts of frames with/without person-with-guitar, average IoU, common false-positive examples (PDF/markdown/CSV)
- Consolidated action-item list derived from recordings (text/markdown)

### Questions For Next Meeting

- Can you confirm which exact meeting recording(s) and flog entries I should review first (provide links/paths)?
- Where would you like me to upload the updated skill and analytics (specific GitHub repo/path or shared folder)?
- What materials will you send on Friday (meeting invite, baseline code, or other reference files)?
- If I can't get the baseline to run on video before Friday, can we allocate time in the meeting for live debugging and what environment/access will you need?
- Do you have a recommended IoU threshold range to consider for 'person playing guitar', or should I purely derive it from the distribution?
- Which dataset split and annotation specification should I use for the IoU analysis (train/val/test and box format)?

### Action Items By Person

**Mentee**

- Task: Send current CV to mentor for review; Context: mentor requested to review and comment on CV for job-search track; Due: Friday; Priority: high
- Task: Restore project context by reviewing meeting recordings and project flog/logs; Context: recover last meeting details and action items so next session is efficient; Due: Friday; Priority: high
- Task: Prepare and send a concise list of specific technical and process questions; Context: come to next meeting with targeted questions about baseline, labeling, and video processing; Due: Friday; Priority: high
- Task: Update the project 'skill' to latest changes; Context: skill is used to find/apply baseline for validation; Due: Friday; Priority: high
- Task: Use updated skill to retrieve/apply baseline and attempt to run baseline on video data (not only images); Context: currently baseline was run on images only; Due: Friday (attempt before meeting); Priority: high
- Task: Compute IoU (intersection-over-union) between detected objects across the dataset and build the IoU distribution; Context: mentor advised IoU rather than center distances to choose thresholds; Due: Friday; Priority: high
- Task: Produce a descriptive analytics report (counts of frames with/without person-with-guitar, average IoU, examples of false positives/negatives); Context: deliver a short report to discuss at the follow-up meeting; Due: Friday; Priority: high
- Task: Share skill/validation artifacts and the location of statistics/results (GitHub link or shared folder); Context: mentor needs access to artifacts to review and comment; Due: Friday; Priority: high
- Task: Consolidate and send the action-item list derived from recordings and flog to mentor; Context: mentor asked for a single action-item list for clarity; Due: Before the Friday meeting; Priority: high

**Mentor**

- Task: Review the mentee's CV and provide comments and clarifying questions; Context: support job-search track and improve CV for machine-engineering roles; Due: After mentee sends CV (by Friday); Priority: high
- Task: Send meeting materials and confirm the follow-up meeting on Friday (same time); Context: mentor said 'я передашу на этой неделе, давай на пятницу'; Due: Friday; Priority: high

### Decisions

- Two parallel tracks confirmed: finish the project and pursue job-search (machine-engineering).
- Follow-up meeting scheduled for Friday at the same time as this session.
- Focus for next meeting: mentee will restore context, update skill, run baseline on video, compute IoU distributions, and bring descriptive analytics and specific questions.

### Open Questions

- Exactly which meeting recordings and flog/log files should the mentee prioritize to restore context (which file paths or links)?
- Where are the existing statistics and short analyses stored (local machine vs GitHub)? The mentor and mentee were unsure if current statistics are present in the GitHub repo.
- What specifically will the mentor 'передашу' on Friday (meeting invite, reference files, baseline code, or other artifacts)?
- If the baseline cannot run on video before Friday, who will lead debugging and what environment/access is required?
- Which dataset splits and annotation formats should be used for the IoU analysis (train/val/test; box vs mask annotations)?
- Is there a required file layout or GitHub path where the mentee must upload the updated skill and analytics (mentor did not specify a path)?
- What is the target/acceptable IoU threshold definition for 'person playing guitar' vs false positive—mentor requested distribution analysis but did not specify threshold criteria.

### Transcript

То есть у нас тут с тобой два трека, то есть с одной стороны мы хотим закончить с тобой проект, который мы с тобой начали, it's ok, а вторая часть это по поиску работы, связанная с машинным инженерингом. Будешь ли ты туда все-таки?
Да, я думаю, что да.
Тогда, если ты думаешь, что да, я от тебя жду твоего текущего CV, мы с тобой обсуждали в последний раз, чтобы было бы хорошо посмотреть твое текущее CV, я бы дала комментарий, задала бы точнящий вопрос и мы бы с тобой его привели к какому-то представляю.
Давай, да.
Давай я сразу здесь пишу нам с тобой сообщение, чтобы ты не забыл.
Да.
С Инкидином у меня тоже там был вопрос, типа, когда я подаюсь как электрико инженер, мне нужно, чтобы этот аккаунт был электрико инженером, когда я буду подаваться как машинленер.
Инкидин — это просто твоя социальная сеть, где ты делишься вообще твоими интересами.
То есть, ты можешь писать какие-то новости, ты можешь писать про твой PET-проект, что ты сейчас делаешь, какие этапы ты совершаешь.
То есть, по сути, это такая, знаешь, просто социальная сеть, и в ней не надо писать, она просто показывает тебя, условно, если ты будешь показывать процесс обучения,
будешь показывать, а, смотрите, вообще-то я умею учиться вот сейчас, у меня такой прогресс, я нашла для этого, для этого.
Хорошо, давай тогда дальше по проекту, что меня интересует.
Меня интересует текущее состояние проекта, потому что у нас с тобой было несколько action items после последней встречи.
Что ты успел сделать, что ты не успел сделать, то есть, какое сейчас состояние?
В течение последних двух недель, мне кажется, я минимально вообще этим занимался, практически не занимался из-за того, что я готовился к интервью.
Вот, что я успел сделать. Сейчас тебе пошерю экранчик.
А у меня есть права для того, чтобы шерить?
Давай я расширю. Обучение должно быть.
Так, класс.
Так.
Где у меня есть VS Code?
У меня после интервью просто миллион окон открыто.
Ага, все, окей, отлично, нашел.
Так, видно?
Мне кажется, я неправильно, неправильное окно, это не то.
Секунду.
Другой рабочий стол.
Так, я думаю, вот это вот оно. Видно?
Да.
Вот, одно из заданий, которое нужно было сделать, такой как бы bullet point, это...
Так, я вас на момент уточнил, это ты прогонял пока что, то есть, у тебя есть какой-то код, который ты прогонял только на картинках.
Пока что на картинках, да.
Да, то есть, нужно было...
А успел ли ты, успел ли ты прогнать на видео baseline?
Нет, на видео, с видео я пока что не работал.
Я выбрал, я выбрал модель.
Построил ли ты этот baseline?
Да.
Построил ли ты этот baseline?
Так.
Ну, то есть, мы с тобой обсуждали, что у нас skill, который ищет данные, ну, то есть, вот этот baseline у нас есть?
Мне кажется, что да.
Мне кажется, что да.
Я чувствую себя немножко виноватым, потому что я не успел...
Мне кажется, что я это делал.
Сейчас, так.
По крайней мере, я помню, что я обновлял skill.
Сейчас я спрошу быстренько у кодекса.
Угу.
Просто смотри, что бы мне хотелось, почему мы с тобой обсуждали, то есть, я сейчас дам комментарий, возможно, мы с тобой,
то есть, я попробовала созвониться тогда на этой неделе еще раз, то есть, сейчас закончится время,
мне бы хотелось все-таки, чтобы ты к занятию пришел с чем-то, что ты уже прогнал, в том числе на видео, чтобы мы разбирали и предыдущий опыт, который у тебя был.
То есть, мы сейчас можем с тобой поработать с этим немного.
Но я думаю, у нас это заняло сильно меньше времени, там, я не знаю, 10 минут.
И потом на неделе еще раз созвонись, иначе у нас с тобой синий клиент очень долго будет идти.
Согласен, да.
Все-таки нужно поработать время, восстановить контекст.
Согласен.
Что ты сделал в прошлый раз, что я тебе задавала, я не могу это подублировать еще раз.
Текст, я тебе закидывала, кстати, записи встреч, через записи встреч, что можно встать.
Угу.
Давай, наверное, то есть, мне не хотелось бы сейчас тратить час...
Да.
Давай, сделаем.
Твоя задача сейчас будет восстановить, то есть, у тебя есть записи встреч, у тебя есть флог, восстановить контекст проекта.
Угу.
У тебя, возможно, были вопросы.
Подготовить вопросы, пожалуйста.
Да.
Подготовить вопросы, восстановить контекст проекта.
Скинуть мне action item, то есть, мы с тобой здесь обсуждали, что ты по результатам записи встреч можешь проанализировать, что нужно было делать, если я тебе отправляла здесь, если я не ошибаюсь, последний раз записи встреч.
А, нет, у тебя последняя запись встреч была.
Да, да, мне есть, да, моя.
Вот, скинуть action item, но не еще раз.
И надо все-таки, давай, вот как мы с тобой обсуждали, что у нас есть силы, которые подменяют бейслайн.
Вот давай все-таки этот бейслайн сейчас возьмем и просто проведем, и дальше будем, то есть, видишь, мы с тобой обсудили уже от начала до конца, как все это идет.
Да.
И уже в момент нашей встречи будем разбирать конкретно твои вопросы и мои комментарии уже по рабочему пейплайну.
Да, да.
Хорошо, и скини мне, пожалуйста, третий пункт, который прошел, скини мне свой скилл или свой на валидацию по бейслайну.
Ага, ага, хорошо.
В следующий раз.
Я думаю, я могу этим сегодня заняться, я не думаю, что это займет прям много времени, то есть, нужно чего?
Нужно обновить скилл, нужно использовать скилл для поиска бейслайна и нужно использовать вот какую-то вот, собственно, попробовать прогнать видео на этих моделях.
Ага.
Если получится, если не получится, мы с тобой будем это отдельно разбирать.
Да.
Но, в целом, попробовать прогнать, мне кажется, более чем у тебя это должно получиться, потому что бейслайн повыбранный и по данным, то есть, уже быстрее.
Да.
Вот, и были вопросы у тебя по разметке данных, мы с тобой их тоже обсудим.
Хорошо, тогда смотри, какое мое действие, я нашу с тобой встречу, тогда.
Ага.
Передашу на этой неделе, давай на пятницу, тебе как в пятницу?
Давай, да, я думаю, все нормально, отлично, отлично.
Ага, замечательно.
Все, тогда я передашу на пятницу.
Ага.
Если у тебя сейчас ко мне вопросы.
Да, быстренько, смотри, я, для вот этих моделей, было ли смысл для тех моделей, которые я сейчас использовал, вычислять вот это вот расстояние между центрами объектов, чтобы определить, играет человек или не играет человек.
Конечно, да.
Я просто не очень понимаю, из-за того, что я пока что не искал и не смотрел, как работают модели для работы с видео, но я так понимаю, они тоже как бы обрабатывают последовательные картинки.
Да, последовательные кадры, то есть у нас история с картинками и с видео очень сильно связана.
И здесь важный момент, нужно, чтобы ты посчитал пересечения, там не центры были, там ай-ю-ю мы с тобой смотрели.
Ай-ю-ю, да, точно.
Мы бы обсуждали в том числе, что по этим картинкам, после того, как ты прогнал получше модели, ты придешь с описательной аналитикой.
То есть условно на стольких кадрах из стольких кадров человека с гитарой, а вот на стольких их нет, среднее ай-ю-ю такое-то.
То есть не сравнение модели, а непосредственно сравнение уже как бы знаешь финальный отчет на картинках.
Хорошо, да, нужно ли мне, вот я сделаю этот отчет.
На самом деле я уже сделал там кое-что, я прогнал, но мне кажется я считал расстояние между центрами, вот, не ай-ю-ю.
Вот, у меня есть там небольшая статистика по этому поводу, но нужно ли мне как-то...
В гитхабе.
А, хороший вопрос. Я не уверен, что она в гитхабе прямо сейчас лежит.
А, давай я сейчас прямо тебе, вот здесь у меня share есть, я тебе покажу.
Вот, у меня краткая статистика по тому, как оно детектировалось, и я потом просмотрел.
Не хватает здесь, смотри, вот у тебя есть board detected, а нам нужно помимо board detected как бы историю про то, что пересечение их.
У тебя же там есть кадры, где ты есть в кадре, где ты играешь, где ты не играешь.
Да, я посмотрел уже эти кадры, и там, конечно, есть очень много, где просто объекты близко находятся,
а он показал, что типа, ну, вот, играет. На самом деле не играет.
А нам нужно ай-ю-ю с тобой посчитать, и понять как бы, какое ай-ю-ю оптимальное.
А чтобы понять, какое ай-ю-ю оптимальное, нужно на всех данных построить распределение ай-ю-ю.
Помнишь, мы с тобой тоже это делали?
Точно, да, да.
Подними, пожалуйста, заднюю встречу, посмотри, что мы обсудили, подготовься, пожалуйста, к следующей встрече,
я думаю, так будет сильно эффективнее, чем мы сейчас с тобой.
Пожалуй, да, да, да, ты права, ты права.
Хорошо.
Хорошо, да, спасибо.
Всё, давай до пятницы.
На сколько в пятницу?
На точно так же.
Хорошо? Класс.
Спасибо.
Пока-пока.
Давай, хорошего вечера.
