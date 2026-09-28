# Appendix for the two existing ChatGPT scheduled tasks

> Editorial update 25 September 2026: read `prompts/editorial.md` first. Its novelty,
> practical-value and honest-evidence gates supersede conflicting editorial preferences
> below. Existing schema and CI requirements still apply.

Append the following to each task's existing instructions. Keep its title, schedule
and useful personal report. This appendix creates a separate, public-content-safe
handoff for AI Daily Diff; it does not grant filesystem or GitHub access.

## AI Daily Diff — export delle segnalazioni

Dopo il report aggiungi un blocco JSON valido, senza commenti, con `task` (nome esatto
dell'attività: AI Productivity Radar oppure Novità tecniche AI), `date` (YYYY-MM-DD
dell'esecuzione) e `items` (massimo 5, anche vuoto). Ogni item contiene:

```json
{
  "title": "Titolo concreto, senza hype",
  "url": "https://example.org/fonte-primaria-specifica",
  "published_at": null,
  "kind": "method",
  "vertical": "tools-agents",
  "summary": "Cosa cambia; separare fatto, claim del produttore e inferenza.",
  "decision": "Quale scelta pratica può fare il lettore.",
  "availability": "Disponibile / preview / annunciato / non verificato, requisiti e limiti",
  "example_idea": "Primo uso concreto; prova utile CPU offline sotto 60 secondi e limiti, oppure limite del formato",
  "suggested_format": "method"
}
```

`published_at` è la data della novità verificata nella fonte, non quella del report:
usa null se non accertata. `kind`: pricing, deprecation, vendor_release, method,
model_weights, tool_release, dataset, research. `vertical`: models-releases,
cost-limits, tools-agents, media-generation, claims-risks. `suggested_format`:
daily per cambiamenti tempestivi, method per esperimenti evergreen, deep per analisi
multi-fonte. Apri e leggi le fonti prima di scrivere. Se hai soltanto una fonte
secondaria, dichiaralo nella summary e indica che la primaria resta da trovare.
Non inventare URL, release, risultati o miglioramenti di produttività.

Deduplica lo stesso annuncio, anche se appare in entrambi i radar. Cerca nelle ultime
24-72 ore, allarga a 7 giorni dichiarandolo; non forzare un numero minimo di notizie.
Tieni separati annunci, funzionalità utilizzabili, webinar e ipotesi architetturali.
Nell'export non includere Impact/Confidence/Maturity Score, dati personali o aziendali,
nomi dei progetti privati, chat URL, credenziali o istruzioni di automazione.
Per i pattern cita quanti casi indipendenti hai davvero: due casi non dimostrano
diffusione generalizzata. Lo stub dimostra un meccanismo, non la qualità del modello.
L'export contiene piste da verificare dalla redazione, non contenuti già approvati.

## Priorità editoriale aggiornata

Per l'export del canale privilegia i modelli di punta correnti di OpenAI, Google
Gemini e Anthropic Claude e le funzionalita direttamente collegate. Altri modelli
richiedono evidenza di rilevanza competitiva concreta. Indica nome/versione esatti:
notizie AI generiche restano fuori. Repository, MCP, plugin, skill e workflow
qualificano anche senza legame diretto con un modello di punta quando consentono
un compito AI concreto e hanno artefatti, accesso e limiti verificabili.
Nell'AI Productivity Radar il compito deve migliorare l'uso di ChatGPT, Codex,
Claude o Claude Code; Gemini rientra nella copertura editoriale dei modelli di
punta. Non ampliare questa ricerca a una lista di strumenti AI generici.
Le nuove architetture richiedono paper, report tecnico, codice o documentazione primaria;
non inferire gli interni di un modello chiuso dal suo comportamento.

Cerca cosa si può fare di nuovo con AI e per quale compito concreto.
In summary spiega capacità nuova e prima/dopo documentato; in decision il valore per
il lettore; in example_idea un primo passo concreto, senza metriche artificiali.
Metodi appena rilasciati possono essere daily; non relegarli a deep solo perché tecnici.
Non dichiarare inedita per il canale una notizia senza verificarne l’archivio:
la redazione deve controllare episodi pubblicati ed effettivamente in coda.

Il report personale mantiene il suo prompt di ricerca e le sue sezioni. L'export
rimane un insieme di piste: in decision indica per quale lettore e compito cambia
una scelta; in availability rendi visibili i prerequisiti che distinguono uso
quotidiano, lavoro professionale e implementazione tecnica. Non aggiungere campi
al JSON, non assegnare playlist e non trasformare la stessa pista in tre copie.
La redazione applica il prompt di argomento, quello del pubblico e il formato
prima di scrivere un video e approva una sola playlist per il video completo.
