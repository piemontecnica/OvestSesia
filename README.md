# Nuovo Scolmatore di Trino – II lotto stralcio
Interfaccia web di monitoraggio allerte meteo e piene (gara 26_066 Ovest Sesia, sub criterio B.2.c – RTI Bertini Srl, Impresa F.lli Sogno & Figli Srl, So.d.i.s. Srl).

## Pubblicazione su GitHub Pages
1. Crea il repository e, da "Add file → Upload files", trascina `index.html`, `README.md` e le cartelle `data` e `scripts`.
2. Il workflow va creato a mano (le cartelle che iniziano con il punto spesso non vengono trascinate): "Add file → Create new file", nome `.github/workflows/idrometri.yml`, incolla il contenuto del file omonimo e salva.
3. Settings → Pages → Source: *Deploy from a branch* → `main`, cartella `/ (root)`.
4. Dopo 1–2 minuti la pagina è su `https://<utente>.github.io/<repository>/` (con `#bacino` si apre sulla vista idrometri).

## Contenuto
- `index.html` – interfaccia (Leaflet 1.9.4 da cdnjs, font Jost da Google Fonts).
- `data/layers.js` – vettoriali dal progetto QGIS in EPSG:4326.
- `data/planimetria.webp` – "Planimetria generale_modificato.tif" come immagine unica georiferita (7000 px, ≈3 MB).
- `scripts/aggiorna_idrometri.py` e `.github/workflows/idrometri.yml` – lettura automatica degli idrometri.

## Letture idrometriche (GitHub Action)
Il servizio ARPA non consente la lettura diretta dal browser da un dominio esterno (blocco CORS): per questo le schede risultavano senza risposta.
La lettura ora la fa GitHub: `.github/workflows/idrometri.yml` esegue ogni 10 minuti `scripts/aggiorna_idrometri.py`, che interroga `meteorologia_clima/TR_idrometri` e salva `data/idrometri.json` nel repository; la pagina legge quel file.

Dopo il primo caricamento:
1. Settings → Actions → General → *Workflow permissions*: seleziona **Read and write permissions** e salva.
2. Actions → "Aggiorna letture idrometri ARPA" → **Run workflow** per la prima esecuzione (poi parte da sola).
3. Nel log dell'esecuzione compaiono gli attributi delle due stazioni lette.

GitHub può ritardare le esecuzioni programmate di qualche minuto e sospende le pianificazioni dopo 60 giorni senza attività sul repository (si riattivano dalla scheda Actions). Se il file è più vecchio di 3 ore la pagina tenta la lettura diretta e, in mancanza, mostra l'ultima copia segnalandola come non aggiornata.

## Allerta sul comune di Trino
Colonna di destra con il widget ARPA `rischi_naturali/widget/comuni/002148`. Tra 761 e 1279 px di larghezza si apre dal pulsante "Allerta Trino" sulla mappa; su smartphone compare sotto la mappa.
