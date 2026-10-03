# Home Soda Machine

## What This Is

A home soda machine — a kitchen appliance that dispenses flavored carbonated water from a faucet. In the prototype, refrigerated carbonated water is provided by an external carbonator (Lillium, Brio). When flow is detected, peristaltic pumps inject flavoring through a parallel line. Two flavors, each primed and valve-locked for instant dispensing. The mixing happens in the user's glass, not before.

The prototype under the counter dispenses from a Lillium-class external carbonator. The integrated soda machine under development consolidates the carbonator into the same enclosure.

See `future/README.md` for where this is going and what done looks like, and `hardware/README.md` for the machine as it stands, subsystem by subsystem.

## Why This Exists

Pepsi and Coke will not sell bag-in-box syrup to home consumers without a business license. Pepsi does sell their own brand formulations as SodaStream-compatible syrup (1:20 ratio, sucralose, no sugar) to home consumers. Diet Mountain Dew syrup made by Pepsi is Diet Mountain Dew — not an off-brand approximation.

Dispensed through chilled carbonated water, the result is indistinguishable from the canned product, with equal or better carbonation and temperature. It is the same product, colder and fizzier than a can, on tap.

There is no machine on the market that gives a home user this experience — turn the handle, soda comes out. The alternatives are hauling cans from the store every week, or home carbonation products that carbonate warm water into bottles that go flat within hours. Despite enormous initial sales, very few people stick with home carbonation because warm water cannot hold carbonation — it is flat before it reaches your glass.

See `marketing/target-market.md` for details.

## Amazon Prime

You have access to my Chrome which is signed in to my amazon through your MCP. I only care about Amazon Prime listings. Non-Prime listings are non-existent as far as I am concerned. Do not read them. Do not mention them. They do not exist.

## History

Git keeps history. Code and docs in this repo describe current state. Don't write "was X, now Y" or decision narratives in current files. Don't defend the current choice against alternatives the reader hasn't asked about. The repo describes only what is.

A commit takes the paths your session changed — `git commit -- <paths>`, with `git add <path>` first for a new file — and every other change stays in the tree as it is. The message ends in one trailer block:

```text
Session: <session title>
Derek: "<his words, exactly as typed>"
Derek: "<another passage, with ... marking a cut; a long one wraps onto
 lines that start with a space>"
Co-Authored-By: <the harness's line, when it adds one>
```

`python3 ~/Developer/claude-code-setup/jsonl2md/jsonl2md.py whoami` prints the session title, marked `(auto-generated)` when Derek hasn't named the session; in a cloud session, the `Claude-Session:` link names it. Each `Derek:` line is a passage of his that the commit answers, quoted exactly — never paraphrased — and never anything the Privacy section keeps out of the repo. A commit nothing of his asked for has no `Derek:` line. `git log --format='%(trailers:key=Derek)'` reads them back.

## Privacy

This repository is public. Do not include the founder's family relationships or private details about relatives in repository content, including examples and transcripts. Refer to participants generically, such as "nearby beta household."

## Publishing

Complete requested repository changes by committing and pushing to `main` without asking for separate confirmation. For website changes, verify that the live site serves the update before reporting completion.
