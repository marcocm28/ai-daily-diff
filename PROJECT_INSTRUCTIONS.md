# ISTRUZIONI DEL PROGETTO — "AI Daily Diff": quotidiano AI in inglese, da slide, con materiali scaricabili

> **Versione:** 3.0 — 03/09/2026. Rendering spostato in CI: il lavoro manuale di Marco scende a trascinare due file nel browser (§9.1, §11). **Fase 0 chiusa:** pipeline provata end-to-end, CI verde, sito online, badge guadagnato (§13). Cadenza rifatta: il settimanale diventa il **Method Diff**, motore di acquisizione (§2.5, §8.2). Filoni e selezione attorno alla decisione (§2.3, §5, §9.2); logo, loghi vendor e musica (§8.4, §8.5). Sostituisce la v2.1 (nome cambiato da "Runnable"). (La v1.0, canale per bambini, è archiviata.)
> **Owner:** Marco
> **Natura del documento:** file operativo master. Ogni sessione di Claude lo legge per intero prima di agire, e lo aggiorna quando una decisione cambia.

---

## 0. Come si usa questo file

**Aggiornamento editoriale 25/09/2026 — richiesta di Marco, prevale sulle regole editoriali storiche.**
Leggere `prompts/editorial.md`: scoprire capacità e usi AI nuovi, verificati e non già
raccontati, con un caso d'uso e un primo passo comprensibili. Controllare archivio e
coda prima della selezione. Prezzi, dismissioni, punteggi e tag non prevalgono sul
valore della novità. Niente numeri artificiali, esempi vuoti o notizie riempitive.
La fedeltà si conquista con utilità e continuità, senza promettere novità certe domani.
Schema, CI e controlli di pubblicazione restano obbligatori. La revisione editoriale
è distinta dai test tecnici; il settimanale può insegnare un metodo evergreen inedito
per il canale senza presentarlo come una nuova uscita.

**Aggiornamento operativo 17/09/2026 (prevale anche sul gate umano storico).**
Marco ha richiesto la sincronizzazione e pubblicazione end-to-end automatica, scegliendo
Codex sul PC e rendering/upload su GitHub. `prompts/scheduled-pipeline.md` governa il
task ricorrente; `docs/AUTOMATION.md` documenta avvio, recupero e collegamento OAuth.
Gli episodi verificati vengono accodati con `tools/queue_episode.py` e inviati su main.
Render produce un artefatto verificato; Pages e Upload lo consumano automaticamente.
Destinazione unica: @aidailydiff, ID UCDEWpe6dU5_-3Im8KxQk5WA. Il vecchio token punta
al canale personale e deve essere ricollegato; un ID diverso blocca ogni upload.
La configurazione richiede public e registra la visibilità effettiva e l'ID del video.
I vecchi video senza publication.ready non vengono ripubblicati. Nessun rendering locale.

**Aggiornamento operativo 16/09/2026 (prevale sulle descrizioni storiche sotto).**
I due radar ChatGPT di Marco, AI Productivity Radar e Novità tecniche AI, alimentano
la selezione tramite JSON editoriali in `data/radar/`; procedura in
`docs/RADAR_INTEGRATION.md`, regole in `prompts/research.md`. Il report è una pista:
la fonte primaria va letta e documentata in `source_review`. Nessun dettaglio privato
del profilo entra nei contenuti del canale. La sincronizzazione dal profilo richiede
import esplicito/lettura assistita: GitHub non accede all'account ChatGPT.

Pipeline corrente: ingest schedulato su GitHub → selezione unita ai radar importati →
authoring locale → PR e anteprima CI → revisione di Marco → render su main → Pages
dall'artefatto della stessa run verificata. Upload YouTube separato e manuale.
I report Method/Deep sono selezionabili con `selection.py --kind method|deep`.
La soglia 0,55 e la finestra 4→7 giorni sono applicate; la deduplica usa gli episodi
già presenti su main, non le semplici selezioni. Versioni dirette Python fissate,
runtime 3.12, esempi portabili Windows/Linux, confronto anche con l'output nel JSON.

1. Leggi questo file per intero.
2. Leggi `RECIPE.md`, `LEDGER.md`, `SOURCES.md`. Se non esistono, creali dai template in §10.
3. Non riaprire le decisioni chiuse in §2 senza evidenza numerica dal ledger. Ogni cambio va scritto in §15.
4. **Marco deve rinominare il Project su claude.ai** (è ancora "canale youtube con video per bambini") e riscriverne la descrizione. Claude non può farlo.

---

## 1. Il canale in una frase

> **Un quotidiano delle novità AI in inglese in cui ogni affermazione ha un esempio che gira davvero, e ogni episodio lascia in mano qualcosa da tenere.**

Il notiziario è la forma. Il prodotto sono due cose: la **riproducibilità** (§3) e i **materiali scaricabili** (§7). Insieme trasformano il canale da trasmissione a risorsa di apprendimento — che è ciò che nessun canale di slop può imitare, perché richiede di aver capito davvero l'argomento.

### 1.1 Metriche

| Orizzonte | Metrica | Target |
|---|---|---|
| Giorno 14 | Pipeline end-to-end, brief pubblicati | 10 |
| Giorno 30 | Brief + Deep pubblicati | 20 + 4 |
| Giorno 30 | Views totali | ≥ 3.000 |
| Giorno 60 | Average % viewed sul brief | ≥ 45% |
| Giorno 60 | Download di cheat sheet / views | ≥ 3% |
| Giorno 90 | Views totali | ≥ 50.000 |
| Giorno 90 | Iscritti | ≥ 1.000 |
| Giorno 120 | Ore di visualizzazione (12 mesi) | ≥ 4.000 |
| Sempre | Esempi falliti in CI e pubblicati comunque | **0** |

L'ultima riga è la più importante. Un solo esempio rotto, pubblicato, distrugge la sola cosa che differenzia il canale.

**Metrica di processo:** esperimenti chiusi con conclusione numerica nel ledger. Una settimana con 5 video e nessuna conclusione scritta è una settimana sprecata.

---

## 2. Decisioni chiuse

### 2.1 Nome: **AI Daily Diff** — serie *Daily Diff* e *Deep Diff*
Handle `@aidailydiff`, **verificato libero il 28/08/2026**. (Il nome precedente, "Runnable", è stato scartato: `@runnable` è un canale gaming turco esistente, e la parola non diceva nulla a chi non conosce già il canale.)

**Perché questo nome.** "AI Daily" porta la categoria cercabile e la promessa di aggiornamento continuo; "Diff" è il termine che gli sviluppatori usano per *esattamente cosa è cambiato* — in una parola dice cos'è il canale, ed è distintivo abbastanza da essere posseduto.

**Da tenere presente per non sprecare energie:** il nome del canale è una leva SEO debole. YouTube posiziona i *video*, non i canali, sulle query di argomento: quello che ranka è il titolo. I lavori reali del nome sono tre — leggibilità sotto ogni miniatura al momento del click, richiamo (la parola che si digita per ritrovarci), e posizionamento su Google, che passa più dal sito GitHub Pages che da YouTube. **L'ottimizzazione SEO vera vive nei titoli dei video e nelle pagine di §7, non nel nome.**

Handle verificati occupati, da non riproporre: `@runnable`, `@aichangelog`, `@aipatchnotes`, `@aidailybuild`, `@thedailydiff`. Verificati liberi come riserva: `@theaidiff`, `@aireleasenotes`, `@aidailytested`.

Resta da fare in fase 0: ricerca marchio su TMview ed EUIPO/USPTO, più una ricerca Google per omonimie note (podcast e newsletter).

### 2.2 Lingua: inglese
Il formato muto rende la localizzazione futura quasi gratuita: si sostituisce lo strato di testo e si rirenderizza. Vantaggio da sfruttare in fase 4.

### 2.3 Pubblico
- **Primario:** chi costruisce con l'AI — ML/backend engineer, data scientist, tech lead, fondatori tecnici. Segue già HN e r/LocalLLaMA. Ha già visto dieci canali di slop e li disprezza.
- **Secondario:** professionisti non-ingegneri che devono capire cosa cambia (PM, ricercatori, decisori).
- **Vuole:** sapere in 4 minuti cosa è cambiato, poterlo verificare, e avere una pagina da salvare. **Odia:** hype, claim senza fonte, tempo perso.
- **Deciso il 02/09/2026 — il criterio di scelta di ogni notizia:** lo spettatore deve poter
  **prendere una decisione** (cambiare modello, stimare un costo, aggiornare o rimandare, patchare
  prima di una rottura). Non "restare aggiornato": quello è ciò che fanno tutti, ed è la commodity.
  Questa riga è il filtro che ha rifatto i filoni di §5 e i pesi di §9.2.

### 2.4 Formato: muto — testo a schermo, codice che si costruisce, musica
**A favore:** elimina il rischio più grande (su pubblico tecnico la voce TTS è *il* marchio dello slop); 100% deterministico; localizzabile; molti guardano in mute.

**Contro, da progettare e non subire:**
- **Il ritmo va calcolato**, non narrato → formula in §8.3, ed è una variabile del ledger.
- **Perdita SEO:** senza parlato non c'è trascrizione da indicizzare. **Mitigazione: §7.** Gli artefatti scaricabili e le pagine GitHub Pages recuperano più indicizzazione di quella persa — la richiesta di Marco sui materiali scaricabili risolve per caso la debolezza maggiore del formato muto.
- **Rischio in revisione YPP:** "slideshow con musica senza commento" è vicino a ciò che YouTube considera basso sforzo. Difese: analisi originale, codice testato, grafici costruiti da noi, materiali scaricabili originali, gate umano. Piano B: voce di Marco sul solo Deep.

**È la scommessa numero uno del progetto**, e per questo è l'esperimento #001 (§10.4), non una convinzione.

### 2.5 Cadenza — **rifatta il 02/09/2026**
- **Daily Diff** — ogni giorno lavorativo, 3 item di notizie. Durata: quella che dice la formula (§8.1).
- **Method Diff** — 1/settimana, 4-6 min, **un'attività e un metodo misurato**, con il titolo a
  forma di query. Variante occasionale dello stesso slot: il **Deep Diff** 10-15 min, per i pattern
  emergenti e le verifiche a più stadi. Uno slot settimanale, due forme possibili, mai entrambe.

**Perché il settimanale è il motore di acquisizione, e il Daily no.** Il traffico evergreen su
YouTube arriva dalla ricerca, e la ricerca premia i video **il cui titolo è la domanda**. Un item di
metodo dentro un brief prende quaranta secondi e resta sotto un titolo che dice "AI Daily Diff Sep
2": quella query non la intercetta mai. Serve un video il cui titolo *sia* la query — quindi il
metodo deve essere un video suo, non un item.
E conta specialmente adesso: **un canale con zero iscritti non riceve traffico da home e
consigliati.** Nei primi mesi le views realistiche vengono da ricerca e link esterni, cioè dove
vince l'evergreen. Il lavoro del Daily nei primi due mesi non è portare views: è far girare la
macchina, riempire l'archivio del sito e dare agli iscritti un motivo per tornare.

**Costo, ed è il vincolo vero:** un item di metodo è il tipo di contenuto più caro che produciamo
(stub deterministico + misura + inquadramento onesto). Con ~3 h/settimana (§11), uno al giorno era
insostenibile *e* inefficace: è il motivo per cui è stata scartata l'ipotesi "un item di metodo
fisso ogni giorno", che sembrava la più ambiziosa ed era la peggiore.

Shorts: rinviati a fase 3 (la pipeline li darà quasi gratis, ma triplicano il volume da revisionare).

### 2.6 Cinque filoni — **rivisti il 02/09/2026**
Models & Releases · Cost & Limits · Tools & Agents · Media Generation · Claims & Risks.
(Prima erano Architectures & Models · Agents & Prompting · Video & Image Generation · Data &
Evaluation · Serving, Inference & Cost: tassonomia da ricerca, che spingeva la selezione verso i
paper. Il pubblico non è cambiato, il criterio sì — vedi §2.3 e §5.)
Ogni item appartiene a **esattamente un** filone. Il Daily bilancia i filoni nel tempo, non dentro il singolo episodio. Specifica operativa completa in §5.

### 2.7 Ogni episodio produce quattro artefatti — non solo il video
Decisione di Marco, ed è la più importante di questa revisione: video, `slides.pdf`, `cheatsheet.pdf`, `brief.md`. Tutti generati dalla stessa sorgente, tutti gratuiti. Specifica in §7. **Verificato funzionante il 28/08/2026** — vedi §9.

### 2.8 Identità visiva: il diff
Il nome regala al canale un linguaggio visivo nativo del tema, e va usato: la slide *what changed* si renderizza **come un diff vero** — riga `−` in rosso per il prima, riga `+` in verde per il dopo, in monospazio. **Implementato e verificato il 28/08/2026** nel deck e nel cheat sheet.

Perché conta più di un vezzo grafico:
- È **immediatamente leggibile** per il pubblico primario, che legge diff tutti i giorni: comunica "cosa è cambiato" senza una parola di spiegazione. Nel formato muto (§2.4) questo vale doppio.
- È **gratuito e deterministico** — è CSS, non un'immagine.
- **Nessun altro canale AI lo fa**, e non è imitabile a buon mercato: funziona solo se hai capito la notizia bene abbastanza da ridurla a un prima e un dopo. È il fossato di §3 reso visibile in due righe.
- Impone una disciplina utile: se un item non si riduce a una riga `−` e una riga `+`, o non è una notizia, o è un Deep.

### 2.9 Nessuna AI generativa per immagini, video o voce
Claude scrive testi e codice; nessun pixel e nessun suono è generato da un modello. Determinismo, costo zero, nessun obbligo di disclosure, nessun segnale di slop.

---

## 3. Il fossato: la riproducibilità, resa meccanica

L'unico vantaggio difendibile. Perché funzioni deve essere **un meccanismo, non un'intenzione.**

### Gate 1 — Ogni claim ha una fonte primaria
- Ogni item è un oggetto JSON con `source_url` obbligatorio verso il **sorgente primario** (paper, repo, blog ufficiale, model card) — mai verso un articolo che ne parla.
- **`source_url` vuoto → la slide non viene renderizzata.** Vincolo nel codice.
- Nessun numero a schermo che non sia (a) citato letteralmente dalla fonte, o (b) calcolato dal nostro codice testato. Nessuna terza via.
- Nessun risultato di benchmark senza nome del benchmark e suo URL.

### Gate 2 — Ogni esempio gira in CI
- Ogni esempio in `examples/YYYY-MM-DD-slug/` con `run.sh` e `expected_output.txt`.
- Vincoli: CPU, meno di 60 secondi, solo pacchetti pip/npm gratuiti, nessuna chiave API a pagamento.
- GitHub Actions li esegue **tutti** a ogni push. **Esempio rotto → il video non si pubblica.**
- Il badge `TESTED IN CI ✓` compare sulla slide e sul cheat sheet **solo** se il test è passato in quella run. È un output del sistema, non grafica.
- Il test deve girare su GitHub, non nella sessione di Claude: il badge va guadagnato su una macchina pulita, non sulla mia parola.

### Politica delle correzioni
Sbaglierai. Ciò che costruisce fiducia non è l'assenza di errori ma come li tratti: commento fissato in cima entro 24h, slide di correzione nel brief successivo, riga in `CORRECTIONS.md`, cheat sheet ripubblicato con nota di errata. Una correzione visibile vale più di dieci video senza errori.

---

## 4. Vincoli non negoziabili

### 4.1 Accuratezza
- Mai attribuire a un'azienda o a un autore qualcosa che non sia nella fonte primaria.
- Mai presentare un preprint come risultato consolidato: **i paper arXiv non sono peer-reviewed, e la slide lo dice.**
- Mai trasformare "un ricercatore ha twittato" in "X ha annunciato".
- Nessun titolo che promette più di quanto la fonte sostenga.
- **Nessun fatto entra in una slide dal solo modello.** Entra dal testo recuperato dalla fonte. Se non è nel testo recuperato, non esiste.

### 4.2 Policy YouTube
- **Inauthentic content:** un canale automatizzato quotidiano è per definizione nel raggio di questa policy. Difese: sintesi e analisi originali, codice originale testato, grafici costruiti da noi, materiali scaricabili originali, **e il gate di approvazione umana su ogni video, che non si automatizza mai.**
- Niente clickbait, miniature ansiogene, keyword stuffing.
- Nessuna disclosure di contenuto sintetico necessaria (§2.8). Riverificare se lo stack cambia.
- Contenuto per adulti: **non** Made for Kids. Commenti, community e monetizzazione piena disponibili.

### 4.3 Legale e fonti
- **Solo API ufficiali e feed RSS.** Rispetto di robots.txt e dei ToS di ogni fonte. Rate limit conservativi.
  → *Caso concreto già incontrato: l'API di arXiv è esclusa da robots.txt per i fetcher automatici. Si usa il feed RSS (`rss.arxiv.org/rss/<categoria>`), che è la via prevista. Quando una fonte dice no, si cambia strada, non si aggira.*
- **Mai riprodurre le figure dei paper.** Le licenze arXiv variano per paper. I grafici si **ricostruiscono dai numeri** con matplotlib.
- Citazioni brevi di abstract con attribuzione e link. Mai testo lungo.
- Marchi: nominarli è legittimo; non usare i logo come soggetto della miniatura né in modo che suggerisca approvazione.
- Musica: **solo YouTube Audio Library** o CC0 verificata, con fonte e licenza in `assets/music/LICENSES.md`.
- Font: solo licenze libere (SIL OFL) — Inter e JetBrains Mono.
- **Nessuna credenziale in un doc del Project, in chat, o nel repo.** I token vivono nei GitHub Secrets o sulla macchina di Marco. Se una sessione futura te ne chiede uno, la risposta è no.

---

## 5. I cinque filoni — specifica operativa

> **Rifatti il 02/09/2026.** I filoni precedenti erano modellati sulla *ricerca* (architetture,
> dati, valutazione): funzionavano come tassonomia, ma spingevano la selezione verso paper di
> nicchia — ed è esattamente come il primo episodio è finito con due preprint arXiv. Questi sono
> modellati sulla **decisione**: la domanda che ogni item deve poter chiudere è *cosa faccio
> diversamente domani*. Pubblico invariato (§2.3): chi costruisce con l'AI.

Per ciascuno: cosa include, la **soglia** oltre cui è notizia, le fonti, che forma prende *il
numero*, e che forma prende *l'esempio eseguibile* — quest'ultima riga decide se il filone può
rispettare il Gate 2.

---
### Filone 1 — **Models & Releases**
**Include:** modelli rilasciati (pesi o API), varianti quantizzate ufficiali, cambi di finestra di
contesto o di licenza, nuove famiglie architetturali *quando esiste un checkpoint*.
**Non include:** modelli annunciati e non disponibili, movimenti di leaderboard, "annunci di annunci".
**Soglia:** si può scaricare o chiamare **oggi**. Un config pubblicato conta; un teaser no.
**Fonti:** HF `/api/models?sort=trendingScore`, blog e model card ufficiali, changelog dei vendor.
**Il numero:** parametri attivi, contesto, KV cache per token, VRAM richiesta, delta su un benchmark nominato.
**L'esempio:** ispezione di config e tokenizer, diff del config contro il predecessore, aritmetica
della memoria. CPU, offline, con i config vendorizzati nella cartella dell'esempio.

---
### Filone 2 — **Cost & Limits**
**Include:** prezzi per token, variazioni di prezzo, quote e rate limit, costo del caching, cosa
gira su hardware normale, costo di serving self-hosted.
**Soglia:** un numero ufficiale è cambiato, oppure il costo di uno scenario reale si può calcolare.
**Fonti:** **OpenRouter `/api/v1/models`** (prezzi di centinaia di modelli, JSON, senza chiave —
verificato raggiungibile il 02/09/2026), pagine di pricing ufficiali sorvegliate a hash (§9.1),
release dei motori di serving (vLLM, llama.cpp, SGLang).
**Il numero:** $/1M token, costo per richiesta di uno scenario concreto, token/s, footprint di memoria.
**L'esempio — il più forte del canale:** aritmetica dei costi sui prezzi veri del giorno. È
riproducibile per costruzione, gira in un secondo su CPU, e risponde alla domanda che il pubblico
si pone davvero. **È il filone da presidiare.**

---
### Filone 3 — **Tools & Agents** — *riscritto il 02/09/2026 sui prompt di Marco*
**La domanda che definisce il filone**, e vale più di qualsiasi elenco di argomenti:

> *È stato pubblicato o documentato un modo migliore, più veloce o più affidabile di fare
> un'attività reale con ChatGPT, Claude, Codex o un agente?*

Non "cosa è uscito", ma "cosa posso fare oggi meglio di ieri". Questo filone **non riporta
notizie**: riporta metodi.

**Include:** metodologie e workflow documentati, architetture agentiche (planner/executor,
orchestrator/workers, critic, subagent, model council), context engineering (memoria,
compressione, progressive disclosure, `AGENTS.md`, `CLAUDE.md`, project instructions), tecniche di
prompting **con effetto misurato**, MCP server, skill, plugin, tool calling, librerie e runtime.
**Non include:** liste di "10 prompt magici", tecniche senza misura, thread motivazionali,
annunci di prodotto senza un metodo dentro.
**Soglia:** esiste una documentazione, un repo o un esempio **riproducibile**. Un aneddoto della
community è un *segnale*, non un item — la distinzione che i prompt di Marco già fanno bene:
*esperienza raccontata* ≠ *tecnica documentata*.
**Fonti, in ordine di priorità:** documentazione ufficiale (OpenAI Cookbook, Anthropic Cookbook,
Claude Code, Model Context Protocol) — sorvegliata **via commit**, che è il feed che le pagine HTML
non danno; poi GitHub search su repo aggiornati di recente (query in `src/ingest.py::GITHUB_SEARCHES`,
**senza filtro sulle stelle**: un repo piccolo con un'architettura interessante è esattamente ciò
che i feed grandi si perdono); poi HN, Reddit, X e blog **solo come segnale di interesse**.
**Il numero — e qui il canale prende posizione:** token per task, passi per completamento, tasso di
retry, success rate su un task fisso. **Niente "IMPACT SCORE X/10".** Un punteggio che ci diamo da
soli non è falsificabile e contraddice §6: il numero viene dalla fonte o lo calcola il nostro
codice. Su un pubblico che verifica, un voto arbitrario insinua che il resto sia arbitrario.
**L'esempio:** dove serve un modello vero, **stub deterministico** — un finto LLM guidato da uno
script, che dimostra la struttura (loop di controllo, packing del contesto, retry, conteggio token,
costo). **Va scritto sulla slide quando l'esempio è uno stub.**
**Perché questo filone conta più degli altri quattro nel tempo:** è il solo che produce **traffico
evergreen**. "Come fare code review con Claude" si cerca per mesi; il config di un modello per tre
giorni. Ed è il filone che rende il cheat sheet un oggetto che si passa a un collega — che è la
distribuzione più economica che il canale possa avere (§7.1).
**Volume atteso:** il più alto di tutti, e in crescita. Il vincolo qui è la qualità, non la quantità.

---
### Filone 4 — **Media Generation**
**Include:** modelli e tool per video, immagini e audio, workflow, metodi di controllo, **termini di
licenza**, requisiti hardware.
**Soglia più alta degli altri, deliberatamente:** entra quando c'è qualcosa di **usabile, prezzato o
licenziato diversamente**. Un paper che descrive un metodo non entra: è il filone più affollato di
concorrenza e quello dove il nostro Gate 2 può fare meno.
**Fonti:** HF filtrato su diffusers e text-to-video, ecosistema ComfyUI, blog ufficiali.
**Il numero:** VRAM, secondi per frame, passi di denoising, risoluzione, termini di licenza.
**L'esempio — qui si analizza, non si genera:** fabbisogno di VRAM dalla model card, dimensione del
latente in funzione della risoluzione, noise schedule ricostruito in numpy, confronto programmatico
delle licenze. **Da dire, non nascondere:** in questo filone l'artefatto eseguibile è la matematica
o l'ispezione. Il canale racconta l'AI generativa senza usarla, ed è una posizione, non un limite.

---
### Filone 5 — **Claims & Risks**
**Include:** deprecazioni e breaking change con una data, incidenti di sicurezza, claim che non
regge alla verifica, benchmark che ingannano, contaminazione dei dataset, differenze fra il modello
certificato e quello deployato.
**Soglia:** una data di rottura annunciata, oppure un claim pubblico che possiamo mettere alla prova
con il nostro codice.
**Fonti:** pagine di deprecazione dei vendor **sorvegliate a hash** (OpenAI, Anthropic, Google),
HF `/api/datasets`, arXiv (`cs.LG`, `cs.CL`) quando il risultato è metodologico e verificabile.
**Il numero:** giorni al breaking change, % di overlap o contaminazione, varianza tra seed,
differenza fra il claim e la nostra misura.
**L'esempio:** far girare la verifica. È il filone che costruisce fiducia più di ogni altro, perché
è l'unico dove diciamo *no, questo numero non torna* — e nessun canale di riciclo lo fa.

---
### 5.1 Il registro delle fonti
`SOURCES.md` tiene una riga per fonte: endpoint, tipo (`kind`), filoni serviti, rate limit, ultimo
controllo e **resa storica**. Il loop B (§10.2) usa quel dato per retrocedere o disattivare le fonti
rumorose.

**Regola trasversale:** HN e Reddit dicono *a cosa la gente tiene*; la fonte primaria dice *cos'è
vero*. Un item si pubblica solo con la seconda.

### 5.2 Il meccanismo delle pagine sorvegliate
Prezzi e deprecazioni non hanno feed. `src/ingest.py` scarica quelle pagine, ne calcola l'hash del
testo e **produce un candidato solo quando l'hash si muove**. È letteralmente un diff, ed è la
fonte con la più alta rilevanza decisionale che esista: nessun RSS ti dice che ieri un prezzo è
cambiato. Il candidato è una **pista, non una notizia**: va aperto, diffato a mano e verificato.

---

## 6. Lo schema canonico di un item

**Identico per ogni item, ogni filone, ogni giorno.** Cinque tempi:

| # | Tempo | Regola |
|---|---|---|
| 1 | **WHAT CHANGED** | una frase, nessun gergo non spiegato, nessun linguaggio da comunicato stampa |
| 2 | **WHY IT MATTERS** | la conseguenza per chi costruisce, non l'importanza in astratto |
| 3 | **THE NUMBER** | **una sola** quantità, presa dalla fonte o calcolata dal nostro codice |
| 4 | **RUN IT** | l'esempio minimo, con il badge CI |
| 5 | **SOURCE** | URL primario, sempre a schermo, mai accorciato |

### 6.1 Perché questo schema rende il contenuto facile da apprendere
Non è una scelta estetica. È la richiesta di Marco — "strutturarle in maniera chiara e facile da apprendere" — tradotta in vincoli:

- **La prevedibilità abbassa il carico cognitivo.** Chi guarda impara il contenitore una volta; dal terzo episodio sa già dove comparirà il numero e dove il codice. Tutta l'attenzione va al contenuto, nessuna alla navigazione. **Nel formato muto questo conta il doppio**, perché non c'è una voce che segnali "e adesso viene la parte importante".
- **Un numero solo, mai tre.** Una quantità si ricorda; una tabella no. Se un item ha tre numeri interessanti, sono tre item o è un Deep.
- **L'esempio è l'ancora di memoria.** Le persone ricordano ciò che hanno eseguito, non ciò che hanno guardato. È anche il motivo per cui l'esempio deve stare sotto i 60 secondi: oltre, non lo esegue nessuno.
- **Il gergo si paga una volta.** Ogni acronimo o termine viene espanso alla prima comparsa, sulla slide. Nessuna eccezione, nemmeno per quelli che "sanno tutti".
- **Tre livelli di profondità sullo stesso contenuto**, ed è la scala che gli artefatti di §7 rendono possibile:

| Livello | Artefatto | Tempo | Cosa produce |
|---|---|---|---|
| Sapere che esiste | video, 4 min | 4 min | consapevolezza |
| Poterlo spiegare | cheat sheet, 1 pagina | 3 min | ritenzione |
| Saperlo fare | esempio eseguibile | 10 min | competenza |

Ogni livello è completo da solo e ogni livello è un passo più a fondo. **È questa scala che trasforma il canale da trasmissione a risorsa** — e nessun canale automatizzato può costruirla, perché il livello 3 richiede di aver capito l'argomento.

### 6.2 Vincoli di forma
Massimo **22 parole per slide**. Un numero per item. Un esempio per item. Massimo 3 item per brief. Nessuna slide senza `source_url`.

---

## 7. I quattro artefatti di ogni episodio

**Una sorgente, cinque uscite.** `data/episodes/YYYY-MM-DD.json` è l'unica fonte di verità dell'episodio; video, slide, cheat sheet, brief testuale e pagina web sono tutte funzioni pure di quel JSON. Nessun contenuto viene riscritto a mano in due posti: è la ragione per cui aggiungere gli artefatti costa quasi nulla.

| Artefatto | Formato | Cosa contiene | Verificato |
|---|---|---|---|
| **Video** | MP4 1080p, 3:30-5:00 | i 3 item, muto | 27 s in 19,6 s di CPU, 430 KB |
| **`slides.pdf`** | PDF 16:9, vettoriale | una pagina per slide, tutto rivelato, testo selezionabile | 5 pagine, 151 KB, ~1 s |
| **`cheatsheet.pdf`** | PDF A4, tema chiaro, stampabile | una pagina per item: schema di §6 + codice completo + tabella di tutte le fonti | 1 pagina, 125 KB, ~2 s |
| **`brief.md`** | testo | il brief completo con tutti gli URL | 1 KB |

Il quinto output è la **pagina web** dell'episodio, generata dallo stesso JSON.

### 7.1 Perché il cheat sheet è l'artefatto più strategico
- È l'unico che le persone **salvano e condividono**. Un buon cheat sheet finisce nei canali Slack dei team, e quella è la distribuzione più economica che il canale possa ottenere: un video si guarda da soli, un cheat sheet si passa a un collega.
- È tema chiaro e stampabile per una ragione precisa: il video è scuro perché si guarda, il cheat sheet è chiaro perché si stampa e si annota.
- Va pubblicato **CC BY 4.0**. Chiedere l'attribuzione e regalare la condivisione è lo scambio giusto.

### 7.2 Dove vivono: GitHub Pages
Gratuito, e fa tre lavori insieme:
1. **Ospita i download.** La descrizione YouTube linka `<org>.github.io/ai-daily-diff/YYYY-MM-DD/`.
2. **Recupera la SEO persa dal formato muto** (§2.4). Il testo di ogni brief diventa una pagina web indicizzabile, con i termini tecnici, i nomi dei modelli e i numeri. Questa è più indicizzazione di quella che avrebbe dato una trascrizione — la richiesta di Marco risolve la debolezza maggiore del formato muto.
3. **Diventa l'archivio della newsletter** in fase 3, a costo marginale nullo: il contenuto testuale è già prodotto.

```
<org>.github.io/ai-daily-diff/
├── index.html              archivio, ultimi 30 episodi
└── 2026-11-12/
    ├── index.html          il brief in testo, con i link — la pagina indicizzabile
    ├── slides.pdf
    ├── cheatsheet.pdf
    └── (link a examples/2026-11-12-*/ nel repo)
```

### 7.3 Cosa va nella descrizione YouTube
Obbligatorio in ogni video: il brief completo in testo, tutti gli URL primari, il link alla pagina dell'episodio, i link diretti a `slides.pdf` e `cheatsheet.pdf`, il link alla cartella `examples/`, e i capitoli con timestamp.

---

## 8. Specifica dei video

### 8.1 Daily Diff — durata: quella che dice la formula
**Misurato il 01/09/2026, primo episodio reale:** 3 item, 29 stati, **2:05**. La stima 3:30-5:00 qui
sotto è stata scritta prima che esistesse un episodio vero: **non si gonfia un video per rispettarla.**
Se i dati di retention diranno che serve più durata, la leva è più contenuto per item, non hold più lenti.
La struttura a blocchi resta valida, i minutaggi indicativi:

### 8.1.1 Struttura (minutaggi indicativi)
```
0:00-0:05  FRONT PAGE — le 3 headline insieme. È l'aggancio del formato
           notiziario: dice subito se vale i 4 minuti.
0:05-1:20  ITEM 1 — lo schema di §6, cinque tempi
1:20-2:35  ITEM 2
2:35-3:50  ITEM 3
3:50-4:10  TOMORROW + dove scaricare slide e cheat sheet
```

### 8.2 Il settimanale — forma predefinita: **Method Diff** (4-6 min)

Un'attività, un metodo, una misura. Cinque tempi, che ricadono sulle slide già esistenti perché il
renderer tratta un episodio di metodo come un episodio a un solo item:

```
COPERTINA   la query, come l'ha scritta chi cerca
IL DIFF     − come si fa di solito     + cosa cambia il metodo
RIPRODUCILO lo stub deterministico + il codice di misura  (la slide dice che è uno stub)
IL NUMERO   token per task, passi, retry, success rate — misurati dal nostro codice
TAKEAWAY    quando usarlo, e quando no
```

**La regola che lo rende efficace: il titolo è la query, e il nome della serie non ci va.** Sul
Daily il prefisso di brand aiuta il richiamo, perché quelle views vengono dagli iscritti. Qui
vengono dalla ricerca: il titolo è finito, e ogni parola spesa in branding è una parola non spesa
sulla query. Il brand vive nel logo in miniatura e nella card finale. Specifica in `prompts/method.md`.

**Requisiti di onestà specifici**, perché questo formato *raccomanda* invece di riportare: dire cosa
è stato misurato e cosa no; dire dove il metodo non conviene; e se il miglioramento è piccolo, dirlo
piccolo. Un metodo che fa risparmiare l'8% vale comunque un video — dichiarare l'80% no.

### 8.2.1 Deep Diff — 10-15 min, variante occasionale dello stesso slot
Un argomento: la promessa → cosa dice la fonte → **noi l'abbiamo eseguito** → l'output reale → **dove si rompe** → cosa significa. La sezione "dove si rompe" è quella che nessun canale di slop può produrre, perché richiede di aver fatto girare le cose. È il pezzo di maggior valore del canale.

**Formato preferenziale, deciso il 02/09/2026 — "il workflow della settimana".** Un workflow
agentico o di prompting reale, costruito, eseguito e rotto:
```
OBIETTIVO → PLANNER → TOOL / MCP / SKILL → SUBAGENT → VERIFICA → OUTPUT
```
con, per ciascuno stadio, il costo in token e i passi misurati dal nostro codice. È qui che vanno
i **pattern emergenti**: un pattern si dichiara solo con evidenza da più fonti indipendenti, e un
Deep settimanale ha lo spazio per mostrarla — un item del Daily no. Le regole di §10.3 valgono
anche qui: se le fonti sono due, si dice "due", non "sta emergendo un trend".

### 8.3 Il ritmo nel formato muto
Senza voce serve una formula. È il nucleo del renderer:
```
hold(state) = clamp(0.9, 4.5,  0.35 × parole_nuove + 0.5)
+ minimo 1.8 s se lo stato introduce un grafico
+ minimo 2.5 s per lo stato finale di un blocco di codice
+ minimo 2.2 s se lo stato mostra un URL di fonte
```
0,35 s/parola ≈ 170 parole al minuto: lettura silenziosa comoda per testo tecnico. **È una variabile del ledger** (§10.1): probabilmente la leva singola più efficace sulla retention di questo formato.

### 8.4 Miniature
Generate dallo stesso motore HTML, parametriche, quindi testabili. Leggibili a 320 px; un numero o
un termine tecnico grande; nessuna faccia, nessuna freccia rossa, **nessun logo aziendale come
soggetto**. Il logo del canale sta in alto a destra come firma, non come soggetto. Nella nicchia
dev, **la miniatura sobria è il segnale di qualità**: sembrare diversi dallo slop è posizionamento.

### 8.5 Logo del canale, loghi dei vendor, musica — deciso il 02/09/2026

**Logo del canale.** Fornito da Marco: due barre, `−` rossa su "AI DAILY" e `+` verde su "DIFF".
È già l'identità di §2.8, e i due segni dentro il logo risolvono gratis il problema del daltonismo
che una coppia rosso/verde avrebbe avuto. Vive in `assets/logos/channel/`, inlineato come data URI
dai renderer (`src/brand.py`) così slide, PDF e frame del video restano autocontenuti. Compare in
copertina, sulla slide finale, nell'header del cheat sheet, sul sito e in miniatura.
La palette del deck è stata avvicinata a quella del logo (`--ok` 5BD6A0→3FD97F, `--bad`
FF6E8C→FF5A72) mantenendo il contrasto leggibile: il rosso puro del logo su fondo scuro vibra e
non si usa per il testo.

**Loghi dei vendor** (`assets/logos/vendors/<slug>.png`, opzionali). Uso nominativo — citare il
marchio di ciò di cui si parla è ciò che fa qualunque testata — con tre regole non negoziabili:
1. **Solo asset ufficiali** dal press kit del vendor. Mai ridisegnati, mai avatar di HuggingFace,
   mai generati (violerebbe §2.9). Ogni file va registrato in `assets/logos/CREDITS.md` con URL di
   provenienza e restrizioni di licenza (diversi vendor vietano ricolorazioni).
2. **Etichetta, non soggetto:** piccolo, accanto al nome del filone, per dire *di chi parliamo*.
3. **Mai accanto a un giudizio:** un logo su una slide che dice "X è meglio di Y" implica
   endorsement. Nei confronti si usano i nomi in testo.
Se l'asset ufficiale manca, `src/brand.py` ripiega su una sigla in monospazio: un file assente non
è mai un errore.

**Musica — scelta il 03/09/2026:** "Nebula" di The Grey Room / Density & Time, dalla YouTube Audio
Library, in `assets/music/daily-bed.mp3` (3:09, quindi un Daily non arriva mai al punto di loop).
Misurata *prima* di montarla: LRA **4,1 LU**, cioè piatta — nessuno swell, ed è il numero che
conta davvero per un letto musicale. Ricodificata a 128 kbps (3,0 MB invece di 7,6): un MP3
committato in git resta lì per sempre, e a −18 LUFS sotto del testo i 320 kbps non si sentono.

**Il livello si misura, non si fissa** — e la regola precedente ("−15 dB sotto la voce") era
sbagliata per un motivo strutturale: nel formato muto **la musica è l'unico audio**, quindi non c'è
niente sotto cui stare. YouTube normalizza *verso il basso* il contenuto sopra i −14 LUFS ma non
alza quello troppo silenzioso: un letto a −26 LUFS suona semplicemente piano, lo spettatore alza il
volume, e il video successivo gli urla addosso. Quindi il renderer legge la loudness integrata
della traccia e calcola il guadagno per far uscire il video a **−18 LUFS**. Verificato sul render
del 02/09: −18,3 LUFS integrata, LRA 4,0 LU, picco reale −7,7 dBFS.

**Il credito in descrizione si mette comunque**, anche se la traccia fosse fra quelle senza obbligo
di attribuzione: costa una riga e rimuove ogni dubbio. Vive in `src/brand.py::MUSIC_CREDIT`, così
brief e descrizione YouTube non possono divergere.

Il formato muto ne ha bisogno: due minuti di silenzio fanno pensare a un video rotto.
Requisiti: ambient o minimale, senza voce, senza batteria marcata, senza build-and-drop, loopabile.
**Una traccia per il Daily e una per il Deep, sempre le stesse** — diventano la firma sonora, come
la sigla di un notiziario. Fonti gratuite in ordine di preferenza: (1) YouTube Audio Library, filtro
"nessuna attribuzione richiesta" — zero rischio di rivendicazioni *su YouTube*; (2) Pixabay Music,
licenza permissiva e usabile anche fuori da YouTube, quindi migliore in vista della newsletter di
fase 3; (3) Incompetech, CC BY, richiede una riga di credito. Da evitare: "royalty free" da
compilation YouTube, ed Epidemic Sound (a pagamento). Implementazione: file `.mp3` in
`assets/music/`, il renderer lo trova, lo mette in loop, lo mixa a −15 dB con fade di 1,5 s in
entrata e in uscita. Licenza registrata in `assets/music/CREDITS.md`. `music_bed` resta una
variabile del loop A (§10.1).

---

## 9. La pipeline, e i vincoli di rete verificati

**Verifiche eseguite il 28/08/2026 in questo ambiente:**

| Cosa | Risultato |
|---|---|
| Render slide → video (Chromium + ffmpeg) | ✅ 17 stati → 27 s di 1080p in **19,6 s di CPU**, 430 KB |
| `slides.pdf` (Chromium, vettoriale) | ✅ 5 pagine, 151 KB, ~1 s |
| `cheatsheet.pdf` (Chromium, A4) | ✅ 1 pagina, 125 KB, ~2 s |
| HuggingFace API via WebFetch | ✅ raggiungibile |
| GitHub API via WebFetch | ✅ raggiungibile |
| arXiv RSS via WebFetch | ✅ raggiungibile (l'**API** no: esclusa da robots.txt) |
| `git` verso github.com | ✅ funzionante |
| curl/requests diretti | ❌ bloccati: solo il tool WebFetch e i registry di pacchetti |

**Conseguenza architetturale, e cambia il piano in meglio:** una sessione di Claude può fare **ingestion, selezione, authoring, esecuzione degli esempi e rendering di tutti gli artefatti**. Non serve una chiave API a pagamento in CI. GitHub Actions resta per due lavori dove è insostituibile: **eseguire i test degli esempi su una macchina pulita** (il badge CI va guadagnato, non autocertificato) e **pubblicare le Pages**.

### 9.1 Il flusso quotidiano — **rivisto il 03/09/2026: il rendering vive in CI**
```
1. INGEST    Claude via WebFetch: HF API, GitHub API, arXiv RSS, prezzi, pagine sorvegliate
2. SELECT    dedup contro l'indice a 30 giorni + scoring (§9.2)
3. AUTHOR    gli item nello schema di §6 → data/episodes/DATA.json
4. EXAMPLES  Claude scrive gli esempi, li ESEGUE, cattura l'output reale
5. RENDER DI PROVA  Claude renderizza in sessione, solo perché Marco possa vedere il video
6. GATE      Marco guarda il video e approva o scarta        ← mai automatico
7. PUBLISH   Marco mette nel repo **due sole cose di testo** (pochi KB):
                data/episodes/DATA.json
                examples/DATA-slug/...
             e `render.yml` fa tutto il resto: riverifica gli esempi su macchina pulita,
             timbra il badge SOLO se passano, renderizza i 4 artefatti + pagina,
             committa indietro → Pages → (dispatch manuale) upload YouTube
```

**Perché questo cambia il carico di lavoro e non solo l'architettura.** Prima il payload da
portare su GitHub era uno zip da 18 MB di video e PDF, con estrazione, robocopy e sei comandi git.
Ora è testo: si trascina dentro **github.com → Add file → Upload files**, senza git, senza
installazioni, senza nemmeno il proprio computer. È la differenza fra un rituale di cinque minuti
al giorno e trenta secondi.

**E il badge diventa davvero prodotto da CI.** Prima il flag `tested_in_ci` lo girava una persona
dopo aver visto la spunta verde; ora è **la stessa run che verifica a timbrare la slide**
(`tools/mark_ci_verified.py` chiamato dentro `render.yml`, dopo il Gate 2 e prima del render). Se
la verifica fallisce il job si ferma e non renderizza niente: un badge non guadagnato non può
esistere come file. È §3 portato alla sua conclusione.

**Cosa resta manuale, e perché.** L'upload su YouTube: è l'unico passo irreversibile, e un click
umano su una cosa irreversibile non è un attrito da eliminare.

**Cosa NON è automatizzabile, ed è meglio dirlo che aggirarlo.** Il push da una sessione Claude è
rifiutato dal proxy git (`not in this session's authorized repository set`) — verificato di nuovo il
03/09/2026, e il meccanismo per autorizzare un repo non è documentato. Quindi il passaggio del
contenuto dalla sessione al repo resta un gesto di Marco. Ridurlo a un trascinamento nel browser è
il massimo ottenibile senza mettere un token di scrittura in una conversazione, che sarebbe un
prezzo di sicurezza sbagliato per il beneficio.
Lo stadio 4 prima dello stadio 5 non è negoziabile: **l'output mostrato a schermo è quello vero**, catturato dall'esecuzione, non trascritto a mano.

### 9.2 Scoring dello stadio 2 — rifatto il 02/09/2026

I pesi originali premiavano novità e fonte primaria, e non chiedevano mai **quante persone toccate**
né **se cambia una decisione**. Erano i due segnali che mancavano, e ora sono i due più pesanti.
Vivono in `src/selection.py::WEIGHTS`, che è la costante che il loop B modifica.

| Segnale | Peso | Cosa misura |
|---|---|---|
| `is_primary_source` | ×1,5 (moltiplicatore) | senza fonte primaria l'item è **scartato**, non penalizzato |
| `blast_radius` | 0,35 | quante persone che costruiscono con l'AI sono toccate |
| `decision_relevance` | 0,30 | cambia una scelta che qualcuno fa questa settimana |
| `has_runnable_artifact` | 0,25 | esiste qualcosa da eseguire o ispezionare |
| `freshness` | 0,20 | decadimento su 4 giorni; un quotidiano parla di oggi |
| `interest_signal` | 0,15 | download, stelle, like — segnale, non prova |
| `source_authority` | 0,10 | affidabilità storica della fonte |
| `corroboration_count` | 0,10 | quante fonti indipendenti lo confermano |
| `research_only_penalty` | **−0,25** | preprint senza nulla di rilasciato |

I due segnali nuovi si stimano da un **profilo per tipo di fonte** (`SOURCE_PROFILE`): un cambio di
prezzo parte da 1,00 su entrambi, un preprint da 0,15 e 0,20. Sono priori dichiarati, non verità: il
loop B li corregge sui dati. La differenza che conta è che ora **esistono**.

**Effetto sul primo episodio, calcolato:** con questi pesi l'item Qwen (model_weights, portata
0,70) resta selezionabile, mentre i due preprint scendono sotto un cambio di prezzo o una release.
Non è un difetto della funzione: è il comportamento richiesto.

**Dedup:** hash di URL e titolo normalizzato su indice a 30 giorni. Ripubblicare la stessa notizia
con un titolo diverso è il pattern che YouTube demonetizza.

**Tracciabilità:** ogni item selezionato porta nel file di selezione il `_breakdown` del punteggio,
così una sessione futura vede *perché* ha vinto, non solo che ha vinto.

## 10. Il loop di auto-miglioramento

Due loop. Il secondo vale più del primo e i canali automatici lo trascurano.

### 10.1 Loop A — confezionamento (settimanale)
Variabili: `thumbnail_template`, `title_pattern`, `front_page_style`, `reading_speed_coeff` (§8.3), `item_count`, `music_bed`, `length_s`, `chart_style`.

### 10.2 Loop B — la funzione di selezione (settimanale)
**Non ottimizza come impacchetti, ma cosa scegli.** Variabili: `vertical`, `source_type`, `has_runnable_artifact`, `example_kind` (esecuzione reale / stub / analisi), `item_age_hours`, `corroboration_count`, **e i pesi stessi di §9.2**.

Meccanismo: si registra la performance del video che conteneva ogni item; con campione sufficiente si correlano gli attributi alla resa; i pesi si aggiornano; `SOURCES.md` accumula la resa per fonte e le fonti rumorose vengono retrocesse.

Dopo qualche mese hai un sistema che **sa che tipo di notizia il tuo pubblico vuole** — l'unico asset del progetto che nessun concorrente può copiare, perché è costruito sui dati del tuo pubblico.

### 10.3 Regole di decisione
1. **Mediana, non media** (distribuzioni a coda pesante).
2. **n ≥ 5** per valore. Sotto: "dato insufficiente", non un'ipotesi.
3. **Coorte temporale:** solo video della stessa finestra di ~2 settimane.
4. **Massimo 2 variabili per volta.**
5. **Epsilon-greedy 80/20**, e il 20% di esplorazione non si abbandona mai. È l'unica difesa contro il massimo locale.
6. **I vincoli di §3 e §4 non sono ottimizzabili.** Se il loop scopre che i titoli esagerati alzano la CTR — e lo scoprirà — si registra il risultato **e non si adotta**. La CTR è affittata, la fiducia è capitale.

### 10.4 Il primo esperimento è già deciso
**Muto contro voce.** Settimane 3-4: 6 brief muti e 6 con TTS Kokoro, tutto il resto costante. Metrica: APV mediana e retention nei primi 30 secondi. Decide il formato per i mesi successivi, e va misurato, non discusso.

### 10.5 Il ciclo settimanale
Ogni lunedì: **raccogli** → **attribuisci** (mediane per valore, con n) → **concludi** nel ledger citando i numeri → **aggiorna** `RECIPE.md` e i pesi di §9.2 → **correggi i prompt** → **dichiara il prossimo esperimento prima di produrre**.

La correzione dei prompt è ciò che rende il sistema auto-migliorante. Se la retention crolla al secondo 12 su 6 brief su 8, la correzione non è "fare video migliori": è una **regola nuova committata in `prompts/daily.md`** — "il primo numero concreto entro il secondo 8" — che la produzione del giorno dopo eredita. I prompt vivono in file versionati, mai inline nel codice, esattamente per questo.

### 10.6 Template — `LEDGER.md`
```markdown
## Esperimento #003 — 2026-09-14 → 2026-09-28
**Loop:** B (selezione)
**Ipotesi:** gli item con esempio a esecuzione reale rendono meglio di quelli con stub o analisi.
**Variabile:** example_kind — real (n=9) vs stub/analysis (n=7). Ricetta v2 costante.
**Risultato:** APV mediana 51% vs 39%. CTR 5,2% vs 5,0% (indifferente).
**Conclusione:** l'esecuzione reale pesa sulla retention, non sul click.
  Peso has_runnable_artifact 0,30 → 0,45. Filone 3 penalizzato di conseguenza.
**Correzione ai prompt:** daily.md — "se l'item ha esecuzione reale, mostrare l'output entro il secondo 25".
**Nota:** campione al minimo. Riconfermare all'esperimento #008.
```

### 10.7 Cosa il loop non può fare
- Non può salvare un formato sbagliato: se dopo 60 brief l'APV mediana resta sotto il 30%, il problema è il formato muto o la cadenza → riaprire §2 con una decisione in §15.
- Non può creare giudizio editoriale: il gate umano resta la difesa contro il video ottimizzato e vuoto.
- Non può recuperare la fiducia persa con un errore non corretto (§3).

---

## 11. Divisione del lavoro

> **Nota di costo aggiunta il 02/09/2026.** Il Method Diff settimanale è il singolo contenuto più
> caro del piano: stub deterministico, misura, e l'inquadramento onesto su cosa è dimostrato. Va
> messo in conto come **il pezzo grosso della settimana**, non come un extra — ed è la ragione per
> cui il metodo non è un item quotidiano. Se in una settimana il budget non regge, salta il Method
> e non i brief: il Daily tiene l'abitudine, e un Method affrettato tradisce esattamente la
> promessa su cui il canale si regge.

| Chi | Cosa |
|---|---|
| **Claude** | ingestion, selezione, authoring, esempi (scritti *e* eseguiti), rendering dei 4 artefatti, codice, prompt, analisi dei due loop, aggiornamento di questo file |
| **GitHub Actions** | test degli esempi su macchina pulita, pubblicazione Pages |
| **Marco** | il gate, il commit, e il giudizio. L'upload è automatico (quota confermata piena). |

Budget di Marco, ~3 h/settimana:

| Attività | Tempo |
|---|---|
| Gate: guardare il brief e approvare o scartare | 6-8 min × 5 = ~35 min |
| Commit (`gh` autenticato, l'upload parte da solo) | 2 min × 5 = ~10 min |
| Gate del Deep, incluso far girare il codice a mano una volta | 45-60 min |
| Sessione settimanale sul ledger e sul prossimo esperimento | 30 min |
| Setup iniziale | 2,5-3 h, una volta sola |

Se una voce gonfia, l'architettura è sbagliata: si torna al codice, non si chiedono più ore a Marco.

---

## 12. Repo

```
ai-daily-diff/
├── PROJECT_INSTRUCTIONS.md   RECIPE.md   LEDGER.md   SOURCES.md   CORRECTIONS.md
├── prompts/                  daily.md  deep.md  title.md  example.md
├── src/
│   ├── ingest.py  selection.py  author.py
│   ├── render_video.py  render_artifacts.py  thumbnail.py  render_page.py
│   ├── upload.py  analyze.py
├── templates/                deck.html  cheatsheet.html  page.html  + il CSS del sistema
├── data/
│   ├── episodes/YYYY-MM-DD.json    ← unica fonte di verità dell'episodio
│   ├── inbox/  dedup_index/  metrics/
├── examples/YYYY-MM-DD-slug/       run.sh  expected_output.txt
├── assets/fonts/  assets/music/ + LICENSES.md
├── site/                     output GitHub Pages
├── output/                   video in attesa del gate
└── .github/workflows/        test.yml   pages.yml
```

---

## 13. Roadmap

**Fase 0 — Fondazioni (settimana 1).** Passi manuali di Marco (documento separato) + verifiche di §14. Sistema visivo definitivo. PoC promosso a `src/`. → *Gate: un brief completo da dati veri, con tutti e 4 gli artefatti, che Marco trova pubblicabile.*

**Fase 0 chiusa il 03/09/2026.** Il gate chiedeva "un brief completo da dati veri, con tutti e 4
gli artefatti, che Marco trova pubblicabile": fatto con l'episodio del 02/09 (due item, prezzi e
Ollama), approvato da Marco, con musica e logo. E in più: CI verde su macchina pulita, sito
pubblicato, badge guadagnato dal meccanismo e non autocertificato. **Resta da fare per aprire la
fase 1:** l'upload del primo video, e poi cinque brief a settimana.

**Stato al 01/09/2026:** primo episodio reale (`data/episodes/2026-09-01.json`) prodotto end-to-end da fonti vere raccolte in sessione: Qwen3.8-Flash-Next (config diff), DAMP (arXiv 2608.27513), backdoor da quantizzazione (arXiv 2608.27512). Tre esempi CPU-only offline, tutti verdi al Gate 2. **Resta per chiudere il gate:** giudizio di Marco sul video, secrets Actions, Pages su "GitHub Actions", e il verde di CI prima dell'upload.

**Stato al 28/08/2026:** repo creato e pubblico, scaffold completo (`src/`, `templates/`, `prompts/`, `.github/workflows/`), pipeline generalizzata dal PoC e verificata end-to-end (schema + Gate 1 + Gate 2 + video + slides.pdf + cheatsheet.pdf + brief.md + pagina, tutto da un solo `data/episodes/*.json`) su un episodio **di prova, non reale** (marcato esplicitamente "PIPELINE TEST — not for publish", fonte generica). Refresh token OAuth ottenuto. **Resta da fare per chiudere il gate:** un episodio con notizie vere (ingestion reale in sessione Claude via WebFetch), il primo push del repo, i secrets GitHub Actions, e il giudizio di Marco che lo trova pubblicabile.

**Fase 1 — Calibrazione (settimane 2-5).** 5 brief + 1 Deep a settimana. Obiettivo: stabilire la mediana di base e chiudere l'esperimento muto-vs-voce. → *Gate: 20 brief + 4 Deep, 3 conclusioni numeriche nel ledger, zero esempi rotti pubblicati.*

**Fase 2 — Segnale (settimane 6-13).** Il loop B corregge i pesi. Si cerca il primo video che sfonda; quando arriva, l'esperimento successivo è obbligatoriamente *cosa aveva di diverso e si può replicare*. → *Gate: 50.000 views, APV ≥ 45%.*

**Fase 3 — Scala (14-26).** Shorts dalla stessa pipeline. Newsletter (contenuto già prodotto, costo marginale nullo). Eventuale voce sul Deep se l'esperimento lo indica. → *Gate: soglie YPP.*

**Fase 4 — Estensione.** Localizzazione (il formato muto la rende quasi gratuita). Monetizzazione: nel pubblico dev/AI le leve non-pubblicitarie (sponsor tecnici, corsi, tooling) sono più forti degli annunci.

---

## 14. Da verificare in fase 0

- [x] Handle YouTube `@aidailydiff` — **verificato libero il 28/08/2026**.
- [x] **Pipeline provata end-to-end il 03/09/2026:** push → Test verde su macchina pulita → Deploy Pages → sito online su `marcocm28.github.io/ai-daily-diff`. Badge CI guadagnato tramite `tools/mark_ci_verified.py`, che si rifiuta di girare il flag se il Gate 2 non passa in locale.
- [ ] Ricerca marchio (TMview, EUIPO/USPTO classi 9 e 41) e ricerca Google per omonimie note su "AI Daily Diff".
- [x] Quota YouTube Data API v3: **10.000 query/day confermate il 28/08/2026**, nessuna restrizione da audit. `videos.insert` costa ~1.600 unità → margine per ~6 upload/giorno contro 1 necessario. **`upload.py` pubblica in automatico.**
- [x] Repo pubblico o privato. **Creato pubblico il 28/08/2026:** `github.com/marcocm28/ai-daily-diff`. Scaffold completo generato e pipeline verificata end-to-end (vedi §15).
- [ ] ToS e rate limit correnti di: HuggingFace API, GitHub API, arXiv RSS, HN Algolia, Reddit API.
- [ ] Licenza YouTube Audio Library per l'uso previsto.
- [ ] Testo corrente della policy inauthentic content, letto pensando a "slideshow muto quotidiano".
- [ ] Caricabilità di un caption track su un video senza parlato, per l'indicizzazione.

---

## 15. Registro delle decisioni

| Data | Decisione | Motivo | Reversibile? |
|---|---|---|---|
| 17/09 | Automazione dalla ricerca alla pubblicazione, Codex sul PC e rendering/upload GitHub, canale dedicato @aidailydiff | richiesta esplicita di Marco: sostituisce l'approvazione manuale per episodio; restano verifica fonti/esempi, blocco canale e registro anti-duplicati | sì |
| 16/09 | Integrati i due radar ChatGPT come piste editoriali importabili; prompt di ricerca unificato e `source_review` obbligatorio per le nuove bozze | richiesta di Marco: ampliare le notizie con metodi, workflow e novità tecniche senza pubblicare contenuti privati o scambiare score soggettivi per misure | sì |
| 16/09 | Corrette soglia/freschezza/dedup e confronto output JSON; Pages consuma l'artefatto del Render verificato | corregge difetti implementativi, senza cambiare pesi, formato o gate umano | sì |
| 28/08 | Pivot da canale bambini a quotidiano AI | pipeline più solida, pubblico adulto, nessun COPPA | — |
| 28/08 | Il prodotto è riproducibilità + materiali, non le notizie | "daily AI news" è commodity satura | no |
| 28/08 | Formato muto | elimina il rischio slop del TTS; localizzabile | sì — esperimento #001 |
| 28/08 | Daily + Deep settimanale | il Daily da solo resta commodity | sì |
| 28/08 | 5 filoni, con Agents & Prompting aggiunto da Marco | copertura ampia; filoni 4-5 come sotto-nicchia dominabile | sì |
| 28/08 | Nessuna AI generativa per immagini/video/voce | determinismo, costo zero, nessun segnale slop | no |
| 28/08 | Slide → Chromium → ffmpeg | **dimostrato:** 27 s di 1080p in 19,6 s | no |
| 28/08 | 4 artefatti per episodio da un solo JSON | richiesta di Marco; **dimostrato**; risolve anche la SEO del muto | no |
| 28/08 | Cheat sheet A4 chiaro, CC BY 4.0 | è l'artefatto che si condivide: distribuzione gratuita | sì |
| 28/08 | Nome: **AI Daily Diff**, `@aidailydiff` | `@runnable` occupato; categoria cercabile + una parola distintiva e nativa del pubblico | no, dopo il lancio |
| 28/08 | Identità visiva basata sul diff `−`/`+` | leggibile senza parole, gratuita, non imitabile a buon mercato | no |
| 28/08 | GitHub Pages come hub dei download | gratuito, e recupera l'indicizzazione persa | sì |
| 28/08 | Ingestion e authoring in sessione Claude, non in CI | **verificato:** WebFetch e git funzionano → nessuna chiave a pagamento | sì |
| 28/08 | Il test degli esempi gira su GitHub, non da me | il badge CI va guadagnato su macchina pulita | no |
| 28/08 | Esempi con stub deterministico dove serve un LLM | Gate 2 vieta chiavi a pagamento; e va dichiarato sulla slide | no |
| 28/08 | Gate umano su ogni video | policy inauthentic content + difesa dal contenuto vuoto | no, mai |
| 28/08 | Nessuna credenziale in doc di Project o in chat | igiene di sicurezza | no |
| 28/08 | Git Credential Manager invece di un Personal Access Token o `gh auth login` | incluso in Git for Windows, login via browser al primo push, nessun segreto di lunga durata da custodire (corretto due volte: prima suggerito un PAT, poi `gh` — nessuno dei due serviva) | no |
| 28/08 | Upload automatico via API | quota 10.000/day confermata piena | sì |
| 28/08 | Canale sull'account Google **personale** di Marco | il canale esiste già lì; il rischio da evitare era l'account Codere, e non si presenta. Un account personale per un canale personale è la norma. Prezzo: la 2FA diventa obbligatoria, perché una sola password protegge posta e canale | sì — YouTube permette di spostare il canale in un account brand, e più il canale è vuoto più è indolore |
| 28/08 | Progetto Google Cloud rifatto sullo **stesso** account personale | il primo era su un'altra mail in un Workspace: schermata consenso forzabile a Internal, e credenziali del canale in un tenant non controllato | no |
| 28/08 | Refresh token OAuth ottenuto (script locale one-shot) | scambio JSON→refresh token richiede un browser e un redirect locale: non eseguibile da una sessione Claude, quindi script consegnato a Marco per l'esecuzione locale | no |
| 03/09 | Rendering spostato in `render.yml`: CI verifica, timbra il badge e renderizza; Marco porta nel repo solo il JSON dell'episodio e gli esempi | il payload scende da 18 MB a pochi KB, quindi si trascina nel browser senza git né computer; e il badge passa dall'essere girato a mano a essere prodotto dalla stessa run che verifica | sì |
| 03/09 | Il push dalla sessione Claude resta impossibile, e si smette di cercare workaround | il proxy git rifiuta i repo non autorizzati e il meccanismo di autorizzazione non è documentato (verificato due volte). L'alternativa — un token di scrittura in chat — è un prezzo di sicurezza sbagliato per risparmiare un trascinamento | sì, se un giorno le sessioni supporteranno il repo come sorgente |
| 03/09 | Musica: livello calcolato dalla loudness misurata, target −18 LUFS, invece del −15 dB fisso | nel muto la musica è l'unico audio: non c'è una voce sotto cui stare, e YouTube non alza il contenuto silenzioso. Il vecchio default avrebbe prodotto video a ~−26 LUFS | sì — target è variabile del loop A |
| 03/09 | Credito musicale in descrizione anche se non obbligatorio, da `brand.py::MUSIC_CREDIT` | una riga costa nulla, e tenerlo in un solo posto impedisce che brief e descrizione YouTube divergano | sì |
| 02/09 | Il settimanale diventa il **Method Diff** (4-6 min, titolo = query); il Deep 10-15 min resta variante occasionale dello stesso slot; nel Daily il metodo è occasionale, non fisso | il traffico evergreen richiede un video il cui titolo *sia* la query: un item di metodo dentro un brief costa il massimo e cattura il minimo. E con zero iscritti la ricerca è l'unico canale di acquisizione reale, quindi il settimanale è il motore, il Daily l'abitudine | sì — riallocazione prevista dopo 8 settimane, con la mediana delle views a 30 giorni per formato |
| 02/09 | Nessun nome di serie nel titolo dei Method Diff | il titolo è finito e quelle views vengono dalla ricerca: il brand sta nel logo in miniatura e nella card finale, non nei caratteri sottratti alla query | sì |
| 02/09 | Filone 3 riscritto attorno alla domanda "esiste un modo migliore di fare X con l'AI?", dai prompt che Marco già usa su ChatGPT | era il filone più debole dei cinque, e quella domanda è una definizione migliore di quella che avevo scritto io. Nessun sesto filone: aggiungerlo diluiva, riscrivere il terzo lo rende il più forte |sì |
| 02/09 | **"IMPACT SCORE X/10" rifiutato** dal formato dei prompt di Marco | un punteggio autoassegnato non è falsificabile e contraddice §6 (il numero viene dalla fonte o dal nostro codice). Sostituito con misure vere: token per task, passi, retry, success rate su task fisso con stub | no |
| 02/09 | Fonti ufficiali sorvegliate **via commit** (OpenAI Cookbook, Anthropic Cookbook, Claude Code, MCP) + GitHub search su repo aggiornati, senza filtro sulle stelle | un commit a un cookbook ufficiale è un metodo appena documentato: è il segnale più pulito che esista per il filone 3, e le pagine HTML non lo danno | sì |
| 02/09 | Deep Diff: formato preferenziale "il workflow della settimana"; i pattern emergenti vanno lì, non nel Daily | dichiarare un trend richiede evidenza da più fonti, e il Deep ha lo spazio per mostrarla. Nel Daily diventerebbe un'affermazione non verificabile | sì |
| 02/09 | Finestra di freschezza 4 giorni, che si allarga a 7 nei giorni magri | riempire un brief con un item debole è peggio che pescare a una settimana un item forte. È la regola dei prompt di Marco (24-72h → 7 giorni), resa meccanica | sì |
| 02/09 | Filoni rifatti: Models & Releases · Cost & Limits · Tools & Agents · Media Generation · Claims & Risks | i filoni da ricerca spingevano la selezione verso paper di nicchia — il primo episodio ne è la prova. Il pubblico resta chi costruisce (§2.3), cambia il criterio: ogni item deve chiudere una decisione | sì, ma non senza dati dal ledger |
| 02/09 | `blast_radius` (0,35) e `decision_relevance` (0,30) diventano i pesi più alti; penalità −0,25 ai preprint senza nulla di rilasciato | erano i due segnali mancanti: la vecchia funzione premiava la novità e non chiedeva mai quante persone toccate. Marco ha detto "troppo tecnici": la diagnosi vera era "troppo di nicchia" | sì — sono i pesi che il loop B corregge |
| 02/09 | Pagine di prezzi e deprecazioni sorvegliate a hash del testo (§5.2) | non hanno feed, e sono la fonte con la più alta rilevanza decisionale che esista. Un hash che si muove è letteralmente un diff: è il canale che applica a sé stesso la propria premessa | no |
| 02/09 | OpenRouter `/api/v1/models` come fonte primaria dei prezzi | JSON, senza chiave, centinaia di modelli con prezzo e contesto — **verificato raggiungibile**. Rende il filone Cost & Limits presidiabile ogni giorno con numeri veri | sì |
| 02/09 | Logo del canale integrato; loghi vendor ammessi come etichette con tre regole (§8.5) | il logo è già l'identità diff, e i segni `−`/`+` al suo interno risolvono il daltonismo. I loghi vendor aiutano la scansione, ma da soggetto sarebbero il segnale slop che stiamo evitando | no |
| 01/09 | Primo episodio reale prodotto: 3 item, 3 filoni, 3 esempi eseguiti, 4 artefatti + pagina. Episodio mock rimosso dal repo | il gate di Fase 0 chiede un brief da dati veri; il mock aveva fatto il suo lavoro e su un sito pubblico sarebbe stato solo rumore | no |
| 01/09 | Contenuto delle slide e del cheat sheet letto **dai file dell'esempio**, non trascritto (`tools/assemble_episode_*.py`, con assert sugli estratti) | elimina per costruzione la deriva fra ciò che si vede a schermo e ciò che CI esegue: era l'unico punto dove un errore onesto poteva diventare un claim falso | no |
| 01/09 | Grafici a più serie, calcolati dagli stessi config che legge l'esempio | la slide THE NUMBER senza grafico era povera; e un grafico che ricalcola i nostri numeri è verificabile come il resto | sì |
| 01/09 | Cheat sheet: shrink-to-fit automatico per tenere un item per pagina | l'alternativa era tagliare contenuto in silenzio o sforare in una quarta pagina: entrambe peggiori di un 0,914 di scala | sì |
| 01/09 | Durata reale 2:05 contro la specifica 3:30-5:00: si registra, non si gonfia | la specifica era una stima a priori; il ritmo lo decide la formula di §8.3 e poi i dati (§10) | sì — è la variabile `length_s` del loop A |
| 01/09 | Badge CI: si renderizza con `tested_in_ci: false` e si ri-renderizza dopo il verde di CI, prima di pubblicare | l'invariante «nessuno spettatore vede un badge non guadagnato» resta vera anche nel caso in cui CI fallisse | no |
| 01/09 | `src/select.py` rinominato in `src/selection.py`; guardia in `tests/` contro i nomi che collidono con la stdlib | primo push, prima CI: `import select` dentro `subprocess` risolveva al nostro file (src/ è primo in sys.path), rompendo tutto con `module 'select' has no attribute 'select'`. **Non riproducibile in sessione**, dove `select` è compilato nell'interprete: solo su runner dove è un'estensione caricata da file. È la dimostrazione che il Gate 2 su macchina pulita serve davvero | no |
| 28/08 | Repo `ai-daily-diff` creato pubblico su `github.com/marcocm28`; scaffold completo generato (src/, templates/, prompts/, .github/workflows/) e pipeline promossa dal PoC, verificata end-to-end su un episodio di prova | push diretto dalla sessione Claude resta bloccato dal git proxy (repo non nell'authorized set, bypassato su richiesta di Marco); deck/cheatsheet ora generici via Jinja2 per N item invece di codificati a mano; timing calcolato dalla formula di lettura invece di hardcoded | no — la struttura può evolvere, ma è la base d'ora in poi |
| 10/09 | Correzione mirata alla riga 03/09 sul push: **il push diretto funziona** da una sessione Claude Code CLI locale (verificato: `git push origin main` → `Everything up-to-date`, nessun rifiuto) | la riga del 03/09 descriveva un contesto diverso — il Project su claude.ai (chat pura, senza filesystem/git) o una sessione sandboxata precedente, non questo ambiente locale con Git Credential Manager già configurato. Il proxy git che rifiuta i repo non autorizzati resta vero in quei contesti; qui non si applica | non è una riapertura della decisione del 03/09, ne restringe il campo |
| 10/09 | Ingestion + selezione (`src/ingest.py`, `src/selection.py`) girano schedulate in `.github/workflows/ingest.yml`, non più in sessione | questa macchina è dietro un proxy TLS aziendale che rompe la verifica dei certificati per tutte e 24 le fonti (`CERTIFICATE_VERIFY_FAILED`, verificato: 0 candidati raccolti in locale). I runner GitHub non hanno quel proxy | sì, se cambia la rete della macchina che gira `tools/run_daily.py` |
| 10/09 | Authoring + costruzione degli esempi delegati a run headless `codex exec` (`tools/run_daily.py`), lanciato da Task Scheduler | chiude il lavoro manuale residuo: Claude non serve più in sessione per scrivere il brief quotidiano. Il driver non si fida mai del resoconto di Codex — ri-verifica Gate 1/2 da sé prima di committare | sì — resta un `codex exec`, sostituibile con un altro agente che rispetti lo stesso contratto (prompt, gate, niente git) |
| 10/09 | Il gate umano (28/08, mai automatizzabile) si sposta da "guardare un'anteprima renderizzata da Claude prima di committare" a "revisionare una PR (diff del contenuto + anteprima renderizzata da CI) prima di mergiare" | questa macchina non ha mai avuto Chromium/ffmpeg installati: l'anteprima "renderizzata in sessione" del §9.1 originale non è mai stata eseguibile qui. La PR su `draft/<data>` con l'anteprima di `render.yml` come build artifact è l'unico modo di dare a Marco qualcosa da guardare prima di pubblicare, dato lo stato reale di questa macchina | no — stesso principio del 28/08, cambia solo il meccanismo |
| 10/09 | `render.yml` + `tools/mark_ci_verified.py` implementati: il rendering vive in CI, sia come anteprima su PR sia come pubblicazione dopo il merge su main | chiude il gap aperto dal §9.1 v3.0 (mai costruito prima d'ora); risolto anche dove scrive il flag `tested_in_ci` (in `example.tested_in_ci`, già previsto da `src/author.py`) | sì, se cambia la strategia di rendering |

---

## 16. I cinque modi in cui questo progetto fallisce

1. **Un errore factuale non corretto.** In questa nicchia il pubblico verifica. Un claim sbagliato lasciato in piedi costa più di venti video mediocri. §3 esiste solo per questo.
2. **Il formato muto non regge sul long-form.** È la scommessa aperta: collaudato su Shorts e contenuti di codice, meno su un brief di 4 minuti. Per questo è l'esperimento #001.
3. **Il badge CI diventa una bugia.** Il giorno in cui un esempio va a schermo con l'output scritto a mano invece che catturato, il fossato è finito e nessuno se ne accorgerà dall'esterno — finché non se ne accorgono tutti. Lo stadio 4 prima dello 5 (§9.1) esiste per questo.
4. **Il canale diventa quello che dice di non essere.** La deriva è graduale: un titolo un po' più forte, un claim non verificato perché la fonte era lenta, un esempio pubblicato senza test perché era tardi. I gate automatici esistono perché la disciplina umana alle 23:00 non è affidabile.
5. **La quantità sostituisce il giudizio.** Davanti a numeri lenti la tentazione sarà pubblicare di più. Con formato o selezione sbagliati, pubblicare di più costruisce solo un archivio più grande di video che nessuno guarda. I gate di §13 esistono per questo.
