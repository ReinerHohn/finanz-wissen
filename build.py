#!/usr/bin/env python3
"""Baut aus wissen/*.json ein durchsuchbares, self-contained dashboard.html.

Nur Python-Standardbibliothek. Aufruf:

    python3 build.py            # baut dashboard.html + KATALOG.md
    python3 build.py --check    # nur validieren, nichts schreiben
"""
import json
import glob
import html
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
WISSEN_DIR = os.path.join(HERE, "wissen")
OUT_HTML = os.path.join(HERE, "dashboard.html")
OUT_MD = os.path.join(HERE, "KATALOG.md")

REQUIRED = ["id", "name", "category", "summary", "kernidee"]
# A = breiter Konsens / gut belegt, B = solide, C = Faustregel / kontextabhängig
LEVELS = {"A", "B", "C"}


def load_cards():
    cards, errors = [], []
    for path in sorted(glob.glob(os.path.join(WISSEN_DIR, "*.json"))):
        base = os.path.basename(path)
        try:
            with open(path, encoding="utf-8") as f:
                data = json.load(f)
        except json.JSONDecodeError as e:
            errors.append(f"{base}: ungueltiges JSON ({e})")
            continue
        for field in REQUIRED:
            if not data.get(field):
                errors.append(f"{base}: Pflichtfeld '{field}' fehlt/leer")
        if data.get("id") and data["id"] != base[:-5]:
            errors.append(f"{base}: id '{data['id']}' != Dateiname '{base}'")
        if data.get("evidence_level") and data["evidence_level"] not in LEVELS:
            errors.append(f"{base}: evidence_level '{data['evidence_level']}' nicht in A/B/C")
        cards.append(data)
    return cards, errors


def render_html(cards):
    cats = sorted({c.get("category", "") for c in cards if c.get("category")})
    data_json = json.dumps(cards, ensure_ascii=False)
    cat_opts = "".join(
        f'<option value="{html.escape(c, True)}">{html.escape(c, True)}</option>' for c in cats
    )
    return (TEMPLATE
            .replace("__DATA__", data_json)
            .replace("__CATS__", cat_opts)
            .replace("__COUNT__", str(len(cards))))


def render_md(cards):
    lines = ["# Finanz-Wissen – Katalog", "",
             "> Bildung, keine Anlageberatung. Siehe `dashboard.html` für die durchsuchbare Version.", ""]
    by_cat = {}
    for c in cards:
        by_cat.setdefault(c.get("category", "Sonstiges"), []).append(c)
    for cat in sorted(by_cat):
        lines.append(f"## {cat}\n")
        for c in sorted(by_cat[cat], key=lambda x: x.get("name", "")):
            lvl = c.get("evidence_level", "-")
            lines.append(f"### {c.get('name','?')}  \n*Evidenz {lvl}*\n")
            lines.append(f"**Kernidee:** {c.get('kernidee','')}\n")
            lines.append(f"{c.get('summary','')}\n")
            if c.get("deep_dive"):
                lines.append(c["deep_dive"] + "\n")
            for kf in c.get("key_facts", []):
                src = f" _(Quelle: {kf['source']})_" if kf.get("source") else ""
                lines.append(f"- **{kf.get('label','')}:** {kf.get('value','')}{src}")
            if c.get("misconceptions"):
                lines.append("\n**Häufige Irrtümer:**")
                for m in c["misconceptions"]:
                    lines.append(f"- {m}")
            lines.append("")
    return "\n".join(lines)


TEMPLATE = r"""<!DOCTYPE html>
<html lang="de">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Finanz-Wissen</title>
<style>
  :root{--bg:#0f1720;--card:#18232f;--ink:#e7eef5;--mut:#8da4b8;--acc:#4ea1ff;--good:#37c07a;--warn:#e0a13b;--bad:#e05a5a;}
  *{box-sizing:border-box}
  body{margin:0;font-family:-apple-system,Segoe UI,Roboto,Helvetica,Arial,sans-serif;background:#0f1720;color:#e7eef5;line-height:1.55}
  header{padding:22px 18px 8px;max-width:900px;margin:0 auto}
  h1{margin:0 0 4px;font-size:24px}
  .sub{color:#93a4b5;font-size:14px;margin-bottom:14px}
  .controls{position:sticky;top:0;background:#0f1720;padding:10px 18px;z-index:5;max-width:900px;margin:0 auto;display:flex;gap:8px;flex-wrap:wrap}
  input,select{background:#18232f;color:#e7eef5;border:1px solid #2b3947;border-radius:8px;padding:9px 11px;font-size:15px}
  input{flex:1;min-width:180px}
  .wrap{max-width:900px;margin:0 auto;padding:0 18px 60px}
  .card{background:#18232f;border:1px solid #263340;border-radius:12px;margin:10px 0;overflow:hidden}
  .head{padding:14px 16px;cursor:pointer;display:flex;gap:10px;align-items:baseline;flex-wrap:wrap}
  .head h2{margin:0;font-size:17px;flex:1;min-width:200px}
  .cat{font-size:12px;color:#93a4b5}
  .lvl{font-size:11px;font-weight:700;padding:2px 7px;border-radius:20px}
  .A{background:#123a29;color:#37c07a}.B{background:#3a3212;color:#e0a13b}.C{background:#2b2f38;color:#9fb0c1}
  .kern{padding:0 16px 12px;color:#bcd; font-size:14px}
  .kern b{color:#4ea1ff}
  .body{display:none;padding:2px 16px 18px;border-top:1px solid #263340}
  .card.open .body{display:block}
  .summary{margin:12px 0}
  .deep{color:#cdd8e2;font-size:14.5px}
  .kf{margin:10px 0;padding:10px 12px;background:#121b25;border-radius:8px}
  .kf .l{font-weight:600;color:#4ea1ff;font-size:13px}
  .kf .s{color:#7f93a6;font-size:12px}
  .miss li{color:#e7b0b0}
  .rel a{color:#4ea1ff;text-decoration:none;font-size:13px;margin-right:10px}
  .src a{color:#8bb7e8;font-size:13px}
  h3{font-size:14px;color:#9fb0c1;margin:16px 0 6px;text-transform:uppercase;letter-spacing:.4px}
  .none{color:#93a4b5;text-align:center;padding:40px}
  .disc{color:#7f93a6;font-size:12px;max-width:900px;margin:0 auto;padding:14px 18px}
</style>
</head>
<body>
<header>
  <h1>💶 Finanz-Wissen</h1>
  <div class="sub">__COUNT__ Karten · verständlich erklärt · Bildung, keine Anlageberatung</div>
</header>
<div class="controls">
  <input id="q" placeholder="Suche… (z. B. ETF, Rebalancing, Steuer, Risiko)">
  <select id="cat"><option value="">Alle Themen</option>__CATS__</select>
</div>
<div class="wrap" id="list"></div>
<div class="disc">Diese Sammlung dient dem Verständnis. Sie ist keine Anlage-, Steuer- oder Rechtsberatung. Investieren birgt das Risiko von Verlusten bis zum Totalverlust.</div>
<script>
const DATA = __DATA__;
const esc = s => (s==null?'':String(s)).replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
function kfHtml(k){return `<div class="kf"><div class="l">${esc(k.label)}</div><div>${esc(k.value)}</div>${k.source?`<div class="s">Quelle: ${esc(k.source)}</div>`:''}</div>`;}
function cardHtml(c){
  const lvl=c.evidence_level||'C';
  const kf=(c.key_facts||[]).map(kfHtml).join('');
  const miss=(c.misconceptions||[]).map(m=>`<li>${esc(m)}</li>`).join('');
  const src=(c.sources||[]).map(s=>`<div class="src"><a href="${esc(s.url)}" target="_blank" rel="noopener">${esc(s.title)}</a></div>`).join('');
  const rel=(c.related||[]).map(r=>`<a href="#" data-go="${esc(r)}">→ ${esc(r)}</a>`).join('');
  return `<div class="card" id="${esc(c.id)}" data-txt="${esc((c.name+' '+c.summary+' '+(c.tags||[]).join(' ')+' '+c.category).toLowerCase())}" data-cat="${esc(c.category)}">
    <div class="head"><h2>${esc(c.name)}</h2><span class="lvl ${lvl}">Evidenz ${lvl}</span><span class="cat">${esc(c.category)}</span></div>
    <div class="kern"><b>Kernidee:</b> ${esc(c.kernidee)}</div>
    <div class="body">
      <div class="summary">${esc(c.summary)}</div>
      ${c.deep_dive?`<div class="deep">${esc(c.deep_dive)}</div>`:''}
      ${kf?`<h3>Fakten</h3>${kf}`:''}
      ${miss?`<h3>Häufige Irrtümer</h3><ul class="miss">${miss}</ul>`:''}
      ${rel?`<h3>Verwandt</h3><div class="rel">${rel}</div>`:''}
      ${src?`<h3>Quellen</h3><div class="src">${src}</div>`:''}
    </div>
  </div>`;
}
const list=document.getElementById('list');
function draw(){
  const q=document.getElementById('q').value.toLowerCase().trim();
  const cat=document.getElementById('cat').value;
  const rows=DATA.filter(c=>(!cat||c.category===cat)&&(!q||(c.name+' '+c.summary+' '+(c.tags||[]).join(' ')+' '+c.category).toLowerCase().includes(q)));
  list.innerHTML=rows.length?rows.map(cardHtml).join(''):'<div class="none">Nichts gefunden.</div>';
}
list.addEventListener('click',e=>{
  const go=e.target.closest('[data-go]');
  if(go){e.preventDefault();const t=document.getElementById(go.dataset.go);if(t){document.getElementById('q').value='';document.getElementById('cat').value='';draw();const el=document.getElementById(go.dataset.go);el.classList.add('open');el.scrollIntoView({behavior:'smooth',block:'start'});}return;}
  const h=e.target.closest('.head');if(h)h.parentElement.classList.toggle('open');
});
document.getElementById('q').addEventListener('input',draw);
document.getElementById('cat').addEventListener('change',draw);
draw();
</script>
</body>
</html>
"""


def main():
    check = "--check" in sys.argv
    cards, errors = load_cards()
    if errors:
        print("VALIDIERUNGSFEHLER:")
        for e in errors:
            print("  -", e)
        return 1
    if check:
        print(f"OK: {len(cards)} Karten valide.")
        return 0
    with open(OUT_HTML, "w", encoding="utf-8") as f:
        f.write(render_html(cards))
    with open(OUT_MD, "w", encoding="utf-8") as f:
        f.write(render_md(cards))
    print(f"Gebaut: {len(cards)} Karten -> dashboard.html, KATALOG.md")
    return 0


if __name__ == "__main__":
    sys.exit(main())
