# Radar ChatGPT → AI Daily Diff

**Aggiornamento 17/09:** la lettura/importazione descritta qui è ora eseguita dal task
ricorrente Codex sul PC. Il flusso completo è in `docs/AUTOMATION.md`; il gate manuale
storico è sostituito, su richiesta di Marco, da verifica automatica e pubblicazione
vincolata al canale dedicato. Rimane disponibile anche l'importazione manuale.

## Cosa è collegato

I due radar hanno ruoli complementari: **Novità tecniche AI** segnala release e
capability ufficiali; **AI Productivity Radar** suggerisce metodi, workflow, skill,
MCP, tool ed esperimenti. I feed pubblici esistenti restano attivi.

Il 16 settembre 2026 sono stati letti dal browser autenticato i prompt e l'ultimo
risultato di entrambe le attività. I report completi contengono anche contesto
personale: nel repository si conservano solo segnalazioni editoriali curate.

## Importazione

1. Nell'attività apri l'ultimo risultato. Copia il solo blocco JSON per AI Daily Diff
   in `.local/radar/report.json`, oppure chiedi a Codex di leggere le due attività
   nel browser collegato e preparare quel JSON. Non incollare cookie o token.
2. Esegui `python src/radar.py .local/radar/report.json`.
3. Esegui `python src/selection.py YYYY-MM-DD`. Unisce l'inbox delle API ai report
   degli ultimi sette giorni, filtra data e soglia, deduplica gli URL e conserva
   le idee Method/Deep nei report per il lavoro settimanale.
4. Esegui `python src/author.py YYYY-MM-DD` e completa l'episodio applicando
   `prompts/research.md`. `source_review` deve documentare la verifica della primaria.
5. Esegui `python tools/queue_episode.py YYYY-MM-DD` prima del push dell'episodio:
   GitHub verifica, renderizza e avvia Pages/YouTube sulla destinazione configurata.

Per il settimanale usa `python src/selection.py YYYY-MM-DD --kind method` seguito da
`python src/author.py YYYY-MM-DD --kind method` (oppure `deep` in entrambi).
Il JSON dell'episodio resta uno per data: scegli una data non già usata da un Daily.
La soglia 0,55 riguarda le notizie Daily. Le piste curate Method/Deep con punteggio
positivo restano selezionabili anche se una ricerca non ha la portata di una release;
i controlli sulle fonti e sugli esempi restano identici.

L'importazione è idempotente: lo stesso report non crea duplicati; se la stessa data
e attività contengono dati diversi, chiede di revisionare il file invece di sovrascriverlo.
L'importatore accetta solo i campi editoriali previsti, ma **non anonimizza il testo**:
chi prepara il JSON deve rimuovere il contesto personale prima di importarlo.

## Limiti espliciti

Non è stato creato un accesso API al profilo ChatGPT né uno scraper di sessione.
GitHub Actions non può leggere automaticamente queste attività private: riceve i
report JSON quando vengono portati nel repository. Il task Codex usa il browser
autenticato per portarli nel repository; il vecchio driver `run_daily.py` usa solo
i report già disponibili e non è l'entrypoint della nuova automazione.
La lettura assistita dal browser richiede una sessione autenticata disponibile.

L'appendice per i prompt programmati è versionata in `prompts/radar-export.md`.
Il 16/09/2026 è stata aggiunta a entrambe le attività una corrispondente appendice
di export editoriale, conservando il prompt precedente e la pianificazione.
Il 17/09/2026 l'esecuzione di **Novità tecniche AI** ha prodotto il blocco JSON
richiesto: il report reale è stato importato in `data/radar/2026-09-17-technical.json`.
Contiene una pista Daily e una Deep, entrambe ancora da verificare sulle fonti.
Alla verifica del 17/09 il risultato più recente di **AI Productivity Radar** era
ancora quello del 16/09: la nuova esportazione sarà verificabile alla prossima esecuzione.
La cartella `.local/` è ignorata da Git. Non pubblicare esportazioni complete delle chat.

## Provenienza e verifica

Gli import conservano nome del radar e data del report, ma non link alle chat private.
`is_primary_source` resta false e `verification_status` resta pending: né il punteggio
di fiducia del radar né un dominio ufficiale provano la correttezza di un'affermazione.
La selezione può proporre una pista; la pubblicazione richiede la lettura della fonte,
un estratto breve, la decisione pratica, la disponibilità e l'esempio verificato.

Gli esempi confrontano tre elementi: stdout reale, `expected_output.txt` e l'output
mostrato nel JSON. Il badge viene timbrato solo nel contesto GitHub Actions.
