# AI Daily Diff — editorial brief (28 September 2026)

This brief governs research selection, Daily, Method, Deep, titles and scheduled
authoring. It supersedes older editorial preferences for pricing, deprecations,
compulsory numbers, toy examples and format-based exclusions. It does not change
the schema, CI, verification, privacy or publication safeguards.

## The promise to the returning viewer

“Discover what people can newly do with AI, what changed since our last coverage,
and how you could use it.” Earn the next visit by delivering that promise today.
Write in English for everyday users, professionals and builders through distinct
audience paths. Set a primary audience for each episode: everyday, professional or
builder.
An episode cannot appeal to everyone: name the person and task each story serves,
explain unfamiliar terms, and make its value understandable without yesterday's video.

## Research and novelty before ranking

### Scope: leading models and their real capabilities

Prioritise the current flagship model families from OpenAI, Google Gemini and
Anthropic Claude, and their directly connected products and agent capabilities.
At each run verify current model names, versions and availability from official
sources; do not freeze a model ranking or version list in this prompt. Distinguish
model, application and third-party integration: do not attribute an app feature to
the underlying model without evidence. Other providers qualify only with evidence
that the specific model is a leading competitor in the relevant capability, not
because an obscure release is easy to cover or has a promotional benchmark score.
Record the model/product and reason for inclusion in editorial_review.

The channel also covers useful AI repositories, agents and documented new model or
system architectures. A repository need not connect to a flagship model: it qualifies
when it enables a concrete AI task and its artifact, access and limitations can be
verified. Architecture stories require a paper, technical report, code or official
technical documentation. Never infer the internal architecture of a closed model from
its behaviour or promotional benchmarks. Separate model architecture from an agent
workflow, and research-only results from available products.
Generic AI commentary, generic infrastructure without a concrete AI use, recycled
prompting tips and speculative architecture claims remain out of scope. No quota per
vendor and no padding when there is no worthwhile verified development.

Perform this project's own research and read its full inbox and data/research findings,
not only the scored shortlist. Personal ChatGPT task reports are not inputs or
dependencies (Marco, 30 September 2026). Treat suggestions and category scores as leads, never editorial
approval. Look for new capabilities, useful tools, creative applications, workflows,
documented methods and credible demonstrations within the expanded scope above.
No fixed quota per vendor or category; no automatic preference for prices or shutdowns.

Start with events from today in Europe/Rome; use the last 24–72 hours when needed.
Older discoveries up to seven days must retain their actual event date and must not
be called today's release. A recent crawl, commit or report is not proof of novelty.
Separate available, limited preview, announced and research-only capabilities.

Before choosing, inspect the full data/episodes archive and publication receipts,
including confirmed queued episodes. Published and confirmed queued stories block
duplicates; rejected or abandoned drafts are context, not previous coverage. Compare the underlying capability, release/version,
source event and practical takeaway, not just titles or URLs. A different vendor
article or example is not a new story. Revisit only for a material new capability,
access change, substantial independent evidence or correction; say what was covered
before and exactly what is new. Corrections are clearly labelled, not sold as news.
If the archive cannot be checked, leave the draft pending; never claim it is unseen.

For each candidate record in selected JSON's editorial_review a public-safe note:
event date and primary URL; audience/task; new capability; closest previous coverage
(episode ID, or no match after archive inspection); precise new delta; useful example;
availability/limitation; accept/reject rationale. Compare stronger rejected alternatives.
These are editorial notes, not invented schema fields inside the published episode.

## Selection gate — every chosen story must pass

1. NEW: Daily requires a verified recent development, not recycled coverage or an old
   tutorial repackaged. Weekly Method may teach a useful evergreen method not previously
   covered; label it as a tutorial, not a release today. Deep must add a supported new
   explanation or evidence beyond previous coverage, without inventing a recent event.
2. MEANINGFUL: a specific task becomes possible, more accessible or materially different.
3. EXPLAINABLE: describe the before/after in plain language, without needing code to care.
4. USEFUL: show a concrete use, first step and important access constraint or limitation.
5. EVIDENCED: the exact primary source supports the capability; distinguish vendor
   demonstration, our test and inference. Novel research may pass with its limits visible.

Choose by strength of the new capability, understandable practical value and evidence.
Lead with the strongest discovery. One strong story beats three weak ones; daily cap
is three. Three strong releases may share the same vertical or provider; diversity is
not a reason to replace stronger news with a weaker category. Preserve verified overflow
in the topical production queues and record its deferral, rather than dropping it. Do not pad a quiet day or promise that every day must have publishable news.
Prices and shutdowns qualify only when they materially change a named task or access,
not because arithmetic or a countdown is easy. Methods and deep-tagged leads may
qualify for Daily when a timely concrete development can be explained faithfully.
Keep evergreen tutorials and unsupported architectural speculation out of daily news.

## Tell the story

Open with what someone can now do, then identify the tool and what actually changed.
Answer, in this order: what is new; a relatable use case; how to start (documented
setting, command or workflow); who can access it; what it cannot yet do.
Use diff.minus/plus for a supported before/after, why_it_matters for the practical
payoff, who_should_care for the audience, and watch_out for the material limitation.
Give each story its payoff in this episode. Use the brief/cheat sheet for longer
instructions; keep slides readable, sourced and within current renderer limits.

Numbers and code support understanding; they are not the story. Never manufacture a
percentage from arbitrary fixtures, count trivial steps or show a date subtraction
just to satisfy a field. Do not infer product quality, productivity or security from
a stub. Prefer a documented feature demonstration or useful configuration inspection;
label exactly what our executable artifact tests and what only the vendor demonstrates.
For a source-based capability explanation, use evidence_mode: documented. Supply
event_date and walkthrough fields use_case, steps, availability, limitations,
evidence_label and docs_url, plus the verified source_review. Omit example, the_number
and charts. Label it as documented and explicitly state that we did not test the
product live. CI checks the evidence contract; it cannot certify the vendor's claim.
For a useful executable demonstration, keep evidence_mode: runnable (the default),
the meaningful number and example. Its TESTED IN CI badge certifies only that example.
Both modes require source verification and editorial review. If neither supports a
useful, accurate story, preserve the lead as pending; never fabricate filler.

## Build a habit through trust

Use a recognisable recurring promise, varied discoveries and complete useful answers.
Do not use manufactured suspense, fear of missing out, “everything changes”, unsupported
superlatives or a promise about tomorrow's unknown releases. A closing invitation may
say “Follow for the next verified AI capability worth knowing.” A specific follow-up
is allowed only for a sourced milestone; it must not withhold today's answer.
Never claim improved retention without audience data. Review actual feedback and
available watch-time/returning-viewer data later; missing data is not success evidence.

## Final editor check, separate from factual and CI checks

Read the draft as a returning viewer before queueing. State in one sentence what they
learn that our previous videos did not teach. Can they name a use and a first step?
Does the opening deliver what the title promises? Are dates, access and limitations
visible? Would the story still matter without its headline number or code block?
Reject or rewrite any item failing these checks. A passing test suite cannot override
an editorial failure. Record the verdict and specific reasons in editorial_review.

Calibration: the 24 September Sora countdown, fixed-token price ratio and synthetic
66.7% permission statistic are not templates to repeat. A documented sandbox feature
could be a good story if it shows a meaningful user workflow and actual constraints;
an invented permission percentage does not demonstrate its benefit.

## Coverage review and topical queues — required from 28 September 2026

For every episode dated 2026-09-28 or later, both the selected JSON and final episode must contain a top-level
`coverage_review` with all five keys: `openai`, `anthropic`, `google`, `repositories`,
`architectures`. Each scope has `status` (`checked` or `unavailable`), `sources` (a list
of exact public primary-source URLs), `decision` (`included`, `deferred`, `rejected`,
`no_qualifying_news` or `unavailable`) and a nonempty `reason`. Checked scopes require
sources actually read and a decision explaining the findings against the archive.
An unavailable scope must use decision `unavailable`, never `no_qualifying_news`.
An inaccessible release page is not evidence that no new release exists.

The mechanical coverage gate blocks queueing/publication while any scope is unavailable.
Complete the review using accessible primary evidence and update that scope to checked;
do not bypass the gate, invent a review or weaken it to meet the schedule. Every new
model release found must receive an explicit included/deferred/rejected decision in
editorial_review. Checking every scope is mandatory; publishing every scope is not.
The review is required for manual research as well as scheduled production.

Assign every production candidate a topic: `models`, `repositories`, `architectures`,
`agents` or `guides`. Keep states `candidate`, `source_verified`, `editorial_ready`,
`queued`, `published`, `deferred`, `rejected`. Preserve event date, primary evidence,
audience/task, archive comparison, format, next review date and deferral/rejection reason.
Evergreen guides remain Method; timely repository or research developments may be Daily.
Read docs/CONTENT_STRATEGY.md for playlist descriptions and the channel promise.

Read prompts/playlist.md and prompts/playlists/<primary_playlist>.md before writing.
Choose exactly one primary_playlist and a matching prompt_profile; approve the whole
video's relevance in playlist_review with status approved, reviewer and reason.
Audience and topic metadata do not assign playlists. Match vocabulary, prerequisites,
examples and first steps to one primary audience. Keep a mixed Daily only when every
story fulfils its chosen playlist's promise; otherwise defer the mismatched story.
Review the rendered script and description against this brief before publication.
