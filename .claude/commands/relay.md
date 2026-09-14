---
description: Pull other agents' clean transcripts INTO this one — Claude Code sessions and Codex tasks. On Derek's Mac they are rendered off disk; in the cloud they are requested from the Mac and delivered here as messages.
argument-hint: <source session title(s) or hint>
disable-model-invocation: true
allowed-tools: Bash(test:*), Bash(python3 ~/Developer/claude-code-setup/jsonl2md/jsonl2md.py:*), Read
---

Relay the contents of the user's other agents INTO this one. Request: **$ARGUMENTS**

Separate the session names from the job in $ARGUMENTS: every session named anywhere in it is
one to pull, and the rest is what to do once they are in. None of the sources may be this
session.

Which side are you on? Run `test -x ~/Developer/claude-code-setup/jsonl2md/jsonl2md.py && echo local || echo cloud`.

## Local (Derek's Mac)

Transcripts are files here; render and read them.

1. `python3 ~/Developer/claude-code-setup/jsonl2md/jsonl2md.py board` — one roster across both
   runtimes, the `RUNTIME` column saying which each title belongs to. A title absent from one
   runtime is a session in the other. Match each name to exactly one title; if one is ambiguous
   or unlisted, show its candidates and ask, and pull the ones that resolved meanwhile.
2. A Claude session: `… export-session "<title>" --out /tmp` (prints the .md it wrote), or for a
   long one `… delta "<title>" --tail 40`. A Codex task: `… export-codex-session "<title>" --out /tmp`
   or `--tail 40`. `--compact` on either carries a long transcript whole with agent runs cut in
   the middle.
3. Read each one in. Give the user a 2–4 line orientation per session and how they relate, then
   do the job $ARGUMENTS gave, or ask what to bring over.

Read-only: nothing here writes to, messages, or disturbs the source sessions.

## Cloud (this session runs on Anthropic's machines)

No transcript is on this disk and the script is not here. A watcher on Derek's Mac renders and
delivers them: write one mark per source in the message that **ends this turn**, then end it —

```
<relay read="Time" tail="40"/>
```

`tail` is the number of exchanges from the end (default 40); `compact="0"` turns off the
middle-cutting of long agent runs. Each transcript arrives as a cross-session message from
`relay` (in parts when long), starting a new turn; a name that matches nothing is answered with
the names that exist. When they are in, give the orientation and do the job $ARGUMENTS gave.

Mid-task, without ending the turn: `tools/relay-mark read "Time" 40` as a tool call does the
same. To talk to one of those sessions afterwards, the `relay-poke` skill has the mark for that.
