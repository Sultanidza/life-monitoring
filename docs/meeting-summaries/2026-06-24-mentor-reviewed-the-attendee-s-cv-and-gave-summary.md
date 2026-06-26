# Mentor project check-in

- Transcription model: `faster-whisper/large-v3`
- Summarization model: `gpt-5-mini`

_Mentor / coaching_

Jun 24, 2026 · 13:02 · summarized · 10 captured items

## Overview

_Mentor reviewed the attendee's CV and gave detailed formatting and content suggestions. They reviewed the attendee's video-analytics experiments: three models (VideoMAE, TimesFormer, Vivid) were evaluated on three ~4-min videos; VideoMAE performed best; smoothing improved recall. Mentor assigned a set of experiments and deliverables to prepare before the next meeting._

The session combined CV / career coaching and technical mentorship for a video-analytics project. On the CV: the mentor recommended condensing the contact block into one line, adding an "about you" summary that states role and years of experience, aligning skills and keywords with target job descriptions, preferring measurable results (numbers, metrics) in work-experience bullets, keeping CV to one page where possible, including GitHub/LinkedIn links, and extracting thesis/publication details into the education block. Mentor demonstrated examples from their own CV and stressed focusing on relevancy for the target role (e.g., electrical engineering vs ML roles), clarifying gaps (e.g., parental leave) directly in the CV, and making soft skills concrete with context (team size, impact). The mentor asked to include required output format and evaluation parameters in project documentation.

On the video-analytics project: the attendee ran three baseline models suggested by the system: VideoMAE, TimesFormer, and Vivid. Evaluation was performed on three videos (~4 minutes each, ~6000+ frames per video). VideoMAE outperformed the other two baselines; initial VideoMAE results reported were ~94% precision and ~84% recall. Labels were created in Label Studio as time intervals (classes like playing / not playing / ambiguous). The mentor strongly recommended avoiding an ambiguous class because it causes noisy/collapsed labels during crowdsourcing/outsourcing and harms metrics. The attendee applied a smoothing (post-processing) procedure over predicted intervals (to merge short not-playing spikes between playing intervals) which increased recall; the exact smoothing hyperparameter used was not recorded and remains to be specified. The attendee wanted to inspect which specific frames the model misclassified but could not yet visualize the error frames.

Mentor guidance for the next steps included: eliminate ambiguous label class and define deterministic class rules; build a test dataset with varied positive/negative prevalence (large number of positive and negative examples) to properly evaluate robustness; run evaluation for detection baselines and tracking baselines (mentor asked to test both detection-only and tracking approaches because tracking is often needed to measure durations); perform hyperparameter tuning for smoothing (and other post-processing) using systematic search (mentor referenced random-search/grid-search style approaches) rather than picking arbitrary values; record and compare inference times (CPU and GPU) for candidate models; prepare an evaluation section that specifies output format and eval parameters; create visualizations/dashboards that show time vs metric, per-video/per-model results, and per-frame error examples; and prepare to measure camera integration constraints (real-time inference feasibility). The mentor offered availability on 1 July and noted travel/unavailability starting 2 July (out of contact until ~10 July) and possible longer unavailability until August depending on visa; they can still provide a pipeline to experiment during absence. The mentee acknowledged understanding next steps and asked for shared materials; mentor agreed to share relevant materials.

## Mentor Review

_Project-focused_

### Project State

- Three baseline models were evaluated: VideoMAE, TimesFormer, Vivid (VideoMAE performed best on the small test set).
- Evaluation was run on three videos (~4 minutes each, ~6000+ frames per video) with reported ~94% precision and ~84% recall for VideoMAE initially.
- Labeling was done in Label Studio using time-interval labels (classes: playing, not playing, ambiguous).
- A smoothing post-processing step was applied and increased recall, but exact smoothing hyperparameters are not recorded.
- Per-frame error visualization and full evaluation pipeline (output format, eval parameters) are not yet completed.

### Changed Since Last Meeting

- Ran three baseline models (VideoMAE, TimesFormer, Vivid) and computed preliminary metrics on three videos.
- Applied smoothing/post-processing which improved recall on the evaluated sample.
- Created annotations in Label Studio with interval labels for the dataset.

### Blockers

- Presence of an 'ambiguous' label class that reduces label quality and harms metrics in crowdsourcing/outsourcing scenarios.
- Missing recorded value(s) for the smoothing hyperparameter used in the preliminary test.
- No per-frame error visualization yet, so specific failure cases are not inspected.
- Evaluation documentation (output format and eval parameters) is incomplete or unspecified.

### Mentor Feedback

- Condense contact info to a single line and remove unnecessary location detail unless relevant.
- Add a short 'about you' summary that states your role and years of experience and aligns with the target job; include domain keywords to match vacancy descriptions.
- In work-experience bullets, focus on results and measurable impact (numbers, metrics) rather than long task lists; consider swapping order of some fields to surface most relevant info first.
- Keep CV to one page when possible; avoid splitting a block header onto a new page.
- Include GitHub and LinkedIn links and highlight concrete artifacts/certificates; extract thesis/publications as separate education/activity items.
- Avoid ambiguous classes in labeling; define deterministic class rules to reduce noise and outsourcing errors.
- Construct a clear evaluation procedure (output format and eval params) and test models on datasets with varied class prevalence (many positives and many negatives).
- Do systematic hyperparameter tuning for smoothing/post-processing (e.g., random search/grid search) instead of arbitrary selection.
- Test both detection and tracking baselines and measure inference times (CPU/GPU); prepare dashboard visualizations comparing models and showing metric over time.

### Before Next Meeting

- Revise CV per mentor recommendations: one-line contact, about-summary, measurable bullets, include GitHub/LinkedIn, one-page layout. Success criteria: a revised CV file ready to share.
- Remove/redefine 'ambiguous' label and update Label Studio annotations; success criteria: dataset contains deterministic playing/not-playing labels only.
- Assemble a larger test dataset with controlled positive/negative prevalence; success criteria: dataset with multiple videos and documented class counts.
- Run detection and tracking baselines on the dataset and compare results; success criteria: short report comparing detection vs tracking metrics.
- Perform systematic hyperparameter search for smoothing and document chosen parameter(s) and results; success criteria: hyperparameter search logs and selected parameter.
- Generate per-frame error visualizations for at least one representative video; success criteria: screenshots or plots showing error frames and model predictions.
- Measure inference latency on CPU and GPU for candidate models and include results in the comparison; success criteria: table of inference times per model and device.
- Prepare an evaluation document that specifies output format, evaluation parameters, and the evaluation sequence used in experiments; success criteria: evaluation.md or equivalent.

### Artifacts To Prepare

- Revised CV file (one-page preferred) with GitHub/LinkedIn links.
- Updated Label Studio annotations (no 'ambiguous' class) and annotation guidelines (deterministic rules).
- Test dataset (videos) with documented class counts and prevalence.
- Hyperparameter search configuration and logs for smoothing/post-processing (e.g., search ranges and results).
- Per-frame error visualization images or export showing misclassified frames/intervals.
- Evaluation document specifying output format and eval parameters.
- Inference time measurement results (CPU and GPU) for each model.
- Dashboard screenshots or a working dashboard demonstrating per-model, per-video metrics and inference-time comparisons.

### Decisions

- Avoid using an 'ambiguous' label class in dataset labeling; prefer deterministic class definitions.
- Evaluate three baseline models (VideoMAE, TimesFormer, Vivid); VideoMAE initially performed best on the tested sample.
- Apply smoothing/post-processing on predicted intervals to reduce short misclassification spikes (this improved recall in preliminary tests).
- Next meeting tentatively planned for 1 July (mentor indicated availability on 1 July and unavailability starting 2 July).

### Open Questions

- What exact smoothing (post-processing) hyperparameter(s) were used in the preliminary run? (attendee did not record exact values)
- What is the final requested output format and the precise evaluation parameters required by the project (the mentor asked to provide 'output format, eval parameters')?
- Who will own each action item listed (no explicit owner assigned in the transcript)?
- Which hyperparameter optimization method and parameter ranges should be used for smoothing and other post-processing (mentor suggested systematic search but not exact config)?
- Can the mentor share the promised materials and example references (the mentor said they would share materials)?
- Confirm exact date/time for the next meeting (mentor proposed 1 July but availability details were discussed and partially tentative).

### Transcript

Привет. Так, секундочку. А, всё, всё, я тебя слышу. Отлично.
Хорошо, слышно меня?
Да, да, отлично.
Замечательно.
Да, хорошо. Как у тебя дела?
Пойдёт, пойдёт. Как у тебя?
Да тоже в целом нормально. В процессе передачи дел и безумного желания отдыхать.
Вот, потому что я до конца июня работаю с Юлей, а уезжаю, поэтому как-то так.
Смотри, как я хочу сегодня выстрелить.
Первое, я хочу посмотреть с тобой сейчас в СиВи, я его посмотрю, я тебе дам свои какие-то комментарии с точки зрения внимающей части, на что обратить внимание и правки, что это значит.
Второе, я отвечу на твои комментарии, которые ты мне присылал, и мы с тобой посмотрим твои результаты, которые ты получил.
Третье, я хочу рассказать тебе, соответственно, я тебе отвечу на комментарии.
Дальше я тебе скажу про отличия моделей.
То есть пока буду отвечать на...
Сейчас, подожди.
Какие-то странные...
Вот, дальше, соответственно, я отвечу на твои вопросы.
После того, как мы с тобой посмотрим на вопросы, я немножко поговорю про архитектуру моделей.
Я отвечу на архитектуру моделей.
Дальше.
После этого я бы хотела поднять тему такой сущности, как куки-катер.
Слышал ли ты про него что-нибудь?
Мы с тобой посмотрим, что такое куки-катер.
Это штука, которая позволит тебе сделать так, чтобы твои репертуары выглядели почище.
И, соответственно, в финале мы с тобой посмотрим, что нам...
То есть какие действия нужны для того, чтобы сейчас, например, получить какой-то дартер, замер, соответственно, и разметку.
По твоей...
Соответственно, работе здесь.
Да.
Хорошо.
Хотел бы ли я что-то еще вставить в этот процесс?
Нет.
Я думаю, все меня устраивает.
Да.
Хорошо.
Я сейчас сразу предупрежу, соответственно, смотри.
Важный момент.
Если у нас такое встречное 1 июля, я сразу скажу.
1 июля я могу еще.
2 июля я улетаю.
Улетаю я буду без связи до 10.
То есть 8 числа у нас выпадает.
И потом до августа меня не уйдет совсем, потому что я улетаю в Европу, точнее так, если мне все-таки дают визу, я улетаю.
Если нет, то я буду только в августе доступна, но я могу тебе, соответственно, понакидать какой-то pipeline работы, чтобы ты за это время мог что-то экспериментировать и что-то ходить ко мне с опросом, потому что желания у тебя не смогут.
Да.
То есть, если как бы у тебя все по плану пойдет, то у нас последняя встреча до какой-нибудь встречи в августе или в сентябре, в августе, наверное, да, это будет первое, 1 июля.
Да, это первое время на следующую неделю.
Потому что потом у меня получается, я июль месяц, у меня такой перерыв на восстановление и отпуск и прочее.
Да, абсолютно.
Хорошо.
Хорошо.
Так, смотри, первое, что сразу бросается в глаза, у тебя достаточно много места занимает вот эта часть с именем, телефоном, имейлом, я бы ее поставила, то есть, в одну строчку, то есть, здесь у тебя имя.
Да, и когда я сейчас готовил свое другое резюме для electrical engineering, я все это в одну строчку сделал.
Так, ну, давай я просто здесь по оформлению, по плану внимания расскажу.
У нас наверху какая-то информация.
Есть информация, где ты указываешь, кто ты, что ты, и тут важный момент, смотри, на будущее, когда ты будешь говорить какие-то истории, ну, то есть, когда ты будешь уже отправлять резюме на позицию, так как занимающий менеджер, то есть, Илья Чарли, кто угодно, он отфильтровывает большое количество резюме, тебе нужно сразу здесь указать, кто ты и на каком позиции.
Соответственно, логично будет, вот, внимание, я не знаю, electrical engineer, Артур, связаться вот так.
Оказывается, Илья, здесь место проживания не надо, ну, то есть, место проживания здесь в данном случае не сильно валидно, потому что это информация, которую можно будет у тебя уточнить в дальнейшем, ну, то есть, максимум можно указать, что ты, например, находишься в USA, в какой-то регионе, подробно это, по сути, смотри, то есть, у тебя вот этот верхний блок занимает очень много информации.
Да.
Тут просто держать в голове, что информацию, когда про тебя читают, ее стараются читать.
Ну, то есть, фокус внимания, вот я тебе еще видео дополнительное потом скину, он идет вот так, вверху вот эта область, давай я даже ее буду рисовать, сейчас, то есть, получается, фокус внимания обычно идет вот отсюда, вот так вот, блин, короче, он идет вот так вот вниз и вот так вот, то есть, как показывает практика вот эта зона,
интересует уже не HR, а уже людей, которые в дальнейшем чуть подробнее смотрят твои, ну, как бы, информацию о тебе.
У нас такая задача максимально быстро, ну, как бы, в целом пройти отсек HR, ну, то есть, чтобы у нас здесь, как бы, не забраковал, ну, в принципе, это очень важно.
Наверное, даже первая задача пройти отсек автоматически.
Об этом мы с тобой поговорим.
Смотри.
Дальше.
Как это передвинуть, вот это, что школьник, он не знал, а так.
Дальше двигаемся.
Соответственно, то есть, мы с тобой здесь у нас фокус, work experience, слишком много, как бы, информации здесь можно, например, я бы рекомендовала до work experience коротко вставить информацию о тебе, about you.
Вот здесь about свой важный список писателей.
Это о чем мы с тобой говорим, правильно?
Четвертый секунд.
Вот, еще что-то.
Если, например, три плюс года в какой-то сфере или в три года, например, три плюс года в какой-то сфере, теперь я вам указываю, что есть как ведут осев большие языковые модели.
Они смотрят соответствие текста, соответствие тебя, вакансии, соответственно, ты пишешь.
Я три плюс года там-то, там-то, двигаюсь туда-туда, туда-туда, зона интереса.
И у тебя каждое твое сили должно быть в соответствии с описанием вакансии.
Чем больше пересекаешься у тебя здесь слов.
Чем лучше.
Хорошо?
Хорошо, отбегаемся дальше.
По поводу work experience.
Ты здесь описываешь компанию, все окей.
Дальше.
Вот это и вот это можно поменять местами.
Потому что, опять же, смотри, фокус того места, где ты работаешь.
А сколько, согласен, да, правда.
Дальше.
Framework, да-да-да-да-да-да, дизайн, трейн, да-да-да-да-да-да-да.
Смотри, важный момент, опять же, на что очень часто смотрят занимающие менеджеры и чарлы, и неонки, и так далее.
Не просто, что ты делал, а что сейчас твой текст читается, я занимался тем-то, тем-то, я занимался тем-то, тем-то.
А, например, я, как бы, for authentication and visual analyze of, там, for, там, for the century, paintings and increase metrics,
or, or, about 20 persons, типа, что-нибудь в таком духе.
То есть результат.
Да.
Ну, то есть, не просто, что я что-то делал, я что-то делал, и я достиг такого результата.
Нужны цифры.
Ага.
Я что-то делал, и я пришел к вот такому результату.
Или, я что-то делал, и я получил вот такой вот опыт.
Всегда важный, всегда важный акцент на твоем полученном либо опыте, либо экспертизе, либо то, что...
Опять же.
Опять же.
Опять же.
показывает тебя, что ты смог сделать.
И здесь тоже самое.
Implemented Embedded.
Вот тут вот можно хорошо, что ты имплементировал
что-то, соответственно.
RISC-C собрал Realtime Control and Monitoring.
Для чего?
То есть, чтобы что?
Да.
Там то-то, то-то, то-то.
И вот смотри, что у тебя получается.
Потенциально у тебя могут уменьшиться
вот эти строчки.
Да, глухо.
И, словно, может стать не 6, а 3, например.
И это окей.
Но ты сконцентрированно пишешь.
Там я сделал вот это, вот это, вот это.
То есть там будут быть цифры, а не количество.
И в целом, в этом случае, это пойдет на плюс.
Потому что ты таким образом сможешь
как бы все уместить на одной странице.
Ты знаешь, хороший тон
в CV это одна страница.
Да.
Далее.
Здесь то-то, то-то.
Ну, тут тоже как бы надо подумать,
стоит это или нет вставлять.
Опять же, смотри, если ты вставляешь
какую-то историю про...
Если ты вставляешь какую-то историю
для конкретной работы,
то лучше оставлять конкретные
твои зоны интереса.
Релевантные какие-то вещи.
Релевантные.
Если ты говоришь про то, что ты устраиваешь
электроник-инженер,
ты говоришь про опыт электроник-инженер
как work experience,
у тебя возникнет вопрос,
на немаловажном уровне возникнет вопрос,
где ты был в конце этого года,
что в ЦСР...
Так и получается, да.
А ты такой смотри, в конце пишешь,
а вообще-то, ну то есть типа
additional information.
Вот эти годы я занимался вот этим, вот этим.
Чем ты занимался?
То есть не провоцировать вопросов, потому что
вопросы могут условно тебя по этой воронке
отодвинуть подальше от собеседования.
А постарайся сразу ответить.
В декрете был три года, почему нет?
Но я прочитал там 10 книг,
спаял 10 штук, написал 100 приложений.
Аналогичным образом, смотри,
ты пишешь, что ты machine learning engineer,
как work experience,
и additional information
про тебя как, знаешь,
achievement, какие-то достижения.
А сделал вот этот подпроект,
вот этот подпроект.
То есть где твои подпроекты?
Вот смотрите мой репозиторий.
Кстати, сразу, если мы говорим про собеседование
на email-инженера,
оставляй свой GitHub, пожалуйста.
Оставляй свою какую-то информацию, помните.
Дальше.
Даже если ты делаешь CV на две страницы,
очень нехорошо, когда у тебя вот здесь вот
название блока,
а блок сам на следующей странице.
Угу.
Ну то есть да, вот смотри,
our professional activities.
Да, согласен, да, да.
Вот, дальше.
Skills.
Skills в таком формате сейчас
сильно меньше интересует людей.
Потому что они такие, ну то есть,
окей, программирование и так далее, и так далее.
Тут скорее, опять же, смотри,
очень похожая история как с описанием.
Типа soft skills.
Там, я не знаю, пробуем solving.
Пробуем solving.
Покажи пример.
Пробуем solving.
Solving.
То есть, условно, пробуем solving.
Там, была такая ситуация, разрешил вот так.
Решил вот так.
Решил вот так.
Да.
Ну то есть, а программирование
machine learning, framework, tools,
ты можешь просто написать, просто через депутую.
То есть, вот здесь вот просто через депутую указал.
Опять же, чтобы у нас был какой-то характер.
А на soft skills очень важно.
Не просто перечислить, что значит teamwork.
Надо написать, работал в команде из трех человек.
Лидил там что-то.
То есть, это будет указать about me, что я не.
Не просто.
Ну и здесь уже вся информация.
То есть, about me ты пишешь.
Как раз таки раскрываешь свою soft skills,
в том числе часть того, как ты можешь себя презентовать.
И ты пишешь.
Я три года занимаюсь machine learning.
Работал в команде из трех человек.
Мог 10 проблем.
Увеличил ROI на 10%.
Ну то есть, вот about me.
Потом они идут раскрывать.
Это как ложный список.
Прочитали.
Уточнили.
Проверили.
Вот.
Ну и доски у вас сюда даже не доходят.
Угу.
Угу.
Так.
Карта фурсес.
Я, кстати, у карты тоже буду вести.
Они позвали меня в сети.
Угу.
Прикольно.
Класс.
Что будешь вести?
ПИ-шкам там.
Угу.
Вот.
Вот.
Которые будут.
Класс.
Так.
Карта фурсес.
Карта фурсес.
Класс.
Класс.
У меня есть линкедин.
У меня есть линкедин.
Но он такой, эээ...
Знаешь, я, я...
Из-за того, что я и электрикл инжинер, и машинливинг
инженер, не понятно, какую роль он сюда вставлять.
А вот.
Поэтому я пока что никуда это не вставляю.
Ха-ха-ха.
Ну смотри, будет, по-словно, и линкедин, и шум какую-то
историю очень хорошо подтверждать.
Ты говоришь сертификейт.
Угу.
Ты не просто говоришь, что ты сет...
Это ты, например, кидаешь ссылку на линкедин.
Ты сертификейт.
какую-то историю, очень хорошо подтверждать,
ты говоришь, сертификейт.
Ты не просто говоришь, что ты сертификейт.
Это ты, например, кидаешь ссылку на LinkedIn,
что ты сертификейт, потому что
какие-то сертификации тебя прямо
дают, ну, то есть дает у тебя прям напрямую
твой обучающий программный
обучающий программный. Да, правда, можно
так сделать, да.
Вот. Так, что еще,
что мне бросалось в глаза?
А, ну и, соответственно,
education.
Смотри, сколько строчек она у тебя занимает.
Я бы просто писала
университет,
специализация, опять же,
не меняем, да,
расположение местами,
и, ну, то есть
вот эти мастер-тезисы ты можешь
и выносить как
блог-эдикейшн.
Вот, условно, это как вот мастер-тезис,
можно вынести как отдельную информацию,
отдельную
активность, потому что твой бакалаврский
стипенд,
и твой магистрский диплом,
это твоя профессиональная
активность. Она не, ну, как бы,
она не работа в корпорации,
она у тебя история
про то, что ты профессионально
получил какие-то навыки.
Что это значит? Это значит, знаешь,
когда вот говорят, типа, что за дичь,
человек там
только вышел из университета,
а у него просто 3 плюс
рабочего опыта. У тебя
важный момент стоит учитывать, у тебя,
эти 3-4 года идут как за рабочий опыт.
Это правда.
Да, да, да.
Особенно, если ты идешь по профессии.
Если не по профессии, то там другие вопросы.
Но, если ты профессионально идешь в эту сторону,
то твоя бакалаврская и твоя
магистрская работа являются
как бы таким аплодисментом
того, чтобы ты к теме погружался
глубоко. Соответственно,
вот это мы выносим с тобой,
профессора, вот сюда.
Если у тебя есть какие-то публикуемые
статьи или твоя магистрская работа,
которая на сайте, ты вставляешь
в люку, это полезное
предупреждение, если ты сможешь
это найти. Обычно можно либо запросить,
либо найти.
И оттуда, условно,
вот это все умещаешь в 3 строчки.
Не больше.
Ну и здесь тоже смотри, как растянулось.
То есть твоя задача уместить
все в CV на 1 листочек.
В CV на 2 листочка?
В CV на 2 листочка.
Это CV, знаешь, не знаю.
Ну, типа 15-летнего инженера.
В смысле, с 15-летним стажем, да.
Да, давай я, как пример,
сейчас покажу тебе свое.
Последнее, что я делаю.
Я еще адаптирую
под каждую...
Под каждую позицию.
Да.
Так, ну вот, у меня как раз таки
звали музыкантку.
Честно скажу, у меня
на 2 страницы.
Ну,
они меня смотрят, чем они отвечают.
Дарья Леонкина,
контактная информация, где можно посмотреть.
Сразу выкликнуть.
Yeah.
То есть сразу всем,
то есть вот здесь вот
сразу написано, что
what do you mean,
medical,
ontologic, и так далее.
Какие мои сильные стороны?
Процессор,
selected impact, вот этот звук,
когда я...
Я прям показываю, что им конкретно может быть максимально
интересно.
Дальше.
Я когда работаю в рамках одной компании, то есть,
смотри, у меня здесь одна компания, но я занималась
разной позицией.
Да.
Соответственно, это влияет, что я сделала.
Elite Data Automation, что я сделала.
То есть, смотри.
Data columns, over data lake, team os and i agents.
Типа, какой вот тут, смотри, у нас сетап написан.
Ага.
780.
Все, люди это видят и такие, окей.
Дальше, меня как менеджера.
Build process from zero engine.
My own cleaning framework.
A team is laid.
Построено.
Fire.
Все.
Человек, когда читает или фишка, если это читает,
они понимают, что я умею строить процессы как менеджер
с нуля, нанимала и управляла людей.
Да.
Ну как?
Уже.
Вот.
И вот здесь one cell.
Моя история какая-то.
Мой проект, который я работала.
Два GIS.
Мой первый опыт.
Вот тут смотри.
Вот эта работа.
Это моя бакалаврская работа.
MML research.
Это у меня, соответственно, prediction для социологии и
генетики.
Вот.
Одна строчка.
Change data to presentation.
So.
Change data to presentation.
So.
Change data to presentation.
So.
Change data to presentation.
So.
Change data to presentation.
So.
Change data to presentation.
So.
Change data to presentation.
So.
Change data to presentation.
So.
Change data to presentation.
So.
Change data to presentation.
Chief inefficient.
Chief engineering.
Chief engineering.
So.
Change data.
So.
Change data to presentation.
Go to the more professional Philip's.
Go there.
Open your head.
And then there is when a guy says надо в тайной дороге
компанию .
В первом месте м Medicine project training desk,
я шли в м enroll as a producer,
therefore some on the starastre class.
He could not be Dr euces после дки.
The doctor had to ask he can play my lead like a
punch button.
He alwaysAbout help putες тут поднимал
грудь performers,
как вы знаете какой-то в наkopиempрессе
передавал.
Итого смотри, одна страница, что я пишу, ну то есть одна
страница это фокус, моя задача фокусировать на
одной странице.
Дальше, скорее всего, если никто не идет, и хорошо,
потому что дальше нету сильно важной информации,
потому что дальше опишем информацию от меня, teaching
writing speaking, дальше, data governance expertise, потому что
у меня просили об этом, то есть смотри, я здесь
корс, ну как бы скиллы раскрываю не с точки зрения,
не только с точки зрения перечисления, а с точки
зрения конкретности, что мы, что я делаю.
Корс скилл, соответственно, вот такие, просто перечислено,
то есть опять же leadership and delivery, и я не просто говорю,
что то есть development я перечисляю, LLM продакшн я перечисляю,
а на тейшн это появляется, то у меня просили я перечислять,
дальше.
Смотри, корс скилл, здесь просто про софт скиллы,
я указываю только leadership и delivery, building teams and process from scratch,
hiring, growing up to 35 people, SLA, OKR, planning, crisis management,
shipping without specs, то есть я могу, то есть shipping without
specs, умение работать в высокой степени неопределенности,
не то, что ты попросишь умереть.
А вот если ты, например, я сделал свой проект, сам поставил
требования, добил диалектику, вот ваш, shipping without specs,
shipping without specs, land language, education, а может, пожалуйста,
скинуть мне свое резюме?
Конечно.
Спасибо.
Да, это очень полезно, спасибо огромное.
Очень.
Хорошо, попробуй, мы с тобой посмотрим и посетим кому-нибудь
из знакомых в твоей истории.
Угу.
Дальше.
Дальше.
Дальше.
Дальше.
Погнали.
Так, у меня что-то компьютер начало, сейчас, секунду,
я думаю, где-то какая-то работа, сейчас, одну минутку,
немного, чуть-чуть, то, правильно, нашел, перегрев.
Угу.
Сейчас.
Дальше.
Угу.
Угу.
Угу.
Угу.
Угу.
Угу.
Угу.
Угу.
Угу.
Угу.
Угу.
Угу.
Угу.
Угу.
Угу.
Угу.
Угу.
Хороший предложение.
Ага.
А что это соmutка?
Я прод LogicE
Выбрали с тобой метрику для PluslineIU для картинок
confused на канале нет
АЮ для картинок.
Здесь мы с тобой, соответственно, можем выбрать
ведемое. Мы просто должны
определиться с одной методикой, но
однишно считать АЮ,
чтобы проанализировать,
что происходило, не будет
бесполезно. Это дополнительная
информация.
Согласен.
Как это?
Это у нас есть уже различные данные.
Окей.
Чтобы проверить видео-вызнание,
мы включим пространство A-Way, где действие
началось и закончилось.
Пока не сделано.
Нет?
Так, вот это вот я уже сделал.
Этот вопрос очень актуален.
Я успел за это время.
А скажи, пожалуйста, как ты его получил?
Я делал все в
Label Studio,
где просто проставляешь интервалы.
Каждый интервал — это один лейбл.
Типа not plain и plain.
У меня был еще один
лейбл, где
непонятно,
то есть, я, например, вышел из кадра,
но музыка играет.
Я там писал так, как
ambiguous,
но, по сути, это тоже not plain.
Это not plain.
У тебя нет в кадре.
Да.
По сути, оно считалось как not plain.
Да.
Я...
Давай в комментариях скажу,
пока мы не ушли далеко, что считаю важным.
Смотри.
Когда мы ведем...
Какую-либо разметку данных,
мы с тобой стараемся максимально отказаться
от ambiguous классов.
Почему?
Потому что, когда у нас есть
это эксперимент, и большим количеством экспериментов
предпринято,
сама на практике медицины не видела.
Когда у нас с тобой есть ambiguous классы,
то размечки, то есть, одно дело ты размечаешь,
а другое дело, когда ты пытаешься на crowdsourcing,
это деликировать, когда ты работаешь в компании,
ты будешь деликировать это на outsourcing.
Скорее всего,
все будут заваливать класс в ambiguous.
То есть, даст какая-то детерминированность.
То есть, по сути, у тебя класс ambiguous,
он будет мусорным просто.
То есть, он тебе не даст никакого результата.
Да, пожалуй, да.
Это большая проблема.
Да.
Согласен.
Из-за того, что это большая проблема,
из-за того, что он тебе не даст результата,
ты здесь...
Здесь не достанешь никакой информации,
но потратишь в тюремные деньги.
На самом деле, у меня метрики даже упали,
потому что он определил это как not playing,
вот, и у меня...
И не спрашивает у тебя ambiguous.
То есть, мы стараемся максимально,
если мы можем описать максимально подробно,
каким образом мы развиваем классы,
то есть, что присутствует, что отсутствует,
мы это делаем.
Да.
Никакого индексу отсутствовать не должно.
Да.
Хорошо, всё разумеется.
Дальше.
Дальше я прогнал три модели, которые сначала мне предложила,
предложил кодекс.
Что за модель?
Что за модель?
Сейчас.
Так.
Одна из них...
Помпа Мае.
Видео Мае.
Вторая TimesFormer.
И Vivid.
Вот.
Они все, насколько я понял,
работают примерно точно так же, как и Видео Мае.
Вот.
Видимо, у них там какая-то другая модель.
Другая архитектура.
Я не разбирался, потому что
в итоге оказалось, что Видео Мае
оно
по всем параметрам очень сильно
бьёт остальные две модели.
Вот.
И сначала у меня получилось
с Видео Мае
где-то
94% пресижена, 84% рекола.
Вот.
Так.
Так.
Да.
Какая выборка, на которую ты считал
пресиженный рекол?
Что, ещё раз?
Выборка, выборка, количество выборки, когда ты считал.
Сколько ты считал пресиженных рекол?
Это было три видео,
которые я, собственно,
на которых я оценивал эти модели.
Сколько?
Каждое видео по 4 минуты.
Там где-то
в каждом видео по 6000 с чем-то фреймов.
Вот.
Да.
И после этого
Кодекс мне предложил сделать смутинг.
Сглаживание.
То есть, когда у нас идёт,
например,
оно
один интервал двухсекундный определил как
playing.
Точнее там
пять интервалов как playing.
Потом один маленький интервал как not playing.
Потом опять пять интервалов как playing.
И получается он ошибся между ними.
И это с большой вероятностью просто ошибка.
Вот.
И мы
сглаживаем здесь.
И это очень сильно подняло рекол.
Вот.
Какой параметр сглаживания ты взял?
Ну да.
Извините.
Мне кажется,
я тут слишком навайпкодил,
чтобы тебе ответить на этот вопрос.
Хорошо.
Я сейчас его добавлю.
А, сейчас.
Быстро скажу.
Помнишь, мы с тобой обсуждали,
что когда мы считаем IUU,
мы строим по всем IUU,
по всей выборке,
распределение данных.
То есть,
на каждое балконное распределение,
чтобы выбрать,
какое взять,
среднее, медиальное.
То есть,
по распределению
какое выбрать.
То есть,
по распределению
какой выбрать.
По распределению
какое взять,
значение.
Да.
Соответственно,
меня интересует,
то есть,
что является,
чем является смурфинг-параметр?
Он не смурфинг-параметр.
Он является у нас,
по сути,
гиперпараметром
оптимизации
результата
отработки.
Да.
Да.
Что ты знаешь
про гиперпараметры?
Ну,
это некоторые параметры,
которые мы можем
крутить.
Уже
уже
уже
мы
уже
уже
после
уже
того,
как модель обучена
и мы можем
ну,
как бы,
в некоторых случаях
это может помочь
увеличить
улучшить метрики.
Смотри.
Когда
мы работаем
с гиперпараметрами,
я не помню уже,
как называют
методы,
но у нас есть
встроенные
методы
оптимизации
гиперпараметров.
То есть,
мы выбираем
какую-то модель.
Габари,
я уже не помню,
что это такое.
А,
я тебе объясню методику.
То есть,
что происходит?
Есть несколько разных
подходов
выбора
оптимальных
гиперпараметров.
Например,
метаглотя.
Знаешь,
что это такое?
Метаглотя.
Нет,
мне кажется,
не слышал.
У нас
есть
распределение
метрики.
И когда
она у нас
выходит
на какую-то
плату,
граничное
значение
в анализе,
когда мы распределили
и посчитали,
есть метод локтя.
И аналогичные
способы
есть в методах
машинного обучения,
в том числе
в биклёрках.
Ну,
то есть,
отчёт,
босс,
метрика и т.д.
это уже
оптимизация
гиперпараметров.
Тоже есть.
Смотри.
Здесь
есть немножко
попроще,
чем
по вычислению
ловкого смутника.
То есть,
смотри.
Смут-параметр
работает
под ним
модель.
Да.
Просто взять
05 или 03,
то есть,
мы всегда
держим
за правила.
Недостаточно
просто взять
какой-то
параметр
числовой,
получить
результаты
и взять
его
как бы
заистить.
Ну,
конечно.
Это может
быть
не самый
лучший
выбор.
Конечно.
Соответственно,
у нас
есть
модель
берет
твою
тестовую
выборку,
меняет
гиперпараметры
перебором,
подставляет
их,
считает
финальные
метрики
и сравнивает
по
этой
финальной
метрики.
Ага.
Я тебе
сейчас
прямо сейчас
скину,
пока я
не забыла.
Гиперпараметрический
поле.
Это
базовый
рандомай
сердж.
Сейчас
я
расшарю.
То есть
вот
про что
идет
китч.
Вот.
То есть
у нас
скиллер
когда мы
изучаем
какую-то
модель,
например,
рандом
хорост,
мы
загружаем
рандом
хорост
грит
сердж,
и дальше
он
изгибается
в параметр
и
в
параметр
охожает.
Аналогичная
история
рандомай
сердж,
он
по-разному
как
всей
этой
расницы
смотрится.
Посмотрим,
пожалуйста,
есть
разные
подходы.
Прочитай сначала
эту
статью
с библиотекой.
Скорее всего
за основу
так секундочку после smooth параметра я не успел сделать то что хотели хотя посмотреть
вот у нас прошел этот smooth параметр улучшились немножко метрики и я хотел
дальше посмотреть на кадры да вот он не показывает в каких кадрах он ошибся я
хотел посмотреть конкретно какие кадры в которых он ошибается и посмотреть могу ли
я что-то с этим сделать здесь
хорошо
давай я дальше чуть-чуть
хорошо
давай я дальше чуть-чуть
ну ты имеешь ввиду если именно случай я сижу спиной я не играю
нет нужно это я тебе пример привела
надо посмотреть надо посмотреть какие там условия ну то есть в какой момент времени ошибается модель что происходит когда она ошибается
это я положила возможность ты спиной мимо проходишь гитарой и что-то происходит
да
считайте просто нахождение гитары по непосредственной действии
да
хорошо
важный момент еще еще новые отличные вопросы
так'm я off
еще вопрос
вопрос
большего хода гордить вот frost
забьет
заказать вот Probist Kentucky
это такой вызов я смотрела лент на сегодня там возле нашей
То есть у тебя есть там в излайне скидка, то есть смотри, здесь тоже комментарий.
Project ND читаем и так далее, и так далее. Здесь подходит, require checks, output format.
Нужно предоставить здесь до output формата, соответственно, eval параметры.
Знаешь, что такое eval параметры?
Ну, по названию evaluation, как мы оцениваем те модели, которые мы нашли?
Да, смотри, мы с тобой с evaluation сталкиваемся с классическим машинным обучением,
когда делаем evaluation каких-то методов, что мы делаем с большими языковыми моделями.
С большими языковыми моделями тоже можно делать evaluation.
Ага.
В связи с этим, если мы делаем evaluation,
с большими языковыми моделями, мы должны сделать, описать, как именно мы делаем этот evaluation.
Если ты выбрал, ну, типа, если мы работаем с проектом видеоналитики,
ты считаешь какую-то метрику, смотришь какие-то данные,
то есть прям последовательность того, что должно произойти, чтобы был какой-то эбак.
Сейчас главное, безусловно, опираться на метрики того, что трудно и наибольшую часть положительных классов,
ну, это не корректно.
Конечно, да.
Это не корректно.
Потому что здесь нужно провести эксперимент.
Тебе ради интереса как образовательная история.
Что можно сделать?
Ты можешь записать видео, где ты не играешь, в большом количестве,
снова программировать в Wi-Fi и посмотреть, какую модель, ну, типа, версию выберет модель.
То есть, что я тебе предлагаю?
Я тебе предлагаю собрать обучающую, ну, не обучающую, собрать тестовую выборку.
Большой количеством положительных классов, большой количеством ответящих классов, ну, то есть просто playing point.
Вот.
Дальше ты прогоняешь выслайм на каждой из версий, текущей свой.
Смотришь, какая образовательная модель.
Скорее всего, полтора.
А может, ты, наверное, не знаешь.
Да.
А дальше вставляешь skill, evaluation part.
И по ней смотришь.
Объективно, то есть мы опять же возвращаемся в то, с чего мы с тобой начинали общаться в TNFC.
Невозможно будет выслайм без метрики.
Если нет, значит, какая-то хуйня.
Да.
Да, я сейчас понял, что я, на самом деле, сейчас провел вот эти три модели, которые уже были выбраны.
Вот, он нашел их, но нашел, он как-то выбрал их как-то по-своему, да?
По факту надо было вот сразу по метрикам.
Да.
Мы никогда не доверяли модели.
То есть мы живем в парадигме на любой гипотезе.
Да.
Что если модель берет?
Что если модель дала неправильный ответ?
И относительно этого мы придумываем...
Мы не то, что отказываемся от работы с большими языковыми моделями.
Нет, нет, нет.
Мы придумываем способ, как проверить результаты больших языковых моделей.
Да.
Да.
Окей.
Так.
Вот, ты, Миша, не заставляешь.
У меня вообще он на автомобиле всегда.
На автомобиле.
Но у меня очень подробно описаны факты.
Ага.
Понятно.
Для каждого чиха.
Для каждого чиха.
В какой момент времени какая используется модель.
Какие права.
Какие нервные расширения.
А можно...
Можешь со мной поделиться?
Или...
Пару с тобой не поделюсь.
Я поделюсь с тобой материалами.
Да.
Потому что, как бы, я...
То, что я, например, смотрел у...
У Клода.
Как бы на их сайте.
Там как бы не все написано.
Вот.
И, я так понимаю, каждый инженер, каждый разработчик, он еще свои, как бы, цифры не
написал.
Да.
Да.
Да.
Да.
Да.
Да.
Да.
Да.
Да.
Да.
Да.
Да.
Да.
Да.
Да.
Я понимаю, что, знаете, что-то они, например, какие-то штучки используют.
Конечно.
То есть, смотри.
Ты смотрел контратрика Официальные курсы популярных
situated?
Да-а-а.
Да.
Я смотрел.
Он Staatsabild.
Зум быстренько закончится.
Так, мне нужно...
Юмитинг...
Тут сверкит edge controlы.
provide...
Да.
Я согласен.
Ну, типа, наверное, углубить там перейти просто всё.
Ну да.
Вот, у скиллов есть прописанные теги Allo Instruments.
Да.
Соответственно, эти Allo Instruments ты можешь использовать как настройки перемещения.
Хорошо, смотри.
Сейчас я свои метки смотрю.
Понимаешь ли ты, чем отличается детекция на видео от детекция на фото?
То есть, в чём тут таймлайн?
То есть, какие основные у нас принципы детекции?
Там и там.
То есть, в чём отличие главное?
Ну, если говорить о тех бейзлайнах, которые я использую сейчас для фото и для видео,
то в первом случае я...
Модель детектирует объекты,
и, собственно,
мы рисуем боксы, когда вот один объект, во второй объект.
А во втором случае модель, она анализирует отрезок видео,
там длиной 2 или 2,5 секунды,
и она детектирует actions, то есть действия, которые происходят на видео.
Вот.
Это как бы не объекты, а вот именно...
Я не заглядывал в архитектуру, я не знаю, как она это делает, да,
но вот то, что я знаю, она может раздавать классы отрезком видео.
Она может детектировать...
Действия на этом видео.
Понять здесь чуть уточню тебе, и ты запомнишь это, пожалуйста,
потому что это могут спросить в собеседовании.
То есть, в чём главная отличие фотографии от видео?
Фотография — это детекция кадров,
видео — это детекция кадров в привязке к оси времени.
То есть, если у тебя в детекции фото ось Y и ось X,
и ты определяешь положение,
соответственно, это объект,
то тут у тебя появляются ещё две оси — X, Y, Z.
То есть, где ты находишься, в какой момент времени.
Это всегда стоит учитывать,
что детекция на фото и на видео отличается только таймлайном.
И у тебя просто появляется дополнительная ось времени.
Дальше.
То, о чём ты говоришь.
У тебя... Ты смотри.
С чем ты уже столкнулся.
С чем ты уже столкнулся.
Вот как раз и к смокинг-параметрам.
Когда мы работаем с видео, у нас есть несколько вариантов.
Первое — просто детекция.
То есть, в каждый момент времени мы на кадре детектируем, что происходит.
А есть трекинг.
Трекинг — это когда мы смотрим текущий кадр, следующий кадр,
и смотрим, изменилось ли необходимое положение человека
относительно того, что происходит.
То есть по сути, теймлайн есть у нас, но мы смотрим связь.
Если, как бы условно...
Боже, как я не люблю рисовать в графике на пальцах.
Если мы говорим про XYZ алфавит,
для этого не
говорим про трекинг, то это прямая.
То есть, это линия.
Угу.
А когда мы говорим про точку и про линию, мы как бы имеем в виду центр массы вот этого бокса или что?
Класс. Класс обнаруживания.
Про класс. Класс человека.
XY, соответственно, его положение в пространстве.
Z, его положение в пространственном времени.
1, 2, 3, 4, точка.
Если говорим про трекинг. Класс делится какой-то день.
Соответственно, когда ты говоришь, что ты делаешь смуфинг, и там у тебя 5 секунд, 5 секунд, 1 секунда, вот у тебя пошел трекинг.
1, 2, 3, 4, 5.
Хочу. Что хочу тебе предложить.
Я бы хотела.
Я бы хотела.
Чтобы ты к следующей встрече сделал, протестировал модели детекции и модели трекинга.
Потому что сейчас он предложил логичный тебе пейплайн.
Вопросов нет.
Вопросов нет.
Все ок.
Все ок.
Да.
Но.
Да.
Чтобы ты просто понимал, что есть детекция, есть трекинг.
Зачастую, смотри, трекинг нам нужен в данном случае.
Потому что мы хотим знать, как долго ты играл.
Детекция может понадобиться в каких-нибудь задачах.
Не знаю.
А вот я у тебя спрошу.
В каких задачах?
Я придумала кейс по сферстройке.
В каких задачах может пригодиться детекция?
В производственных.
В каких-нибудь случаях, когда ты работаешь на работе.
Вообще, первый случай детекции, это не производство, но в целом, которое пришло в голову, это распознавание лиц.
То есть, тебе особо там не нужно отслеживать передвижение.
Тебе нужно просто увидеть лицо.
Вот.
Один объект.
Наличное.
Наличное.
Ну, то есть, это условно на камерах.
Да.
То есть, человек идет.
Оп, он здесь был.
Оп, он здесь был.
Да.
В производстве есть.
Почему она заземляет в производственных кейсах?
Потому что, ну, то есть, где...
Чаще всего, где используется детекция, часто, и она используется в заводах.
Если у тебя произошел какой-то инцидент, уяксен у тебя в секунду.
Ну, да.
Тебе нужно брак отследить, например, какой-то.
Вот.
После этого процесса произошел брак.
Да.
Что надо понимать.
Что надо понимать.
Вот тут тоже сравни по вычислительным мощностям детекцию и трекинг.
Детекция у тебя будет висеть всегда на меньшей части трекинга.
Ну, да.
Конечно.
Детекция быстро решает вопрос твой бизнесовый.
Да.
Трекинг.
Да.
Да.
Хорошо.
Хорошо.
Дальше.
Дальше.
Да.
То есть, итого.
Попробуй детекцию.
Попробуй.
Мы с тобой решили сделать.
Историю с трекингом.
Что еще?
У тебя есть видео.
Мы с тобой обсудили.
Давайте, Вар.
Позитивный и негативный класс.
Позитивный и негативный класс.
Сравнений.
Пэйплайнов.
Пэйплайнов.
Да.
Идет детекция.
Детекция.
Сравнений.
Ага.
То есть, в первом шаге ты улучшаешь стиль.
Ты улучшаешь стиль.
И убираешь модель.
Методики выбираешь.
Методики выбираешь.
Ага.
И третий этап.
Третий этап.
И третий этап – визуализация.
Пожалуйста, дашборд.
Сколько времени, какая метрика, сколько времени ты проходишь.
И давай посмотрим возможности твоей камеры работать постоянно и интегрировать туда модель.
Сейчас я объясню, почему.
Зачастую, мы с тобой, когда работаем с CV-моделем и видеомоделем,
мы ограничиваемся не только частью, связанной с тем, насколько качественно мы что-то распознаем,
а мы ограничиваемся вычислительными мощностями.
Так, во многих камерах, то есть мы загружаем модель,
и смотри, нам в том случае можно расправлять, записываясь везде,
мы отправляем на А, пишем, читаем, читаем, читаем, читаем, читаем, читаем.
Но бывают ситуации, когда тебе нужно в момент что-то задетектировать или узнать.
В соответствии, такой соц. интегрируется прямо в камеру.
Соответственно, я хочу увидеть здесь.
Распределение.
Сравнение моделей, которые могут работать в пул и как быстро.
То есть твоя задача замерить время реинференса.
В том числе, у нас появляется новый метрик.
Первый метрик, который нам нужен в работе.
И только ту метрику, которую хорошо будут указать в своем CV,
типа не просто.
Она училась детектировать в своем бэд-проекте, достиг такой-то АЮ,
и ускорила работу модели в два раза.
И дашборд.
Давай посмотрим.
Вопросы.
Вот к последнему.
К последнему.
То есть мне нужно просто проверить обе бейсблайн модели,
на то, как они работают.
С CPU и с GPU.
Да.
Хорошо.
И посмотреть, какой вариант подойдет.
Какой вариант подойдет.
Какой случай.
Когда нам нужно afterwards расчет.
Или когда вот прямо сейчас.
Да.
Угу.
Так.
Хорошо.
По поводу поиска.
То есть я переделаю скилл, вот, чтобы он у меня работал так, чтобы я модель, кодекс выбирал модель в зависимости от расчитанных метрик.
То есть, как, можешь описать, как это будет происходить?
Я не очень догоняю.
Это должно, он должен просто, как это сформулировать-то?
Можешь еще раз повторить, что должно быть в скилле, чтобы скилл работал правильно?
Он у тебя работает правильно.
Да.
Смотри.
Наша задача сейчас с тобой сделать какой-то эволюэйшн.
Да.
Чтобы понять, кому нужен эволюэйшн, нам нужно проверить работу качества этого скилла.
То есть мы ставим гипотезу.
Он говорит.
Я говорю, что вот эта модель хорошая.
А там что?
Что там больше всего позитивных классов?
Мы такие, не приноси, а если там меньше?
Ну, то есть, а если я, на самом деле, на видео было больше других классов?
Или вообще, а как ты работаешь с негативными классами?
Мы ставим гипотезу.
Записываем данные на превалирование позитивных классов, на превалирование негативных классов.
Запускаем скилл, который есть.
Смотрим, одинаковые результаты или не одинаковые результаты.
Угу.
Если не одинаковые,
Какие у него аргументы?
Далее.
Нам с тобой нужно сказать, если ты смотрите.
Мы с тобой, когда работали с картинками, мы с тобой выбирали метрику .
Да.
Вот в видео у нас можно выбрать точно такую же метрику.
То есть, если ты работаешь, abilities.
Если если ты выбираешь.
Для компании.
хорошо но это я буду делать уже на выбранных кодекса моделях вот этих трех
или он должен найти как бы заново искать модели и сравнивать их или как
качественный результат
статистик
хорошо хорошо
наверное у меня пока что все
что мне делать к следующему разу я знаю нужно ли мне
да он сейчас пишется
спасибо да и уже на следующем занятии мы решим что я буду делать вот пока у нас не будет встреч
видимо там нужно будет за большой какой-то план составить
давай так подумай
прям
нет
еще
будет
ластすごい
какое-то
благо
спасибо такая
класс спасибо reduction
спасибо
не забудь об этом
не забудьте Bedizel.com
Не забудьте композировать задачу, если будешь писать план.
Это важно.
Хорошо. Обязательно.
Всё.
Да, спасибо.
Хорошо.
Давай, хорошего вечера тебе.
Хорошего. Пока-пока.
Пока-пока.
