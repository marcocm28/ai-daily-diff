# Music — track, source, license

The silent format needs a bed: two minutes of silence reads as a broken video. But it sits
*under* the reading — mixed at −15 dB with 1.5 s fades, looped to length by
`src/render_video.py`. One track for the Daily and one for the Deep, kept for good: they become
the channel's sonic signature.

What to look for: ambient or minimal, no vocals, no prominent drums, no build-and-drop, loopable,
1–3 minutes.

Where to get it, in order of preference:

1. **YouTube Audio Library** (YouTube Studio → Audio Library) — filter "no attribution required",
   genre Ambient/Cinematic, mood Calm. Zero claim risk *on YouTube*, which is where the video runs.
2. **Pixabay Music** — permissive license and usable off YouTube too (the site, and the phase-3
   newsletter). The better choice if the audio will ever leave YouTube.
3. **Incompetech** (Kevin MacLeod), CC BY — huge catalogue, needs a credit line in the description.

Avoid: anything labelled "royalty free" from a YouTube compilation, and Epidemic Sound (paid).

| File | Used for | Track / artist | Source | License | Attribution required | Added |
|---|---|---|---|---|---|---|
| `daily-bed.mp3` | Daily Diff | "Nebula" — The Grey Room / Density & Time | YouTube Audio Library (youtube.com/audiolibrary) | Standard YouTube License — **attribution not required** (confirmed by Marco, 2026-09-03) | no, but credited anyway | 2026-09-03 |
| — | Method / Deep | — | — | — | — | — |

**License, settled 2026-09-03:** taken from the Audio Library's "attribution not required"
filter, so **no credit is owed**. We put one in the description anyway (`src/brand.py::MUSIC_CREDIT`)
because it costs one line and removes any question about where the audio came from. Being a choice
rather than an obligation, it can be dropped without consequence — unlike a Creative Commons
track, where the credit would be mandatory in every single video.

**Measured on arrival (2026-09-03)**, before it went anywhere near a video:

| Measure | Value | Reading |
|---|---|---|
| Duration | 3:09 (189.5 s) | longer than a Daily, so no loop point is ever heard |
| Integrated loudness | −11.6 LUFS | loud as delivered; the renderer computes the gain down to −18 |
| Loudness range (LRA) | 4.1 LU | **flat** — no swells, no build-and-drop. This is the number that matters for a bed |
| True peak | −1.0 dBFS | headroom fine |

Stored at 128 kbps stereo (3.0 MB) rather than the 320 kbps original (7.6 MB): a bed that plays
at −18 LUFS under text does not need 320, and an mp3 committed to git is there for good.
