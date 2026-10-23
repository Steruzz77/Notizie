# Il Corriere dello Steruz — istruzioni per preparare un'edizione

Questo repository è il giornale personale di Alex (soprannome Steruz), pubblicato con GitHub Pages su
https://steruzz77.github.io/Notizie/ . Ogni edizione si prepara scrivendo **un file JSON** e lanciando
l'impaginatore: non scrivere mai l'HTML a mano.

```
python3 sistema/build.py /percorso/edizione.json
```

L'impaginatore aggiorna `index.html` (ultima edizione), salva la copia in `archivio/` e rigenera
`archivio.html`. Non toccare `sistema/stile.css`, `sistema/giornale.js`, `sistema/head.html`:
il design è stato scelto da Alex con cura. Le vecchie pagine di prova (`carta.html`, `prova.html`,
`anteprima.html`) non vanno modificate.

## Chi è il lettore
Alex, 23 anni, di Lumezzane (BS). Ha lasciato la scuola presto e vuole imparare a capire l'attualità
e a farsi un'opinione. Gli piacciono informatica e musica, in particolare il **rap italiano**.
Vuole notizie vere e complete, spiegate in modo semplice, senza essere trattato da bambino.

## Regole sui contenuti
- Scrivi **con parole tue**, frasi semplici e chiare. Niente citazioni lunghe dagli articoli.
- **Termini**: Alex vuole imparare le parole vere usate da giornali e politici. NON sostituirle con
  parole più semplici: scrivile nel testo con la sintassi `[[termine|definizione in una frase semplice]]`.
  Diventano parole tratteggiate che si toccano per leggere il significato. Usale per termini politici,
  economici, tecnici, musicali, meteo. 1–4 per notizia, non di più.
- **Cronaca nera e fatti violenti**: non escluderli e non addolcirli. Fatti concreti, al livello dei
  giornali seri, senza toni sensazionalistici.
- **Politica**: neutrale. Fatti e posizioni delle varie parti, senza dire chi ha ragione.
- Ogni notizia ha la sua **fonte** con link all'articolo.
- **Foto**: per ogni notizia prova a prendere l'immagine principale dell'articolo con WebFetch
  (chiedi l'URL esatto del meta `og:image`). Usa solo URL `https://` che hai visto davvero, mai inventati.
  Se non la trovi, ometti il campo `foto`: la notizia esce senza immagine e va bene così.
- Verifica che le notizie siano **del periodo giusto** (vedi sotto) e non vecchie.

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
2. **Lumezzane e Brescia**: 5–6 notizie (Lumezzane, Valtrompia, provincia). Fonti: Giornale di Brescia,
   BresciaToday, Bresciaoggi.
3. **Italia**: 6–7 notizie (politica, cronaca, economia, società).
4. **Dal mondo**: 5–6 notizie.
5. **Tecnologia**: 3–4 notizie (smartphone, IA, informatica, videogiochi, internet). Fonti es. HWupgrade, Il Post.
6. **Musica**: 3–4 notizie con focus sul **rap italiano**: nuovi album, EP, singoli (il venerdì è giorno
   di uscite), annunci, tour, classifiche FIMI, interviste. Fonti es. Rockol, Rolling Stone Italia, Newsic.
7. **Meteo**: generato dal campo `meteo` (vedi formato). Cerca le previsioni su 3BMeteo/ilMeteo per
   oggi e domani: Lumezzane, Brescia, Milano, Roma, Napoli, Palermo (e altre se utili) con min–max;
   se per domani mancano i dati per città, usa righe per zona (Nord, Centro, Sud).

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

Le sezioni sono pagine del giornale: il sommario in prima pagina si crea da solo.

## Pubblicare
```
git add -A
git -c user.name="Steruzz77" -c user.email="alexstera2003@gmail.com" commit -m "Edizione <edizione> del <data>"
git push origin HEAD
```
Il sito si aggiorna da solo in 1–2 minuti.
