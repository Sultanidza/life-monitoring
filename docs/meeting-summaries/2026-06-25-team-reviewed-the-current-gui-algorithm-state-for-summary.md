# Project technical review

- Transcription model: `faster-whisper/large-v3`
- Summarization model: `gpt-5-mini`

_Mentor / coaching_

Jun 25, 2026 · 17:29 · summarized · 12 captured items

## Overview

_Team reviewed the current GUI/algorithm state for pigment identification, discussed metrics/visualisation, data saving format, and dependencies on server/data. Assignments: Артур to investigate cosine-distance vs feature-based approaches; Сережа to finish work toward production. Plan to share a demo and schedule a meeting with chemists._

The meeting focused on the pigment-identification tool: UI, how results and metrics are shown, how items from the database map to displayed descriptions, and how mixtures are reported. Participants discussed removing per-coefficient pixel coefficients and combining them into a single 'Similarity' metric (speaker: "я"). There is a test-mode UI that currently shows checkboxes for name matches; those checkboxes and some visual elements will be removed in the final program. The team decided (for now) to save results as a CSV table for chemists to process further.

There is uncertainty about how the algorithm handles spectra that are mixtures: currently the system searches for pigments one-by-one and reports single matches, but mixtures may correspond to multiple pigments and the mapping between a measured spectrum and multiple database samples is unclear. The transcript shows confusion about identification of mixtures and how description entries should be combined when multiple pigments are present.

Metrics and visualization issues were discussed: some non-matching items are highlighted in grey or orange; the team wants different triangle colors or other visual cues to make matches clearer. The speaker plans to combine pixel coefficients into one Similarity metric and to refine the metric further.

On algorithmic approach, a suggestion was made to first identify features and then compute cosine distance in feature space, rather than applying raw cosine distance between whole images; also the idea of using a neural network that first extracts features and then compares them was raised (reference to reading a Google approach). Артур was explicitly asked to look into the cosine-distance/feature-extraction approach and how to modify the algorithm.

Data and infrastructure: the project needs large data downloads (mentioned: "все два миллиона картинок"). A server is currently not available and that blocks main work; as a temporary measure someone can upload data to Google Drive. The transcript contains plans to get data or have IT make it available so metrics and images can be pulled and the second paper ("второй статье") can be finished. There is an instruction that Сережа should finish development toward production ("Сережа должен доделать все... в продакшн").

Next coordination items mentioned: send a demo, schedule a meeting with the chemists next week, post a couple of screenshots in chat showing what changed, and prepare a production tab earlier than Thursday so chemists can test it.

Other personnel/coordination notes: Денис, Питер, Игорь, and Энджи were mentioned in connection with server/data and paper submission responsibilities, but specific assigned tasks for them are unclear or unresolved in the transcript.

## Mentor Review

_Project-focused_

### Project State

- There is an existing database of pigments and a color-markup/annotation (sample color) in the markup; color info is present but currently not used in the algorithm.
- A GUI exists (test-mode) showing identification results with checkboxes and visual highlights; some UI elements will be removed in final program.
- Current implementation returns identified pigment(s) in a description table; behavior with mixtures is unclear (algorithm seems to search pigments one-by-one).
- Intermediate metrics/coefficient pixels exist and will be merged into a single 'Similarity' metric.
- Results are currently saved (or will be saved) as CSV for chemists' use in test mode.
- No dedicated server is currently available for large dataset download; Google Drive was proposed as a temporary solution.

### Changed Since Last Meeting

- A test-mode UI exists and currently shows identification results with checkboxes; speaker modified UI to show certain features for testing.
- Temporary CSV save mechanism was implemented/decided to allow chemists to receive results for now.
- Plans to combine pixel coefficients into a single Similarity metric were created (work to be performed).

### Blockers

- Lack of a server and accessible data (the two-million-image dataset) is pausing major parts of the project.
- Unclear algorithm behavior for mixtures versus single pigment identification — needs clarification and possibly algorithm change.
- Metrics/visualization are not tuned: mismatches between metric results and visual indicators exist (triangles/colors need adjustment).
- Ownership/responsibility for making data available and coordinating downloads is not clearly assigned in the meeting.

### Mentor Feedback

- Combine per-pixel coefficients into one similarity metric and refine that metric (speaker: "я").
- Before applying cosine distance between full images, first identify features and then compute cosine distance in feature space; consider a neural network that extracts features before comparison (a referenced Google approach may be relevant).
- Create both a debug/demo build and a production build to show functionality and provide a stable release.

### Before Next Meeting

- Serежа: move the current work toward a production-ready build (not just final demos); success = production tab available earlier than Thursday for testing (explicit timing to be clarified).
- Артур: investigate cosine-distance vs feature-based (and possible neural-net) approaches and report back with recommended approach and references.
- Provide a demo and schedule the chemists meeting for next week; success = meeting scheduled and demo sent.
- Post screenshots in chat showing UI/metric changes before the next review.
- Obtain or arrange access to the full dataset/metrics (server or Google Drive) so algorithm improvements can be tested on real data.

### Artifacts To Prepare

- Demo build of the tool (for showing to chemists).
- A couple of screenshots showing UI/metric changes (post in chat).
- CSV export of results (test-mode output) to share with chemists.
- Plan or notes on cosine-distance vs feature-extraction approach (references / short recommendation from Артур).
- Access to metrics and image data (or a link to Google Drive with the dataset) for development and paper work.

### Action Items By Person

**Артур**

- Task: Investigate cosine-distance approach and feature-extraction / neural-net alternative; Context: determine whether to compute cosine distance on raw images or on extracted features and read relevant references (mention of Google approach); Due: unknown; Priority: unknown

**Сережа**

- Task: Finish development and deliver a production-ready build; Context: complete interface and algorithm work and move towards prod ("Сережа должен доделать все... в продакшн"); Due: unknown; Priority: unknown

### Decisions

- Save algorithm results as a CSV table in the short term (test-mode agreed).
- Combine multiple per-pixel coefficients into a single metric named 'Similarity' (speaker: "я").
- Produce two builds: one debug version to show that it works and one production-ready version.

### Open Questions

- Who will own making the server/data available (specific IT owner not confirmed)?
- Will color/sample labeling ("sample color") from the markup be used in test/production runs? Transcript: color info exists in markup but is currently not used.
- How exactly should mixtures be represented in 'description' when multiple pigments are found for a spectrum (the current behavior finds pigments one-by-one and reporting multiple pigments into description is unclear)?
- Which precise algorithm is currently implemented under the GUI (the team needs to confirm what algorithm the code executes)?
- What metric tuning is required to make 'matches' and 'first metric' align better (triangles/visual cues and metric weighting need specification)?
- Who will send the demo and who schedules the chemists meeting (speaker said "я пошлю демку", but owner not explicitly named)?
- Who will post the required screenshots in chat to show changes?
- What exact dataset download workflow will be used for the ~two million images (server vs Google Drive) and who performs the download?
- What is the exact deadline for Сережа to provide the production-ready build?

### Transcript

как бы не выбранные другим цветом подсвечивать так они подсвечивают серый не на диаграмме а
даже это я думаю да то что но самым последним оранжевый ну тут так не
которые которые уже как бы совпали да да да значит первое второе сейчас соображу и а вот
их название это п.п. это вот из базы они называются вот так да
и галочки если они совпадают с названиями которые у тебя в дискрипшн ну да в реальном
программке этого не будет сейчас для теста я оставил окей но ключевая вещь тогда вот
этого не будет и вот этих галочек тоже не будет ну тогда нужно понять что за чё под капотом и
и
что за метрике и в мануале палпы к этой хреновине вам больше означает такое или под
знаком вопроса нажал получилось да да конечно это гуд вроде бы ну и для тебя ты должен блин
понимать чьеечь неронку тебя сделала да да да я теперь исперпел разобраться то есть а уберу эти
коэффициенты пикс
я их объединю в какую-нибудь одну просто метрику в Similarity, и над самой метрикой еще поработаю.
Не, но надо понимать, что за алгоритм у тебя реализует этот код, потому что я думаю, если честно,
что у тебя твой алгоритм завернут в GUI, а у тебя некий алгоритм.
Да, да, да, я знаю, я просто еще не успел, говорю, уже с этим разобраться до конца.
Угу, так. Дальше. У тебя длины волны...
Название этого, и ты куда-то можешь засейвить состав, да? В чего, в какой файл?
Ну вот как это там, accept там, и в каких файлах?
Accessмал аксэпт, грубо говоря, да.
Accept, там.. accept, вон там, save.
Chalupak gateau?
цсв в чем в цсв почему не в цсв каком виде в каком виде скажет такому будет как бы это
договорюсь химиками каком виде сохранять результаты да ага как бы я у них просто
уточнил я пока что хоть как-то сохраню дальше пускай хотят вырабатывать это будет табличка
цсв да да да ну хорошо совпадаем не совпадаем ключевой вопрос ну как и было раньше то что там
первые пики там хорошо совпадает да в целом как бы вот галочки и часто встречаются нет
галочки то встречаются но значит первый в топ там 10 пигментов которые находят он попадает
и
да значит свою задачку вы грубо говоря решаем те нужно какой-нибудь ответ что
твой алгоритм работает в стальки тот лучик и стальки то или ну да просто я все еще не до
конца могу сопоставить то что там есть это что есть базе данных чтобы ты понимал давай
сейчас я
остановить то есть как бы что у меня есть давайте покажу у меня есть база данных у меня есть вот
собственно говоря как видит выглядит разметка да то есть вот есть идентификация и как бы вот
и вот с этим работаю здесь вообще как бы есть три разных варианта да как бы как минимум причем не
и
да вот это вот просто это название пигментов да и это там description мне нравится да да да но
description это цвета до 0 до пигменты пигменты пигменты окей а используется люди от световая
где-то информация что у тебя желтый желтый желтый не желтый пока нет у нас эта информация есть но
она есть в разметке повторюсь вот она вот вот вот в разметке есть сэмпл color есть сейчас это
тестовый или это что это у нас просто это у нас это разметка
цветовая разметка краски да вы мне дали образцы разметки она есть да и как бы семья будет делать
перед подачей в алгоритм то я могу как бы то есть тебе бы должны говорить зеленый или фотку
прикладывать что-нибудь ну пока информация никак не учитывается короче она есть она есть сейчас я
не знаю будет ли ее делать при тестов
в тестовом режиме в боевом да вообще должны потому что мы иначе один из инструментов теряем
тогда мне должны как бы пускай они мне предоставляют информацию в каком-то виде
давайте договоримся каком виде это сейчас блин у нас есть три правильно понимаю
этой формы а записана то ли что то на Kristandia любая версия анализifer
многолетний образца выздоровлеющего процесса
reasonable у нас есть бакамetic Ender
это вот так вот хасид если у васiency почему если у вас‌то denk сиял fis они
начинают работает так вы тут бить но вот тем не менее поэтому на вас eyesight
четырем 15 3 или пигмент yellow ну как вот смотрю тебе одному роман спектра нет
название да у тебя одному роман спектра соответствует несколько не фигей шинов
так но скорее они не знают какой из них они настолько одинаковы чтобы ответа
правильно высвечивается у тебя один у меня конечно один однозначное
соответствие делать нет не имеется ввиду смотри вот у тебя длина вам как все
работает вот длина волны вот из длины волны ты получаешь что это
а д 63 например 55 и blue green spot без ты был алгоритм вот это не фиксирует так
эта смесь до
а значит и он говорит у тебя вот этот
пигмент и чем пишет вот открой теперь вы свой вот вот description results это
это что из этой таблички это пигменты вот это айдентификация но он пишет тебя
один
по одному да мы ищем по одному пигменту так правильно но смотри я не понимаю ничего у тебя
этот спектр может соответствовать одному количеству пигментов так это смесь этих
пигментов то мы находим их по одному нашли в начале это точно здесь есть ищем еще чуть в
этой смеси нашли то что здесь тайтани у вайт летим елау и там я не знаю но у description добавили их
все три все нашли нашу смесь смесь состоит из тайтани у вайт летим елау и но description
наверное блин у меня что-то это сегодня меня я глупый слишком сегодня всякой фигней замучили
поэтому соображаю медленно а значит вот это вот табличка эта табличка чего эта табличка образцов
которые образцы романсе одно и то же нет нет нет вот арт discovery которая это вот это да это то
что у тебя пигменты это образцы с их цветом образцы смеси смеси понял и ленты то есть вот
рамын спектра это вот то что у тебя справа сейчас в табличке нет вот и слева вот эти
схема слева из-за не слева в табличке это средняя колонка да окей а значит открой пожалуйста еще раз
до
значит у нее у нее есть спектрография вот а почему значит какая-то вот а.д. и а.д. там что-то там с
02 она состоит из вот этих раз два три 4 пигмента нифига и эти четыре индификация выводится у тебя
ну не они а то что мы алгоритм предлагает нет а выше вот где то что сейчас есть а потом этого не
будет а вот эти коллеги нас осталось это как-то мы хотим да мы хотят я хочу вот это понять как
работает и мы хотим понять что мы делаем с
с этим
с задачи который денис поставил
как я понимаю будет сложно да давайте я закончу с этой задачей что как бы вот я
сейчас доделывать интерфейс доделаю алгоритм разберусь с ним и как бы ну как бы пока что так
таком виде вы принципе не примерно и оставлю да потом я наверно бля раздеваю
создам две версии одну для дебага просто чтобы показать что она работает и одну
типа ну реальную рабочую рабочую продакшн продакшн а собственно вопрос
есть в принципе нету даже чем понятно сейчас последнее последний вам куда
ушло значит последний вопрос у меня крайне вот это свежая табличка которая
прислал вниз где она используется до этого у меня были просто вот эти p2
что-то там и так далее теперь можно смотреть что это совпадает и она
галочки это которая совпадает название все есть так ну все значит замечание
понятны надо чтобы треугольнички были условно другого цвета или чего-нибудь и
над понять и понять час метриками делать потому что вот здесь у тебя два
совпадает а первая метрика нет может быть надо поиграться с метриками так
чтобы у тебя
совпадающие были получше метриками я еще не успел поиграть и понять как это
устроено здесь все значит второй вопрос картуру ты разобрался с сервером который
мы хотим покупать
сидит рядом я
вышел в течение после прям после нашего разговора я прям пойду его кушу значит
это второе третье а чем мы делаем с вот этой задачей как где у тебя косинусное
расстояние было закусил мне кажется сначала нужно идентифицировать какие-то
признаки а потом в пространстве признаков смотреть косинусное расстояние
а если у тебя абсолютно эквивалентные картинки ты можешь сразу смотреть
косинусное расстояние проклятость больше не немножко отвлекся может
повторить алгоритм модификации картинок сейчас у артура реализована просто
косинусное расстояние между двумя картинами значит ты утверждаешь что это
будет работать криво до нужно значит нейрон q или что-то которое сначала
выбирает признаки а потом
нужно почитать как это делает там какой-то google если они раскрывают задача
очень знаменитая я думаю это очень это очень распространена задача решенная
нужно просто посмотреть как это делают хорошо давайте и первое перед этим что
нужно будет сделать точнее перед реализация алгоритма это скачать все
данные и
вот скачать все два миллиона картинок для этого нужен сервер это уже сервер да
но не обязательно для что для этого нужен серая на самом деле я могу просто
просто это загрузить на google drive пока что вот и как мы будем работать на
google drive ну так и будем будем хороший вопрос по крайней мере у нас
будет данное и когда будет сервера нужно будет можно будет просто эти данные и
вот только частенькие данные и� Toyota2020 так у нас в интернете идёт
этим
теме
секрет километров
вот
вот
так
надо
граф cesar
залился
мне
к следующему
разу Сережа
должен доделать все
до финала.
Ну, окей.
Не до финала, но
в продакшн.
Ну, давайте я просто пошлю
демку, назначим на следующей
неделе встречу с химиками.
Да, не обязательно.
В четверг
значит
Артур, а ты тогда
разбираешься
с космическим расстоянием
от задачи.
Окей, хорошо.
Вот.
И сервер, потому что, как я понимаю, пока у нас
нет сервера, у нас основная
часть проекта на паузе.
Да.
Все.
Значит,
можно ли вытащить метрики
и картинки для того, чтобы...
Это что у тебя там? Ну-ка.
У тебя там Артур пушистая.
На коленке так, что сел.
Знакомьтесь, это был...
По-моему, это абсолютно черное тело.
Это абсолютно черное тело.
Вот.
Окей. Значит,
тогда
на этом все.
Значит,
если получится вытащить
данные
с сервера, или чтобы
эти айтишники сделали это
доступным, скачать
метрики
и доделать
то, что мы держим Энджи
со второй статьей.
Да, да.
Да, надо бы уже заниматься, конечно.
Энджи, скажи вкратце, нету новостей
о...
Нет, новостей нет, к сожалению.
Чего-то они...
Я не знаю, как это называется.
Это называется
все очень некрасиво,
поэтому нужно дописывать вторую статью
и присылать в другой журнал.
Я Денису
завтра... У нас завтра...
Завтра снимут телепатическую связь.
Я ему завтра напишу, что
с сервером Питер
ты определишься,
что нам нужны данные
для Энджи.
Да, и
когда мы разберемся
с Игорем,
когда мне Игорь скажет, что он думает
по этому поводу, я...
Все, написано меньше одной минуты, поэтому
через минуту он уже разберется.
Хорошо, отлично.
Ладно-ка.
Ну, у меня все.
Все, Серег.
Таб-продакшн не к четвергу,
а заранее, чтобы они подтестить могли.
Да, да, конечно.
Хорошо.
Вот.
Все, давай. И перед этим пару
скринов в чат кинь, что у тебя
поменялось, как ты
изменил чего-то.
Мы посмотрим все вместе,
да, и все.
Все, давай.
Угу, хорошо.
Ну все, коллеги, тогда.
Два, один, все.
Я раздавлен.
Меня придавило.
Все?
Да, все.
Меня наш вот этот парень придавил.
Не дает никуда идти.
Буд-да.
Он наслышал твой голос и так
в твою сторону повернулся.
Чего?
Хорошенький-хорошенький.
Как насчет твою кашку сделать?
Да, знаешь, я не знаю.
Я не знаю.
Я правильно написал?
Да.
А ты, конечно же, скажи, что ты
был Banksy, ты не понимаешь, что
при этом у тебя была же
вся эта область общая.
Ну, я думаю, подсознавание
оказалось чем-то подобным.
Да, да, да, да.
Ты даже que estoy entendiendo bien
de tu hablañ de Kate ya.
Что?
Вы понимаете, что, ну,
оно не так сильно, что
вы понимаете, что такая
непонятная вещь.
Это, конечно, очень
непонятная вещь.
Возможно, что она
изменилась, но, наверное,
такое, как ты уже
понимаешь, что у тебя
сейчас все Кажется так,
что нам нужно
