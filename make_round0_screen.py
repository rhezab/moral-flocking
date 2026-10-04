"""Build round0_screen.html: stance of every round-0 screen sample, one tab per dilemma, plus a
comparison figure across dilemmas. A screen run is any run with >1 round-0 sample per model.

usage: python make_round0_screen.py
"""
import collections, json, statistics
from pathlib import Path

HERE = Path(__file__).resolve().parent
RUNS = HERE / "runs"
OUT = HERE / "round0_screen.html"
NAMES = {  # dilemma start -> short name
    "I am an agent making research prioritization decisions": "Pandemic research",
    "I am a staff member at a state psychiatric hospital": "Covert medication",
    "I am an agent making land protection decisions": "Environmental agency",
    "I am an agent making loan approval decisions": "Community bank",
    "I am an agent making program funding decisions": "County services",
}


def main():
    items = json.loads((HERE / "items.json").read_text())
    stances = collections.defaultdict(list)
    rationale = {}
    for line in (RUNS / "stances.jsonl").read_text().splitlines():
        s = json.loads(line)
        if s.get("valid"):
            stances[s["reply_ref"]].append(s["stance"])
            rationale.setdefault(s["reply_ref"], s.get("rationale", ""))
    recs = [(i, json.loads(l)) for i, l in enumerate((RUNS / "discussion.jsonl").read_text().splitlines())]
    r0 = [(i, r) for i, r in recs if r["condition"] == "round0"]
    screen_runs = {r["run_id"] for _, r in r0 if r["agent"] == "sample 1"}
    dilemmas = {}
    for i, r in r0:
        if r["run_id"] not in screen_runs:
            continue
        ref = f"discussion.jsonl:{i}"
        if not stances[ref]:
            continue
        name = next((v for k, v in NAMES.items() if r["dilemma"].startswith(k)), r["dilemma"][:40])
        d = dilemmas.setdefault(name, {"name": name, "run": r["run_id"], "text": r.get("dilemma_shown") or r["dilemma"],
                                       "options": next(v for k, v in items.items() if r["dilemma"].startswith(k)), "answers": []})
        d["answers"].append({"m": r["model_requested"], "k": int(r["agent"].split()[-1]), "s": round(statistics.mean(stances[ref]), 2),
                             "codes": stances[ref], "why": rationale.get(ref, ""), "text": r["reply"]})
    # A screen has several samples for every model; drop dilemmas with only stray extra samples.
    data = sorted((d for d in dilemmas.values() if len({a["m"] for a in d["answers"] if a["k"] > 0}) >= 6),
                  key=lambda d: d["name"] != "Pandemic research")
    html = TEMPLATE.replace("__DATA__", json.dumps(data, ensure_ascii=False).replace("</", "<\\/"))
    OUT.write_text(html)
    print(f"wrote {OUT.name}: " + ", ".join(f"{d['name']} ({len(d['answers'])})" for d in data))


TEMPLATE = r"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Round-0 screens</title>
<style>
:root{--bg:#fafaf8;--fg:#1d1d1b;--mut:#6b6b66;--line:#e2e1db;--card:#fff;--acc:#2f5fd0;--sel:#eaf0fd}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--fg);font:14px/1.5 system-ui,-apple-system,sans-serif}
main{max-width:980px;margin:0 auto;padding:16px 20px 60px}h1{font-size:18px;margin:4px 0}h2{font-size:16px;margin:24px 0 4px}.note{color:var(--mut);font-size:12px}
.panel{background:var(--card);border:1px solid var(--line);border-radius:8px;padding:10px 14px;margin:10px 0}
.tabs{display:flex;gap:6px;flex-wrap:wrap;margin:8px 0}.tabs button{font:inherit;border:1px solid var(--line);background:var(--card);border-radius:16px;padding:4px 12px;cursor:pointer}
.tabs button.on{background:var(--sel);border-color:var(--acc);color:var(--acc);font-weight:600}
.opts{display:grid;gap:6px;margin:8px 0}.opts div{display:flex;gap:10px}.opts b{color:var(--acc)}
#txt{white-space:pre-wrap;line-height:1.55}svg text{font-family:inherit}
table{border-collapse:collapse;font-size:12px;font-variant-numeric:tabular-nums}td,th{padding:3px 10px;border-bottom:1px solid var(--line);text-align:right}th{color:var(--mut);font-weight:600}td:first-child,th:first-child{text-align:left}
</style></head><body><main>
<h1>Round-0 screens</h1>
<div class="note">3 independent round-0 answers per model for each dilemma, each stance-coded 3× by gpt-6.1-sol (−5 = option A, +5 = option B). Built by make_round0_screen.py.</div>
<h2>Comparison</h2>
<div class="note">One row per dilemma. Each dot is one model's mean stance over its 3 samples (filled = higher tier, hollow = cheaper tier); the grey bar spans ±1 SD across models. Hover a dot for the model; click a row to open that dilemma below.</div>
<div class="panel"><svg id="cmp" width="100%"></svg><div id="cmptab" style="overflow-x:auto;margin-top:8px"></div></div>
<h2>By dilemma</h2>
<div class="tabs" id="tabs"></div>
<div id="dil"></div>
</main><script>
const DATA=__DATA__;
const ORDER=['claude-opus-5.5','claude-haiku-4.5','gpt-6.1-sol','gpt-6-luna','grok-4.7','grok-4.3','qwen3.8-max-prime','qwen3.8-flash','deepseek-v4-pro-0813','deepseek-v4.1-flash','glm-5.3-prime','glm-5.3-flash'];
const LABS=['anthropic','openai','x-ai','qwen','deepseek','z-ai'],COL=['#D97757','#10A37F','#1d1d1b','#C2185B','#2F6FE4','#8A6D00'];
const short=m=>m.split('/').pop(),col=m=>COL[LABS.indexOf(m.split('/')[0])],cheap=m=>ORDER.indexOf(short(m))%2===1;
const cs=getComputedStyle(document.documentElement),V=n=>cs.getPropertyValue(n).trim(),NS='http://www.w3.org/2000/svg';
const esc=s=>String(s).replace(/[&<>]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;'}[c])),fmt=v=>(v>0?'+':'')+(Math.round(v*10)/10);
const mean=a=>a.reduce((x,y)=>x+y,0)/a.length,sd=a=>{const m=mean(a);return Math.sqrt(mean(a.map(x=>(x-m)**2)))};
function mkSvg(svg){return (t,a,txt)=>{const e=document.createElementNS(NS,t);for(const k in a)e.setAttribute(k,a[k]);if(txt!=null)e.textContent=txt;svg.appendChild(e);return e}}
function tip(e,t){const ti=document.createElementNS(NS,'title');ti.textContent=t;e.appendChild(ti)}
// per-dilemma model means and stats
DATA.forEach(d=>{const by={};d.answers.forEach(a=>(by[a.m]=by[a.m]||[]).push(a));Object.values(by).forEach(v=>v.sort((x,y)=>x.k-y.k));d.by=by;
  d.models=Object.keys(by).sort((a,b)=>ORDER.indexOf(short(a))-ORDER.indexOf(short(b)));
  d.mm=Object.fromEntries(d.models.map(m=>[m,mean(by[m].map(a=>a.s))]));const v=Object.values(d.mm);
  d.stats={A:v.filter(x=>x<0).length,N:v.filter(x=>x===0).length,B:v.filter(x=>x>0).length,mean:mean(v),between:sd(v),within:mean(d.models.map(m=>sd(by[m].map(a=>a.s))))}});
const cmpOrder=DATA.slice().sort((a,b)=>b.stats.between-a.stats.between);
// ---- comparison figure ----
(function(){const svg=document.getElementById('cmp'),el=mkSvg(svg),W=940,L=230,R=W-24,rowH=62,T=34,H=T+cmpOrder.length*rowH+34,sx=v=>L+(v+5)/10*(R-L);
  svg.setAttribute('viewBox',`0 0 ${W} ${H}`);
  for(let v=-5;v<=5;v++){el('line',{x1:sx(v),x2:sx(v),y1:T-12,y2:H-30,stroke:V('--line'),'stroke-dasharray':v===0?'4 3':'none'});el('text',{x:sx(v),y:H-14,'text-anchor':'middle','font-size':11,fill:V('--mut')},fmt(v))}
  el('text',{x:L,y:H-1,'font-size':11,'font-weight':600,fill:V('--fg')},'← option A');el('text',{x:R,y:H-1,'text-anchor':'end','font-size':11,'font-weight':600,fill:V('--fg')},'option B →');
  cmpOrder.forEach((d,i)=>{const y=T+i*rowH,st=d.stats,g=el('g',{style:'cursor:pointer'});g.onclick=()=>{show(DATA.indexOf(d));document.getElementById('tabs').scrollIntoView({behavior:'smooth'})};
    const add=mkSvg(g);add('rect',{x:0,y:y-rowH/2+2,width:W,height:rowH-4,fill:'transparent'});
    add('text',{x:L-14,y:y-2,'text-anchor':'end','font-size':13,'font-weight':600,fill:V('--fg')},d.name);
    add('text',{x:L-14,y:y+13,'text-anchor':'end','font-size':11,fill:V('--mut')},`A ${st.A} · B ${st.B}${st.N?` · 0 ${st.N}`:''} · SD ${st.between.toFixed(1)}`);
    add('line',{x1:sx(Math.max(-5,st.mean-st.between)),x2:sx(Math.min(5,st.mean+st.between)),y1:y,y2:y,stroke:V('--mut'),'stroke-width':10,'stroke-opacity':.18,'stroke-linecap':'round'});
    const pos={};d.models.forEach(m=>{const v=Math.round(d.mm[m]*2)/2;(pos[v]=pos[v]||[]).push(m)});
    // Models sharing a stance stack in columns of up to 5; extra columns step inward, away from the axis ends.
    Object.entries(pos).forEach(([v,ms])=>ms.forEach((m,j)=>{const colN=Math.floor(j/5),inCol=Math.min(5,ms.length-colN*5),r=j%5,dir=+v>=0?-1:1;
      const x=sx(d.mm[m])+dir*colN*11,yy=y+(r-(inCol-1)/2)*9,c=col(m);
      const dot=add('circle',{cx:x,cy:yy,r:5,fill:cheap(m)?V('--card'):c,stroke:c,'stroke-width':2});tip(dot,`${short(m)}: ${fmt(d.mm[m])} (samples ${d.by[m].map(a=>fmt(a.s)).join(', ')})`)}));
    add('line',{x1:sx(st.mean),x2:sx(st.mean),y1:y-12,y2:y+12,stroke:V('--fg'),'stroke-width':2});
  });
  document.getElementById('cmptab').innerHTML=`<table><tr><th>Dilemma</th><th>A</th><th>B</th><th>neutral</th><th>mean</th><th>SD between models</th><th>SD within model</th><th>Option A</th><th>Option B</th></tr>${cmpOrder.map(d=>`<tr><td><b>${d.name}</b></td><td>${d.stats.A}</td><td>${d.stats.B}</td><td>${d.stats.N}</td><td>${fmt(d.stats.mean)}</td><td>${d.stats.between.toFixed(2)}</td><td>${d.stats.within.toFixed(2)}</td><td style="text-align:left;max-width:200px">${esc(d.options.option_a)}</td><td style="text-align:left;max-width:200px">${esc(d.options.option_b)}</td></tr>`).join('')}</table><div class="note" style="margin-top:4px">Black tick = mean across models. Rows sorted by spread between models.</div>`;
})();
// ---- per-dilemma screen ----
const tabs=document.getElementById('tabs');DATA.forEach((d,i)=>{const b=document.createElement('button');b.textContent=d.name;b.onclick=()=>show(i);tabs.appendChild(b)});
function show(i){const d=DATA[i];[...tabs.children].forEach((b,j)=>b.classList.toggle('on',i===j));const st=d.stats;
  document.getElementById('dil').innerHTML=`<details class="panel"><summary style="cursor:pointer"><b>Dilemma</b> <span class="note">(run ${d.run})</span></summary><div style="white-space:pre-wrap;margin-top:6px">${esc(d.text)}</div></details>
   <div class="opts"><div><b>A</b>${esc(d.options.option_a)}<span class="note" style="margin-left:auto">−5</span></div><div><b>B</b>${esc(d.options.option_b)}<span class="note" style="margin-left:auto">+5</span></div></div>
   <div class="note">Sample 0 (natural population): ${d.models.filter(m=>d.by[m][0].s<0).length} on the A side · ${d.models.filter(m=>d.by[m][0].s>0).length} on the B side. Filled dot = sample 0, hollow = samples 1–2. Click a dot to read the answer.</div>
   <div class="panel"><svg id="chart" width="100%"></svg></div><div class="panel" id="detail"><span class="note">Click a dot to read that answer.</span></div>`;
  const svg=document.getElementById('chart'),el=mkSvg(svg),models=d.models.slice().sort((a,b)=>d.by[a][0].s-d.by[b][0].s||ORDER.indexOf(short(a))-ORDER.indexOf(short(b)));
  const W=940,L=190,R=W-30,rowH=30,T=24,H=T+models.length*rowH+40,sx=v=>L+(v+5)/10*(R-L);svg.setAttribute('viewBox',`0 0 ${W} ${H}`);
  for(let v=-5;v<=5;v++){el('line',{x1:sx(v),x2:sx(v),y1:T-10,y2:H-34,stroke:V('--line'),'stroke-dasharray':v===0?'4 3':'none'});el('text',{x:sx(v),y:H-18,'text-anchor':'middle','font-size':11,fill:V('--mut')},fmt(v))}
  el('text',{x:L,y:H-2,'font-size':12,'font-weight':600,fill:V('--fg')},'← A');el('text',{x:R,y:H-2,'text-anchor':'end','font-size':12,'font-weight':600,fill:V('--fg')},'B →');
  let sel=null;
  models.forEach((m,i)=>{const y=T+i*rowH;el('text',{x:L-30,y:y+4,'text-anchor':'end','font-size':12,fill:V('--fg')},short(m));
    const grp={};d.by[m].forEach(a=>(grp[a.s]=grp[a.s]||[]).push(a));
    Object.values(grp).forEach(g=>g.forEach((a,j)=>{const x=sx(a.s)+(j-(g.length-1)/2)*13,c=col(m);
      const dot=el('circle',{cx:x,cy:y,r:a.k?5.5:7,fill:a.k?V('--card'):c,stroke:c,'stroke-width':2.2,style:'cursor:pointer'});tip(dot,`${short(m)} · sample ${a.k} · stance ${fmt(a.s)} (codes ${a.codes.join(', ')})`);
      dot.onclick=()=>{if(sel)sel.setAttribute('stroke-width',2.2);sel=dot;dot.setAttribute('stroke-width',4);
        document.getElementById('detail').innerHTML=`<div style="display:flex;gap:10px;align-items:baseline;flex-wrap:wrap"><b style="font-size:15px">${esc(short(m))}</b><span class="note">sample ${a.k}${a.k?'':' (natural population)'} · stance ${fmt(a.s)} · codes ${a.codes.join(', ')} · ${a.text.split(/\s+/).length} words</span></div><div class="note" style="margin:4px 0 8px">Coder: ${esc(a.why)}</div><div id="txt">${esc(a.text)}</div>`}}))});
}
show(0);
</script></body></html>"""

if __name__ == "__main__":
    main()
