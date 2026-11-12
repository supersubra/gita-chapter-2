import json, re, sys, html, glob, os
S, ROOT = sys.argv[1], sys.argv[2]
D = json.load(open(ROOT + "/content/verses-2.1-2.20.json"))
def q(s):
    s = re.sub(r'"([^"<>]*?)"', "“\\1”", s)
    s = re.sub(r"(?<=\w)'(?=\w)", "’", s)
    return re.sub(r"(?<=\w)' ", "’ ", s).replace(" '", " ’")
def md(s): return re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", html.escape(s, quote=False))
E = lambda s: q(html.escape(s, quote=False))
parts = []; V = {}
for p in D["parts"]:
    parts.append({"title": p["title"], "intro": p["intro"], "verses": list(p["verses"])})
    for n in p["verses"]:
        v = D["verses"][n]
        V[n] = {"who": v["who"], "sk": D["sk"][n], "read": re.sub(r"</?i>", "", v["read"]), "t": D["TITLE"][n], "one": E(D["ONE"][n]),
                "meaning": q(v["meaning"]), "gem": E(v["gem"]), "next": E(D["NEXT"][n]) if n in D["NEXT"] else "",
                "stories": [(E(l), q(s)) for l, s in zip(D["LEAD"][n], v["stories"])],
                "helps": [q(h) for h in v["helps"][:-1]], "try": q(re.sub(r"^<b>Try this today:</b>\s*", "", v["helps"][-1])),
                "note": q(v["note"]), "bhakti": q(v["bhakti"])}
V["2.2"]["who"] = "Krishna speaking"; V["2.10"]["who"] = "Sanjaya narrating"
for f in sorted(glob.glob(ROOT + "/content/*.txt"), key=lambda x: float(re.search(r"verses-2\.(\d+)", x).group(1))):
    cur = None
    for ln in open(f):
        ln = ln.rstrip("\n")
        if not ln.strip(): continue
        if ln.startswith("# "): parts.append({"title": ln[2:], "intro": "", "verses": []}); continue
        if ln.startswith("## "):
            n = ln[3:].strip(); cur = V[n] = {"who": "", "stories": [], "helps": [], "next": "", "note": ""}; parts[-1]["verses"].append(n); continue
        k, val = ln.split(": ", 1)
        if k == "intro": parts[-1]["intro"] = E(val)
        elif k == "s": l, s = val.split(" | ", 1); cur["stories"].append((E(l), E(s)))
        elif k == "h": cur["helps"].append(q(md(val)))
        elif k == "sk": a, b = val.split("।"); cur["sk"] = a.strip() + " ।<br>" + b.strip()
        elif k in ("read", "who", "t"): cur[k] = val
        else: cur[k] = E(val)
order = [n for p in parts for n in p["verses"]]
assert order == ["2.%d" % i for i in range(1, 73)], order
for n in order:
    v = V[n]; assert len(v["stories"]) == 3 and 3 <= len(v["helps"]) <= 4, n
    for k in ("sk", "read", "t", "one", "meaning", "gem", "try", "bhakti"): assert v.get(k), (n, k)
parts[1]["title"] = "Part 2: Who am I, really? (2.11–2.30)"

# transliteration sanity check
C = dict(zip("कखगघङचछजझञटठडढणतथदधनपफबभमयरलवशषसह", "k kh g gh n ch chh j jh n t th d dh n t th d dh n p ph b bh m y r l v sh sh s h".split()))
VW = {"अ": "a", "आ": "aa", "इ": "i", "ई": "ee", "उ": "u", "ऊ": "oo", "ऋ": "ri", "ए": "e", "ऐ": "ai", "ओ": "o", "औ": "au"}
M = {"ा": "aa", "ि": "i", "ी": "ee", "ु": "u", "ू": "oo", "ृ": "ri", "े": "e", "ै": "ai", "ो": "o", "ौ": "au"}
def tl(s):
    o = ""; i = 0
    while i < len(s):
        c = s[i]; nx = s[i + 1] if i + 1 < len(s) else ""
        if c in C:
            o += C[c]
            if nx in M: o += M[nx]; i += 1
            elif nx == "्": i += 1
            else: o += "a"
        elif c in VW: o += VW[c]
        elif c == "ं": o += "n"
        elif c == "ः": o += "h"
        i += 1
    return o
nz = lambda s: re.sub(r"[mn]", "n", re.sub(r"[^a-z]", "", s.lower()))
bad = [n for n in order if nz(tl(re.sub(r"<br>", "", V[n]["sk"]))) != nz(V[n]["read"])]
import difflib
for n in bad:
    a, b = nz(tl(V[n]["sk"].replace("<br>", ""))), nz(V[n]["read"])
    print("translit?", n, [(a[i1:i2], b[j1:j2], a[max(0, i1 - 5):i2 + 5]) for op, i1, i2, j1, j2 in difflib.SequenceMatcher(None, a, b).get_opcodes() if op != "equal"])

INDEX = [
("Nerves before an exam, interview or presentation", "2.2 2.18 2.32 2.35 2.50"),
("Worry about marks and results", "2.38 2.47 2.48"),
("Low marks, failure and setbacks", "2.3 2.11 2.17 2.21 2.47"),
("Winning and losing", "2.15 2.37 2.38 2.48"),
("Being hard on yourself", "2.11 2.17 2.25 2.40"),
("Comparison and jealousy", "2.4 2.8 2.16 2.25 2.57"),
("Phone, games and scrolling", "2.41 2.58 2.59 2.60 2.67"),
("Posts, likes and comments online", "2.14 2.15 2.16 2.36 2.44"),
("Wanting things", "2.44 2.55 2.62 2.70"),
("Anger and quarrels", "2.56 2.62 2.63 2.65"),
("Hurtful words and teasing", "2.14 2.19 2.23 2.36"),
("Friendship trouble and being left out", "2.1 2.9 2.12 2.23 2.30 2.71"),
("Friends moving away and goodbyes", "2.13 2.22 2.27 2.28"),
("Pressure from friends, and saying no", "2.31 2.56 2.68 2.69"),
("Standing up for someone", "2.30 2.33"),
("Honesty, promises and sharing credit", "2.5 2.34 2.51 2.71"),
("Respect for teachers and elders", "2.4 2.5 2.7"),
("Choosing a stream, a course or a job", "2.6 2.41 2.52 2.53"),
("Too much advice, and asking for help", "2.7 2.52 2.53"),
("Putting things off", "2.14 2.18 2.39 2.40"),
("Feeling empty or restless", "2.8 2.9 2.66"),
("Change and new stages of life", "2.13 2.22"),
("Losing a place, a role or a title", "2.12 2.17 2.21"),
("Being there for someone who is upset", "2.10 2.20 2.26"),
("Grief and loss", "2.20 2.27 2.28"),
("Prayer and quiet time", "2.61 2.65 2.72"),
]
CSS = """
/* Layout: one narrow reading column set like a printed booklet. One accent colour, no boxes. */
:root { --bg: #ffffff; --ink: #1f2328; --muted: #646a73; --line: #e2e2de; --accent: #8a2c2c;
  --text: "Source Serif 4", Georgia, "Times New Roman", serif;
  --sanskrit: "Tiro Devanagari Sanskrit", "Kohinoor Devanagari", "Noto Serif Devanagari", serif; }
@media (prefers-color-scheme: dark) { :root:not([data-theme="light"]) { --bg: #17181b; --ink: #e7e5e0; --muted: #a1a5ab; --line: #313338; --accent: #e3a594; color-scheme: dark } }
:root[data-theme="dark"] { --bg: #17181b; --ink: #e7e5e0; --muted: #a1a5ab; --line: #313338; --accent: #e3a594; color-scheme: dark }
* { box-sizing: border-box; }
html { scroll-padding-top: 1rem; -webkit-text-size-adjust: 100%; }
body { margin: 0; background: var(--bg); color: var(--ink); font-family: var(--text); font-size: 1.125rem; line-height: 1.65; }
main { max-width: 36rem; margin: 0 auto; padding-block: 2rem 5rem; padding-left: max(18px, env(safe-area-inset-left, 0px)); padding-right: max(18px, env(safe-area-inset-right, 0px)); }
h1, h2, h3 { font-weight: 600; line-height: 1.25; margin: 0; text-wrap: balance; }
h1 { font-size: 1.8rem; }
h2 { font-size: 1.35rem; margin-top: 3rem; }
p { margin: .8rem 0 0; }
ul { margin: .6rem 0 0; padding-left: 1.2rem; }
li { margin-top: .35rem; }
a { color: var(--accent); text-underline-offset: .15em; }
a:focus-visible, summary:focus-visible { outline: 2px solid var(--accent); outline-offset: 3px; }
.sub, .muted { color: var(--muted); }
.sub { margin-top: .3rem; }
details { border-bottom: 1px solid var(--line); }
details:first-of-type { border-top: 1px solid var(--line); }
summary { cursor: pointer; padding: .6rem 0; }
details > p:last-child, details > ol:last-child { margin-bottom: .9rem; }
details > p:first-of-type { margin-top: 0; }
.group { margin-top: .8rem; }
.toc { list-style: none; margin: 0 0 .9rem; padding: 0; }
.toc li { margin: 0; }
.toc a { display: flex; gap: .7rem; padding: .3rem 0; text-decoration: none; color: var(--ink); }
.toc a span:first-child { color: var(--accent); min-width: 2.4rem; font-variant-numeric: tabular-nums; }
.find { list-style: none; margin: .8rem 0 0; padding: 0; }
.find li { margin: 0; padding: .55rem 0; border-bottom: 1px solid var(--line); }
.find a { margin-right: .7rem; font-variant-numeric: tabular-nums; white-space: nowrap; }
.part { margin-top: 4rem; padding-top: 2rem; border-top: 2px solid var(--ink); }
.part h2 { margin-top: 0; }
.verse { margin-top: 3.2rem; padding-top: 2.2rem; border-top: 1px solid var(--line); }
.part + .verse { border-top: 0; padding-top: 0; margin-top: 2.2rem; }
.num { margin: 0; color: var(--accent); font-size: 1rem; }
.verse h3 { font-size: 1.3rem; margin-top: .3rem; }
.sk { font-family: var(--sanskrit); font-size: 1.2rem; line-height: 1.9; text-align: center; margin-top: 1.4rem; overflow-wrap: anywhere; }
.read { font-style: italic; color: var(--muted); text-align: center; font-size: 1rem; margin-top: .4rem; overflow-wrap: anywhere; }
.meaning { margin-top: 1.2rem; }
.h { font-weight: 600; margin-top: 1.6rem; }
.h + .group, .h + ul { margin-top: .5rem; }
.top { position: fixed; right: max(14px, env(safe-area-inset-right, 0px)); bottom: calc(14px + env(safe-area-inset-bottom, 0px)); background: var(--bg); border: 1px solid var(--line); border-radius: 4px; padding: .3rem .7rem; font-size: .95rem; text-decoration: none; }
footer { margin-top: 4rem; padding-top: 1.2rem; border-top: 1px solid var(--line); color: var(--muted); font-size: 1rem; }
@media print { .top { display: none; } body { font-size: 11pt; } main { max-width: none; padding: 0; }
  summary { break-after: avoid; } .h, .num, .verse h3 { break-after: avoid; } .sk, .read, li { break-inside: avoid; } .part { break-before: page; } }
"""
vid = lambda n: "v" + n.replace(".", "-")
def page(finder, title, standalone):
    H = []
    head = f'<title>{title}</title>\n<meta name="claude:viewport-fit-sides" content="cover">\n<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Source+Serif+4:ital,opsz,wght@0,8..60,400;0,8..60,600;1,8..60,400&family=Tiro+Devanagari+Sanskrit&display=swap">\n<style>{CSS}</style>'
    if standalone:
        H.append('<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n<meta name="description" content="Bhagavad Gita, Chapter 2, in simple words for young readers, with real-life moments for every verse.">\n' + head + "\n</head>\n<body>")
    else: H.append(head)
    H.append('<main id="top">')
    H.append("<h1>Bhagavad Gita, Chapter 2</h1><p class='sub'>A readable edition for young people. All 72 verses.</p>")
    H.append("<p>Every verse is set out the same way. First comes its message in one line, then the Sanskrit, how to read it aloud, and the meaning. After that are three real-life moments. Tap a title to open the one that sounds like your day. Each verse ends with what helps, one thing to try today, and a bhakti thought.</p>")
    H.append("<p>The chapter is one conversation, so it is best read in order, a few verses at a time.</p>" if not finder else "<p>The chapter is one conversation, so it is best read in order, a few verses at a time. If something particular is on your mind, the list further down will take you to a verse that speaks to it.</p>")
    H.append("<h2>Four Gems to carry through the chapter</h2><ul>")
    for g in D["gems"]: H.append(f"<li>{q(g)}</li>")
    H.append("</ul><p><b>When it feels heavy.</b> If a feeling stays for many days, talk to a parent, an elder, a close friend, a cousin or a sibling you trust.</p>")
    H.append('<h2 id="contents">Contents</h2><div class="group">')
    for p in parts:
        H.append(f"<details><summary>{E(p['title'])}</summary><ul class='toc'>")
        for n in p["verses"]: H.append(f"<li><a href='#{vid(n)}'><span>{n}</span><span>{E(V[n]['t'])}</span></a></li>")
        H.append("</ul></details>")
    H.append("</div>")
    if finder:
        H.append('<h2 id="find">Find a verse by what is on your mind</h2><ul class="find">')
        for topic, vs in INDEX:
            H.append(f"<li>{E(topic)}<br>" + "".join(f'<a href="#{vid(n)}">{n}</a>' for n in vs.split()) + "</li>")
        H.append("</ul>")
    for p in parts:
        t, name = re.match(r"(Part \d+): (.*)", p["title"]).groups()
        H.append(f'<section class="part"><h2>{t}<br>{E(name)}</h2><p>{q(p["intro"])}</p></section>')
        for n in p["verses"]:
            v = V[n]
            who = f" · {v['who']}" if v["who"] else ""
            H.append(f'<article class="verse" id="{vid(n)}"><p class="num">Verse {n}{who}</p><h3>{v["one"]}</h3>')
            H.append(f'<p class="sk" lang="sa">{v["sk"]}</p><p class="read">{html.escape(v["read"], quote=False).replace(chr(39), "’")}</p>')
            H.append(f'<p class="meaning">{v["meaning"]}</p><p class="muted">Gem: {v["gem"]}</p>')
            if v["next"]: H.append(f'<p><b>What Krishna will teach next:</b> {v["next"]}</p>')
            H.append('<p class="h">Real-life moments</p><div class="group">')
            for l, s in v["stories"]: H.append(f"<details><summary>{l}</summary><p>{s}</p></details>")
            H.append('</div><p class="h">What helps</p><ul>')
            for h_ in v["helps"]: H.append(f"<li>{h_}</li>")
            H.append(f'</ul><p><b>Try this today:</b> {v["try"]}</p>')
            if v["note"]: H.append(f'<p>{v["note"]}</p>')
            H.append(f'<p><b>Bhakti thought:</b> {v["bhakti"]}</p></article>')
    H.append("<footer>The Sanskrit follows the Gita Press, Gorakhpur edition. The meanings are in simple words, and the real-life moments are illustrations, not case studies.</footer>")
    H.append('</main><a class="top" href="#contents">Contents</a>')
    if standalone: H.append("</body>\n</html>")
    return "\n".join(H)
w = lambda path, s: open(path, "w").write(s)
w(ROOT + "/docs/index.html", page(False, "Bhagavad Gita, Chapter 2", True))
w(ROOT + "/docs/finder.html", page(True, "Bhagavad Gita, Chapter 2", True))
w(ROOT + "/Gita Chapter 2 Reader.html", page(True, "Gita Chapter 2 Reader", False))
w(ROOT + "/Gita Chapter 2 Reader (in order).html", page(False, "Gita Chapter 2 In Order", False))
w(S + "/print.html", page(False, "Bhagavad Gita, Chapter 2", True).replace("<details>", "<details open>").replace("</style>", "@page{size:A4;margin:16mm}</style>"))
words = sum(len(re.sub(r"<[^>]+>", " ", s).split()) for v in V.values() for _, s in v["stories"])
print("verses", len(V), "story words", words, "bytes", os.path.getsize(ROOT + "/docs/index.html"))
