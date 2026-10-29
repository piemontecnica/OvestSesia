#!/usr/bin/env python3
"""Scarica l'ultima lettura degli idrometri ARPA Piemonte di riferimento e la salva
in data/idrometri.json, letto dalla pagina web (stessa origine, nessun blocco CORS).
Eseguito ogni 10 minuti dalla GitHub Action .github/workflows/idrometri.yml."""
import json, math, sys, datetime, urllib.request, urllib.parse, pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "idrometri.json"
URLS = [
    "https://webgis.arpa.piemonte.it/server/rest/services/meteorologia_clima/TR_idrometri/MapServer/4/query",
    "https://webgis.arpa.piemonte.it/ags/rest/services/meteorologia_clima/TR_idrometri/MapServer/4/query",
]
PARAMS = {"where": "1=1", "outFields": "*", "returnGeometry": "true", "outSR": "4326", "f": "json"}
RAGGIO_KM = 8      # stazioni conservate attorno a ciascun idrometro del progetto
CHIAVI = ["SEBASTIANO", "VEROLENGO", "253700", "293700"]

def idrometri_progetto():
    txt = (ROOT / "data" / "layers.js").read_text(encoding="utf-8")
    js = json.loads(txt[txt.index("{"):txt.rindex("}") + 1])
    return [f["geometry"]["coordinates"] for f in js["idrometri"]["features"]]

def km(a, b):
    dx = (a[0] - b[0]) * math.cos(math.radians(b[1])); dy = a[1] - b[1]
    return math.hypot(dx, dy) * 111.2

def scarica():
    errori = []
    for u in URLS:
        url = u + "?" + urllib.parse.urlencode(PARAMS)
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "RTI-Bertini-monitoraggio-cantiere/1.0"})
            with urllib.request.urlopen(req, timeout=40) as r:
                d = json.load(r)
            if d.get("features"):
                return u, d
            errori.append(f"{u}: {d.get('error', 'nessuna feature')}")
        except Exception as e:  # noqa: BLE001
            errori.append(f"{u}: {e}")
    raise RuntimeError(" | ".join(errori))

def main():
    pts = idrometri_progetto()
    try:
        fonte, d = scarica()
    except Exception as e:  # noqa: BLE001
        print(f"::warning::Servizio ARPA non raggiungibile, mantengo la copia precedente. {e}")
        return 0
    tenute = []
    for ft in d["features"]:
        a = ft.get("attributes", {}); g = ft.get("geometry") or {}
        testo = "|".join(str(v) for v in a.values()).upper()
        vicino = g.get("x") is not None and min(km([g["x"], g["y"]], p) for p in pts) <= RAGGIO_KM
        if vicino or any(k in testo for k in CHIAVI):
            tenute.append(ft)
    if not tenute:
        print("::warning::Nessuna stazione ARPA trovata vicino agli idrometri di progetto.")
        return 0
    out = {
        "aggiornato": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
        "fonte": fonte,
        "fields": d.get("fields", []),
        "features": tenute,
    }
    OUT.write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"Salvate {len(tenute)} stazioni da {fonte}")
    for ft in tenute:
        print(" ", ft["attributes"])
    return 0

if __name__ == "__main__":
    sys.exit(main())
