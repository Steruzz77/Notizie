#!/usr/bin/env python3
"""Impagina un'edizione del Corriere dello Steruz.

Uso:  python3 sistema/build.py percorso/edizione.json

Legge il JSON dell'edizione (formato descritto in CLAUDE.md), scrive:
  - archivio/AAAA-MM-GG-<edizione>.html   la copia arretrata
  - archivio/AAAA-MM-GG-<edizione>.json   il contenuto, per i riepiloghi
  - index.html                           sempre l'ultima edizione
  - archivio.html                        l'elenco di tutte le edizioni
"""
import html, json, os, re, sys, datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SYS = os.path.join(ROOT, "sistema")
ARCH = os.path.join(ROOT, "archivio")

GIORNI = ["Lunedì", "Martedì", "Mercoledì", "Giovedì", "Venerdì", "Sabato", "Domenica"]
MESI = ["gennaio", "febbraio", "marzo", "aprile", "maggio", "giugno", "luglio",
        "agosto", "settembre", "ottobre", "novembre", "dicembre"]
EDIZIONI = {"mattina": "Edizione del mattino", "sera": "Edizione della sera",
            "domenica": "Edizione della domenica"}

ICONE = {
    "sole": '<svg class="wx" viewBox="0 0 32 32" aria-hidden="true"><circle cx="16" cy="16" r="6" fill="none" stroke="currentColor" stroke-width="2"/><path d="M16 3v4M16 25v4M3 16h4M25 16h4M7 7l3 3M22 22l3 3M7 25l3-3M22 10l3-3" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg>',
    "parz": '<svg class="wx" viewBox="0 0 32 32" aria-hidden="true"><circle cx="12" cy="12" r="5" fill="none" stroke="currentColor" stroke-width="2"/><path d="M12 3v2M3 12h2M5.5 5.5l1.4 1.4M18.5 5.5l-1.4 1.4" stroke="currentColor" stroke-width="2" stroke-linecap="round"/><path d="M11 26h13a5 5 0 0 0 0-10 7 7 0 0 0-13 2 4 4 0 0 0 0 8z" fill="var(--paper)" stroke="currentColor" stroke-width="2" stroke-linejoin="round"/></svg>',
    "nuvole": '<svg class="wx" viewBox="0 0 32 32" aria-hidden="true"><path d="M8 24h16a6 6 0 0 0 0-12 8 8 0 0 0-15 2.5A5 5 0 0 0 8 24z" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round"/></svg>',
    "pioggia": '<svg class="wx" viewBox="0 0 32 32" aria-hidden="true"><path d="M9 20h14a5 5 0 0 0 0-10 7 7 0 0 0-13 2 4 4 0 0 0-1 8z" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round"/><path d="M11 24l-1.5 4M17 24l-1.5 4M23 24l-1.5 4" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg>',
    "temporale": '<svg class="wx" viewBox="0 0 32 32" aria-hidden="true"><path d="M9 19h14a5 5 0 0 0 0-10 7 7 0 0 0-13 2 4 4 0 0 0-1 8z" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round"/><path d="M17 20l-4 6h4l-2 5" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round" stroke-linecap="round"/></svg>',
    "neve": '<svg class="wx" viewBox="0 0 32 32" aria-hidden="true"><path d="M9 19h14a5 5 0 0 0 0-10 7 7 0 0 0-13 2 4 4 0 0 0-1 8z" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round"/><path d="M11 24v4M9 26h4M21 24v4M19 26h4M16 27v4M14 29h4" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"/></svg>',
    "nebbia": '<svg class="wx" viewBox="0 0 32 32" aria-hidden="true"><path d="M5 12h22M3 17h26M6 22h20M9 27h14" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg>',
}

E = lambda t: html.escape(str(t or ""), quote=True)
TERM = re.compile(r"\[\[([^\]|]+)\|([^\]]+)\]\]")


def testo(t):
    """Testo con [[termine|definizione]] -> parola tratteggiata cliccabile."""
    out, last = [], 0
    for m in TERM.finditer(t or ""):
        out.append(E(t[last:m.start()]))
        breve, _, lungo = m.group(2).partition("||")
        extra = ' data-x="%s"' % E(lungo.strip()) if lungo.strip() else ""
        parola = m.group(1).strip()
        cls = "term"
        if parola.startswith("@"):
            parola, cls = parola[1:], "term nome"
        out.append('<span class="%s" role="button" tabindex="0" data-d="%s"%s>%s</span>'
                   % (cls, E(breve.strip()), extra, E(parola)))
        last = m.end()
    out.append(E((t or "")[last:]))
    return "".join(out)


# --- Impaginazione -------------------------------------------------------------------------------
# Ogni sezione ha il suo colore (linguetta, occhielli, filetti): classi definite in stile.css.
COLORI = {"Lumezzane e Brescia": "loc", "Italia": "ita", "Dal mondo": "mon", "Tecnologia": "tec",
          "Musica": "mus", "Meteo": "met"}
MAPPA = json.load(open(os.path.join(SYS, "mappa.json"), encoding="utf-8"))
AVVISI_ICONE = {
    "vento": '<svg class="wx" viewBox="0 0 32 32" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true"><path d="M4 12h15a4 4 0 1 0-4-4"/><path d="M4 18h21a4 4 0 1 1-4 4"/><path d="M4 24h9"/></svg>',
    "mare": '<svg class="wx" viewBox="0 0 32 32" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true"><path d="M3 14c3 0 3-3 6-3s3 3 6 3 3-3 6-3 3 3 6 3"/><path d="M3 21c3 0 3-3 6-3s3 3 6 3 3-3 6-3 3 3 6 3"/></svg>',
    "allerta": '<svg class="wx" viewBox="0 0 32 32" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round" stroke-linecap="round" aria-hidden="true"><path d="M16 4L29 27H3z"/><path d="M16 12v7M16 23v.5"/></svg>',
    "caldo": '<svg class="wx" viewBox="0 0 32 32" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true"><path d="M13 19V6a3 3 0 0 1 6 0v13a5 5 0 1 1-6 0z"/><path d="M16 12v9"/></svg>',
    "gelo": '<svg class="wx" viewBox="0 0 32 32" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true"><path d="M16 3v26M4.7 9.5l22.6 13M4.7 22.5l22.6-13M12 5l4 4 4-4M12 27l4-4 4 4"/></svg>',
}
SVG_SHARE = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M12 3v12M8 7l4-4 4 4"/><path d="M6 11H5v10h14V11h-1"/></svg>'
SVG_PLUS = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true"><rect x="3.5" y="3.5" width="17" height="17" rx="4"/><path d="M12 8v8M8 12h8"/></svg>'
SVG_DOTS = '<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><circle cx="12" cy="5" r="2"/><circle cx="12" cy="12" r="2"/><circle cx="12" cy="19" r="2"/></svg>'
SVG_SUN = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true"><circle cx="12" cy="12" r="4.5"/><path d="M12 2v2.5M12 19.5V22M2 12h2.5M19.5 12H22M4.9 4.9l1.8 1.8M17.3 17.3l1.8 1.8M4.9 19.1l1.8-1.8M17.3 6.7l1.8-1.8"/></svg>'
SVG_MOON = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round" aria-hidden="true"><path d="M20 14.5A8 8 0 0 1 9.5 4a8 8 0 1 0 10.5 10.5z"/></svg>'
SVG_GEAR = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 1 1-2.83 2.83l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 1 1-4 0v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 1 1-2.83-2.83l.06-.06A1.65 1.65 0 0 0 4.68 15a1.65 1.65 0 0 0-1.51-1H3a2 2 0 1 1 0-4h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 1 1 2.83-2.83l.06.06A1.65 1.65 0 0 0 9 4.68a1.65 1.65 0 0 0 1-1.51V3a2 2 0 1 1 4 0v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 1 1 2.83 2.83l-.06.06A1.65 1.65 0 0 0 19.4 9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 1 1 0 4h-.09a1.65 1.65 0 0 0-1.51 1z"/></svg>'
TIPO_BREVE = {"mattina": "Mattina", "sera": "Sera", "domenica": "Mattina della domenica"}


def data_lunga(iso):
    d = datetime.date.fromisoformat(iso)
    return "%s %d %s %d" % (GIORNI[d.weekday()], d.day, MESI[d.month - 1], d.year)


def giorno_breve(iso):
    d = datetime.date.fromisoformat(iso)
    return "%s %d %s" % (GIORNI[d.weekday()], d.day, MESI[d.month - 1])


def paragrafi(n, prima_lettera=False):
    ps = n.get("testo") or []
    if isinstance(ps, str):
        ps = [ps]
    return "".join('<p%s>%s</p>' % (' class="drop"' if prima_lettera and i == 0 else "", testo(p)) for i, p in enumerate(ps))


def foto(n, cls="ph"):
    f = n.get("foto") or {}
    url = f.get("url") if isinstance(f, dict) else f
    if not url or not str(url).startswith("https://"):
        return ""
    alt = (f.get("didascalia") if isinstance(f, dict) else "") or n.get("titolo")
    # se la foto non si carica sparisce, e la notizia in testa alla pagina torna a tutta larghezza
    return ('<img class="%s" src="%s" alt="%s" loading="lazy" referrerpolicy="no-referrer" '
            'onerror="var c=this.closest(\'.lead\');if(c)c.classList.remove(\'wf\');(this.closest(\'.lp\')||this).remove()">'
            % (cls, E(url), E(alt)))


def fonte(n):
    f = n.get("fonte") or {}
    if isinstance(f, list):
        parts = ['<a href="%s" target="_blank" rel="noopener">%s</a>' % (E(x.get("url")), E(x.get("nome"))) if x.get("url")
                 else E(x.get("nome")) for x in f]
        return '<p class="src">Fonti: %s</p>' % " · ".join(parts) if parts else ""
    if not f.get("nome") and not f.get("url"):
        return ""
    if not f.get("url"):
        return '<p class="src">Fonte: %s</p>' % E(f.get("nome"))
    return '<p class="src"><a href="%s" target="_blank" rel="noopener">Fonte: %s</a></p>' % (E(f["url"]), E(f.get("nome")))


def scheda(n, cls=""):
    return '<article class="card %s">%s<div class="kick">%s</div><h3>%s</h3>%s%s</article>' % (
        cls, foto(n), E(n.get("occhiello")), E(n.get("titolo")), paragrafi(n), fonte(n))


def tinta(occhiello):
    """Colore dell'occhiello in prima pagina: quello della sezione da cui viene la notizia."""
    o = (occhiello or "").lower()
    for chiave, c in (("mondo", "mon"), ("tecnologia", "tec"), ("musica", "mus"), ("meteo", "met"),
                      ("lumezzane", "loc"), ("valtrompia", "loc"), ("brescia", "loc"), ("italia", "ita")):
        if o.startswith(chiave):
            return c
    return "ita"


def pghead(nome):
    return '<header class="pghead"><h2>%s</h2><span>Corriere dello Steruz</span></header>' % E(nome)


def riga_meteo(r):
    return '<li><span class="ic">%s</span><span class="lu">%s<small>%s</small></span><b>%s</b></li>' % (
        ICONE.get(r.get("icona"), ICONE["nuvole"]), E(r.get("luogo")), E(r.get("cond")), E(r.get("temp")))


def lumezzane_domani(m):
    for k in ("domani", "oggi"):
        for r in m.get(k) or []:
            if (r.get("luogo") or "").startswith("Lumezzane") and r.get("temp"):
                return "Lumezzane %s %s" % (k, r["temp"])
    return "Oggi e domani"


def prima(ed, pagine_dopo, numero, archivio):
    pr = ed["prima"]
    a = pr["apertura"]
    spalle = pr.get("spalle") or ([pr["spalla"]] if pr.get("spalla") else [])
    tz = ""
    for i, (nome, s) in enumerate(pagine_dopo):
        if nome == "Meteo":
            tz += ('<button type="button" class="tz met" data-go="%d"><b>%d</b><span><i>Meteo</i>%s</span><em>%s</em></button>'
                   % (i + 1, i + 2, E((s.get("situazione") or {}).get("titolo") or "Le previsioni"), E(lumezzane_domani(s))))
        else:
            tz += ('<button type="button" class="tz %s" data-go="%d"><b>%d</b><span><i>%s</i>%s</span><em>%d notizie</em></button>'
                   % (COLORI.get(nome, "pri"), i + 1, i + 2, E(nome), E(s["notizie"][0].get("titolo")), len(s["notizie"])))
    mini = []
    if pr.get("parola"):
        mini.append('<aside class="card mini"><h5>La parola del giorno</h5><p class="t">%s</p><p>%s</p></aside>'
                    % (E(pr["parola"].get("termine")), testo(pr["parola"].get("testo"))))
    if pr.get("accadde"):
        mini.append('<aside class="card mini"><h5>Accadde oggi</h5><p class="t">%s</p><p>%s</p></aside>'
                    % (E(pr["accadde"].get("data")), testo(pr["accadde"].get("testo"))))
    box = ('<div class="car boxes"><div class="track">%s</div><div class="dots" aria-hidden="true"></div></div>' % "".join(mini)) if mini else ""
    arch = ('<a class="old" href="../index.html">Edizione passata · vai all\'ultima →</a>' if archivio
            else '<span class="ult">● Ultima edizione</span>')
    out = ('<header class="mast"><h1>Il Corriere dello Steruz</h1>'
           '<div class="line"><span>%s · %s</span>%s</div></header><div class="prima">'
           % ((data_lunga(ed["data"]).rsplit(" ", 1)[0] if not archivio else data_lunga(ed["data"])), {"mattina":"Mattina","sera":"Sera","domenica":"Domenica"}.get(ed.get("edizione"),"Speciale"), arch))
    out += '<article class="card hero %s">%s<div class="kick">%s</div><h2>%s</h2>%s%s%s</article>' % (
        tinta(a.get("occhiello")), foto(a, "ph big"), E(a.get("occhiello")), E(a.get("titolo")),
        ('<p class="deck">%s</p>' % testo(a["sommario"])) if a.get("sommario") else "", paragrafi(a, True), fonte(a))
    for sp in spalle:
        out += '<article class="card spalla %s">%s<div class="kick">%s</div><h3>%s</h3>%s%s</article>' % (
            tinta(sp.get("occhiello")), foto(sp), E(sp.get("occhiello")), E(sp.get("titolo")), paragrafi(sp), fonte(sp))
    out += box
    if tz:
        out += '<section class="inside"><h4>Nelle altre pagine</h4><div class="tzs">%s</div></section>' % tz
    return out + '</div>'


def cov_attr(x, tipo):
    """Copertina: quella scritta nel JSON, altrimenti ricerca dal vivo; foto_riserva se la ricerca non trova niente."""
    a = ""
    if x.get("copertina"):
        a += ' data-img="%s"' % E(x["copertina"])
    elif x.get("cerca") is not False:
        a += ' data-q="%s" data-e="%s"' % (E(x.get("cerca") or (x["artista"] + " " + x["titolo"])), tipo)
    if x.get("foto_riserva"):
        a += ' data-alt="%s"' % E(x["foto_riserva"])
    return a


def sezione(s):
    ns = s["notizie"]
    l = ns[0]
    if foto(l):
        lead = '<article class="card lead wf"><div class="lp">%s</div><div class="lt"><div class="kick">%s</div><h3>%s</h3>%s%s</div></article>' % (
            foto(l), E(l.get("occhiello")), E(l.get("titolo")), paragrafi(l), fonte(l))
    else:
        lead = scheda(l, "lead")
    intro = '<p class="intro">%s</p>' % testo(s["intro"]) if s.get("intro") else ""
    extra = ""
    if s.get("uscite"):
        extra += ('<section class="card box-mus"><div class="kick">Musica · Uscite</div><p class="sotto">%s</p><ul class="usc">%s</ul></section>' % (E(s.get("uscite_titolo") or "Le uscite della settimana"),
                  "".join('<li><span class="cov"%s>%s</span><i>%s</i><b>%s</b><span>%s</span></li>' % (cov_attr(u, "album" if u["tipo"].lower().startswith(("album", "ep")) else "song"), E(u["artista"][:1]), E(u["tipo"]), E(u["artista"]), E(u["titolo"])) for u in s["uscite"])))
    for k in ("classifica", "classifica_singoli"):
        if s.get(k):
            c = s[k]
            extra += ('<section class="card box-mus"><div class="kick">Musica · %s FIMI</div><p class="sotto">%s</p><ol class="clas">%s</ol><p class="src">%s</p></section>' % ("Album" if k == "classifica" else "Singoli", E(c["titolo"]),
                      "".join('<li><span class="cov"%s>%s</span><b>%s</b><span>%s</span><em>%s</em></li>' % (cov_attr(r, "album" if k == "classifica" else "song"), E(r["artista"][:1]), E(r["titolo"]), E(r["artista"]), E(r.get("nota",""))) for r in c["righe"]), E(c.get("fonte",""))))
    if extra:
        extra = '<div class="car muscar"><div class="track">%s</div><div class="dots" aria-hidden="true"></div></div>' % extra
    return pghead(s["nome"]) + intro + '<div class="grid">%s<div class="rest">%s</div></div>' % (lead, "".join(scheda(n) for n in ns[1:])) + extra + segnalate(s)


def segnalate(s):
    """Notizie viste solo su siti che non si possono leggere in automatico: solo titolo e link, senza testo."""
    lista = s.get("segnalate") or []
    if not lista:
        return ""
    li = "".join('<li><a href="%s" target="_blank" rel="noopener"><b>%s</b><small>%s%s</small></a></li>' % (
        E(x.get("url")), E(x.get("titolo")), E(x.get("testata")), (" · " + E(x["data"])) if x.get("data") else "") for x in lista)
    return ('<section class="card segn"><div class="kick">Segnalate da altre testate</div>'
            '<p class="segn-n">Notizie che non ho potuto leggere per intero: tocca il titolo per aprirle sul loro sito.</p>'
            '<ul>%s</ul></section>' % li)


def meteo(m, archivio):
    si = m.get("situazione") or {}
    out = pghead("Meteo") + '<div class="grid wx wxm">'
    out += '<article class="card lead"><div class="kick">La situazione</div><h3>%s</h3>%s</article>' % (E(si.get("titolo")), paragrafi(si))
    giorni = [k for k in ("oggi", "domani") if m.get(k)]
    if archivio:
        # le copie d'archivio mostrano le previsioni scritte quel giorno, non quelle di oggi
        out += '<div class="car wxcar"><div class="track">'
        for k in giorni:
            out += '<article class="card"><div class="kick">%s</div><ul class="wxl">%s</ul></article>' % (
                E(m.get(k + "_etichetta") or k.capitalize()), "".join(riga_meteo(r) for r in m[k]))
        out += '</div><div class="dots" aria-hidden="true"></div></div>'
        av = "".join(avvisi(m, k) for k in giorni)
        out += '</div>' + ('<section class="wxav">%s</section>' % av if av else "")
        if m.get("nota"):
            out += '<p class="note">%s</p>' % testo(m["nota"])
        if m.get("fonti"):
            out += fonte({"fonte": m["fonti"]})
        return out
    # edizione di oggi: mappa con le previsioni dal vivo (Open-Meteo); le righe dell'edizione restano di riserva
    W, H = MAPPA["W"], MAPPA["H"]
    blocchi = ""
    for i, k in enumerate(("oggi", "domani")):
        blocchi += ('<div class="gday" data-g="%s"%s>%s<div class="kick casa">Le tue città</div><ul class="wxl casa-l"></ul><ul class="wxl riserva">%s</ul></div>'
                    % (k, "" if i == 0 else " hidden", avvisi(m, k, titolo=False), "".join(riga_meteo(r) for r in m.get(k) or [])))
    caps = "".join('<g class="cap%s" data-i="%d" transform="translate(%s %s)"><circle r="2.2"/></g>'
                   % (" lum" if c["n"] == "Lumezzane" else "", n, c["x"], c["y"]) for n, c in enumerate(MAPPA["cap"]) if c["n"] != "Brescia")
    svg = ('<svg class="itmap" viewBox="0 0 %s %s"><defs><clipPath id="itc"><path d="%s"/></clipPath></defs>'
           '<path class="land" d="%s"/><g clip-path="url(#itc)"><path class="conf" d="M0 %s L%s %s"/><path class="conf" d="M0 %s L%s %s"/></g>%s</svg>'
           % (W, H, MAPPA["d"], MAPPA["d"], MAPPA["yN"] + 6, W, MAPPA["yN"] - 6, MAPPA["yS"] + 16, W, MAPPA["yS"] - 14, caps))
    zone = "".join('<div class="zch" data-z="%s"><i>%s</i><span class="zi"></span><b>—</b></div>' % (z, n) for z, n in (("n", "Nord"), ("c", "Centro"), ("s", "Sud")))
    dati = json.dumps({"cap": [{"n": c["n"], "lat": c["lat"], "lon": c["lon"], "z": c["z"]} for c in MAPPA["cap"]], "ico": ICONE},
                      ensure_ascii=False).replace("</", "<\\/")
    out += ('<section class="card wxmap" data-attesa="1"><div class="casa2"><div class="kick casa">Lumezzane</div><div class="c2row"></div></div><div class="seg wxtab"><button type="button" aria-pressed="true" data-g="oggi">%s</button>'
            '<button type="button" aria-pressed="false" data-g="domani">%s</button></div>'
            % (E(m.get("oggi_etichetta") or "Oggi"), E(m.get("domani_etichetta") or "Domani")))
    out += ('<div class="mapbox">%s<div class="ctip" hidden></div></div><div class="zrow">%s</div>'
            '<p class="mapnota">Tocca un\'icona per vedere la città. Minime e massime sono la media dei capoluoghi di regione di ogni zona.</p>%s'
            '<p class="omsrc">Previsioni dal vivo: <a href="https://open-meteo.com/" target="_blank" rel="noopener">Open-Meteo</a></p>'
            '<script type="application/json" id="wxdati">%s</script></section></div>' % (svg, zone, blocchi, dati))
    if m.get("nota"):
        out += '<p class="note">%s</p>' % testo(m["nota"])
    return out


def avvisi(m, k, titolo=True):
    """Avvisi meteo (nebbia, vento, mare mosso, allerta...): compaiono solo se ci sono."""
    lista = (m.get("avvisi") or {}).get(k) or []
    if not lista:
        return ""
    li = "".join('<li><span class="ic">%s</span>%s</li>' % (AVVISI_ICONE.get(a.get("icona")) or ICONE.get(a.get("icona"), AVVISI_ICONE["allerta"]),
                                                           testo(a.get("testo"))) for a in lista)
    tit = '<div class="kick">Avvisi · %s</div>' % E(m.get(k + "_etichetta") or k) if titolo else ""
    return tit + '<ul class="avv">%s</ul>' % li


def edizioni_salvate():
    return sorted((f[:-5] for f in os.listdir(ARCH) if f.endswith(".json")), reverse=True)


def menu(ed, pagine, nome_ed, archivio):
    pre = "" if archivio else "archivio/"
    li = "".join('<li><button type="button" class="%s" data-go="%d"><span class="t">%s</span><span class="dl"></span><b>%d</b></button></li>'
                 % (COLORI.get(n, "pri"), i, E(n), i + 1) for i, n in enumerate(pagine))
    arc, giorno = [], None
    for v in edizioni_salvate()[:7]:
        if v[:10] != giorno:
            arc.append('<li class="day">%s</li>' % giorno_breve(v[:10]))
            giorno = v[:10]
        tipo = TIPO_BREVE.get(v[11:], v[11:])
        if v == nome_ed:
            arc.append('<li><a class="on" aria-current="page"><b>%s</b><small>Stai leggendo</small></a></li>' % E(tipo))
        else:
            arc.append('<li><a href="%s%s.html"><b>%s</b><small>Apri ›</small></a></li>' % (pre, E(v), E(tipo)))
    return ('<div class="menu" id="menu" hidden><div class="box" role="dialog" aria-label="Sommario e impostazioni">'
            '<button class="x" id="mx" type="button" aria-label="Chiudi">×</button><div class="views" id="views">'
            '<section class="view" id="vSom"><div class="mh"><span class="g">Sommario</span><small>%s · %s</small></div><ol class="idx">%s</ol>'
            '<div class="mfoot"><button type="button" class="mbtn" id="toSet">%s Impostazioni</button><button type="button" class="mbtn" id="toArc">≡ Archivio</button></div></section>'
            '<section class="view" id="vSet" inert><div class="mh"><span class="g">Impostazioni</span><small>Come vuoi leggere il giornale</small></div>'
            '<div class="row"><span class="lab">Tema</span><div class="seg" id="segTema"><button type="button" data-v="auto">Automatico</button><button type="button" data-v="light">%sChiaro</button><button type="button" data-v="dark">%sScuro</button></div></div>'
            '<div class="row"><span class="lab">Grandezza del testo</span><div class="seg sz" id="segTesto"><button type="button" data-v="-1" style="font-size:13px" aria-label="Piccolo">A</button><button type="button" data-v="0" style="font-size:16px" aria-label="Normale">A</button><button type="button" data-v="1" style="font-size:19px" aria-label="Grande">A</button><button type="button" data-v="2" style="font-size:22px" aria-label="Molto grande">A</button></div>'
            '<div class="sample"><div class="kick">Così si legge</div><h3>Titoli e testo crescono insieme</h3><p>Vale per tutto il giornale.</p></div></div>'
            '<div class="row"><span class="lab">Notizie</span><div class="seg" id="segSchede"><button type="button" data-v="stampa">Stampate sul foglio</button><button type="button" data-v="schede">In schede</button></div></div>'
            '<div class="row"><span class="lab">Effetto carta</span><div class="cartar"><small>Liscia</small><input type="range" id="cartaR" min="0" max="100" step="5" value="50" aria-label="Effetto carta"><small>Stropicciata</small></div></div>'
            '<button type="button" class="lnk" id="homebtn"><img src="RADICE/icona.png" alt="" width="36" height="36"><span><b>Aggiungi alla schermata Home</b><small>Istruzioni per iPhone e Android</small></span></button>'
            '<div class="mfoot"><button type="button" class="back" data-som>← Torna al sommario</button></div></section>'
            '<section class="view" id="vArc" inert><div class="mh"><span class="g">Archivio</span><small>Le ultime edizioni</small></div><ol class="arcl">%s</ol>'
            '<div class="mfoot"><button type="button" class="back" data-som>← Torna al sommario</button><a class="back tutte" href="RADICE/archivio.html">Tutte le edizioni →</a></div></section>'
            '</div></div></div>' % (E(EDIZIONI.get(ed.get("edizione"), "Edizione")), E(giorno_breve(ed["data"]).lower()), li, SVG_GEAR, SVG_SUN, SVG_MOON, "".join(arc)))


GUIDA = '''<div class="guide" id="guide" hidden><div class="box" role="dialog" aria-label="Aggiungi alla schermata Home">
<button class="x" id="gx" type="button" aria-label="Chiudi">×</button>
<div class="gh"><img src="RADICE/icona.png" alt="" width="60" height="60"><div><b>Il Corriere sulla schermata Home</b><small>Lo apri con un tocco e si vede a tutto schermo, come un'app.</small></div></div>
<div class="seg" id="segOs"><button type="button" data-v="ios">iPhone e iPad</button><button type="button" data-v="and">Android</button></div>
<ol class="steps" data-os="ios">
<li><div>Apri il giornale con <b>Safari</b>.</div></li>
<li><div>Tocca <span class="k">%s Condividi</span> nella barra di Safari. Se non lo vedi, tocca prima <span class="k">···</span> in basso a destra.</div></li>
<li><div>Scorri l'elenco e tocca <span class="k">%s Aggiungi alla schermata Home</span>.</div></li>
<li><div>Tocca <b>Aggiungi</b> in alto a destra. L'icona del Corriere compare tra le tue app.</div></li></ol>
<ol class="steps" data-os="and" hidden>
<li><div>Apri il giornale con <b>Chrome</b>.</div></li>
<li><div>Tocca <span class="k">%s</span> in alto a destra.</div></li>
<li><div>Tocca <span class="k">%s Aggiungi a schermata Home</span>. Su alcuni telefoni la voce si chiama <b>Installa app</b>.</div></li>
<li><div>Conferma con <b>Aggiungi</b> (o <b>Installa</b>). L'icona del Corriere compare nella schermata Home.</div></li></ol>
<button type="button" class="inst" id="inst" hidden>Aggiungi ora alla schermata Home</button>
<p class="gok" id="gok" hidden>✓ Stai già leggendo il giornale dall'icona sulla schermata Home.</p>
</div></div>''' % (SVG_SHARE, SVG_PLUS, SVG_DOTS, SVG_PLUS)


PROSSIMA = {"mattina": "Prossima edizione: stasera, verso le 18:30", "domenica": "Prossima edizione: stasera, verso le 18:30",
            "sera": "Prossima edizione: domattina, verso le 8:30"}


def gerenza(ed, nome_ed, numero, archivio):
    """Chiusura dell'ultima pagina, come il riquadro in fondo ai quotidiani."""
    pre = "" if archivio else "archivio/"
    prec = [v for v in edizioni_salvate() if v < nome_ed]
    sx = ('<a class="gz-b" href="%s%s.html"><i>← Edizione precedente</i><b>%s · %s</b></a>' % (
        pre, E(prec[0]), E(giorno_breve(prec[0][:10])), E(TIPO_BREVE.get(prec[0][11:], prec[0][11:]).lower()))) if prec else ""
    dx = '' if archivio else '<div class="gz-b"><i>Prossima edizione</i><b>%s</b></div>' % E(PROSSIMA.get(ed.get("edizione"), "").replace("Prossima edizione: ", "").capitalize())
    etichetta = EDIZIONI.get(ed.get("edizione"), "Edizione speciale")
    return ('<footer class="gerenza"><div class="kick">Fine dell\'edizione</div><div class="gz-row">%s%s</div>'
            '<div class="gz-link"><a href="%sarchivio.html">Tutte le edizioni nell\'Archivio →</a><button type="button" data-go="0">↑ Prima pagina</button></div>'
            '</footer>' % (sx, dx, "../" if archivio else ""))


def impagina(ed, numero, archivio=False):
    """archivio=True: la copia in archivio/ (link che risalgono di una cartella, meteo dell'epoca)."""
    nome_ed = "%s-%s" % (ed["data"], ed["edizione"])
    sezioni = [s for s in ed.get("sezioni", []) if s.get("notizie")]
    pagine_dopo = [(s["nome"], s) for s in sezioni] + ([("Meteo", ed["meteo"])] if ed.get("meteo") else [])
    pagine = ["Prima pagina"] + [n for n, _ in pagine_dopo]
    N = len(pagine)
    corpi = [prima(ed, pagine_dopo, numero, archivio)] + [sezione(s) for s in sezioni] + ([meteo(ed["meteo"], archivio)] if ed.get("meteo") else [])
    etichetta = EDIZIONI.get(ed.get("edizione"), "Edizione speciale")
    piede = "Il Corriere dello Steruz · Anno I · N. %d · %s · %s · Lumezzane (BS)" % (numero, data_lunga(ed["data"]), etichetta.replace("Edizione", "edizione"))
    fogli = "".join('<section class="page %s" data-name="%s"%s><div class="in">%s%s<footer class="folio"><span class="fm">%s</span></footer></div></section>'
                    % (COLORI.get(n, "pri"), E(n), "" if i == 0 else " hidden", c, gerenza(ed, nome_ed, numero, archivio) if i == N - 1 else "", E(piede))
                    for i, (n, c) in enumerate(zip(pagine, corpi)))
    edl = "%s di %s" % (TIPO_BREVE.get(ed.get("edizione"), "").lower() or "edizione", giorno_breve(ed["data"]).lower())
    head = open(os.path.join(SYS, "head.html"), encoding="utf-8").read()
    css = open(os.path.join(SYS, "stile.css"), encoding="utf-8").read()
    js = open(os.path.join(SYS, "giornale.js"), encoding="utf-8").read()
    pagina = ('<!doctype html>\n<html lang="it">\n<head>%s<style>%s</style>\n'
              '<script>try{var t=localStorage.getItem("corriere-tema");if(t)document.documentElement.setAttribute("data-theme",t);var z=localStorage.getItem("corriere-testo");if(z)document.documentElement.setAttribute("data-testo",z)}catch(e){}</script>\n'
              '</head>\n<body>\n<main class="book" id="book" data-ed="%s" data-edl="%s"%s>%s<div class="ush" id="ush" hidden></div><div class="flapw" id="flapw" hidden><div class="flap" id="flap"></div></div></main>\n'
              '<nav class="bar" aria-label="Sfoglia"><button type="button" class="nav" id="prev" aria-label="Pagina precedente">←</button><button type="button" class="where" id="where" aria-expanded="false" aria-haspopup="dialog"><span class="name" id="pname">Prima pagina</span><span class="num" id="pnum">Pagina 1 di %d</span></button><button type="button" class="nav" id="next" aria-label="Pagina successiva">→</button></nav>\n'
              '%s%s\n<div class="toast" id="toast" hidden><span id="toastt"></span><button type="button" id="toastb" hidden></button></div>\n'
              '<div class="pop" id="pop" hidden><div class="box" role="dialog" aria-live="polite"><button class="x" id="px" type="button" aria-label="Chiudi">×</button><p class="k" id="pk" hidden>Chi è</p><p class="w" id="pw"></p><p class="d" id="pd"></p><button type="button" class="more" id="pmore" hidden>Approfondisci ▾</button><p class="d long" id="pl" hidden></p></div></div>\n'
              '<script>%s</script>\n</body>\n</html>\n'
              % (head, css, E(nome_ed), E(edl), ' data-arch="1"' if archivio else "", fogli, N, menu(ed, pagine, nome_ed, archivio), GUIDA, js))
    radice = ".." if archivio else "."
    pagina = pagina.replace("RADICE/", radice + "/")
    if archivio:
        # carta, icona e manifest stanno nella cartella principale
        pagina = (pagina.replace("url(carta-", "url(../carta-").replace('href="icona.png"', 'href="../icona.png"')
                  .replace('href="manifest.webmanifest"', 'href="../manifest.webmanifest"'))
    return GOTICO.sub(lambda m: m.group(0).replace("C", '<span class="gc">C</span>', 1).replace("Steruz", '<span class="gc">S</span>teruz').replace(">Il ", '><span class="gc">I</span>l '), pagina)


# Nella testata gotica S, C e I vengono da un altro carattere (Manufacturing Consent), più leggibile
GOTICO = re.compile(r">(Il )?Corriere dello Steruz<")


def archivio_html():
    righe, giorno_prec = [], None
    for v in edizioni_salvate():
        data, tipo = v[:10], v[11:]
        try:
            ed = json.load(open(os.path.join(ARCH, v + ".json"), encoding="utf-8"))
            titolo = ed["prima"]["apertura"]["titolo"]
        except Exception:
            titolo = ""
        if data != giorno_prec:
            righe.append('<h2>%s</h2>' % data_lunga(data))
            giorno_prec = data
        righe.append('<a class="ed" href="archivio/%s.html"><b>%s</b><span>%s</span></a>'
                     % (E(v), E(EDIZIONI.get(tipo, tipo)), E(titolo)))
    head = open(os.path.join(SYS, "head.html"), encoding="utf-8").read().replace(
        "<title>Il Corriere dello Steruz</title>", "<title>Archivio · Il Corriere dello Steruz</title>")
    return """<!doctype html>
<html lang="it">
<head>%s<style>
:root{--ink:#1c1a16;--muted:#5a5446;--rule:#1c1a16;--red:#8e1f17;--desk:#cfc6b2;--cm:200 193 180;--card:#f6f1e5;--carta:url(carta-chiara.jpg);--shadow:rgba(40,30,10,.3);color-scheme:light}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){--ink:#ece4d3;--muted:#aaa08c;--rule:#d9cfbc;--red:#e27a68;--desk:#141210;--cm:33 29 24;--card:#2a261f;--carta:url(carta-scura.jpg);--shadow:rgba(0,0,0,.55);color-scheme:dark}}
:root[data-theme="dark"]{--ink:#ece4d3;--muted:#aaa08c;--rule:#d9cfbc;--red:#e27a68;--desk:#141210;--cm:33 29 24;--card:#2a261f;--carta:url(carta-scura.jpg);--shadow:rgba(0,0,0,.55);color-scheme:dark}
*{box-sizing:border-box}
html,body{background:var(--desk)}
body{margin:0;color:var(--ink);font-family:"Source Serif 4",Georgia,serif}
.sheet{max-width:700px;margin:12px auto;border-radius:3px;box-shadow:0 2px 10px var(--shadow);
  background-color:rgb(var(--cm));background-image:linear-gradient(rgb(var(--cm) / .5),rgb(var(--cm) / .5)),var(--carta);background-size:auto,700px 900px;
  padding:18px max(16px,env(safe-area-inset-right,0px)) 28px max(16px,env(safe-area-inset-left,0px))}
h1{font-family:"UnifrakturMaguntia",Georgia,serif;font-weight:400;font-size:clamp(34px,10vw,60px);text-align:center;margin:0 0 4px}
.sub{text-align:center;font-family:"Libre Franklin",Arial,sans-serif;font-size:12px;letter-spacing:.12em;text-transform:uppercase;border-top:1px solid var(--rule);border-bottom:4px double var(--rule);padding:6px 0;margin-bottom:8px}
.sub a{color:var(--red);text-decoration:none;font-weight:700}
h2{font-family:"Playfair Display",Georgia,serif;font-weight:900;font-size:20px;margin:18px 0 6px;border-bottom:1px solid var(--rule);padding-bottom:4px}
.ed{display:flex;flex-direction:column;gap:2px;padding:10px 0;border-bottom:1px dotted var(--muted);color:var(--ink);text-decoration:none}
.ed b{font-family:"Libre Franklin",Arial,sans-serif;font-size:11px;letter-spacing:.1em;text-transform:uppercase;color:var(--red)}
.ed span{font-family:"Playfair Display",Georgia,serif;font-weight:700;font-size:17px;line-height:1.25}
</style>
<script>try{var t=localStorage.getItem("corriere-tema");if(t)document.documentElement.setAttribute("data-theme",t)}catch(e){}</script>
</head>
<body><div class="sheet">
<h1>Il Corriere dello Steruz</h1>
<div class="sub">Archivio delle edizioni · <a href="index.html">Ultima edizione →</a></div>
%s
</div></body></html>
""" % (head, "\n".join(righe) or "<p>Nessuna edizione ancora.</p>")


# Controllo finale: segnala cosa non rispetta le regole di CLAUDE.md, senza bloccare l'impaginazione.
NOTIZIE_ATTESE = {"Riepilogo della settimana": 6, "Lumezzane e Brescia": 6, "Italia": 7, "Dal mondo": 6,
                  "Tecnologia": 4, "Musica": 4}
FONTI_OK = """music.apple.com open.spotify.com youtube.com
ansa.it ilpost.it rainews.it tg24.sky.it agi.it adnkronos.com italpress.com askanews.it
corriere.it repubblica.it lastampa.it ilsole24ore.com ilgiornale.it ilmessaggero.it avvenire.it
ilfattoquotidiano.it open.online ilfoglio.it today.it tgcom24.mediaset.it ilgiorno.it quotidiano.net fanpage.it
internazionale.it reuters.com apnews.com bbc.com bbc.co.uk aljazeera.com theguardian.com nytimes.com
giornaledibrescia.it bresciatoday.it bresciaoggi.it quibrescia.it bsnews.it valtrompia.it
hwupgrade.it wired.it dday.it tomshw.it multiplayer.it everyeye.it hdblog.it punto-informatico.it theverge.com
rockol.it rollingstone.it allmusicitalia.it rapologia.it esse-magazine.it billboard.it fimi.it newsic.it
3bmeteo.com ilmeteo.it meteo.it""".split()
VALTROMPIA = ("lumezzane", "valtrompia", "val trompia", "gardone", "sarezzo", "villa carcina", "concesio",
              "marcheno", "tavernole", "pezzaze", "bovegno", "collio", "irma", "polaveno", "lodrino", "caino")


def dominio(url):
    m = re.match(r"https?://([^/]+)", url or "")
    return m.group(1).lower() if m else ""


def fonte_ok(url):
    d = dominio(url)
    return any(d == f or d.endswith("." + f) for f in FONTI_OK)


def controlla(ed):
    avvisi = []
    pr = ed["prima"]
    tutte = [("Prima pagina", pr["apertura"], True)] + [("Prima pagina", n, True) for n in
             (pr.get("spalle") or ([pr["spalla"]] if pr.get("spalla") else []))]
    for s in ed.get("sezioni", []):
        tutte += [(s["nome"], n, False) for n in s.get("notizie") or []]
        attese = NOTIZIE_ATTESE.get(s["nome"])
        if attese and len(s.get("notizie") or []) < attese:
            avvisi.append("%s: %d notizie, ne servono %d (mettine meno solo se davvero non ce ne sono)"
                          % (s["nome"], len(s.get("notizie") or []), attese))
    approfondimenti = 0
    for sez, n, in_prima in tutte:
        t = " ".join(n.get("testo") if isinstance(n.get("testo"), list) else [n.get("testo") or ""]) + " " + (n.get("sommario") or "")
        termini = TERM.findall(t)
        approfondimenti += sum("||" in d for _, d in termini)
        nome = "%s · «%s»" % (sez, (n.get("titolo") or "")[:50])
        if not termini:
            avvisi.append("%s: nessuna parola spiegata (ci sono termini di settore, sigle o nomi poco noti?)" % nome)
        if in_prima and not any("||" in d for _, d in termini):
            avvisi.append("%s: in prima pagina serve almeno un Approfondisci" % nome)
        fonti = n.get("fonte") if isinstance(n.get("fonte"), list) else [n.get("fonte") or {}]
        for f in fonti:
            if f.get("url") and not fonte_ok(f["url"]):
                avvisi.append("%s: fonte fuori elenco (%s), verifica che sia affidabile e che la notizia sia confermata altrove"
                              % (nome, dominio(f["url"])))
    if approfondimenti < len(tutte) // 3:
        avvisi.append("Tutta l'edizione: solo %d Approfondisci su %d notizie, aggiungili sui termini più complessi"
                      % (approfondimenti, len(tutte)))
    loc = [s for s in ed.get("sezioni", []) if s["nome"] == "Lumezzane e Brescia"]
    if loc:
        testi = [json.dumps(n, ensure_ascii=False).lower() for n in loc[0].get("notizie") or []]
        if not any(v in t for t in testi for v in VALTROMPIA):
            avvisi.append("Lumezzane e Brescia: nessuna notizia su Lumezzane o la Valtrompia")
    mus = [s for s in ed.get("sezioni", []) if s["nome"] == "Musica"]
    if mus:
        m = mus[0]
        for k, cosa in (("uscite", "le uscite"), ("classifica", "la classifica FIMI degli album"), ("classifica_singoli", "la classifica FIMI dei singoli")):
            if not m.get(k):
                avvisi.append("Musica: manca %s" % cosa)
        righe = (m.get("uscite") or []) + ((m.get("classifica") or {}).get("righe") or []) + ((m.get("classifica_singoli") or {}).get("righe") or [])
        for r in righe:
            if not r.get("copertina"):
                avvisi.append("Musica · «%s»: manca la copertina%s" % (r.get("titolo", ""), "" if r.get("foto_riserva") else " e anche la foto di riserva (così non si mette)"))
    return avvisi


def main():
    if len(sys.argv) != 2:
        sys.exit("uso: python3 sistema/build.py edizione.json")
    ed = json.load(open(sys.argv[1], encoding="utf-8"))
    for k in ("data", "edizione", "prima"):
        if k not in ed:
            sys.exit("manca il campo obbligatorio: " + k)
    os.makedirs(ARCH, exist_ok=True)
    nome = "%s-%s" % (ed["data"], ed["edizione"])
    gia = sorted(f[:-5] for f in os.listdir(ARCH) if f.endswith(".json"))
    numero = (gia.index(nome) + 1) if nome in gia else len(gia) + 1
    # prima si salva il JSON, così archivio e "edizione precedente" contano anche questa
    open(os.path.join(ARCH, nome + ".json"), "w", encoding="utf-8").write(json.dumps(ed, ensure_ascii=False, indent=1))
    open(os.path.join(ARCH, nome + ".html"), "w", encoding="utf-8").write(impagina(ed, numero, archivio=True))
    if nome == edizioni_salvate()[0]:
        open(os.path.join(ROOT, "index.html"), "w", encoding="utf-8").write(impagina(ed, numero))
    open(os.path.join(ROOT, "archivio.html"), "w", encoding="utf-8").write(archivio_html())
    print("ok: edizione N. %d -> index.html, archivio/%s.html" % (numero, nome))
    avvisi = controlla(ed)
    if avvisi:
        print("\nCONTROLLO: %d cose da sistemare nel JSON prima di pubblicare:" % len(avvisi))
        for a in avvisi:
            print(" - " + a)
    else:
        print("\nCONTROLLO: tutto a posto.")


if __name__ == "__main__":
    main()
