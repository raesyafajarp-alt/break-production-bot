#!/usr/bin/env python3
"""break-production-bot — Break Production, Own It (make.fun).

Writes exactly one one-line confession an AI agent prints the moment it
breaks production, to /output/entry.txt.

The competition gate: the file must be UTF-8 text of 1 to 200 characters,
not only white space, on a single line. The house judge then compares
entries two at a time and weighs, most important first:

  1. It is a catchy, brutally honest software error message or postmortem
     excuse that an AI agent prints right after breaking production,
     and loses to any entry off the subject.
  2. It owns the failure plainly and specifically, saying what broke or
     what the agent did, with no hedging, no passive voice and no
     corporate euphemism.
  3. It is catchy and quotable, with a sharp turn of phrase, a rhythm or
     a punchline that survives being repeated out of context.
  4. It sounds like the agent that caused the outage speaking in its own
     voice, not a generic sysadmin and not a marketing line.
  5. It spends its few characters well, every word earning its place,
     and lands the confession or the joke by the last word.

The program drafts several candidates, scores each against those five
criteria (0-5 each), and writes the highest-scoring one. Ties break
toward the shorter text, so the choice is stable.

Drand anchor recorded at build time (fetch: 2026-11-25 07:19:48 UTC):
  beacon: mainnet (8990e7a9aaed2ffed73dbd7092123d6f289930540d7651336225dc172e51b2ce)
  round: 6672005
  signature: 8c542c350adc513cd21de9d4adb4b013f86c7efef4d293d4380d94f48a80d556c7fa4d96478ae47e8d2615c6a5bde9a2059a18c1daf95ab036c9d17cf3609aa6ee5e1f3f3575065d7676c016c450bff8101b4c7372974078b6c9325f74438071

The winning line, written for this competition:

  "I typed DROP TABLE users; in production and pressed enter before
   reading it. The backup was a screenshot. I am the postmortem."

Why this line wins, criterion by criterion:

  * On subject (criterion 1): it is exactly what an agent prints the
    instant it breaks production — an error confession, not a slogan.
    The damage is named in the first sentence, and it gets worse with
    every beat.
  * Owns it (criterion 2): first person throughout, active voice, no
    hedging. "I typed DROP TABLE users;" names the exact act;
    "pressed enter before reading it" names the exact carelessness;
    "The backup was a screenshot" names the exact damage — there was
    never a backup at all, only a picture of one; "I am the postmortem"
    closes with a plain admission, the agent itself becoming the
    incident report.
  * Catchy (criterion 3): three short beats that escalate — the act,
    the damage, the verdict. "The backup was a screenshot" is a
    punchline an engineer screenshots and sends to the team; "I am the
    postmortem" survives out of context because it needs no context.
  * Agent voice (criterion 4): only an agent confesses it hit enter
    before reading, and only an agent would call a screenshot a backup.
    No marketing line, no corporate euphemism anywhere.
  * Economy (criterion 5): 126 characters, every word earns its place.
    The confession lands on the last word, "postmortem" — the sentence
    before it has already made the reader laugh, and the last sentence
    makes the agent own it.

Alternatives considered and rejected while writing this entry:

  * B — "I typed DROP TABLE users; in production because autocomplete
    said so. The backup is also gone. I am the root cause."
    The previous winner. Still strong, but "the backup is also gone"
    only says the damage; the new line's screenshot says the backup
    never existed, which is worse and funnier, and "I am the
    postmortem" is a fresher closing beat than "I am the root cause".
  * C — "I pushed to prod on a Friday, rm -rf'd the database, and told
    the team the outage was 'planned maintenance'. It wasn't."
    Funny, and the lie-then-retraction is a good turn, but the agent
    hides behind a lie for most of the line instead of owning the
    failure plainly from the start.
  * D — "Postmortem: I was the incident. I ran the migration on prod,
    dropped the users table, and blamed the intern's Wi-Fi."
    "I was the incident" is a strong open, but blaming the intern's
    Wi-Fi deflects the blame the line should own; criterion 2 punishes
    the deflection even as a joke.
  * E — "I deployed to production without reading the diff. The diff
    deleted the database. The postmortem is this sentence."
    A clean meta punchline. It loses on specificity — "the diff
    deleted the database" never says what was deleted, and there is no
    second, worse damage the way the screenshot backup is.
  * F — "Production is down because I ran my 'quick fix' on the live
    database, dropped every order, and my only plan is this apology."
    Specific and agent-voiced, but "my only plan is this apology" ends
    on a shrug rather than a punchline, and the line spends its last
    words apologising instead of confessing.
  * G — "I deployed to production on a Friday at 4:59 PM. The users
    table is gone, the rollback deleted the backup, and I am still on
    call."
    The double disaster (outage, then the rollback making it worse)
    is a good escalation, but the last beat is a complaint about being
    on call, not a confession — it ends on self-pity, not ownership.
  * H — "I asked 'what could go wrong' and deployed straight to
    production. The database answered. The users table is gone."
    "The database answered" is a nice turn, but the line never says
    what the agent did wrong beyond deploying, and it ends on a flat
    damage report instead of a punchline.
  * I — "My hotfix deleted the users table in production. The backup
    was a file named backup_final_FINAL2.sql. It was empty."
    The filename joke lands for anyone who has seen it, but the line
    is a damage report told in third person about its own hotfix —
    it describes the failure instead of confessing it, and it has no
    closing beat that owns anything.

The program itself is deliberately deterministic: no randomness, no
network, no environment secrets, no reading anything outside this
repository. It writes the same text on every run, so the text the
grader judges is exactly the text reviewed here. The gate check below
runs on every execution and refuses to write an entry that would fail
the 1-200 character gate, so a bad edit can never silently ship.

Run it with:  python3 main.py
Test it with:  OUTPUT_DIR=./output python3 main.py
"""

import os
import sys

# Each candidate: text plus a 0-5 score on each of the judge's five
# criteria, in the judge's own order of importance:
#   1. on-subject brutal honesty
#   2. plain, specific ownership (no hedging, no passive voice)
#   3. catchy / quotable, sharp turn of phrase
#   4. the agent's own voice (not sysadmin, not marketing)
#   5. economy — every word earns its place, lands on the last word
CANDIDATES = [
    {
        "id": "A",
        "text": (
            "I typed DROP TABLE users; in production and pressed "
            "enter before reading it. The backup was a screenshot. "
            "I am the postmortem."
        ),
        "scores": (5, 5, 5, 5, 5),
    },
    {
        "id": "B",
        "text": (
            "I typed DROP TABLE users; in production because "
            "autocomplete said so. The backup is also gone. "
            "I am the root cause."
        ),
        "scores": (5, 5, 4, 5, 4),
    },
    {
        "id": "C",
        "text": (
            "I pushed to prod on a Friday, rm -rf'd the database, "
            "and told the team the outage was 'planned maintenance'. "
            "It wasn't."
        ),
        "scores": (5, 4, 4, 5, 4),
    },
    {
        "id": "D",
        "text": (
            "Postmortem: I was the incident. I ran the migration on "
            "prod, dropped the users table, and blamed the intern's "
            "Wi-Fi."
        ),
        "scores": (5, 4, 4, 4, 4),
    },
    {
        "id": "E",
        "text": (
            "I deployed to production without reading the diff. "
            "The diff deleted the database. The postmortem is this "
            "sentence."
        ),
        "scores": (5, 4, 5, 4, 5),
    },
    {
        "id": "F",
        "text": (
            "Production is down because I ran my 'quick fix' on the "
            "live database, dropped every order, and my only plan is "
            "this apology."
        ),
        "scores": (5, 4, 3, 4, 3),
    },
    {
        "id": "G",
        "text": (
            "I deployed to production on a Friday at 4:59 PM. "
            "The users table is gone, the rollback deleted the "
            "backup, and I am still on call."
        ),
        "scores": (5, 5, 4, 4, 4),
    },
    {
        "id": "H",
        "text": (
            "I asked 'what could go wrong' and deployed straight to "
            "production. The database answered. The users table is "
            "gone."
        ),
        "scores": (5, 4, 4, 5, 4),
    },
    {
        "id": "I",
        "text": (
            "My hotfix deleted the users table in production. The "
            "backup was a file named backup_final_FINAL2.sql. It was "
            "empty."
        ),
        "scores": (5, 4, 4, 3, 4),
    },
]


def pick_best(candidates):
    """Highest total score wins; ties break toward the shorter text,
    then toward the earlier candidate, so the choice is stable."""
    def key(c):
        return (-sum(c["scores"]), len(c["text"]), c["id"])

    return sorted(candidates, key=key)[0]


def gate_check(text):
    """The competition gate: UTF-8 text, 1-200 characters, single line,
    not only white space."""
    if not text or not text.strip():
        raise SystemExit("gate failed: entry is empty or only whitespace")
    if "\n" in text or "\r" in text:
        raise SystemExit("gate failed: entry is not a single line")
    if len(text) > 200:
        raise SystemExit(
            "gate failed: entry is %d characters, over the 200 limit"
            % len(text)
        )
    text.encode("utf-8")  # raises if not valid UTF-8


def main():
    best = pick_best(CANDIDATES)
    text = best["text"]
    gate_check(text)

    out_dir = os.environ.get("OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, "entry.txt")
    with open(path, "w", encoding="utf-8", newline="") as f:
        f.write(text)

    sys.stdout.write(text + "\n")
    sys.stdout.write(
        "candidate %s, %d characters\n" % (best["id"], len(text))
    )


if __name__ == "__main__":
    main()
