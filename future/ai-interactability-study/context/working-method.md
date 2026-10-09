# How the study runs

One coordinator and eight continuing explorers. Each explorer sees the whole problem — gun, workpiece, supports, operation, and what software could control and observe — through one framing. Explorers persist as identities: the same framing, notebook, idea files and scenes across waves. The runtime runs each wave as a separate set of agent calls, so continuity lives in the files below.

## Waves

| Wave | What happens |
|---|---|
| 1 Explore | Each explorer develops several ideas from its framing, takes a few past the first sketch, starts rough scenes, notes representative purchasable parts. Four explorers hold Derek's examples from the start; four begin without them. |
| checkpoint | The coordinator reads every explorer's return, maps the arrangements by how they assign motion, carry load, set position and observe, notices convergence, writes `digest-wave1.md`, shares the examples with all, and pairs explorers across framings. |
| 2 Exchange | Each explorer works on a partner's ideas and scenes: names the particular difficulty, the assumption behind it, and attempts a repair or branch. The four explorers who began without the examples take them through their own framing. |
| 3 Revise | Originators work through the critiques, revise ideas and scenes, and take a new direction the coordinator names. |
| checkpoint | Digest, second pairing, combination candidates. |
| 4 Exchange and combine | New partners. Combinations cross framings; each original stays. |
| 5 Respond and develop | Originators respond; ideas get another development pass; scenes are made understandable. |
| 6 Finish | Scenes are opened and exercised; notes, sourcing and connections are completed. |

Nothing is scored or ranked. An idea stays in the study whatever its maturity.

## Files

```
context/                     shared context, goals, assignment texts, digests, coordinator log
kit/                         shared scene kit: kit/README.md documents it
tools/check-scene.mjs        opens scenes headless, drives their controls, writes screenshots
scenes/<id>/index.html       one interactive scene per materially different idea
explorers/<code>/notebook.md running log; ends each wave with open threads
explorers/<code>/ideas/<id>.md   one file per idea (format below)
explorers/<code>/index.md    every arrangement the explorer holds, kept current
explorers/<code>/calc/       scripts behind any number a scene or idea file shows
exchange/<critic>--on--<originator>-w<N>.md    critique that develops the idea
sourcing/<code>.md           observed prices, delivery, availability, sales evidence
thumbs/                      scene screenshots (written by the tool)
```

Explorer codes: `freedom`, `room`, `travel`, `trials` (start with the examples); `datum`, `eyes`, `borrowed`, `use` (start without them).
Scene ids: `<code>-<NN>-<slug>`; a branch of an idea is `<code>-<NN>b-<slug>`; a combination is `x-<codeA>-<codeB>-<slug>`, built in one partner's directory of scenes and naming both.

## An idea file

Opens with **Picture it**: two to four sentences someone can see. Then, in this order: the proposal; what carries the loads, what establishes position, what stays free and what is restrained; what software could command, what it could observe, what stays manual or unresolved; what was tried to break it (each entry: the specific conflict in the specific variant, the assumption behind it, what the change alters, what it leaves uncertain); branches and combinations, with ids; unresolved problems, and questions that need Derek's observation; assumptions, each tagged **[Derek] [repo] [manual] [derived] [unknown]** as in `shared-context.md`; sourcing pointers; the scene id. Original ideas keep their file; variants get their own.

## A scene

A scene is a page that opens from `file://`, built with the kit. It shows what attaches to what, what carries weight, where supports and actuators sit, what moves and what stays fixed relative to what; the dot, wire approach and umbilical where they matter. Controls are marked as *actuator* (a proposed motor or axis software would command), *scene* (edits the explanatory scene), *state* (setup, operating, welding), *branch* or *view*. A scene states which behaviour it models and which it only depicts. Links stay rigid, anchors stay fixed, constrained parts do not pass through each other; when a relationship is unresolved the scene shows a labelled schematic branch. Illustrative dimensions, travel limits, cable paths, compliance and sensor views are labelled illustrative. The exact scene geometry is not a sensor reading; an observer view shows what a proposed sensor could and could not see.

## Sourcing

Observations go in `sourcing/<code>.md`, one entry per part: what it is, vendor, URL, price, delivery or availability, the date observed, and the evidence for sales volume (rank, review counts, "bought in past month", or none). On Amazon only Prime listings count, and each entry states how Prime was confirmed on the product page. Other vendors are recorded the same way. An unchecked claim is marked unchecked.

## Boundaries

Nothing is built, bought, operated or sent to a vendor. Files outside `future/ai-interactability-study/` are read and left as they are. Nothing is committed.
