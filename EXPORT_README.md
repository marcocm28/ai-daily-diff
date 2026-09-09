# Export del progetto "AI Daily Diff" — 09/09/2026

Questo archivio contiene **tutto il progetto realizzato fino a oggi**: il codice, i prompt, i
documenti operativi, i due episodi reali prodotti con i loro artefatti, il sito, gli asset e i
workflow di CI.

**Sorgente dell'export:**
- repo pubblico `github.com/marcocm28/ai-daily-diff`, commit `078115a` — *"Real episode 2026-09-02, logo, music bed, decision-shaped selection"*
- documento master `PROJECT_INSTRUCTIONS.md` **v3.0** dal Project su claude.ai (più recente del repo — vedi §3)

Nessuna credenziale è inclusa: lo scan su `refresh_token`, `client_secret`, chiavi API e token
GitHub ha trovato solo **nomi di variabili d'ambiente** in `src/upload.py` e le regole di
esclusione in `.gitignore`. I segreti vivono nei GitHub Secrets, come prescrive §4.3.

---

## 1. Cosa c'è dentro

| Cartella / file | Contenuto |
|---|---|
| `PROJECT_INSTRUCTIONS.md` | **il documento master, v3.0** — la versione più aggiornata |
| `RECIPE.md` · `LEDGER.md` · `SOURCES.md` · `CORRECTIONS.md` | i quattro registri operativi |
| `README.md` | il readme del repo |
| `src/` (10 moduli, ~100 KB) | `ingest.py` `selection.py` `author.py` `schema.py` `brand.py` `render_video.py` `render_artifacts.py` `render_page.py` `thumbnail.py` `upload.py` `analyze.py` |
| `templates/` | `deck.html` `cheatsheet.html` `page.html` `index.html` — il sistema visivo |
| `prompts/` | `daily.md` `deep.md` `method.md` `title.md` `example.md` |
| `data/episodes/` | `2026-09-01.json` (3 item) e `2026-09-02.json` (2 item) — l'unica fonte di verità di ogni episodio |
| `data/inbox/` | i candidati raccolti in ingestion nei due giorni |
| `data/metrics/manifest.csv` | il manifest per il loop di analisi |
| `examples/` | 5 esempi eseguibili, ognuno con `run.sh`, `run.py`, `expected_output.txt` e i config vendorizzati |
| `output/2026-09-01/` e `output/2026-09-02/` | i 4 artefatti renderizzati: `video.mp4`, `slides.pdf`, `cheatsheet.pdf`, `brief.md` + `thumbnail.png` |
| `site/` | l'output GitHub Pages: archivio + pagina per episodio con i PDF |
| `assets/` | logo del canale, letto musicale `daily-bed.mp3`, `CREDITS.md` e `LICENSES.md` |
| `.github/workflows/` | `test.yml` (Gate 2) · `pages.yml` · `upload.yml` |
| `tests/test_schema.py` | validazione dello schema + guardia sui nomi che collidono con la stdlib |
| `tools/` | `assemble_episode_2026-09-01.py` e `assemble_episode_2026-09-02.py` |
| `_export_docs/` | materiale aggiunto da questo export, non presente nel repo (vedi §3) |

**91 file, ~18 MB** (di cui ~13,5 MB sono i video, i PDF e la musica). La cronologia git non è
inclusa: l'archivio è lo stato del contenuto, non del versionamento.

---

## 2. Stato del progetto al 09/09/2026

**Fase 0 chiusa il 03/09/2026.** Il gate chiedeva un brief completo da dati veri con tutti e
quattro gli artefatti, giudicato pubblicabile da Marco: raggiunto con l'episodio del 02/09. In più:
CI verde su macchina pulita, sito online su `marcocm28.github.io/ai-daily-diff`, e badge CI
guadagnato da un meccanismo invece che autocertificato.

**Cosa è dimostrato e funzionante:**

- la pipeline end-to-end da un solo JSON ai 5 output (video, slides.pdf, cheatsheet.pdf, brief.md, pagina web)
- il render video: Chromium + ffmpeg, 1080p, con il ritmo calcolato dalla formula di §8.3
- il mix audio con livello calcolato dalla loudness misurata, target −18 LUFS (verificato: −18,3 LUFS, LRA 4,0 LU, picco −7,7 dBFS)
- Gate 1 nel codice: nessuna slide senza `source_url`
- Gate 2 in CI su runner GitHub pulito: 5 esempi su 5 verdi
- la selezione con i pesi orientati alla decisione (`blast_radius` 0,35 · `decision_relevance` 0,30) e il `_breakdown` tracciabile
- il sito pubblicato e i due episodi archiviati

**Cosa resta aperto per aprire la Fase 1:**

1. **l'upload del primo video su YouTube** — è l'unico gesto ancora mai eseguito, e apre la fase
2. poi il ritmo di cinque brief a settimana + un Method Diff
3. i quattro punti di §14 non ancora spuntati: ricerca marchio (TMview, EUIPO/USPTO classi 9 e 41),
   ToS e rate limit correnti delle fonti, licenza YouTube Audio Library per l'uso previsto, testo
   corrente della policy *inauthentic content*, caricabilità di un caption track su un video muto
4. l'esperimento #001 (muto contro voce), previsto per le settimane 3-4
5. **rinominare il Project su claude.ai** — la descrizione è ancora quella del canale per bambini,
   archiviata dal pivot del 28/08. Claude non può farlo.

---

## 3. Divergenze trovate durante l'export — da sanare

Sono due, e vanno nella stessa direzione: **il repo è indietro rispetto alle decisioni del 03/09.**

### 3.1 `PROJECT_INSTRUCTIONS.md` — repo alla v2.8, Project alla v3.0

Nell'archivio il file in radice è la **v3.0**, che è la versione buona. La v2.8 del repo è
conservata in `_export_docs/PROJECT_INSTRUCTIONS_v2.8_repo.md`, con il diff completo in
`_export_docs/DIFF_v2.8_to_v3.0.patch` (8 righe rimosse, 39 aggiunte).

La v3.0 aggiunge esattamente tre cose:

- §9.1 riscritta: **il rendering vive in CI**, e Marco porta nel repo solo il JSON dell'episodio e
  gli esempi (pochi KB di testo invece di uno zip da 18 MB)
- §13: la chiusura formale della Fase 0
- §15: due righe nuove nel registro delle decisioni (rendering in CI; il push da sessione Claude
  resta impossibile e si smette di cercare workaround)

**Azione:** caricare la v3.0 nel repo, così le due copie tornano a essere una.

### 3.2 Il flusso di §9.1 v3.0 è deciso ma non ancora implementato

La v3.0 descrive un `render.yml` che riverifica gli esempi, timbra il badge con
`tools/mark_ci_verified.py` e renderizza i quattro artefatti in CI. **Nessuno dei due file esiste
nel repo:**

- `.github/workflows/` contiene solo `test.yml`, `pages.yml`, `upload.yml`
- `tools/` contiene solo i due `assemble_episode_*.py`

Quindi oggi il flusso reale è ancora quello della v2.8: **Claude renderizza in sessione e Marco
porta nel repo anche gli artefatti già renderizzati.** Lo conferma il commento in cima a
`pages.yml`, che dà per scontato che `site/` sia «already rendered ... before commit».

**Azione:** scrivere `render.yml` e `tools/mark_ci_verified.py`. È il lavoro tecnico che chiude la
decisione del 03/09 — e finché non è fatto, il carico di lavoro quotidiano di Marco resta quello
vecchio, non i trenta secondi promessi.

### 3.3 Nota minore

Nei due `data/episodes/*.json` il campo `tested_in_ci` non è presente a livello di item: il badge è
gestito altrove nella catena di render. Se `mark_ci_verified.py` verrà scritto come descritto in
§9.1, va deciso dove scrive il flag — e la scelta va allineata a ciò che leggono `deck.html` e
`cheatsheet.html`.

---

## 4. I due episodi prodotti

### `2026-09-01` — 3 item, il primo episodio reale
| Filone | Item |
|---|---|
| Models & Releases | Qwen3.8-Flash-Next: nuovo `model_type` `qwen4_exp`, MoE a 512 esperti (diff dei config) |
| Cost & Limits | DAMP: stati ricorrenti quantizzati a 9,9 bit per valore in media |
| Claims & Risks | quantizzazione formalizzata come mappa molti-a-uno, con payload innestato |

Durata misurata: **2:05** per 29 stati — contro la specifica a priori di 3:30-5:00. Registrata come
dato, non corretta gonfiando il video (§8.1).

### `2026-09-02` — 2 item, l'episodio che ha chiuso la Fase 0
| Filone | Item |
|---|---|
| Cost & Limits | i prezzi di output dei modelli long-context su una piattaforma vanno da $0,15 a $5+ |
| Tools & Agents | release v0.33.3: i parametri di default definiti nel GGUF vengono rispettati |

È quello approvato da Marco, con musica e logo, ed è quello pubblicato sul sito.

---

## 5. Come far ripartire il lavoro da questo archivio

```bash
pip install -r requirements.txt          # + requirements-dev.txt per i test
python -m pytest tests/                  # schema + guardia sui nomi stdlib
for d in examples/*/; do bash "$d/run.sh"; done   # Gate 2 in locale
```

Il rendering richiede Chromium e ffmpeg. Il render di un episodio parte dal solo
`data/episodes/YYYY-MM-DD.json`: tutti gli altri output sono funzioni pure di quel file, che è la
proprietà su cui si regge l'intera economia del progetto.

**La regola da non rompere, in una riga:** lo stadio 4 (esegui l'esempio e cattura l'output vero)
viene **prima** dello stadio 5 (renderizza). Il giorno in cui un output va a schermo trascritto a
mano invece che catturato, il fossato del progetto è finito e non se ne accorge nessuno dall'esterno
— finché non se ne accorgono tutti.
