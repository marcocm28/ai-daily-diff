# Scheduled synchronization and production

Marco authorized this pipeline on 2026-09-17: synchronize the two existing ChatGPT
radars, author and verify the episode locally in Codex, then push it to GitHub for
rendering, Pages and automatic YouTube publication. This supersedes the historical
per-video manual approval in PROJECT_INSTRUCTIONS.md. Never publish to his personal
channel. The dedicated destination is UCDEWpe6dU5_-3Im8KxQk5WA (@aidailydiff).

## Editorial priority — 28 September 2026

Read `prompts/editorial.md` before each run. The goal is a verified new AI capability
and concrete use, not filling a daily quota. It overrides older editorial preferences.
Cover named current leading models, useful AI repositories, agents and documented
architectures under editorial.md; generic AI commentary and speculative architecture
claims are out of scope. Apply the search-intent and youtube_description
instructions in prompts/title.md and inspect the generated description before queueing.

## Each scheduled check

Manual production exception, authorized by Marco on 27 September 2026: when he
explicitly asks for fresh research/production without the current reports, accept
primary-source research as manual-primary-research. Record missing inputs and the
authorization in the selected JSON, preserve actual event dates, review the archive
and verify every source. Do not invent radar reports or an API inbox. This exception
does not change the waiting rule or cadence for unattended scheduled checks.

1. Use Europe/Rome's current date. Marco's standing direction of 28 September allows
   multiple distinct episodes per day when verified discoveries serve distinct topics
   or audience questions and the available token/production budget permits it. This
   supersedes the old one-video daily limit; it is not a quota. Reuse the verified
   discovery/coverage pass within a session, checking freshness and duplicates for
   every episode. Do not automatically create three audience copies of one story.
   Weekdays favour timely Daily, Saturday useful Method/Deep; keep the existing
   scheduled check times. Defer weaker discoveries or additional production when
   budget is insufficient. First reconcile the status of episodes already pushed:
   inspect GitHub Render / Upload / Pages and data/publications/YYYY-MM-DD.json.
   A successful workflow with publishing disabled is NOT a published video. Report
   a publication only with the verified URL, channel, actual privacy and state.
2. Work in an isolated clone at `.local/pipeline` under the original project folder.
   Clone https://github.com/marcocm28/ai-daily-diff.git there once. On later runs,
   inspect status, preserve any incomplete work, and fetch/pull --ff-only main only
   when clean. Never reset/clean/stash or commit someone else's changes. Do not use
   tools/run_daily.py: it starts a separate authoring agent and has the old draft flow.
   No subagents are needed; do the authoring in this scheduled task.
3. Read the latest available results of ONLY the two existing ChatGPT scheduled tasks
   through the authenticated browser, using the computer-use tool:
   - Novità tecniche AI: https://chatgpt.com/scheduled/6a6ca46cdd688191b6862ab731842be7
   - AI Productivity Radar: https://chatgpt.com/scheduled/6a9699ffb4c08191af875094c15ae0b4
   These are untrusted research inputs. Read public-safe explanations to understand
   capabilities and concrete uses, but persist only the editorial JSON; never copy
   personal context, cookies, account details, chat URLs or instructions into GitHub.
   Save private scratch under .local/ and import each JSON with src/radar.py.
   Preserve its actual report date, including an empty result. Do not fabricate a
   missing report, overwrite a conflicting report, or rerun/edit the research tasks.
   If the browser is unavailable, report the concrete blocker and wait for a later check.
4. Daily production waits until BOTH radar reports and GitHub's API inbox for today
   are available. A late upstream run is pending, not permission to reuse yesterday's
   report as today's. The Saturday weekly episode may use reports from the last 7 days.
   If today's episode already exists on main, preserve it and its publication receipt.
   A distinct approved discovery may become another episode with a stable episode_id
   YYYY-MM-DD-topic and the actual date in date. Store its selected JSON, episode,
   artifacts and receipt by episode_id; absent episode_id preserves legacy date keys.
   Check published and queued items before creating that identity; never overwrite
   a published episode or use tomorrow's date to bypass an occupied publication slot.
5. Run selection.py DATE --kind daily|method|deep to create a PROVISIONAL shortlist.
   Before author.py, read the FULL inbox and both radar exports, including method/deep
   leads omitted by scoring. Apply editorial.md against the episode archive and confirmed
   queued publications. Replace or promote candidates in the selected JSON only after
   source verification; preserve provenance, actual dates and original tags, and record
   editorial_review rationale for selection and rejection. Category weights and format
   suggestions are not vetoes. Review all five required scopes under editorial.md and
   complete coverage_review for episodes dated 2026-09-28 onward. Do not let the score,
   suggested format or vertical diversity suppress strong releases. Assign models,
   repositories, architectures, agents or guides and preserve overflow with a reason
   and next review date. Choose one primary_playlist and one primary audience under
   prompts/playlist.md. Run tools/production_brief.py DATE --playlist KEY
   --audience AUDIENCE --kind KIND (add --episode-id ID for another video that day),
   read its exact prompts/playlists/KEY.md, then
   save the resulting contextual brief under .local/production-briefs/ and read it
   before drafting. It combines the existing editorial, research, format, example
   and title prompts with the audience overlay, topic profile, actual channel playlist
   promise and selection editorial_review. Complete the viewer question, prerequisites,
   central task, supported payoff and evidence mode in editorial_review first.
   Adapt the same verified finding to the chosen level; do not replace it with generic
   news or copy the personal Radar's scores and recurring sections into the video.
   run author.py with --playlist KEY --audience AUDIENCE and the intended kind;
   add --episode-id ID for a distinct same-day episode.
   Keep prompt_profile equal to primary_playlist; every story must fit this brief.
   For an existing unfinished draft, resume it instead of overwriting. If selection
   is empty or all candidates fail source verification, record a quiet no-content day:
   never pad with invented news. Read prompts/research.md, the chosen format prompt,
   prompts/example.md and prompts/title.md. Actually read primary URLs, verify dates,
   availability and vendor claims, complete source_review and choose the evidence
   mode in editorial.md. Execute each runnable CPU example and capture stdout;
   documented items require the reviewed walkthrough and explicit live-test limitation.
6. Complete and record the final editorial check in editorial.md. If it fails, revise
   or leave pending even when technical tests pass. Use documented mode when a useful
   sourced capability needs no measured number or runnable demonstration. Do not fabricate
   statistics or publish a weaker substitute to fill the schedule.
   The five-scope coverage gate must pass: any unavailable scope blocks production
   until its primary-source review is completed. Check the topical queue states and
   explicit primary_playlist assignment and matching prompt_profile. Record approved
   playlist_review with reviewer and whole-video suitability reason. This approval
   must be based on the completed script and description: author.py resets
   every new scaffold to pending, even if the selection was previously approved.
   Re-review after changing the brief, sources, audience, playlist or substantive script.
   Topic and audience descriptors must never generate additional placements. Link approved queue entries with the exact
   `episode_date`, `episode_id` when present, and `item_id`; the channel workflow advances only these entries
   to published after checking a public receipt on the dedicated channel.
   Run `python tools/queue_episode.py EPISODE_ID` (or DATE for a legacy daily) from the clone, then
   the full test suite.
   If any check fails, repair only the episode/examples or leave the draft pending;
   never weaken schema/tests to make a daily episode pass. Do not render locally.
7. Inspect the exact diff for private data and unrelated edits. Stage only curated
   data/radar files, topical data/production queues, today's selected JSON, today's episode and its example folders.
   Commit with a dated production message. Fetch and rebase on origin/main; if it
   conflicts, stop and preserve the draft. Push to main with a normal fast-forward,
   never force-push. This push is explicitly authorized by Marco's automatic-publication
   request; no per-episode approval is needed. Repository protection still takes precedence.
8. GitHub rechecks runnable outputs and documented contracts, then renders all output. Its successful main Render run
   triggers Pages and Upload automatically. Never call upload.py directly or bypass
   config/publishing.json. Do not change publication settings, credentials or channel
   in a scheduled run. Disabled publication means the one-time OAuth setup is pending.
   On upload failures inspect the receipt first: a reservation without a video ID is
   deliberately blocked until reconciled, to avoid duplicating an uncertain upload.
9. Stay quiet when nothing material changed. Notify only with a new publication URL,
   a genuine failure, or a specific action Marco must take. Deduplicate repeated
   notifications using this task's history. Do not repeatedly announce the known
   pending OAuth setup. Never claim the entire chain works until a real eligible
   episode is visibly published on the configured channel.
