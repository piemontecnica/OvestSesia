#!/usr/bin/env python3
"""Scarica dall'API realtime di ARPA Piemonte i livelli degli ultimi 3 giorni dei due
idrometri di riferimento e li salva in data/idrometri.json (letto dalla pagina web).
Eseguito ogni 10 minuti dalla GitHub Action .github/workflows/idrometri.yml."""
import json, sys, datetime, urllib.request, urllib.parse, pathlib, re

ROOT = pathlib.Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "idrometri.json"
API = "https://utility.arpa.piemonte.it/api_realtime"
UA = {"User-Agent": "RTI-Bertini-monitoraggio-cantiere/1.0", "Accept": "application/json"}

def get(path, **q):
    url = API + path + ("?" + urllib.parse.urlencode(q) if q else "")
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=30) as r:
        return json.load(r)

def stazioni():
    txt = (ROOT / "data" / "layers.js").read_text(encoding="utf-8")
    js = json.loads(txt[txt.index("{"):txt.rindex("}") + 1])
    out = []
    for f in js["idrometri"]["features"]:
        p = f["properties"]
        out.append((p["Nome"], re.search(r"id=(\d+)", p["Link"]).group(1)))
    return out

def serie(codice):
    candidati = list(dict.fromkeys([codice.lstrip("0")[-6:], codice, codice.lstrip("0")]))
    for c in candidati:
        d = get("/data_pie", station_code=c, page_size=2000)
        pts = [{"t": r["date"], "h": r["hydrometric_level"]} for r in d.get("data", []) if r.get("hydrometric_level") is not None]
        if pts:
            return c, sorted(pts, key=lambda x: x["t"])
        print(f"  station_code={c}: nessun livello")
    return None, []

def main():
    try:
        print("Stato API:", get("/status"))
    except Exception as e:  # noqa: BLE001
        print(f"::warning::API ARPA non raggiungibile da GitHub: {e}")
        return 0
    out = {"aggiornato": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"), "stazioni": {}}
    for nome, codice in stazioni():
        try:
            c, pts = serie(codice)
        except Exception as e:  # noqa: BLE001
            print(f"::warning::{nome}: {e}"); continue
        print(f"{nome}: codice {c}, {len(pts)} misure" + (f", ultima {pts[-1]}" if pts else ""))
        if pts:
            out["stazioni"][nome] = {"station_code": c, "dati": pts}
    if not out["stazioni"]:
        print("::warning::Nessun livello trovato: controllare i codici stazione (vedi /pie_anag)")
        try:
            anag = get("/pie_anag")
            righe = anag.get("data", anag) if isinstance(anag, dict) else anag
            for r in righe:
                if re.search(r"SEBASTIANO|VEROLENGO", json.dumps(r, ensure_ascii=False), re.I):
                    print("  anagrafica:", r)
        except Exception as e:  # noqa: BLE001
            print("  anagrafica non disponibile:", e)
        return 0
    OUT.write_text(json.dumps(out, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    return 0

if __name__ == "__main__":
    sys.exit(main())
