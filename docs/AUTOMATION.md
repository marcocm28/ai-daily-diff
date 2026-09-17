# Ricerca → GitHub → YouTube

## Decisione del 17 settembre 2026

Marco ha richiesto l'esecuzione automatica completa e scelto Codex sul PC per leggere
i due radar ChatGPT e completare l'authoring. Rendering e upload rimangono su GitHub.
Questa decisione sostituisce il precedente gate umano per ogni episodio.

Il canale dedicato **@aidailydiff** esiste già e ha ID
`UCDEWpe6dU5_-3Im8KxQk5WA`, verificato nelle impostazioni YouTube il 17/09/2026.
L'ultimo upload precedente, https://youtu.be/H_InfyggYMs, era invece Non in elenco sul
canale personale **@marcocomande8253**, ID `UCya_uag0-DwHL2XlP3hIB6w`.
Il nome del canale nel README non sceglie la destinazione: la sceglie il token OAuth.

## Catena automatica

1. I due task ChatGPT mantengono i loro orari e producono il report + JSON editoriale.
2. Il task ricorrente in Codex segue `prompts/scheduled-pipeline.md`, con controlli alle
   13:30 e 17:30 da lunedì a sabato (Europe/Rome). Richiede PC acceso, Codex aperto e
   browser collegato con sessione ChatGPT valida. Se i report o l'inbox sono in ritardo,
   attende un controllo successivo; non inventa l'input mancante.
3. La copia isolata `.local/pipeline` importa, seleziona, verifica le fonti, scrive ed
   esegue gli esempi. `tools/queue_episode.py DATE` abilita SOLO quell'episodio alla
   pubblicazione. Il push normale su main avvia GitHub, senza un'altra approvazione.
4. Render verifica tutto su un runner senza secret YouTube, crea video/materiali e
   un manifest SHA-256 legato alla run e al commit. Non committa più binari nel repo.
5. Una run Render main riuscita avvia Pages e Upload. Upload scarica proprio il suo
   artefatto, confronta i digest e controlla che l'episodio sia ancora quello di main.
6. Prima di caricare, interroga `channels.list(mine=true)` e richiede l'ID configurato.
   Un token del canale personale fallisce PRIMA dell'upload.
7. Il registro `data/publications/DATE.json` su GitHub conserva prenotazione, video ID,
   canale, visibilità reale e stato. Una prenotazione viene scritta PRIMA dell'upload.
   Se la risposta dell'upload si perde, il riavvio cerca il marcatore nella playlist
   del canale; se non riesce a riconciliare, si ferma senza creare un duplicato.

I video storici non vengono caricati automaticamente: servono `publication.ready`,
la data minima configurata e una data episodio negli ultimi sette giorni. I report
di ricerca sono input, non materiale già verificato. Il settimanale usa il sabato;
la domenica non vengono creati nuovi episodi.

## Collegamento OAuth una tantum (ancora necessario)

I secret GitHub sono presenti, ma quelli aggiornati l'11/09 hanno caricato sul canale
personale. Cambiare canale nel browser NON modifica un refresh token già emesso.

1. Eseguire localmente `python tools/get_refresh_token.py "PERCORSO/client_secret.json"`
   con il file OAuth Desktop del progetto Google Cloud già usato. Nel consenso Google
   selezionare il canale del brand **aidailydiff**, non il canale personale. Il consenso
   e l'eventuale autenticazione vanno completati da Marco.
2. Lo script verifica l'ID prima di salvare. Scrive i tre valori solo in
   `.local/youtube-secrets.env` (ignorato da Git), senza stamparli nei log.
   Copiare i valori nei corrispondenti secret esistenti del repository:
   https://github.com/marcocm28/ai-daily-diff/settings/secrets/actions
3. Eseguire **Verify YouTube channel** da GitHub Actions: deve riportare esattamente
   `UCDEWpe6dU5_-3Im8KxQk5WA`. Questa verifica non carica alcun video.
4. La pipeline è già configurata per richiedere visibilità **public** solo su quel
   canale. Se YouTube applica restrizioni e restituisce private, il job segnala errore
   e registra la visibilità reale; non dichiara pubblicato un video privato.

Non incollare credenziali nelle chat. Il vecchio video personale non viene cancellato,
spostato o reso pubblico da questa configurazione.

## Arresto e recupero

- `config/publishing.json`: impostare `enabled` a false interrompe i nuovi upload.
- Per un errore, leggere prima `data/publications/DATE.json` e i log Actions.
  Il workflow manuale Upload richiede una run Render main riuscita; il default è dry-run.
  Ripetere una run con ricevuta nota non carica un secondo video.
- `state=processing` significa che il video esiste ma YouTube non ha ancora terminato:
  ricontrollare la stessa run Upload, non creare un nuovo episodio.
- Prenotazione senza ID: riconciliare il canale; non cancellarla per tentare alla cieca.
- Token scaduto/revocato: ripetere il collegamento sullo stesso canale; nessun fallback
  su un account diverso. Il task avverte sui problemi nuovi, senza ripetere notifiche
  quando la condizione è invariata.

Riferimenti: [task programmati](https://learn.chatgpt.com/docs/automations),
[identità del canale](https://developers.google.com/youtube/v3/docs/channels/list),
[upload e restrizioni](https://developers.google.com/youtube/v3/docs/videos/insert).
