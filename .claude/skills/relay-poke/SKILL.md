---
name: relay-poke
description: Reach a Claude session or Codex task on Derek's Mac from a session running in the cloud — ask it for its summary, hand it a fact, get an answer back. Use when you are a cloud session (CLAUDE_CODE_REMOTE) and need something from a local session, or were asked to coordinate with one by name.
---

# Reaching Derek's Mac from the cloud

You cannot message another session with `SendMessage`: the server accepts a cloud session's
credential for its own work only, and the tool says so if you try. Do not retry it.

What works is a mark in your own reply. Write this in the message that **ends your turn**
(narration between tool calls is not always recorded; the message that ends a turn is):

```
<relay to="Time">
What is the current state of the funnel-mold trial? One paragraph is enough.
</relay>
```

A watcher on Derek's Mac tails this session and delivers the body into the session named by
`to` within seconds, the way a local peer message arrives. That session answers by posting to
this session, and the answer reaches you as a cross-session message — a new turn if you are
idle, your next tool round if you are working. Continue with anything that does not depend on
the answer; do not poll for it.

## Without ending the turn

Text between tool calls is not always recorded, but a tool call is, the moment it runs. So
mid-task, run the mark instead of writing it:

```
tools/relay-mark to "Time" "What is the state of the funnel-mold trial?"
tools/relay-mark read "Time" 40
```

The script only checks the arguments; the watcher reads the mark out of your tool call and
acts on it within seconds. Keep working; the answer arrives at a later tool round as a
cross-session message. A mark found more than ten minutes after it was written (the watcher was
not running) is bounced rather than delivered, so write it again if it still matters.

## Addressing

`to` is a session's name exactly as it appears in the `from-name` of a message you received, or
any live local session name. Sessions are named by their title (`Time`, `System status`) or a
derived name (`homesodamachine-f8`); a Codex task by its title. A name that matches nothing is
answered in place: a notice names the sessions that are live right now, so write the mark again
with one of those.

## Reading a local session's transcript

`/relay <title>` works here too: it writes the read mark. Or write it yourself, in the message
that ends your turn:

```
<relay read="Time" tail="40"/>
```

The watcher renders that session's clean transcript on the Mac (what was typed and what was
answered; tool calls and thinking stripped) and posts it here as a message from `relay`, in
parts when long. `tail` is exchanges from the end; `compact="0"` keeps long agent runs whole.

## What not to do

- Do not ask the local session to reply through `SendMessage`; tell it nothing about transport.
  The delivered message already carries the exact command that reaches you.
- Do not put the mark inside quoted text you mean as a quotation; every mark in your visible
  text is delivered.
- One mark per request; several marks in one reply are several deliveries.
