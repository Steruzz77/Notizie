# Il Corriere dello Steruz — istruzioni per preparare un'edizione

Questo repository è il giornale personale di Alex (soprannome Steruz), pubblicato con GitHub Pages su
https://steruzz77.github.io/Notizie/ . Ogni edizione si prepara scrivendo **un file JSON** e lanciando
l'impaginatore: non scrivere mai l'HTML a mano.

```
python3 sistema/build.py /percorso/edizione.json
```

L'impaginatore aggiorna `index.html` (ultima edizione), salva la copia in `archivio/` e rigenera
`archivio.html`. Non toccare `sistema/stile.css`, `sistema/giornale.js`, `sistema/head.html`:
il design è stato scelto da Alex con cura. `anteprima.html` è la pagina
che Alex usa per vedere le modifiche prima di approvarle: non toccarla durante le uscite.

## Chi è il lettore
Alex, 23 anni, di Lumezzane (BS). Ha lasciato la scuola presto e vuole imparare a capire l'attualità
e a farsi un'opinione. Gli piacciono informatica e musica, in particolare il **rap italiano**.
Vuole notizie vere e complete, spiegate in modo semplice, senza essere trattato da bambino.

## Regole sui contenuti
- Scrivi **con parole tue**, frasi semplici e chiare. Niente citazioni lunghe dagli articoli.
- **Termini**: Alex vuole imparare le parole vere usate da giornali e politici. NON sostituirle con
  parole più semplici: scrivile nel testo con la sintassi `[[termine|definizione in una frase semplice]]`.
  Diventano parole tratteggiate che si toccano per leggere il significato. Spiega **tutti** i termini
  di settore e le parole poco comuni: termini politici, economici, tecnici, musicali, meteo; sigle (Cpr,
  Anm, Ue, Pil...); nomi di istituzioni e cariche (Viminale, prefetto, Consulta...); parole straniere
  non comuni; espressioni giuridiche e giornalistiche (indagato, rinvio a giudizio, ballottaggio...);
  luoghi o personaggi poco noti. Non c'è un numero fisso: ogni termine così va spiegato, senza saltarne.
  **Non spiegare le parole comuni** che chiunque conosce (podio, classifica, Suv, smartphone, album,
  sciopero, polizia...): Alex non va trattato da bambino. Ogni parola va spiegata solo la prima volta
  che compare nella notizia.
- **Approfondisci**: per le 1–2 parole più complesse di una notizia (termini di settore, sigle o
  espressioni strane che meritano più contesto) aggiungi anche un
  approfondimento, con la sintassi `[[termine|spiegazione corta||approfondimento]]`. La spiegazione
  corta resta di una frase; l'approfondimento (2–4 frasi) aggiunge contesto: come funziona, da dove
  viene, un esempio concreto, perché se ne discute, collegandolo se possibile alla notizia. Nella
  pagina compare il tasto "Approfondisci" sotto la spiegazione corta. Mettilo sempre nell'apertura e
  nella spalla, e in tutte le notizie dove c'è un termine complesso. Non metterlo su parole che si
  capiscono già con la frase corta: solo dove c'è davvero qualcosa in più da capire.
  Esempio: `[[direttissima|Un processo veloce, fatto subito dopo l'arresto quando le prove sono già chiare.||Di solito tra arresto e processo passano mesi. Con la direttissima l'arrestato va davanti al giudice entro pochi giorni, perché colto sul fatto o reo confesso. Si usa spesso dopo scontri o furti in flagrante.]]`
- **Cronaca nera e fatti violenti**: non escluderli e non addolcirli. Fatti concreti, al livello dei
  giornali seri, senza toni sensazionalistici.
- **Politica**: neutrale. Fatti e posizioni delle varie parti, senza dire chi ha ragione.
- Ogni notizia ha la sua **fonte** con link all'articolo.
- **Fonti affidabili**: prendi le notizie solo da testate serie e conosciute. Nazionali: ANSA, Il Post,
  Rainews, Sky TG24, AGI, Adnkronos, Corriere, Repubblica, La Stampa, Il Sole 24 Ore, Open, Il Giorno.
  Mondo: le stesse, più Reuters, AP, BBC, Al Jazeera. Brescia: Giornale di Brescia, Il Giorno
  (cronaca di Brescia), QuiBrescia, BsNews (BresciaToday e Bresciaoggi non si aprono: vedi sotto). Tecnologia: HWupgrade, Il Post, Wired, DDay,
  Tom's Hardware, Multiplayer.it. Musica: Rockol, Rolling Stone Italia, All Music Italia, Rapologia,
  Esse Magazine, Billboard Italia, FIMI. Vanno bene anche siti piccoli o poco noti, purché affidabili:
  testate giornalistiche vere (con redazione e direttore) o siti specializzati seri. Da evitare blog
  anonimi, siti acchiappa-clic, pagine che copiano altri articoli e qualsiasi sito che diffonde notizie
  false. Se usi un sito fuori da questo elenco, controlla che la notizia sia confermata anche da
  un'altra fonte seria; se non lo è, scegli un'altra notizia. L'elenco completo dei siti accettati è `FONTI_OK` in `sistema/build.py`.
- **Niente sport**: è una scelta di Alex. Non mettere partite, risultati, calciomercato o gare,
  nemmeno in Italia o in cronaca. Fa eccezione solo un fatto che esce dallo sport (es. un'inchiesta
  giudiziaria o un fatto di cronaca grave).
- **Foto**: per ogni notizia prova a prendere l'immagine principale dell'articolo con WebFetch
  (chiedi l'URL esatto del meta `og:image`). Usa solo URL `https://` che hai visto davvero, mai inventati.
  Se non la trovi, ometti il campo `foto`: la notizia esce senza immagine e va bene così.
- Verifica che le notizie siano **del periodo giusto** (vedi sotto) e non vecchie: guarda la data
  dell'articolo, non solo quella del risultato di ricerca.
- **Solo fatti letti davvero.** Scrivi una notizia solo se hai letto l'articolo intero con WebFetch,
  o un altro articolo serio che racconta lo stesso fatto. Se la fonte non si apre, **non scrivere
  partendo dal titolo o dall'anteprima della ricerca**: cerca lo stesso fatto su un'altra testata
  dell'elenco e apri quella (e metti quella come fonte). Se non trovi nessun articolo leggibile,
  scarta la notizia e scegline un'altra. Non aggiungere dettagli presi dalla memoria o "di contesto"
  (numeri, date, nomi, posizioni dei partiti) che non hai letto in una fonte. Riporta sempre le
  precisazioni che cambiano il senso: pena sospesa, "secondo la polizia", stime, dati non verificati.
- **Precisione prima di tutto.** Numeri, date, nomi, età e luoghi devono essere esattamente quelli
  dell'articolo letto. Non prendere mai un numero dal titolo di un risultato di ricerca. Fai attenzione
  ai bilanci che sommano più fatti (es. "da ieri sera un morto e 14 feriti in tutta la città") e non
  attribuirli a un solo episodio; non confondere la data di un fatto con quella di un altro (es. data
  del trapianto e data della morte). Non lasciare fuori i dettagli che servono a capire la notizia
  (es. che la vittima era un bambino). Se servono due frasi in più per essere chiari e precisi,
  scrivile: meglio una notizia un po' più lunga che una notizia imprecisa.

## Come cercare (importante per non bloccarti)
- Usa **solo WebSearch e WebFetch** per cercare notizie, leggere articoli e trovare le foto.
  Non usare mai curl, wget o script Python per scaricare pagine o immagini dai siti di notizie:
  dalla shell quei siti sono bloccati e serve un'approvazione che durante le uscite automatiche
  nessuno può dare.
- Con WebFetch apri **solo indirizzi che hai visto nei risultati di WebSearch**, copiati esattamente.
  Non costruire indirizzi a mano (es. `sito.it/meteo/milano`) e non aprire homepage digitate
  a memoria: vengono bloccati perché richiedono l'approvazione di Alex. Per trovare una pagina, prima
  cercala con WebSearch e poi apri il link esatto del risultato.
- **Non aprire i link letti dentro una homepage o un elenco di notizie** (es. "ultime notizie" di ANSA,
  la pagina Valtrompia del Giornale di Brescia): WebFetch li riscrive a modo suo, a volte sbagliati, e
  il sistema li blocca anche sui siti autorizzati, facendo perdere 5 minuti a ogni tentativo. Se una
  homepage ti fa vedere un titolo interessante, cerca quel titolo con WebSearch e apri il link del
  risultato. Se un WebFetch si blocca in attesa di approvazione, non riprovare lo stesso link: cercalo.
- I siti dell'elenco `FONTI_OK` sono già autorizzati in `.claude/settings.json`: WebFetch li apre
  senza chiedere. Se aggiungi un sito a `FONTI_OK`, aggiungilo anche lì.
- Se un sito rifiuta WebFetch (paywall, blocco dei robot) o chiede un'approvazione, non insistere:
  passa subito a un'altra fonte che racconta lo stesso fatto (es. ANSA, Il Post, Sky TG24, Rainews,
  Giornale di Brescia, QuiBrescia, BsNews).
- Lavora con ordine: fai le ricerche delle varie sezioni in parallelo, così resta tempo per la
  verifica finale (vedi "Verifica delle notizie prima di pubblicare").

## Le due edizioni
- **Mattina** (`"edizione": "mattina"`): cosa è successo dalle 18 del giorno prima a stamattina, più le
  notizie che domineranno la giornata. Non ripetere notizie già chiuse ieri pomeriggio; se una storia
  importante ha sviluppi, raccontala come aggiornamento dicendo in una frase da dove si era rimasti.
- **Sera** (`"edizione": "sera"`): le novità della giornata, dopo le 8 del mattino.
- **Domenica mattina** (`"edizione": "domenica"`): come la mattina, ma aggiungi come **prima sezione**
  `"Riepilogo della settimana"` con le 6–8 notizie più importanti degli ultimi 7 giorni. Per sceglierle
  leggi i JSON degli ultimi 7 giorni in `archivio/`, e completa con una ricerca se mancano giorni.

Per sapere cosa è già uscito, guarda il JSON più recente in `archivio/` prima di cercare.

## Le sezioni (in quest'ordine)
1. **Prima pagina**: `apertura` = la notizia più importante (testo in 2–3 paragrafi, con sommario);
   `spalle` = 1 notizia importante (1–2 paragrafi); `parola` = la parola del giorno, un termine
   importante tra quelli usciti oggi, spiegato meglio in 2–3 frasi; `accadde` = un fatto storico
   **verificato** avvenuto in questa data (preferisci tecnologia, musica, scienza, storia d'Italia).
2. **Lumezzane e Brescia**: 5–6 notizie. **Prima cerca Lumezzane e la Valtrompia** (Sarezzo, Gardone,
   Villa Carcina, Concesio, Marcheno, Tavernole, Bovegno, Collio, Polaveno, Lodrino, Caino...): cronaca,
   Comune, lavori e strade, scuole, aziende, eventi, la squadra no (niente sport). Metti in cima alla pagina
   la notizia più vicina a Lumezzane. Poi completa con Brescia città e il resto della provincia.
   Fonti: Giornale di Brescia, Il Giorno (cronaca di Brescia), QuiBrescia e BsNews: sono tutte testate
   registrate e si aprono con WebFetch. Cercale con WebSearch usando `allowed_domains` (es. "Lumezzane"
   o il nome di un comune della Valtrompia su quibrescia.it e bsnews.it). **BresciaToday e Bresciaoggi
   bloccano i programmi automatici**: non provare ad aprirli e non aggirare il blocco. Usa i loro titoli
   nei risultati di ricerca solo per scoprire le notizie, poi leggi lo stesso fatto su una delle altre
   testate. Se un fatto importante su Lumezzane o la Valtrompia c'è solo su BresciaToday o Bresciaoggi,
   non scriverlo: segnalalo in una riga nel riepilogo finale con il link, così Alex lo apre da sé.
3. **Italia**: 6–7 notizie (politica, cronaca, economia, società).
4. **Dal mondo**: 5–6 notizie.
5. **Tecnologia**: 3–4 notizie (smartphone, IA, informatica, videogiochi, internet). Fonti es. HWupgrade, Il Post.
6. **Musica**: 3–4 notizie con focus sul **rap italiano**: nuovi album, EP, singoli (il venerdì è giorno
   di uscite), annunci, tour, classifiche FIMI, interviste. Fonti: Rockol, Rolling Stone Italia, All Music Italia, Rapologia, Esse Magazine,
   Billboard Italia, classifiche FIMI. Fai almeno due ricerche separate (es. "rap italiano nuovo album" e
   "rapper tour date annuncio") per arrivare a 4 notizie: valgono anche annunci di concerti, featuring,
   certificazioni FIMI e classifiche Spotify.
7. **Meteo**: la pagina dell'ultima edizione mostra da sola una mappa dell'Italia con le previsioni dal vivo
   (Open-Meteo, aggiornate ogni volta che Alex apre il giornale): non devi cercare i capoluoghi. Il campo
   `meteo` serve comunque: la situazione, le righe che restano nelle copie d'archivio e fanno da riserva se la
   mappa non si carica, e gli avvisi. Cerca le previsioni su 3BMeteo/ilMeteo per oggi e domani: righe per
   Lumezzane e Brescia (sempre, con min–max) e per Nord, Centro e Sud (o città come Milano, Roma, Napoli,
   Palermo) con min–max. Se le fonti segnalano fenomeni particolari (nebbia, vento forte, mare mosso, allerte
   della Protezione civile, caldo o gelo intensi) mettili in `avvisi`; se non ce ne sono, ometti il campo.

Ogni notizia normale: titolo breve e 2–4 frasi. Alex vuole un giornale ricco: punta al numero massimo
di notizie indicato per ogni sezione. Solo se davvero non ci sono notizie rilevanti mettine meno, ma
non inventare nulla e non gonfiare notizie minori.

## Formato del JSON
Esempio completo e funzionante: `sistema/esempio.json`.

```json
{
 "data": "AAAA-MM-GG",
 "edizione": "mattina | sera | domenica",
 "prima": {
  "apertura": NOTIZIA (con "sommario"),
  "spalle": [NOTIZIA],
  "parola": {"termine": "...", "testo": "..."},
  "accadde": {"data": "23 ottobre 2001", "testo": "..."}
 },
 "sezioni": [ {"nome": "Lumezzane e Brescia", "notizie": [NOTIZIA, ...]}, ... ],
 "meteo": {
  "situazione": {"titolo": "...", "testo": ["..."]},
  "oggi_etichetta": "Oggi · venerdì 23", "oggi": [RIGA, ...],
  "domani_etichetta": "Domani · sabato 24", "domani": [RIGA, ...],
  "avvisi": {"oggi": [AVVISO, ...], "domani": [AVVISO, ...]},
  "nota": "facoltativa",
  "fonti": [{"nome": "3BMeteo", "url": "https://..."}]
 }
}
```
NOTIZIA = `{"occhiello": "Sezione · Tema", "titolo": "...", "sommario": "solo per l'apertura",
"testo": ["paragrafo 1", "paragrafo 2"], "fonte": {"nome": "ANSA", "url": "https://..."},
"foto": {"url": "https://...", "didascalia": "facoltativa"}}`

RIGA meteo = `{"luogo": "Brescia", "icona": "sole|parz|nuvole|pioggia|temporale|neve|nebbia",
"cond": "Pioggia debole in serata", "temp": "11°–16°"}`

AVVISO meteo (facoltativo, solo se le fonti lo dicono) = `{"icona": "nebbia|vento|mare|allerta|caldo|gelo|pioggia|neve|temporale",
"testo": "Nebbia al mattino nella pianura del Nord"}`

Le sezioni sono pagine del giornale: il sommario in prima pagina si crea da solo.

## Controllo prima di pubblicare
Dopo aver lanciato `build.py`, leggi il **CONTROLLO** che stampa in fondo: elenca le notizie senza
nessuna parola spiegata, l'apertura o la spalla senza Approfondisci, le edizioni con pochi Approfondisci,
le sezioni sotto il numero di notizie richiesto, le fonti fuori dall'elenco (da verificare, non per forza da togliere) e l'assenza di notizie su
Lumezzane o la Valtrompia. Per ogni avviso sulle parole rileggi la notizia e spiega i termini di settore,
le sigle e i nomi poco noti che hai lasciato senza spiegazione; se davvero non ce ne sono, lascia
com'è e non aggiungere parole comuni solo per far sparire l'avviso. Per le fonti fuori elenco controlla che la notizia sia confermata da una fonte seria, altrimenti sostituiscila; cerca
le notizie mancanti, poi rilancia `build.py`: riscrive la stessa edizione. Ripeti finché restano solo
avvisi che non si possono risolvere (es. davvero nessuna notizia su Lumezzane oggi).

## Verifica delle notizie prima di pubblicare
Dopo il CONTROLLO di `build.py` e prima del `git push`, rileggi l'edizione notizia per notizia e
confrontala con gli articoli che hai letto (riaprili con WebFetch se non hai più i dettagli). Per ogni
notizia controlla: numeri, date, nomi, età e luoghi uguali alla fonte; nessun dettaglio preso da un
titolo o dalla memoria; precisazioni importanti presenti ("secondo la polizia", "indiscrezione", pena
sospesa); data dell'articolo nel periodo giusto; nessuna notizia già uscita nelle ultime edizioni. Per
la politica controlla che ci siano le posizioni di tutte le parti citate nella fonte. Correggi il JSON,
rilancia `build.py` e solo dopo pubblica. Nel riepilogo finale scrivi in una riga cosa hai corretto
durante la verifica (o "nessuna correzione").

## Pubblicare
```
git add -A
git -c user.name="Steruzz77" -c user.email="alexstera2003@gmail.com" commit -m "Edizione <edizione> del <data>"
git push origin HEAD
```
Il sito si aggiorna da solo in 1–2 minuti.
