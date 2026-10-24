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
        out.append('<span class="term" role="button" tabindex="0" data-d="%s"%s>%s</span>'
                   % (E(breve.strip()), extra, E(m.group(1).strip())))
        last = m.end()
    out.append(E((t or "")[last:]))
    return "".join(out)


def paragrafi(n, prima_lettera=False):
    ps = n.get("testo") or []
    if isinstance(ps, str):
        ps = [ps]
    res = []
    for i, p in enumerate(ps):
        cls = "just dropcap" if (prima_lettera and i == 0) else "just"
        res.append('<p class="%s">%s</p>' % (cls, testo(p)))
    return "\n".join(res)


def foto(n, cls="photo", eager=False):
    f = n.get("foto") or {}
    url = f.get("url") if isinstance(f, dict) else f
    if not url or not str(url).startswith("https://"):
        return ""
    return ('<img class="%s" src="%s" alt="%s" loading="%s" referrerpolicy="no-referrer" onerror="this.remove()">'
            % (cls, E(url), E((f.get("didascalia") if isinstance(f, dict) else "") or n.get("titolo")),
               "eager" if eager else "lazy"))


def fonte(n):
    f = n.get("fonte") or {}
    if isinstance(f, list):
        parts = ['<a href="%s" target="_blank" rel="noopener">%s</a>' % (E(x.get("url")), E(x.get("nome"))) for x in f]
        return '<div class="src">Fonti: %s</div>' % " · ".join(parts) if parts else ""
    if not f.get("url"):
        return '<div class="src">Fonte: %s</div>' % E(f.get("nome")) if f.get("nome") else ""
    return '<div class="src"><a href="%s" target="_blank" rel="noopener">Fonte: %s</a></div>' % (E(f["url"]), E(f.get("nome")))


def apertura(n):
    did = (n.get("foto") or {}).get("didascalia") if isinstance(n.get("foto"), dict) else ""
    return """  <article class="lead">
    %s%s
    <div class="kicker" style="margin-top:10px">%s</div>
    <h2>%s</h2>
    %s
    %s
    %s
  </article>
""" % (foto(n, eager=True), ('\n    <div class="cap">%s</div>' % E(did)) if did and foto(n) else "",
       E(n.get("occhiello")), E(n.get("titolo")),
       ('<p class="deck">%s</p>' % testo(n["sommario"])) if n.get("sommario") else "",
       paragrafi(n, True), fonte(n))


def spalla(n):
    return """  <article class="spalla">
    %s
    <div>
      <div class="kicker">%s</div>
      <h3>%s</h3>
      %s
      %s
    </div>
  </article>
""" % (foto(n), E(n.get("occhiello")), E(n.get("titolo")), paragrafi(n), fonte(n))


def notizia(n, idx):
    return """  <article class="item" id="n%d">
    <div class="kicker">%s</div>
    <div class="pr">%s<h3>%s</h3></div>
    %s
    %s
  </article>
""" % (idx, E(n.get("occhiello")), foto(n), E(n.get("titolo")), paragrafi(n), fonte(n))


def folio(num, data_breve, ultima=False):
    return ('  <div class="folio"><span>Il Corriere dello Steruz</span><span>Pagina %d</span><span>%s</span></div>\n'
            % (num, "Fine" if ultima else data_breve))


def foglio(nome, corpo, hidden=True):
    return ('<section class="sheet" data-name="%s" aria-label="%s"%s>\n <div class="inner">\n%s </div>\n</section>\n'
            % (E(nome), E(nome), " hidden" if hidden else "", corpo))


def tabella_meteo(righe):
    r = []
    for x in righe or []:
        r.append('<tr><th scope="row">%s</th><td>%s</td><td>%s</td><td class="tt">%s</td></tr>'
                 % (E(x.get("luogo")), ICONE.get(x.get("icona"), ICONE["nuvole"]), E(x.get("cond")), E(x.get("temp"))))
    return '<div class="wxwrap"><table class="wxt">%s</table></div>' % "".join(r)


def pagina_meteo(m):
    s = m.get("situazione") or {}
    corpo = """  <article class="item wxpage">
    <div class="kicker">La situazione</div>
    <h3>%s</h3>
    %s
  </article>
""" % (E(s.get("titolo")), paragrafi(s))
    for chiave, etichetta in (("oggi", "oggi_etichetta"), ("domani", "domani_etichetta")):
        if m.get(chiave):
            corpo += """  <article class="item">
    <div class="kicker">%s</div>
    %s
  </article>
""" % (E(m.get(etichetta) or chiave.capitalize()), tabella_meteo(m[chiave]))
    if m.get("nota"):
        corpo += '  <article class="item"><p class="just">%s</p></article>\n' % testo(m["nota"])
    if m.get("fonti"):
        corpo += "  " + fonte({"fonte": m["fonti"]}) + "\n"
    return corpo


def impagina(ed, numero):
    d = datetime.date.fromisoformat(ed["data"])
    data_lunga = "%s %d %s %d" % (GIORNI[d.weekday()], d.day, MESI[d.month - 1], d.year)
    data_breve = d.strftime("%d.%m.%Y")
    etichetta = EDIZIONI.get(ed.get("edizione"), "Edizione speciale")
    pr = ed["prima"]

    sezioni = [s for s in ed.get("sezioni", []) if s.get("notizie")]
    pagine_dopo = [s["nome"] for s in sezioni] + (["Meteo"] if ed.get("meteo") else [])
    N = 1 + len(pagine_dopo)

    sommario = "\n".join('    <button type="button" class="goto" data-page="%d"><b>%d</b> %s</button>'
                         % (i + 1, i + 2, E(nome)) for i, nome in enumerate(pagine_dopo))

    box = ""
    if pr.get("parola") or pr.get("accadde"):
        mini = []
        if pr.get("parola"):
            mini.append('<div class="mini"><h5>La parola del giorno</h5><p class="t">%s</p><p>%s</p></div>'
                        % (E(pr["parola"].get("termine")), testo(pr["parola"].get("testo"))))
        if pr.get("accadde"):
            mini.append('<div class="mini"><h5>Accadde oggi</h5><p class="t">%s</p><p>%s</p></div>'
                        % (E(pr["accadde"].get("data")), testo(pr["accadde"].get("testo"))))
        box = '  <div class="box2">\n    %s\n  </div>\n' % "\n    ".join(mini)

    prima = """  <header class="mast">
    <h1>Il Corriere dello Steruz</h1>
    <div class="line"><span>%s</span><span>Anno I · N. %d</span></div>
    <div class="line2"><span>%s</span><a href="archivio.html" class="arch">Archivio →</a></div>
  </header>
  <nav class="summary" aria-label="Sommario">
%s
  </nav>
  <div class="tip">Trascina il bordo destro per girare pagina · tocca le <b>parole tratteggiate</b> per il significato</div>
%s%s%s%s""" % (data_lunga, numero, etichetta, sommario,
               apertura(pr["apertura"]),
               "".join(spalla(x) for x in (pr.get("spalle") or ([pr["spalla"]] if pr.get("spalla") else []))),
               box, folio(1, data_breve, N == 1))

    fogli = [foglio("Prima pagina", prima, hidden=False)]
    idx, num = 0, 2
    for s in sezioni:
        corpo = '  <div class="pghead"><h2>%s</h2><span>Corriere dello Steruz</span></div>\n' % E(s["nome"])
        if s.get("intro"):
            corpo += '  <p class="just" style="margin:0">%s</p>\n' % testo(s["intro"])
        for n in s["notizie"]:
            idx += 1
            corpo += notizia(n, idx)
        corpo += folio(num, data_breve, num == N)
        fogli.append(foglio(s["nome"], corpo))
        num += 1
    if ed.get("meteo"):
        corpo = '  <div class="pghead"><h2>Meteo</h2><span>Corriere dello Steruz</span></div>\n' + pagina_meteo(ed["meteo"])
        corpo += folio(num, data_breve, True)
        fogli.append(foglio("Meteo", corpo))

    head = open(os.path.join(SYS, "head.html"), encoding="utf-8").read()
    css = open(os.path.join(SYS, "stile.css"), encoding="utf-8").read()
    js = open(os.path.join(SYS, "giornale.js"), encoding="utf-8").read()
    return """<!doctype html>
<html lang="it">
<head>%s<style>%s
.line2 .arch{color:var(--red);text-decoration:none;font-weight:700}
.pop .more{margin-top:8px;background:none;border:0;border-top:1px dotted var(--soft);width:100%%;text-align:left;padding:8px 0 0;font:700 12px var(--label);letter-spacing:.08em;text-transform:uppercase;color:var(--term);cursor:pointer}
.pop .long{margin-top:6px;font-size:15px;color:var(--ink)}
.pop .box{max-height:calc(100vh - var(--barh,64px) - 40px);overflow-y:auto}
</style>
</head>
<body>

<main class="stack" id="stack">
<div class="edge l" id="edgeL"></div><div class="edge r" id="edgeR"></div>
<div class="book" id="book">
%s<div class="crease l" id="crL"></div><div class="crease r" id="crR" hidden></div><div class="flap" id="flap" hidden></div><div class="fshadow" id="fshadow" hidden></div>
</div>
</main>

<nav class="bar" id="bar" aria-label="Sfoglia">
  <button id="prev" type="button">← Indietro</button>
  <div class="where"><span class="name" id="pname">Prima pagina</span><span class="num" id="pnum">Pagina 1 di %d</span></div>
  <button id="next" type="button">Avanti →</button>
</nav>

<div class="pop" id="pop" hidden><div class="box" role="dialog" aria-live="polite"><button class="x" id="px" type="button" aria-label="Chiudi">×</button><p class="w" id="pw"></p><p class="d" id="pd"></p><button type="button" class="more" id="pmore" hidden aria-expanded="false">Approfondisci ▾</button><p class="d long" id="pl" hidden></p></div></div>

<script>%s</script>
</body>
</html>
""" % (head, css, "".join(fogli), N, js)


def archivio_html():
    voci = sorted((f[:-5] for f in os.listdir(ARCH) if f.endswith(".json")), reverse=True)
    righe, giorno_prec = [], None
    for v in voci:
        data, tipo = v[:10], v[11:]
        try:
            ed = json.load(open(os.path.join(ARCH, v + ".json"), encoding="utf-8"))
            titolo = ed["prima"]["apertura"]["titolo"]
        except Exception:
            titolo = ""
        d = datetime.date.fromisoformat(data)
        if data != giorno_prec:
            righe.append('<h2>%s %d %s %d</h2>' % (GIORNI[d.weekday()], d.day, MESI[d.month - 1], d.year))
            giorno_prec = data
        righe.append('<a class="ed" href="archivio/%s.html"><b>%s</b><span>%s</span></a>'
                     % (E(v), E(EDIZIONI.get(tipo, tipo)), E(titolo)))
    head = open(os.path.join(SYS, "head.html"), encoding="utf-8").read().replace(
        "<title>Il Corriere dello Steruz</title>", "<title>Archivio · Il Corriere dello Steruz</title>")
    return """<!doctype html>
<html lang="it">
<head>%s<style>
:root{--paper:#ede6d7;--ink:#1c1a16;--muted:#5a5446;--rule:#1c1a16;--soft:#b9b09c;--red:#8e1f17;--desk:#cfc6b2}
*{box-sizing:border-box}
body{margin:0;background:var(--desk);color:var(--ink);font-family:"Source Serif 4",Georgia,serif}
.sheet{max-width:700px;margin:12px auto;background:var(--paper);box-shadow:0 2px 10px rgba(40,30,10,.3);
  padding:18px max(16px,env(safe-area-inset-right,0px)) 28px max(16px,env(safe-area-inset-left,0px))}
h1{font-family:"UnifrakturMaguntia",Georgia,serif;font-weight:400;font-size:clamp(34px,10vw,60px);text-align:center;margin:0 0 4px}
.sub{text-align:center;font-family:"Libre Franklin",Arial,sans-serif;font-size:12px;letter-spacing:.12em;text-transform:uppercase;border-top:1px solid var(--rule);border-bottom:4px double var(--rule);padding:6px 0;margin-bottom:8px}
.sub a{color:var(--red);text-decoration:none;font-weight:700}
h2{font-family:"Playfair Display",Georgia,serif;font-weight:900;font-size:20px;margin:18px 0 6px;border-bottom:1px solid var(--rule);padding-bottom:4px}
.ed{display:flex;flex-direction:column;gap:2px;padding:10px 0;border-bottom:1px dotted var(--soft);color:var(--ink);text-decoration:none}
.ed b{font-family:"Libre Franklin",Arial,sans-serif;font-size:11px;letter-spacing:.1em;text-transform:uppercase;color:var(--red)}
.ed span{font-family:"Playfair Display",Georgia,serif;font-weight:700;font-size:17px;line-height:1.25}
</style>
</head>
<body><div class="sheet">
<h1>Il Corriere dello Steruz</h1>
<div class="sub">Archivio delle edizioni · <a href="index.html">Ultima edizione →</a></div>
%s
</div></body></html>
""" % (head, "\n".join(righe) or "<p>Nessuna edizione ancora.</p>")


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
    pagina = impagina(ed, numero)
    # la copia in archivio sta in una sottocartella: i link relativi devono risalire
    arch_pag = pagina.replace('href="archivio.html"', 'href="../archivio.html"')
    open(os.path.join(ARCH, nome + ".json"), "w", encoding="utf-8").write(json.dumps(ed, ensure_ascii=False, indent=1))
    open(os.path.join(ARCH, nome + ".html"), "w", encoding="utf-8").write(arch_pag)
    open(os.path.join(ROOT, "index.html"), "w", encoding="utf-8").write(pagina)
    open(os.path.join(ROOT, "archivio.html"), "w", encoding="utf-8").write(archivio_html())
    print("ok: edizione N. %d -> index.html, archivio/%s.html" % (numero, nome))


if __name__ == "__main__":
    main()
