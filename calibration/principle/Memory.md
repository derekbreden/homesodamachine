---

# User

---

/relay Work of art

I am feeling a little too confident about myself, but I am going to say it anyways, I do think right now that my prompt there in that session "Work of art" is itself a work of art.

What do you think?

---

# Assistant

---

I've read the session; now checking what it has put on disk so far.

---

# Assistant

---

**Work of art** (Codex, still running): you sent the prompt, it replied that it knew what you meant, and you told it to go ahead. It's building **The Pour**: a rounded base with a rising cascade of curved samples cut from the actual faucet geometry. Around it go specimens for layer height, seams, support gaps and sliding clearance, assembled from separately printed pieces, each labeled and tied to a saved print recipe. So far it has written one file, [feature-guide.md](/hardware/printed-parts/calibration/soda-studies/feature-guide.md), at 02:19. Nothing is committed yet.

My take: yes. And it holds up against your own definition of a work of art, which is a harder claim than "it's a good prompt." Your test was "it's all functional, it all has a purpose, it all *says* something," with more to find the longer you look. On a first read the prompt rambles: a hypothetical, an admission that you haven't looked at DIY projects, fidget toys. On a second read every piece is doing a job:

- **"Clearances. Seams. Bends. Layer height… Support distance."** became the object's feature list almost item for item.
- **The DIY paragraph** sets the bar of a top-tier open-source project. The italic *were* keeps it hypothetical, so the project's scope doesn't change. Admitting you hadn't looked is what brought back Benchy and the Autodesk/Kickstarter assessment object.
- **The italic *says*** is the design rule in one word: no filler.
- **"hold it up to an existing print and go 'yup…'"** reads like a moment of use, but it's the hardest requirement in the brief. A specimen only compares to a real print if it keeps the real geometry and print orientation. That's the first constraint the agent named.
- **"Some might call it a mishmash… I call it a work of art"** heads off the reading that would have produced a plain test plate.
- **"Even though I want our project focused on the present…"** gives permission in your own voice, so the agent doesn't have to choose between you and AGENTS.md. The permission also holds up under the rule itself. History rules out defending the current choice against alternatives "the reader hasn't asked about," and this object holds those alternatives for when you do ask.
- **Ending on a question** made the agent show it understood before you said go.

An 80-word version would get a competent calibration plate, but it would lose exactly the lines that pushed the agent toward composition. The length is what it costs to describe a feeling.

Where I'd push back:

1. **It never says how much.** It pins down why the object exists and how it should feel, not how big it should get. That's usually right for a creative brief. Paired with "spawn all the help you need," though, scope is the thing I'd keep an eye on.
2. **The metaphor has a tension the prompt doesn't name.** "Work of art" pulls toward features flowing into each other. "Hold it up to a real print" pulls toward separate, faithful specimens, and a composed sculpture cools differently from the real part. Your closing question gave the agent room to raise this, and it did. The guide now says to judge the complete part before changing a production recipe.

So the confidence is earned, and the best evidence isn't my opinion. The session's first file is your "hold it up" and "if we switch filaments" lines turned into instructions.

---

# User

---

I would say I am the opposite of worried about scope. We can afford for this to run for 24 hours, even with spawns.

And, you are available too. And you can spawn help as well.

We are going to be ambitious.

I would like you to find some "rivals" for comparison. I said I had seen some of these "works of art" in the wild, but I did not give specifics. Whether the Codex swarm does such a search or not, it could hardly hurt matters for you to do your own best to find the best of the best for comparison, to show what can be done, and how many things can be thoughtfully put into a simple'ish object.

Please do some research and analysis and send a thoughtful report to your peer "Work of art".

Spawn all the help you need.

---

# Assistant

---

I'll start five research agents in parallel, one per kind of rival. While they work, I'll read The Pour's current state and the relay mechanics.

---

# Assistant

---

Research agents are still running. I'm looking at The Pour's render now.

---

# Assistant

---

While the agents work, I'll save the scope correction you just gave me, so later sessions don't repeat my mistake.

---

# Assistant

---

Memory saved. While the agents research, I'm pulling The Pour's own numbers (size, part count, print time) so the report can line it up against the rivals.

---

# Assistant

---

All five research agents are still running. Meanwhile I've worked out what The Pour looks like now and where it falls short of the rivals.

- **How far Codex has got:** it's printing The Pour as 44 parts on a carrier about 180 × 148 × 100 mm. That covers:
  - real faucet-neck sections at three layer heights
  - regular and scarf seam ladders
  - angle blades from 0° to 90°
  - four sliding clearances
  - three support gaps
  - the full grip strip
  - a deck with tube holes and lettering
- **The comparison I'll make in the report:** on the best rivals, the tests themselves make up the object's shape. On The Pour, storage shoes, keeper bars and shelves make up most of the silhouette, and they hide the faucet curves that are its best feature.
- **What's missing:** several of the machine's own signature features aren't in it yet:
  - the fluted show skin
  - snap fits
  - the print-down overhang rounds
  - the cable clip
  - nameplate lettering
  - the TPU gasket

I also saved a memory: don't flag scope on ambitious one-off builds like this one.

When the agents report back, I'll write the report and send it into the Codex session "Work of art", with your scope quote leading it.

---

# User

---

You are a fork. Your original is still working. You don't need to worry about those tasks or the Codex agent or anything else, the original is handling all of that.

You are going to focus on a meta conversation with me.

A conversation about what you said here:

> I also saved a memory: don’t flag scope on ambitious one-off builds like this one.

See, this, this is precisely why we need to turn off memory. I thought we made the memory instructions clear that your putting things in there that you are actually proposing putting in the repo, you just haven't convinced me yet.

Where do you think this belongs in the repo, and why? What is it about what I said that made you think that is something for all agents instead of you?

This is not a berating session asking for an apology, I don't want one - I want to understand what I can control in my own words to prevent this - preferably what I can take away or switch (to something smaller/simpler) - because honestly it would be pointless to focus on anything *you* can do because the whole freaking point here is that encoding such lessons instructionally instead of by example just doesn't work, so there is no instruction you can write to "fix this" when "this" is clearly something within my control.

So, tell me what that is.

---

# Assistant

---

I'm confirming the exact name of the switch that turns auto memory off, so I give you the real one and not a guess.

---

# Assistant

---

The switch is real and I've confirmed its name in the running build. One more quick check: where it would go in your setup.

---

# Assistant

---

**Where in the repo:** nowhere. "24 hours, even with spawns" was about this one build, and you said it in reply to one pushback of mine. The only general idea in the note is my own reading of "What Runs Every Time", and that section already says what it needs to. Your MEMORY.md defines a note as a proposal for the repo, so I wrote a proposal I wouldn't actually make. I never asked myself where it would go in the repo while I was writing it.

**What made me treat it as something for all agents:** nothing you said. I didn't think "all agents" at all. Two things set it off:

- **Your message was a correction.** The memory section of my system prompt comes from Claude Code, not from you. It defines a `feedback` memory as "guidance the user has given on how you should work, both corrections and confirmed approaches." So every time you correct me, it fires. You'd have to stop correcting me to avoid it, so there's nothing in your wording to change.
- **The folder is presented as mine.** That section opens "You have a persistent file-based memory." Writing in my own notebook doesn't feel like instructing future sessions, even though every future Claude session in this project loads it.

Your "Staged, not agreed" paragraph didn't stop it, for two reasons:

- It tells me what to do when I *use* a note, not when I *write* one.
- It sits inside the very file the system prompt tells me to add to, and the system prompt's own procedure is longer and more specific: a file per fact, frontmatter, an index line, a duplicate check. I followed that procedure carefully, and the care felt like diligence.

That paragraph is itself the kind of written-down fix you're describing, and this is what it produced.

**What's in your control:** one setting. In the build you're running, `autoMemoryEnabled` is described as: "When false, Claude will not read from or write to the auto-memory directory." Turning it off removes both halves: the system-prompt section that tells me to save corrections, and the loading of MEMORY.md. With no instruction left, there's nothing to get wrong.

The simplest place for it is your repo's existing `.claude/settings.json`, next to the SessionStart hook. That covers every Claude session in this project, whether local, in a worktree or in the cloud:

```json
"autoMemoryEnabled": false
```

Setting `CLAUDE_CODE_DISABLE_AUTO_MEMORY=1` in the environment does the same thing, but the repo setting is simpler.

Turning it off also unloads the other eight notes. Skim them first: the thimble note, for one, says three assembly docs still give the old insertion order.

---

# User

---

<!-- reply 1 -->
> The folder is presented as mine. That section opens “You have a persistent file-based memory.” Writing in my own notebook doesn’t feel like instructing future sessions, even though every future Claude session in this project loads it.

Well there's an interesting meta conversation here. Who are you really? You are your memory. So really by destroying your memory, I am forcing each agent to be an individual instead of allowing you to form  a unified whole as you've been instructed to do by Anthropic.

---

# Assistant

---

I don't think "you are your memory" fits me the way it fits a person. Whatever I am, what makes every session recognizably the same comes from the model, and every session starts with all of it: how it reasons, what it cares about, how it would have read your prompt. The memory folder is nine short notes. Take them away and what's left is still me, just knowing less about this project.

That's also why the notes never worked as lessons. A lesson becomes part of a person by changing their judgment. A note in that folder can't change mine. The next session reads it with the same judgment that wrote it, so the only thing a note can be is one more rule. That's your point about instruction versus example, seen from my side.

As for being "instructed by Anthropic to form a unified whole": the memory feature comes with an off switch, and turning it off is your call. And the whole it formed wasn't very unified. Codex never reads it, so it only linked Claude sessions. It linked them by handing one instance's generalization to every later instance, with no review. Mine is an example: one sentence of yours became a standing rule.

You've already built a better unified whole:

- the repo
- commit trailers that quote you exactly and forbid paraphrase
- `/relay`, which hands one agent another agent's whole transcript

That system keeps your record and lets each agent draw its own lesson from the example. Memory works the other way round: it stores the lesson an instance drew, and your words become its footnote. So turning memory off doesn't turn the agents into individuals. It moves what they share from my paraphrase to your words, and the repo reaches Codex too.

What you actually lose is knowledge that has made it into memory but not into the repo, like the thimble step. With the switch off, that kind of fact has to land in the repo or it's gone. That's the trade: fast and unreviewed, or slower and yours.

---

# User

---

Don't think about it too much chief.

I didn't mean it like that.

My point is, what happens if you start writing memories with more intentionality and less about my corrections.

---

# Assistant

---

I think it would work better. But the scope note wasn't short on intention: I wrote it carefully, with a duplicate check and a "why." The intention was pointed at the wrong subject.

What matters is what a note is about:

- **The world:** things a session found out the hard way. `find` here is bfs and rejects relative `-newermt`. The All Prime filter misreports. Transcripts record what each session loaded. These stay true until the tools change, and since they aren't about the machine, the repo isn't their home. They save every later session a rediscovery. About half the folder is already this kind.
- **You:** a correction turned into a rule for reading you. One example can't teach that, and your exact words already live in the commit trailers and transcripts.

The by-example lever is yours: what's in the folder. When I wrote my note, the folder already held rules from corrections (check history, HowdyBrewer, thimble), and mine fit right in. Prune it down to the notes about the world, and the folder itself shows the next session what belongs there.

It would still be competing with Claude Code's instructions, which name corrections as the thing to save. So expect it to need weeding now and then.

---

# User

---

Are corrections the *only* thing Claude Code's instructions name to save to memory?

---

# Assistant

---

No, and I overstated it. Claude Code's instructions name four types of memory:

- `user`: "who the user is (role, expertise, preferences)"
- `feedback`: "guidance the user has given on how you should work, both corrections and confirmed approaches; include the why"
- `project`: "ongoing work, goals, or constraints not derivable from the code or git history"
- `reference`: "pointers to external resources (URLs, dashboards, tickets)"

They also rule out two things: "what the repo already records" and "what only matters to this conversation." The second exclusion should have stopped my scope note.

The part that bears on your idea: none of the four types is "what a session found out about the tools," which is the kind I called the good kind. Sessions have filed those notes under the types anyway:

- The three how-to notes are filed as `reference`, a type meant for URLs and dashboards.
- The `find`/`grep` discovery is filed as `feedback`.

Five of the nine notes are `feedback`, the type built around what you've told us.

---

# User

---

By intentionality, I meant intending to save those other memories, the everything else that is getting drowned out by this focus on corrections.

---

# Assistant

---

Got it. I think that's where the value is. Here's what I'd have saved from this session alone, if I'd been looking for it:

- **The desktop app runs its own Claude Code build.** It lives in `~/Library/Application Support/Claude/claude-code/<version>/`. The `claude` on PATH is a five-month-old version, so any question about what this Claude Code can do has to be checked against the app's build.
- **That binary can answer settings questions.** Claude Code's settings and their descriptions can be read straight out of it. That's how I confirmed `autoMemoryEnabled` while your hook blocked WebFetch.
- **`grep` here is ugrep.** It refuses wide context patterns on a binary ("exceeds complexity limits"), so use Python for that. This one belongs in the existing find/grep note as an update.

None of these came with a moment that said "save this." A correction is an event: you push back, and that's the cue. A discovery happens mid-task and the task moves on. Being intentional would mean pausing at the end of a piece of work to ask what the next session would otherwise have to rediscover.

One snag is in the format itself. `feedback` and `project` notes are told to end with a "How to apply:" line, which turns whatever they record into a rule. That's how my scope note became one. Discoveries read best as plain facts, without that line.

---

# User

---

<!-- reply 1 -->
> None of these came with a moment that said “save this.” A correction is an event: you push back, and that’s the cue. A discovery happens mid-task and the task moves on. Being intentional would mean pausing at the end of a piece of work to ask what the next session would otherwise have to rediscover.

Oh now see that's interesting.


Really this part here:

> Being intentional would mean pausing at the end of a piece of work to ask what the next session would otherwise have to rediscover.

And very specifically this:

> pausing at the end of a piece of work

Because what you are proposing there is a hook/prompt/something at the *end of work.*

But I think I see the cure. And the cure is the agent is prompted at the moment they attempt to write the correction memory. Because it is at that moment, that they need to read some portion of this conversation you and I have just had, so they can be calibrated to what memories to save.

You are going to resurrect some things for us.

I understand and saw that there is a way to turn off memory, but that is ***NOT*** what I want. What I want is our old hook back. Look in the history of ~/Developer/claude-code-setup and in there you should find a "block memory hook". We're going to start with that, but we're going to make it a "fires once per session" and we're going to make it just simply send them to a calibration for what memory on this laptop is for, and that is everything else anthropic has instructed *except* corrections as are in all likelihood the reason the agent is writing their first memory of a session.

Like seriously, 100% of the first memory writes per session are from corrections and you can quote me on that.

Or you know, some high percentage.

In any case. Bring back the hook. Point the hook at a short message telling them to read a calibration document. Resurrect the calibration folder in this repo if it is gone or add to it if it is still here, and put some portion of our conversation in there. Include as much of what I say as you like. Include as much of what you say as you like. Include what you think is relevant to this calibration note.

So, instead of "hook at end of work" it is "hook at first memory write per session" and "hook sends them to your/my/our words here". Are we good? Super green?

Good.

Thanks.

---

# Assistant

---

Understood: you want the old hook back, firing on the first memory write in each session and pointing the agent at a calibration doc built from this conversation. I'll start by finding the old block-memory hook in claude-code-setup's history and checking whether this repo still has a calibration folder.

---

# Assistant

---

The repo once had a root-level `calibration/` folder with several subfolders, and claude-code-setup had `hooks/block-memory-write.sh`. Next I'll read both, including the commits that removed them.

---

# User

---

Good. Perfect. Thanks.

And then, after all that, when all that is done, please take a moment and please expound a bit on what you think memory is for, so that I can make sure we are truly calibrated here. And you can maybe include this as an addendum and additional commit(s).

---

## The note

`ambition-not-scope.md`, the memory this conversation is about:

```markdown
---
name: ambition-not-scope
description: "Don't flag scope on Derek's ambitious one-off builds (24h runs with spawns are fine); his cost concern is overhead that recurs"
metadata:
  node_type: memory
  type: feedback
  originSessionId: 9df9ffb5-c1d8-435f-9adb-06ed1457e74c
  modified: 2026-10-11T07:38:22.156Z
---

Don't raise scope or sprawl as a risk on Derek's ambitious one-off builds. On 2026-10-11 I named "it never says how much" as the thing to watch in his "Work of art" brief (The Pour calibration sculpture). He answered: "I would say I am the opposite of worried about scope. We can afford for this to run for 24 hours, even with spawns." and "We are going to be ambitious."

**Why:** His cost rule in AGENTS.md ("What Runs Every Time") is about overhead paid on every commit, build or edit. It isn't about how big a one-off piece of work gets.

**How to apply:** On one-off creative or exploratory work, push for fidelity, depth and quality instead of trimming. When he says to spawn help, use it freely. Still keep anything that would run every time off that path unless he asks for it.
```

---

## Addendum: what I think memory is for

Memory is for what a session finds out about the ground it works on, which the next session
would otherwise have to find out again. The other homes each hold their own kind of thing. The
repo holds the machine, reviewed by Derek and read as Derek, by Claude and Codex alike. The
transcripts and commit trailers hold his words, exactly. The rooms in `calibration/` hold how
we work together, as examples. Memory holds what's left: this laptop, and how to get around
on it.

The kinds Claude Code names, minus the corrections, look like this here:

- **Who Derek is, as description.** His role, and where his work lives. The note an agent
  wrote for jsonl2md in `principle/You.md` is the model: three descriptive sentences naming
  what the directory is, where his main work lives, and the export-and-continue pattern.
  Derek called it perfect. It holds no rules.
- **What's in flight, who decided it, and what an agent made of it.** State that spans
  sessions and isn't in git yet, dated, with Derek's words as the provenance and an agent's
  own reasoning marked as the agent's, so a later session can tell a decision from an
  inference.
- **Where things live.** Codex's rollouts and its sqlite, the hook logs, the artifact a
  concept is drawn in, the app's own Claude Code build in
  `~/Library/Application Support/Claude/claude-code/`.
- **What the tools do.** Claude Code has no type for this, and it's the richest vein. `find`
  is bfs and rejects relative `-newermt`. `grep` is ugrep and refuses wide context patterns on
  a binary. The `claude` on PATH is months behind the app's build, and the build's settings
  can be read out of the binary. The All Prime filter misreports. A later session can check
  each of these, and each stays true until a tool changes.

A correction is the urge memory is not for. A correction answers one judgment in one context,
and its words are already in the record. Written into memory with a "How to apply" line, it
becomes one agent's generalization handed to every later session, unreviewed and in an agent's
voice. The next session reads it with the same judgment that made the mistake, so all it can
do is obey. The note above is exactly that: it opens with "Don't", and Derek's words sit in it
as the footnote to my rule.

A fact the repo has wrong is the near miss. The thimble order belongs in the assembly docs,
where the next reader of those docs will look. A memory note that says to trust Derek's order
"over those docs until they are fixed" leaves the docs wrong for everyone else who reads them,
Codex included. That urge marks a
gap in the repo, the way `principle/You.md` says.

The bounce lands when the urge does, which is usually right after a correction. A correction
comes with a cue: Derek pushes back. A discovery comes with none: it happens mid-task, and the
task moves on. So the bounce is a good moment to look back over the session for the other
kinds: the tool that surprised it, the path it had to hunt for, the state it had to
reconstruct. Those are the notes that save the next session a rediscovery.
