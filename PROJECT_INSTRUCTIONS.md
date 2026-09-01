# ISTRUZIONI DEL PROGETTO — "AI Daily Diff": quotidiano AI in inglese, da slide, con materiali scaricabili

> **Versione:** 2.3 — 28/08/2026. Repo creato e scaffold generato (§13, §15). Sostituisce la v2.1 (nome cambiato da "Runnable"). (La v1.0, canale per bambini, è archiviata.)
> **Owner:** Marco
> **Natura del documento:** file operativo master. Ogni sessione di Claude lo legge per intero prima di agire, e lo aggiorna quando una decisione cambia.

---

## 0. Come si usa questo file

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

### 2.4 Formato: muto — testo a schermo, codice che si costruisce, musica
**A favore:** elimina il rischio più grande (su pubblico tecnico la voce TTS è *il* marchio dello slop); 100% deterministico; localizzabile; molti guardano in mute.

**Contro, da progettare e non subire:**
- **Il ritmo va calcolato**, non narrato → formula in §8.3, ed è una variabile del ledger.
- **Perdita SEO:** senza parlato non c'è trascrizione da indicizzare. **Mitigazione: §7.** Gli artefatti scaricabili e le pagine GitHub Pages recuperano più indicizzazione di quella persa — la richiesta di Marco sui materiali scaricabili risolve per caso la debolezza maggiore del formato muto.
- **Rischio in revisione YPP:** "slideshow con musica senza commento" è vicino a ciò che YouTube considera basso sforzo. Difese: analisi originale, codice testato, grafici costruiti da noi, materiali scaricabili originali, gate umano. Piano B: voce di Marco sul solo Deep.

**È la scommessa numero uno del progetto**, e per questo è l'esperimento #001 (§10.4), non una convinzione.

### 2.5 Cadenza
- **Daily Diff** — 3:30-5:00, ogni giorno lavorativo, 3 item.
- **Deep Diff** — 10-15 min, 1/settimana, un argomento eseguito davvero.

Il Daily costruisce l'abitudine, il Deep l'autorità. Il Daily da solo resta una commodity.
Shorts: rinviati a fase 3 (la pipeline li darà quasi gratis, ma triplicano il volume da revisionare).

### 2.6 Cinque filoni
Architectures & Models · Agents & Prompting · Video & Image Generation · Data & Evaluation · Serving, Inference & Cost.
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

Per ciascuno: cosa include, la soglia oltre cui una novità è notizia, le fonti, che forma prende *il numero*, e che forma prende *l'esempio eseguibile*. Quest'ultima riga è la più importante: definisce se il filone può rispettare il Gate 2.

---
### Filone 1 — **Architectures & Models**
**Include:** rilasci di modelli con pesi disponibili, paper di architettura, tecniche di training, lavoro su attention e kernel, risultati di scaling, efficienza.
**Non include:** voci su modelli non rilasciati, movimenti di classifica sulle leaderboard, annunci di annunci.
**Soglia:** esistono pesi scaricabili **oppure** un paper con metodo descritto in modo riproducibile. "L'azienda X rilascerà Y" non è una notizia.
**Fonti:** `rss.arxiv.org/rss/cs.LG`, `cs.CL`, `cs.CV`; HuggingFace `/api/models?sort=trendingScore`; HF daily papers; blog ufficiali.
**Il numero:** parametri, lunghezza di contesto, token di training, delta su un benchmark nominato, memoria o FLOPs.
**L'esempio:** ispezione di config e tokenizer da HF; il meccanismo reimplementato in numpy a scala giocattolo; il confronto della config con quella del predecessore; l'aritmetica dell'attention su dimensioni piccole. Tutto CPU-friendly.
**Volume atteso:** abbondante. Il vincolo è la selezione, non la disponibilità.

---
### Filone 2 — **Agents & Prompting**  *(aggiunto da Marco)*
**Include:** architetture agentiche, orchestrazione, tool use, context engineering, memoria, protocolli per tool, eval per agenti, tecniche di prompt **con effetto misurato**, pattern d'uso reali.
**Non include:** liste di "10 prompt magici", thread motivazionali, tecniche senza misura.
**Soglia:** una tecnica con un claim misurato, o un'implementazione funzionante e leggibile.
**Fonti:** `rss.arxiv.org/rss/cs.CL` e `cs.AI`; GitHub API (repo nuovi e release nei framework di agenti); documentazione e cookbook ufficiali; HN e r/LocalLLaMA **come segnale di interesse, non come fonte**.
**Il numero:** delta di success rate su un task, costo in token per task, passi per completamento, latenza, tasso di retry.
**L'esempio — e qui c'è una difficoltà vera:** la maggior parte dei risultati richiederebbe una chiamata a un modello, che il Gate 2 vieta (niente chiavi a pagamento in CI). La soluzione è **uno stub deterministico**: un finto LLM che risponde da uno script, con cui si dimostra la *struttura* — il loop di controllo, il packing del contesto, la logica di retry, il conteggio dei token, il costo. Dove serve un modello vero, un modello piccolo che sta in CI. **Da scrivere apertamente sulla slide quando l'esempio usa uno stub:** l'onestà su cosa è dimostrato è parte del prodotto.
**Volume atteso:** alto e in crescita rapida. Probabilmente il filone con più interesse in questo momento.

---
### Filone 3 — **Video & Image Generation**
**Include:** rilasci di modelli generativi, tool, workflow, metodi di controllo, valutazione della qualità, termini di licenza.
**Soglia:** pesi o tool disponibili, oppure paper con metodo.
**Fonti:** HF `/api/models` filtrato su diffusers e text-to-video; `rss.arxiv.org/rss/cs.CV`; blog ufficiali; GitHub (ecosistema ComfyUI).
**Il numero:** risoluzione, passi di denoising, VRAM richiesta, secondi per frame, termini di licenza.
**L'esempio — il filone più difficile per il Gate 2:** far girare un modello generativo in CI su CPU è escluso. Quindi l'esempio **analizza invece di generare**: calcola il fabbisogno di VRAM dalla model card, ricostruisce e traccia il noise schedule in numpy, calcola la dimensione del latente in funzione della risoluzione, confronta i termini di licenza in modo programmatico. **Questo va detto, non nascosto:** in questo filone l'artefatto eseguibile è la matematica o l'ispezione, non la generazione. Se non si può fare né l'una né l'altra, l'item scende di priorità.
**Nota editoriale:** il canale racconta l'AI generativa senza usarla. Non è una contraddizione, è una posizione — e vale la pena dirla una volta nel trailer del canale.
**Volume atteso:** alto, e il più affollato di concorrenza.

---
### Filone 4 — **Data & Evaluation**
**Include:** dataset, benchmark, metodologia di valutazione, contaminazione, critiche alla misurazione, validità delle leaderboard, riproducibilità dei risultati.
**Soglia:** dataset o benchmark pubblicamente disponibile, oppure un risultato metodologico.
**Fonti:** HF `/api/datasets`; `rss.arxiv.org/rss/cs.LG` e `cs.CL`; repo ufficiali dei benchmark.
**Il numero:** dimensione del dataset, percentuale di overlap o contaminazione, accordo tra annotatori, varianza del punteggio tra seed, differenza tra formati di prompt.
**L'esempio — il filone più forte del canale:** carica una fetta di dataset da HF, calcola l'overlap di n-grammi con un benchmark, misura la varianza tra seed, mostra come una metrica cambia cambiando il formato del prompt. Tutto su CPU, tutto veloce, e tutto rivelatore. **Qui il canale può essere indiscutibilmente il migliore**, perché richiede esattamente ciò che lo slop non fa: far girare le cose.
**Volume atteso:** medio. Poco coperto dagli altri, quindi ogni item vale doppio in termini di posizionamento.

---
### Filone 5 — **Serving, Inference & Cost**
**Include:** deployment, quantizzazione, batching, caching, latenza, prezzo per token, motori di serving.
**Soglia:** un cambiamento rilasciato in un motore di serving, una tecnica misurata, una variazione di prezzo ufficiale.
**Fonti:** GitHub API release (vLLM, llama.cpp, SGLang, TGI e simili); pagine di pricing ufficiali; blog tecnici ufficiali.
**Il numero:** token/secondo, $/1M token, footprint di memoria, latenza p99, perdita di qualità da quantizzazione.
**L'esempio:** conteggio token e aritmetica dei costi (esattamente il PoC già costruito), dimensione della cache KV da formula, matematica della quantizzazione, aritmetica del batching. Molto CPU-friendly.
**Volume atteso:** medio. È il filone con il pubblico che ha più potere di spesa, e quindi il RPM più alto.

---
### 5.1 Il registro delle fonti
`SOURCES.md` tiene una riga per fonte: endpoint, rate limit, ultimo controllo, filoni serviti, e **resa storica** — quanti item pubblicati e come hanno performato. Il loop B (§10.2) usa questo dato per retrocedere o disattivare le fonti che portano rumore.

**Regola trasversale:** HN e Reddit dicono *a cosa la gente tiene*; la fonte primaria dice *cos'è vero*. Un item si pubblica solo con la seconda.

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

### 8.1 Daily Diff — 3:30-5:00
```
0:00-0:05  FRONT PAGE — le 3 headline insieme. È l'aggancio del formato
           notiziario: dice subito se vale i 4 minuti.
0:05-1:20  ITEM 1 — lo schema di §6, cinque tempi
1:20-2:35  ITEM 2
2:35-3:50  ITEM 3
3:50-4:10  TOMORROW + dove scaricare slide e cheat sheet
```

### 8.2 Deep Diff — 10-15 min
Un argomento: la promessa → cosa dice la fonte → **noi l'abbiamo eseguito** → l'output reale → **dove si rompe** → cosa significa. La sezione "dove si rompe" è quella che nessun canale di slop può produrre, perché richiede di aver fatto girare le cose. È il pezzo di maggior valore del canale.

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
Generate dallo stesso motore HTML, parametriche, quindi testabili. Leggibili a 320 px; un numero o un termine tecnico grande; nessuna faccia, nessuna freccia rossa, nessun logo aziendale come soggetto. Nella nicchia dev, **la miniatura sobria è il segnale di qualità**: sembrare diversi dallo slop è posizionamento.

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

### 9.1 Il flusso quotidiano
```
1. INGEST    Claude via WebFetch: HF API, GitHub API, arXiv RSS, blog RSS
2. SELECT    dedup contro l'indice a 30 giorni + scoring (§9.2)
3. AUTHOR    3 item nello schema di §6 → data/episodes/DATA.json
4. EXAMPLES  scrive gli esempi, li ESEGUE, cattura l'output reale
5. RENDER    JSON → video + slides.pdf + cheatsheet.pdf + brief.md + pagina
6. GATE      Marco guarda il video e approva o scarta        ← mai automatico
7. PUBLISH   commit (Marco) → CI verifica gli esempi → Pages + upload YouTube
```
Lo stadio 4 prima dello stadio 5 non è negoziabile: **l'output mostrato a schermo è quello vero**, catturato dall'esecuzione, non trascritto a mano.

### 9.2 Scoring dello stadio 2
I pesi iniziali sono un'ipotesi. Sono ciò che il loop B impara.

| Segnale | Peso iniziale |
|---|---|
| `is_primary_source` | ×1,5 (moltiplicatore; senza fonte primaria l'item è scartato) |
| `has_runnable_artifact` | 0,30 |
| `corroboration_count` | 0,20 |
| `interest_signal` (HN points, stelle, download HF) | 0,20 |
| `source_authority` | 0,15 |
| `freshness` (decadimento su 48h) | 0,15 |
| `vertical_balance_bonus` | variabile |

**Dedup:** hash di URL e titolo normalizzato + similarità di embedding su indice a 30 giorni. Ripubblicare la stessa notizia con un titolo diverso è esattamente il pattern che YouTube demonetizza.

---

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
│   ├── ingest.py  select.py  author.py
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

**Stato al 28/08/2026:** repo creato e pubblico, scaffold completo (`src/`, `templates/`, `prompts/`, `.github/workflows/`), pipeline generalizzata dal PoC e verificata end-to-end (schema + Gate 1 + Gate 2 + video + slides.pdf + cheatsheet.pdf + brief.md + pagina, tutto da un solo `data/episodes/*.json`) su un episodio **di prova, non reale** (marcato esplicitamente "PIPELINE TEST — not for publish", fonte generica). Refresh token OAuth ottenuto. **Resta da fare per chiudere il gate:** un episodio con notizie vere (ingestion reale in sessione Claude via WebFetch), il primo push del repo, i secrets GitHub Actions, e il giudizio di Marco che lo trova pubblicabile.

**Fase 1 — Calibrazione (settimane 2-5).** 5 brief + 1 Deep a settimana. Obiettivo: stabilire la mediana di base e chiudere l'esperimento muto-vs-voce. → *Gate: 20 brief + 4 Deep, 3 conclusioni numeriche nel ledger, zero esempi rotti pubblicati.*

**Fase 2 — Segnale (settimane 6-13).** Il loop B corregge i pesi. Si cerca il primo video che sfonda; quando arriva, l'esperimento successivo è obbligatoriamente *cosa aveva di diverso e si può replicare*. → *Gate: 50.000 views, APV ≥ 45%.*

**Fase 3 — Scala (14-26).** Shorts dalla stessa pipeline. Newsletter (contenuto già prodotto, costo marginale nullo). Eventuale voce sul Deep se l'esperimento lo indica. → *Gate: soglie YPP.*

**Fase 4 — Estensione.** Localizzazione (il formato muto la rende quasi gratuita). Monetizzazione: nel pubblico dev/AI le leve non-pubblicitarie (sponsor tecnici, corsi, tooling) sono più forti degli annunci.

---

## 14. Da verificare in fase 0

- [x] Handle YouTube `@aidailydiff` — **verificato libero il 28/08/2026**.
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
| 28/08 | Repo `ai-daily-diff` creato pubblico su `github.com/marcocm28`; scaffold completo generato (src/, templates/, prompts/, .github/workflows/) e pipeline promossa dal PoC, verificata end-to-end su un episodio di prova | push diretto dalla sessione Claude resta bloccato dal git proxy (repo non nell'authorized set, bypassato su richiesta di Marco); deck/cheatsheet ora generici via Jinja2 per N item invece di codificati a mano; timing calcolato dalla formula di lettura invece di hardcoded | no — la struttura può evolvere, ma è la base d'ora in poi |

---

## 16. I cinque modi in cui questo progetto fallisce

1. **Un errore factuale non corretto.** In questa nicchia il pubblico verifica. Un claim sbagliato lasciato in piedi costa più di venti video mediocri. §3 esiste solo per questo.
2. **Il formato muto non regge sul long-form.** È la scommessa aperta: collaudato su Shorts e contenuti di codice, meno su un brief di 4 minuti. Per questo è l'esperimento #001.
3. **Il badge CI diventa una bugia.** Il giorno in cui un esempio va a schermo con l'output scritto a mano invece che catturato, il fossato è finito e nessuno se ne accorgerà dall'esterno — finché non se ne accorgono tutti. Lo stadio 4 prima dello 5 (§9.1) esiste per questo.
4. **Il canale diventa quello che dice di non essere.** La deriva è graduale: un titolo un po' più forte, un claim non verificato perché la fonte era lenta, un esempio pubblicato senza test perché era tardi. I gate automatici esistono perché la disciplina umana alle 23:00 non è affidabile.
5. **La quantità sostituisce il giudizio.** Davanti a numeri lenti la tentazione sarà pubblicare di più. Con formato o selezione sbagliati, pubblicare di più costruisce solo un archivio più grande di video che nessuno guarda. I gate di §13 esistono per questo.
