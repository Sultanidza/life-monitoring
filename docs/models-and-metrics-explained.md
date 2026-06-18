# Models & Metrics — Plain-English Guide

A simple but complete explanation of the two models this project uses, how they
work, how they were trained, how we use them, and every metric we measure them
with. No prior ML background assumed.

---

## 1. The big picture — what are we even doing?

**Goal:** automatically tell, from video, when the user is playing guitar.

That splits into two different questions, and we use a different kind of model
for each:

| Level | Question | Model | Kind of model |
|---|---|---|---|
| **Image** | "Where is the person and the guitar in this frame?" | **Grounding DINO** | Object detector |
| **Video** | "Is the person *playing* guitar in this clip?" | **VideoMAE** | Action recognizer |

The image model is the foundation (find the objects, measure how they relate);
the video model adds the time dimension (recognize the *action* of playing).
They are complementary, not competitors.

A key idea throughout: **we don't train these models ourselves.** We take
models that other people trained on huge datasets and use them "off the shelf"
on our data. This is called **zero-shot** (or near-zero-shot) use, and it lets
us get results with almost no labeling.

---

## 2. Model 1 — Grounding DINO (the image detector)

This was our main **image-level** baseline: given a still frame, it finds the
person and the guitar and draws boxes around them.

### What it does

You give it:
- an **image**, and
- a **text prompt** listing what to look for, e.g. `"person. guitar."`

It returns:
- a **box** (rectangle) around each thing it found,
- which prompt word that box matches ("person" or "guitar"),
- a **confidence score** (0–1) for how sure it is.

### Why it's special: "open-vocabulary"

Classic detectors (like YOLO) only know a **fixed list** of categories — YOLO's
standard list has 80 things, and **"guitar" is not one of them.** Grounding DINO
is **open-vocabulary**: you describe what you want in words, and it finds it,
even categories it was never explicitly trained as a fixed class. That's exactly
why we can ask it for "guitar."

### How it works (simplified)

It has two "senses" that meet in the middle:
1. An **image encoder** looks at the picture and turns it into features (it uses
   a vision transformer — a network that splits the image into patches and lets
   them "pay attention" to each other).
2. A **text encoder** reads the prompt words and turns them into features.
3. A **fusion** step matches words to image regions — "this region looks like
   the word *guitar*" — and outputs the boxes with scores.

### How it was trained

Its authors trained it on **millions of image + text pairs with box
annotations** (large public detection and "grounding" datasets, where grounding
means linking a phrase to a region of an image). Through that, it learned to
align *language* with *image regions*. **We did not train it** — we just feed it
our frames and prompts.

### How we use it in this project

1. Extract frames from videos.
2. Run Grounding DINO on labeled frames → get person/guitar boxes.
3. Save the predictions.
4. Compare the predicted boxes to our **ground-truth** labels (the boxes we drew
   by hand in Label Studio, stored in COCO format) → compute detection metrics
   (Section 5).
5. Measure how the person box and guitar box **overlap** (IoU) → decide
   "person-with-guitar."

### Why we chose it, and its weakness

Across the models we compared, Grounding DINO was the **most balanced** on our
data (good at both finding objects and not inventing false ones). Its main
failure mode is **mirror reflections** — reflected guitars/people confuse it.

---

## 3. Model 2 — VideoMAE (the video action recognizer)

This is our **current video-level** baseline: given a short clip, it says *what
action* is happening.

### What it does

You give it a short **clip** (16 frames). It outputs a probability for each of
**400 possible human actions** (a standard list called **Kinetics-400**). One of
those 400 actions is literally **"playing guitar"** — which is why this model
fits our project so well, with no training needed.

### How it works (simplified)

It's a **video transformer**: it chops the clip into small **space-time
patches** (little cubes of pixels across a few frames), lets them pay attention
to each other, and finally outputs the 400 action probabilities. The action with
the highest probability is its answer.

### How it was trained (two stages)

This is the clever part, and worth understanding:

1. **Self-supervised pretraining (the "MAE" = Masked AutoEncoder part).** Take
   lots of unlabeled video, **hide ~90% of the patches**, and train the model to
   **reconstruct the missing pieces**. To fill in the blanks it must learn how
   bodies, objects, and motion behave — *without anyone labeling the videos.*
   This is where most of its "understanding" comes from.
2. **Supervised fine-tuning.** Then train it on **Kinetics-400** (clips labeled
   with one of 400 actions) so it can actually *name* the action. After this it
   can output "playing guitar," "juggling balls," etc.

**We use the already-fine-tuned checkpoint** (`videomae-base-finetuned-kinetics`)
as-is. Because "playing guitar" is one of the 400 classes, it works on our
videos near-zero-shot.

### How we use it in this project

1. Take a real video.
2. **Slide a window** across it (a 2.5-second clip every 2 seconds).
3. Classify each clip → record when "playing guitar" is the top prediction.
4. The result is a **playing timeline** across the whole video, plus a summary
   (what fraction of the video was playing).

### One technical fix worth noting

The downloaded weights stored two small internal values (`q_bias`/`v_bias`) in an
older format that the current software dropped, which silently broke predictions
(it reported 0% playing). We **remapped** those values into the format the
software expects; after the fix the model worked correctly. (Detail for the
record — not something you need day to day.)

### Why VideoMAE over the alternatives

We compared three video models on all three real videos. VideoMAE won on every
one (top-1 "playing guitar" rate **53% vs 35% vs 20%**), so we selected it.

---

## 4. Detection vs. action recognition — the core difference

- **Grounding DINO (detection):** answers *"what objects are where"* in a
  **single image**. Output = boxes.
- **VideoMAE (action recognition):** answers *"what is happening"* across
  **time**. Output = an action label for a clip.

A detector can see a person holding a guitar in one frame but can't tell
*strumming* from *just holding* — that needs motion over time, which is what the
video model adds.

---

## 5. The metrics — how we measure performance

Metrics are just **numbers that describe how good the output is.** Here are all
the ones we use.

### 5.1 IoU — Intersection over Union (the overlap measure)

How much two boxes overlap, from 0 (no overlap) to 1 (identical):

```
IoU = (area where the two boxes overlap) / (area they cover together)
```

We use IoU in **two different ways**:
- **Detection quality:** does the model's predicted box line up with the
  hand-drawn true box? (A match needs IoU ≥ 0.5.)
- **Relationship:** do the **person box and guitar box** overlap — i.e., are they
  *together*? High overlap ≈ holding/playing; zero overlap ≈ guitar sitting apart.

### 5.2 Precision & Recall (for the detector)

When checking detection against ground truth, every predicted box is one of:
- **TP (true positive):** a correct detection (matches a real object).
- **FP (false positive):** a box for something that isn't really there.
- **FN (false negative):** a real object the model **missed**.

From those:
- **Precision** = TP / (TP + FP) = *of the boxes it drew, how many were right?*
  (High precision = few false alarms.)
- **Recall** = TP / (TP + FN) = *of the real objects, how many did it find?*
  (High recall = misses little.)

There's a **trade-off**: a model can be cautious (high precision, lower recall)
or eager (high recall, more false positives). We want both reasonably high —
which is why Grounding DINO ("balanced") won.

### 5.3 Mean IoU

The **average overlap** of the correct matches — not just *whether* boxes
matched, but *how tightly*. Higher = the boxes sit more precisely on the objects.

### 5.4 Two thresholds (and how we pick them)

- **Matching threshold = 0.5.** A predicted box only "counts" as matching a true
  box if their IoU ≥ 0.5. This is the standard cutoff for detection evaluation.
- **Person-with-guitar threshold = 0.26.** For deciding "are person and guitar
  together," we don't guess a cutoff — we look at the **distribution** of all the
  person↔guitar IoU values across the dataset and use **Otsu's method** (a
  standard technique that finds the cutoff which best splits the values into two
  groups). It landed on 0.26. We also report a **sweep** (how many frames qualify
  at 0.1, 0.2, 0.3, …) so the choice is transparent.

  Important honesty point: 0.26 is **descriptive** — derived from the data's
  shape, *not yet validated* against frames hand-labeled "playing / not playing."

### 5.5 Top-1 rate & mean probability (for VideoMAE)

The video model outputs 400 probabilities per clip. We measure:
- **Top-1 rate:** the fraction of clips where **"playing guitar" is the
  single highest-scoring action.** This is our main video metric.
- **Mean probability:** the average probability it assigns to "playing guitar."

**Why top-1 and not "probability ≥ 0.5"?** With 400 classes, the probability is
spread thin, and related classes ("strumming guitar," "playing bass guitar")
steal some of it — so the score rarely crosses 0.5 even when guitar is clearly
the answer. A 0.5 cutoff badly **undercounts**; **top-1 is the honest signal.**
(Same lesson as the IoU threshold: read the decision rule from how the scores
actually behave, not an arbitrary number.)

### 5.6 Descriptive rates (the report numbers)

Plain counts that describe the data:
- **Both-detected rate:** fraction of frames with *both* a person and a guitar.
- **Person-with-guitar rate:** fraction of frames passing the IoU ≥ 0.26 test.
- **Playing rate (video):** fraction of clips where the video model says "playing
  guitar."

"**Descriptive**" means they *describe what the model output*, not validated
accuracy — because we don't yet have a hand-labeled "truth" for *playing*.

### 5.7 What we deliberately **don't** use yet

- **Full COCO mAP** (the heavyweight detection score) — postponed until the
  classes and data are more stable; precision/recall at IoU 0.5 is enough for now.
- **Validated precision/recall for "playing"** — needs a small hand-labeled set
  of playing/not-playing clips, which is a planned next step.

---

## 6. The whole pipeline in one view

```
                    ┌─────────────── IMAGE LEVEL ───────────────┐
 video ──> frames ──> Grounding DINO ──> person & guitar boxes ──> person↔guitar IoU
                                                                      │
                                                          IoU ≥ 0.26 ? → "person with guitar"
                                                          (precision / recall vs hand labels)

                    ┌─────────────── VIDEO LEVEL ───────────────┐
 video ──> sliding 2.5s clips ──> VideoMAE ──> 400 action scores ──> top-1 == "playing guitar"?
                                                                      │
                                                          → playing timeline across the video
```

---

## 7. Mini-glossary

- **Ground truth:** the correct answer (here, boxes we drew by hand). Models are
  graded against it.
- **COCO:** a standard file format for storing image annotations (our boxes live
  in COCO JSON).
- **Zero-shot / near-zero-shot:** using a model on a new task *without* training
  it on your data.
- **Open-vocabulary:** a detector that finds categories described in words, not
  limited to a fixed list.
- **Checkpoint:** a saved file of a trained model's weights (what you download).
- **Fine-tuning:** continuing to train a pretrained model on a specific task.
- **Self-supervised:** learning from unlabeled data by solving a made-up task
  (e.g., reconstructing hidden patches).
- **Softmax / probability:** the model's confidence spread across the possible
  answers, summing to 1.
- **Kinetics-400:** a standard dataset of 400 human-action classes; "playing
  guitar" is one of them.
- **Transformer / attention:** the network design both models use, where pieces
  of the input (image patches, words, video cubes) "pay attention" to each other.

---

## 8. One-paragraph summary

We use **Grounding DINO** to find the **person and guitar** in each frame
(open-vocabulary detection, used zero-shot), and measure it with **IoU,
precision, and recall** against hand-drawn labels. We then use **person↔guitar
IoU** with a data-chosen **0.26** threshold to decide "person with guitar."
Separately, we use **VideoMAE** to recognize the **action of playing guitar**
across a video (a Kinetics-400 action model, used near-zero-shot), measured by
the **top-1 "playing guitar" rate**. Neither model is trained by us; both run on
downloaded checkpoints, which is what makes this fast and low-cost.
