# Prompt — author for one playlist and one audience

Read editorial.md and this contract before the Daily, Method or Deep format prompt.
Research covers all five required scopes; the published video fulfils one playlist's
promise. Research breadth does not require a mixed video or multiple placements.

## Decide before writing

Choose `primary_playlist` from everyday, professional, builder, models,
repositories, architectures, agents or guides. Choose one `primary_audience` from
everyday, professional or builder. An audience playlist requires its matching
primary audience. A topic playlist still needs one audience and a coherent level. Apply its audience
profile as a vocabulary/prerequisite overlay without changing the primary playlist.
Repositories and architectures require builder; agents requires professional or
builder. Guides uses Method only; architectures uses Daily or Deep. Everyday and
professional audience playlists use Daily or Method; builder permits all three.
Models, repositories and agents permit all three formats at their allowed levels.

Write a production brief in selected JSON's editorial_review before scaffolding:
playlist key, primary audience, assumed knowledge, one viewer question, one
central subject or task, supported payoff, evidence mode and appropriate format.
Read the chosen playlist description in config/channel.json. The whole video must
answer that description and question: title, opening, examples, vocabulary, first
steps and conclusion. Popular keywords or one relevant slide never justify placement.

## Use the chosen playlist's brief

| Playlist | Authoring brief | Required specialization |
| --- | --- | --- |
| everyday | Explain one useful consumer task: identify the app, demonstrate or document the first action, account access and limits. | No programming assumed. Avoid API budgets, code migrations and architecture jargon. |
| professional | Solve a named work task, such as document review or project tracking. Explain setup, permissions, a useful output and when human review is needed. | Practitioner vocabulary; explain unfamiliar technical terms. Do not substitute developer operations for a workplace task. |
| builder | Explain a technical development or a coherent technical briefing and the implementation or evaluation decision it changes. | Developers/researchers: exact artifacts, API/setup requirements, tests or evaluation plan and limitations. Mixed news is allowed only when every item serves this audience. |
| models | Focus the whole video on verified model releases or model capability changes, their access and what they enable. Compare releases only when they answer one clear viewer question. | Select one audience and keep that level throughout. An app integration is not an underlying model release. |
| repositories | Explain one useful AI repository or a purposeful comparison: actual artifact, license, setup, maintained/release state, task, starting steps and limits. | Usually builder. A passing GitHub link or vendor cookbook citation is not a repository review. |
| architectures | Explain a documented model or system mechanism, its components, supported consequences and research limits. Use the original paper/report/code. | Builder/researcher, with prerequisites named. Never infer closed-model internals or equate app integrations with architecture. |
| agents | Explain one agent capability or workflow: goal, tools, permissions, coordination, output and failure conditions. Show how the parts interact. | Choose professional for an operational task or builder for implementation; do not mix the levels. Mentioning tool use is insufficient. |
| guides | Deliver one practical how-to question with ordered steps, prerequisites, expected result and recovery/limits. | Choose one audience. A news roundup with a one-line first step for each story is not a tutorial. |

## Keep videos coherent

Daily can contain one to three timely stories only if all fulfil the chosen playlist's
promise at the chosen level. Keep other strong stories in their appropriate queues;
do not add a consumer integration to a builder briefing just to cover every vendor.
Prefer a focused one-story video when subjects need different prerequisites. The
existing daily/weekly cadence remains unchanged; queues are not permission to upload
extra videos. Method and Deep use the same playlist brief with the appropriate depth.

From 2026-09-29, audiences contains only primary_audience. For a topical playlist,
topics contains only that primary topic. Audience briefings may describe their actual
multiple topics; none creates a secondary membership. These are content descriptors,
not playlist instructions.
Publish to exactly the reviewed `primary_playlist`; never calculate placements by
concatenating topics and audiences. No automatic secondary playlist. An existing
mixed video is reviewed as a complete video, not classified from its individual items.
If no current playlist fits the whole video, leave it unassigned pending editorial
repair instead of filling unrelated playlists. Do not reupload an identical video to
create the appearance of a separate audience edition.

## Content creator and publisher handoff

Persist `primary_playlist`, matching `prompt_profile` and `playlist_review` in both selected JSON and final
episode. playlist_review records status approved, reviewer and a reason explaining
why the whole script fulfils that playlist at the primary audience's level. The
publisher checks this exact placement before queueing and in the published membership;
missing, conflicting or unsuitable placement blocks publication. The rendered video
and generated description must agree with the reviewed brief. Technical CI alone
cannot approve relevance.

Before approval ask: would someone opening this playlist understand why this entire
video belongs here? Does every story meet their knowledge level? Does it provide the
promised task or explanation? Are any other playlist keywords present only for SEO?
Rewrite or defer a failing story; never solve an editorial mismatch through cross-posting.
