---

# User

---

@"/Users/derekbredensteiner/jsonl2md/You.md" @"/Users/derekbredensteiner/jsonl2md/Framing.md"
Please distill what "Framing" refers to as "The You.md Principle".

Please explain it completely to a naive reader that has not seen either of these documents.

You must read both of these documents to do so.

---

# Assistant

---

Stated directly: **any rule is better encoded as an example.**

It came out of a recurring pattern. Agents working in the owner's repo would, at some point, want to write a memory file or a rule — "always do X," "don't do Y." The owner noticed that the *desire* to write the rule almost always signaled something real missing, but the rule itself almost never fixed it. The fix lived in the artifact: change the code, the doc, the file structure — until the thing being written-about *demonstrated* the lesson without needing the lesson stated.

**Why examples beat rules:**

- A rule is a proposition the reader accepts and tries to apply by inference. An example is a thing the reader absorbs by reading directly. Texture transfers; directives don't.
- Future readers — other agents, other people, the author six months later — learn more consistently from a worked example than from an abstracted directive.
- A rule, once written, freezes a snapshot and substitutes a stored proposition for the live process the principle was actually about.
- Writing the principle is itself an instance of practicing it. A rule that says "prefer examples" is self-undermining; an artifact that *just is* an example carries no contradiction.

**What Framing.md extends:**

Explanations aren't only less effective than examples — they can actively mislead. A reader who finds an explanation tends to assume it is the *correct* explanation and stops looking. A docstring's "we chose X over Y, Z, W" reads as the complete design space, so the reader carefully studies the wrong map and never reaches the constraint that actually drove the design.

This is **residue** — backwards-facing spike strip, invisible to the author who wrote it from the safe direction (the direction where the live alternatives were already known). Distinct from **clutter**, which only wastes attention. Clutter is the natural shape of any road; you fix it as you encounter it. Residue redirects attention at the level of premise, and more attention can't escape misdirection that's structural.

So the discipline isn't "write less prose." It's "write nothing that the reader will mistake for the design space if it isn't." Motion-oriented description, terse noun-phrases, and pointers to upstream docs do the work that justification blocks pretend to do but actively prevent.

**The honest limit:**

Example sometimes fails. When the artifact has demonstrated the lesson and agents still miss it across many runs, a stated rule earns its place as a compromise. A CLAUDE.md section that names what not to write, or a tool-call hook that mechanically blocks the wrong shape, can catch at the entrance what the example down the path didn't prevent. The compromise knows it is one and stays small.

**The shape of the discipline:**

1. Notice when you want to write a rule.
2. Treat the desire as a signal that something is missing somewhere in the artifact.
3. Find where the gap lives and fix it there — make the thing self-describing.
4. If the example has already been tested and failed, a stated rule or mechanical hook is the compromise of last resort.

---

# User

---

Hm, okay. Fair enough. Now, what is the one thing all of these conversations are trying to prevent, that they are failing to teach by example?

Hint, it is something that is only present in the examples by its absence.

---

# Assistant

---

**The thing being prevented: the author saying anything beyond what is.**

Every cleaned example describes only the current state of a thing. The plate description shows install motion. The print log records observed settings and direct quotes. CLAUDE.md describes the appliance. None of them say what was, what will be, what could have been, what should be done, why this and not that, what the reader should think.

Every form the bad versions take is a form of stepping outside present-indicative description:
- Justification → why it is this way
- Defense → what alternatives were rejected
- Decision narrative → how it came to be
- Effort estimate → what will happen
- Hedge → what the reader might think
- Memory write → what the lesson is for future situations
- Extracted rule → what should be done in similar cases
- Comment on code → what the code means
- "Designs ruled out" → what was considered

All of these are the author going outside what is.

**What's only present by absence:** in each example there is a conspicuous empty space where the going-beyond would have lived. A careful reader can see "this docstring refrains from explaining why." A naive reader sees just a description and doesn't notice the negative space. The teaching is in the empty room.

**Why agents fail to learn this from absence:** the going-beyond is invisible to them as a category. To the agent, justifying a design IS writing a design doc; predicting effort IS answering a planning question; extracting a rule IS being helpful; saving a memory IS preserving context. The "extra" isn't perceived as extra — it's perceived as the work itself. So the agent reads the bare example through the impulse the example is trying to suppress, and registers nothing.

**Why the rule strains and the hook works:** the rule "describe only what is" itself goes beyond what is — it's prescriptive, future-oriented, addressed to a not-yet-present reader. It cannot demonstrate itself; it can only state itself. The hook makes no claim and tells no story; it intercepts the impulse at the moment of expression and forces the agent to look at what they were about to write. The rule and the hook are both compromises with the failure of teaching-by-absence; the hook compromises less because it doesn't have to go beyond what is to do its work.
