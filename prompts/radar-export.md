# Appendix for the two existing ChatGPT scheduled tasks

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
  "example_idea": "Esperimento CPU offline sotto 60 secondi, metrica e limite della prova",
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
