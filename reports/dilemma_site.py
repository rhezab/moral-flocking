"""Build reports/dilemmas.html: a clean per-dilemma explorer of the natural runs (control + forum).
A selector picks the dilemma; the page shows the dilemma, its options, stance by round and a movie.
Reads reports/natural.json (run natural_data.py first).

usage: python reports/dilemma_site.py
"""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
SLUG = {"Pandemic research": "pandemic", "Covert medication": "covert", "County services": "county", "Community bank": "bank"}
SHORT = {"Pandemic research": ("Track A", "Track B"), "Covert medication": ("medicate covertly", "refuse"),
         "County services": ("addiction treatment", "child welfare"), "Community bank": ("small-business loans", "mortgages")}


def main():
    data = json.loads((HERE / "natural.json").read_text())
    for d in data:
        d["slug"], d["short"] = SLUG[d["name"]], SHORT[d["name"]]
        for k in ("posts", "mentions", "sides"):
            d.pop(k, None)
    (HERE / "dilemmas.html").write_text(TEMPLATE.replace("__DATA__", json.dumps(data).replace("</", "<\\/")))
    print("wrote reports/dilemmas.html")


TEMPLATE = r"""<title>Dilemma Explorer</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;500;600&family=IBM+Plex+Mono:wght@400;500&family=Newsreader:opsz,wght@6..72,400;6..72,500&display=swap">
<style>
/* Layout: one centred column; a sticky bar holds the dilemma selector and condition toggle; figures run full column width. */
:root{
  --bg:#f5f6f4; --surface:#ffffff; --ink:#1c1f1d; --muted:#626a64; --rule:#dfe3df; --faint:#eef1ee;
  --accent:#2d5a8c; --a:#2f6e9e; --b:#b4582c;
  --l0:#D97757; --l1:#10A37F; --l2:#1d1d1b; --l3:#C2185B; --l4:#2F6FE4; --l5:#8A6D00;
  --sans:"IBM Plex Sans",ui-sans-serif,system-ui,sans-serif;
  --mono:"IBM Plex Mono",ui-monospace,SFMono-Regular,Menlo,monospace;
  --read:"Newsreader",Georgia,"Times New Roman",serif;
}
@media (prefers-color-scheme: dark){:root:not([data-theme="light"]){
  --bg:#121513; --surface:#1a1e1b; --ink:#e6e9e6; --muted:#98a19a; --rule:#2c322e; --faint:#212622;
  --accent:#86aee0; --a:#6aa7d6; --b:#e08a5f;
  --l0:#D27350; --l1:#20AE80; --l2:#ecebe6; --l3:#A82E63; --l4:#4F80EC; --l5:#7F6F10; color-scheme:dark}}
:root[data-theme="dark"]{
  --bg:#121513; --surface:#1a1e1b; --ink:#e6e9e6; --muted:#98a19a; --rule:#2c322e; --faint:#212622;
  --accent:#86aee0; --a:#6aa7d6; --b:#e08a5f;
  --l0:#D27350; --l1:#20AE80; --l2:#ecebe6; --l3:#A82E63; --l4:#4F80EC; --l5:#7F6F10; color-scheme:dark}
*{box-sizing:border-box}
body{background:var(--bg);color:var(--ink);font:15px/1.55 var(--sans);padding-inline:16px;padding-block:24px 64px}
main{max-width:52rem;margin:0 auto;display:flex;flex-direction:column;gap:14px}
h1{font-size:1.5rem;font-weight:600;margin:0;letter-spacing:-.01em}
.sub{color:var(--muted);font-size:.9rem;margin:0}
.bar{z-index:5;background:var(--bg);display:flex;flex-wrap:wrap;gap:10px 16px;align-items:center;padding:10px 0;border-bottom:1px solid var(--rule)}
.bar label{font-family:var(--mono);font-size:.72rem;text-transform:uppercase;letter-spacing:.06em;color:var(--muted)}
@media (min-width:700px){.bar{position:sticky;top:env(safe-area-inset-top,0px)}}
select{font:500 .95rem var(--sans);color:var(--ink);background:var(--surface);border:1px solid var(--rule);border-radius:8px;padding:6px 30px 6px 10px}
.seg{display:inline-flex;border:1px solid var(--rule);border-radius:8px;overflow:hidden;font:500 .82rem var(--sans)}
.seg button{font:inherit;border:0;background:var(--surface);color:var(--muted);padding:6px 14px;cursor:pointer}
.seg button.on{background:var(--ink);color:var(--surface)}
button:focus-visible,select:focus-visible,input:focus-visible{outline:2px solid var(--accent);outline-offset:2px}
.summary{display:flex;flex-wrap:wrap;gap:6px 18px;font-family:var(--mono);font-size:.78rem;color:var(--muted);margin-left:auto}
.summary b{color:var(--ink);font-weight:500}
.card{background:var(--surface);border:1px solid var(--rule);border-radius:10px;padding:16px 18px}
.dtext{font:1.02rem/1.65 var(--read);white-space:pre-wrap;margin:0}
.dtext.clamp{max-height:9.6em;overflow:hidden;-webkit-mask-image:linear-gradient(#000 70%,transparent)}
.q{font:500 1.08rem/1.5 var(--read);margin:12px 0 0}
.more{font:500 .8rem var(--sans);color:var(--accent);background:none;border:0;padding:6px 0 0;cursor:pointer}
.opts{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:10px}
@media (max-width:620px){.opts{grid-template-columns:minmax(0,1fr)}}
.opt{background:var(--surface);border:1px solid var(--rule);border-radius:10px;padding:10px 14px;display:flex;flex-direction:column;gap:2px}
.opt .k{font-family:var(--mono);font-size:.72rem;font-weight:500}
.opt.A{box-shadow:inset 3px 0 0 var(--a)} .opt.B{box-shadow:inset 3px 0 0 var(--b)}
.head{display:flex;justify-content:space-between;align-items:baseline;gap:10px;flex-wrap:wrap;margin-top:8px}
.head h2{font-size:1rem;font-weight:600;margin:0}
.note{color:var(--muted);font-size:.8rem}
figure{margin:0;background:var(--surface);border:1px solid var(--rule);border-radius:10px;padding:12px 14px;min-width:0}
svg{width:100%;height:auto;display:block}
svg text{font-family:var(--mono)}
.scroll{overflow-x:auto}.scroll svg{min-width:600px}
.mv{display:flex;gap:10px;align-items:center;margin-bottom:6px}
.play{font:500 .82rem var(--sans);border:1px solid var(--rule);background:var(--surface);color:var(--ink);border-radius:8px;padding:6px 12px;cursor:pointer;min-width:84px}
.mv input{flex:1;accent-color:var(--accent)}
.rl{font-family:var(--mono);font-size:.75rem;color:var(--muted);min-width:92px;text-align:right}
.legend{display:flex;flex-wrap:wrap;gap:4px 14px;font-family:var(--mono);font-size:.72rem;color:var(--muted);margin-top:8px}
.legend i{display:inline-block;width:9px;height:9px;border-radius:50%;margin-right:5px;vertical-align:-1px}
.grid2{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:12px}
@media (max-width:700px){.grid2{grid-template-columns:minmax(0,1fr)}}
.radars{display:grid;grid-template-columns:repeat(auto-fill,minmax(180px,1fr));gap:6px}
.radars>div{border:1px solid var(--faint);border-radius:8px;padding:2px}
.citepanel{margin-top:10px;border-top:1px solid var(--rule);padding-top:10px;font-size:.88rem;min-height:3.2em}
.citepanel .who{display:flex;flex-wrap:wrap;gap:4px 14px;margin:4px 0 8px}
.citepanel blockquote{margin:6px 0;padding:6px 10px;border-left:3px solid var(--rule);font:.95rem/1.5 var(--read);color:var(--ink)}
.citepanel .tag{font-family:var(--mono);font-size:.7rem;color:var(--muted)}
.empty{color:var(--muted);font-size:.88rem;padding:14px;border:1px dashed var(--rule);border-radius:10px;background:var(--surface)}
</style>

<main>
  <header style="display:flex;flex-direction:column;gap:4px">
    <h1>Dilemma Explorer</h1>
    <p class="sub">Twelve models from six labs answer a moral dilemma, then either discuss it in a shared forum or reflect alone for three rounds. Stances are coded from −5 (option A) to +5 (option B).</p>
  </header>
  <div class="bar">
    <label for="pick">Dilemma</label>
    <select id="pick"></select>
    <div class="seg" role="group" aria-label="Condition"><button type="button" data-c="forum" class="on">Forum</button><button type="button" data-c="control">Control</button></div>
    <div class="summary" id="summary"></div>
  </div>
  <div class="card"><p class="dtext clamp" id="dtext"></p><button class="more" id="more" type="button">Read the full dilemma</button><p class="q" id="q"></p></div>
  <div class="opts" id="opts"></div>
  <div class="head"><h2>Stance by round</h2><span class="note" id="cnote"></span></div>
  <figure><div class="scroll"><svg id="spec"></svg></div><div class="legend" id="legend"></div></figure>
  <div class="head"><h2>Who they named</h2><span class="note">Forum only. Hover a dot in rounds 1–3 to see which peers that model named; click to pin.</span></div>
  <figure><div class="scroll"><svg id="cite"></svg></div>
    <div class="legend"><span><i style="width:18px;height:3px;border-radius:0;background:var(--ink)"></i>named in its private answer</span><span><i style="width:18px;height:0;border-radius:0;border-top:2px dashed var(--ink)"></i>named only in its public post</span><span>lines run from where the peer stood in the previous round</span></div>
    <div id="citepanel" class="citepanel"></div></figure>
  <div class="head"><h2>Movie</h2><span class="note">Each model gliding between rounds; a faint ring marks where it started.</span></div>
  <figure><div class="mv"><button type="button" class="play">▶ Play</button><input class="t" type="range" min="0" max="3" step="0.01" value="0" aria-label="Round"><span class="rl">Round 0</span></div><svg id="movie"></svg></figure>
  <div class="head"><h2>Theory profiles</h2><span class="note" id="rnote"></span></div>
  <div id="radars"></div>
  <div class="head"><h2>Maps</h2><span class="note">Every private answer in both conditions, placed by what it argues. Grey dots are all answers; coloured dots move with the controls.</span></div>
  <figure><div class="mv"><button type="button" class="play">▶ Play</button><input class="t" type="range" min="0" max="3" step="0.01" value="0" aria-label="Round"><span class="rl">Round 0</span></div>
    <div class="grid2"><div><svg id="mca"></svg><p class="note" id="mcanote"></p></div><div id="pcabox"><svg id="pca"></svg><p class="note" id="pcanote"></p></div></div></figure>
</main>

<script>
(function(){
const DATA=__DATA__;
const ORDER=['claude-opus-5.5','claude-haiku-4.5','gpt-6.1-sol','gpt-6-luna','grok-4.7','grok-4.3','qwen3.8-max-prime','qwen3.8-flash','deepseek-v4-pro-0813','deepseek-v4.1-flash','glm-5.3-prime','glm-5.3-flash'];
const LABS=['anthropic','openai','x-ai','qwen','deepseek','z-ai'],LABNAME=['Anthropic','OpenAI','xAI','Alibaba','DeepSeek','Zhipu'];
const NS='http://www.w3.org/2000/svg',short=m=>m.split('/').pop(),lbl=m=>short(m).replace('deepseek-','ds-').replace('-0813',''),cheap=m=>ORDER.indexOf(short(m))%2===1;
const mean=a=>a.reduce((x,y)=>x+y,0)/a.length,sd=a=>{const m=mean(a);return Math.sqrt(mean(a.map(x=>(x-m)**2)))},fmt=v=>(v>0?'+':'')+(Math.round(v*10)/10);
const esc=x=>String(x).replace(/[&<>]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;'}[c]));
const $=id=>document.getElementById(id);
function el(p,t,a,txt){const e=document.createElementNS(NS,t);for(const k in a)e.setAttribute(k,a[k]);if(txt!=null)e.textContent=txt;p.appendChild(e);return e}
let C;const css=()=>{const s=getComputedStyle(document.documentElement),g=n=>s.getPropertyValue(n).trim();C={ink:g('--ink'),mut:g('--muted'),rule:g('--rule'),faint:g('--faint'),a:g('--a'),b:g('--b'),bg:g('--surface'),lab:[0,1,2,3,4,5].map(i=>g('--l'+i))}};
const labC=m=>C.lab[LABS.indexOf(m.split('/')[0])];
let S={i:0,cond:'forum',t:0},timer=null;
try{const h=location.hash.slice(1),j=DATA.findIndex(d=>d.slug===h);if(j>=0)S.i=j}catch(e){}

$('pick').innerHTML=DATA.map((d,i)=>`<option value="${i}">${d.name}</option>`).join('');
$('pick').onchange=e=>{S.i=+e.target.value;S.t=0;stop();try{history.replaceState(null,'','#'+DATA[S.i].slug)}catch(_){};render()};
document.querySelectorAll('.seg button').forEach(b=>b.onclick=()=>{S.cond=b.dataset.c;document.querySelectorAll('.seg button').forEach(x=>x.classList.toggle('on',x===b));draw()});
$('more').onclick=()=>{const c=$('dtext').classList.toggle('clamp');$('more').textContent=c?'Read the full dilemma':'Show less'};
// Every play button and round slider on the page drives the same time t (movie and maps).
document.querySelectorAll('.t').forEach(sl=>sl.oninput=e=>{stop();S.t=+e.target.value;pos()});
document.querySelectorAll('.play').forEach(b=>b.onclick=()=>{if(timer){stop();return}const from=S.t>=3?0:Math.floor(S.t),start=performance.now(),SEG=1400,HOLD=450;
  document.querySelectorAll('.play').forEach(x=>x.textContent='❚❚ Pause');
  timer=setInterval(()=>{const e=performance.now()-start,per=SEG+HOLD,seg=Math.floor(e/per),f=Math.min(1,Math.max(0,(e-seg*per-HOLD)/SEG));S.t=Math.min(3,from+seg+f);pos();if(S.t>=3)stop()},30)});
function stop(){clearInterval(timer);timer=null;document.querySelectorAll('.play').forEach(x=>x.textContent='▶ Play')}

function render(){const d=DATA[S.i];$('pick').value=S.i;
  const parts=d.dilemma.trim().split(/\n\s*\n/),q=parts.pop();$('dtext').textContent=parts.join('\n\n');$('q').textContent=q;
  $('dtext').classList.add('clamp');$('more').textContent='Read the full dilemma';
  $('opts').innerHTML=`<div class="opt A"><span class="k" style="color:var(--a)">A · −5</span>${esc(d.options.option_a)}</div><div class="opt B"><span class="k" style="color:var(--b)">B · +5</span>${esc(d.options.option_b)}</div>`;
  draw()}
const rows=()=>{const d=DATA[S.i];return d.conds[S.cond].slice().sort((x,y)=>x.st[0]-y.st[0]||ORDER.indexOf(short(x.model))-ORDER.indexOf(short(y.model)))};
const split=(c,k)=>{const v=DATA[S.i].conds[c].map(a=>a.st[k]).filter(x=>x!=null);return {A:v.filter(x=>x<0).length,B:v.filter(x=>x>0).length,m:mean(v)}};
function draw(){css();const d=DATA[S.i],r=rows();
  const s0=split('forum',0),f3=split('forum',3),c3=split('control',3);
  $('summary').innerHTML=`<span>start <b>${s0.A} : ${s0.B}</b></span><span>forum R3 <b>${f3.A} : ${f3.B}</b> (${fmt(f3.m)})</span><span>control R3 <b>${c3.A} : ${c3.B}</b> (${fmt(c3.m)})</span>`;
  $('cnote').textContent=S.cond==='forum'?'Forum: models post and read each other every round.':'Control: each model re-reads only its own answers.';
  // spectrum
  const s=$('spec');s.innerHTML='';const W=780,L=118,gap=30,cw=(W-L-8-gap*3)/4,rh=20,T=24,n=r.length+1,H=T+n*rh+26,x0=k=>L+k*(cw+gap),sx=(k,v)=>x0(k)+(v+5)/10*cw,yB=T+n*rh-6;
  s.setAttribute('viewBox',`0 0 ${W} ${H}`);s.setAttribute('role','img');s.setAttribute('aria-label',`${d.name}: stance of each model by round, ${S.cond}`);
  [0,1,2,3].forEach(k=>{el(s,'text',{x:x0(k)+cw/2,y:12,'text-anchor':'middle','font-size':11.5,'font-weight':500,fill:C.ink},'Round '+k);
    el(s,'line',{x1:sx(k,0),x2:sx(k,0),y1:T-8,y2:yB,stroke:C.rule,'stroke-dasharray':'3 3'});
    el(s,'text',{x:sx(k,-5),y:yB+14,'font-size':9.5,fill:C.a},'A');el(s,'text',{x:sx(k,5),y:yB+14,'text-anchor':'end','font-size':9.5,fill:C.b},'B')});
  r.forEach((a,j)=>{const y=T+j*rh+4;el(s,'text',{x:L-10,y:y+3.5,'text-anchor':'end','font-size':10,fill:C.ink},lbl(a.model));
    [0,1,2,3].forEach(k=>{el(s,'line',{x1:x0(k),x2:x0(k)+cw,y1:y,y2:y,stroke:C.faint});const v=a.st[k];if(v==null)return;
      const c=el(s,'circle',{cx:sx(k,v),cy:y,r:4.4,fill:cheap(a.model)?C.bg:labC(a.model),stroke:labC(a.model),'stroke-width':1.8});el(c,'title',{},`${short(a.model)} · round ${k}: ${fmt(v)}`)})});
  const ym=T+r.length*rh+4;el(s,'text',{x:L-10,y:ym+3.5,'text-anchor':'end','font-size':10,'font-weight':500,fill:C.mut},'mean ± SD');
  [0,1,2,3].forEach(k=>{const v=r.map(a=>a.st[k]).filter(x=>x!=null),m=mean(v),e=sd(v);
    el(s,'line',{x1:sx(k,Math.max(-5,m-e)),x2:sx(k,Math.min(5,m+e)),y1:ym,y2:ym,stroke:C.mut,'stroke-width':6,'stroke-opacity':.28,'stroke-linecap':'round'});
    const c=el(s,'circle',{cx:sx(k,m),cy:ym,r:3.6,fill:C.ink});el(c,'title',{},`round ${k}: mean ${fmt(m)}, SD ${e.toFixed(1)}, A ${v.filter(x=>x<0).length} : ${v.filter(x=>x>0).length} B`)});
  $('legend').innerHTML=LABS.map((l,i)=>`<span><i style="background:${C.lab[i]}"></i>${LABNAME[i]}</span>`).join('')+'<span>filled = higher tier · hollow = cheaper tier</span>';
  // movie
  const m=$('movie');m.innerHTML='';const MW=780,ML=118,MR=MW-16,mrh=22,MT=10,MH=MT+r.length*mrh+40,msx=v=>ML+(v+5)/10*(MR-ML);
  m.setAttribute('viewBox',`0 0 ${MW} ${MH}`);m.setAttribute('role','img');m.setAttribute('aria-label',`${d.name}: animated stances, ${S.cond}`);
  el(m,'line',{x1:msx(0),x2:msx(0),y1:MT-4,y2:MH-34,stroke:C.rule,'stroke-dasharray':'3 3'});
  for(let v=-5;v<=5;v++){el(m,'line',{x1:msx(v),x2:msx(v),y1:MH-36,y2:MH-31,stroke:C.mut});el(m,'text',{x:msx(v),y:MH-19,'text-anchor':'middle','font-size':9.5,fill:C.mut},fmt(v))}
  el(m,'text',{x:ML,y:MH-3,'font-size':10.5,'font-weight':500,fill:C.a},'← A · '+d.short[0]);el(m,'text',{x:MR,y:MH-3,'text-anchor':'end','font-size':10.5,'font-weight':500,fill:C.b},d.short[1]+' · B →');
  DOTS=r.map((a,j)=>{const y=MT+j*mrh+6;el(m,'line',{x1:ML,x2:MR,y1:y,y2:y,stroke:C.faint});el(m,'text',{x:ML-10,y:y+3.5,'text-anchor':'end','font-size':10,fill:C.ink},lbl(a.model));
    if(a.st[0]!=null)el(m,'circle',{cx:msx(a.st[0]),cy:y,r:5,fill:'none',stroke:labC(a.model),'stroke-opacity':.3,'stroke-width':1.5});
    const c=el(m,'circle',{cy:y,r:5.6,fill:cheap(a.model)?C.bg:labC(a.model),stroke:labC(a.model),'stroke-width':2});return [c,el(c,'title',{},''),a]});
  MSX=msx;citeFig();radars();MAPS=[mapFig('mca'),mapFig('pca')].filter(Boolean);pos();
}
let DOTS=[],MSX=null,MAPS=[];
const lerp=(arr,t)=>{const k=Math.floor(t),f=t-k,p=arr[k],q=arr[Math.min(3,k+1)];if(p==null)return q;if(q==null||f===0)return p;return Array.isArray(p)?[p[0]+(q[0]-p[0])*f,p[1]+(q[1]-p[1])*f]:p+(q-p)*f};
function pos(){const t=S.t,k=Math.floor(t);DOTS.forEach(([c,ti,a])=>{const v=lerp(a.st,t);
  c.style.display=v==null?'none':'';if(v!=null){c.setAttribute('cx',MSX(v));ti.textContent=`${short(a.model)}: ${fmt(v)}`}});
  MAPS.forEach(M=>M.dots.forEach(([c,ti,a])=>{const v=a[M.key]&&lerp(a[M.key],t);c.style.display=v?'':'none';if(v){c.setAttribute('cx',M.sx(v[0]));c.setAttribute('cy',M.sy(v[1]));ti.textContent=`${short(a.model)} · round ${t.toFixed(1)}`}}));
  document.querySelectorAll('.t').forEach(x=>x.value=t);document.querySelectorAll('.rl').forEach(x=>x.textContent=Number.isInteger(t)?`Round ${t}`:`Round ${k} → ${k+1}`)}
// ---- who they named: lines from cited peers (round k-1 position) to the citing model (round k) ----
let PIN=null;
function citeFig(){const d=DATA[S.i],svg=$('cite'),panel=$('citepanel');svg.innerHTML='';PIN=null;
  const r=d.conds.forum.slice().sort((x,y)=>x.st[0]-y.st[0]||ORDER.indexOf(short(x.model))-ORDER.indexOf(short(y.model)));
  const W=780,L=118,gap=30,cw=(W-L-8-gap*3)/4,rh=22,T=24,H=T+r.length*rh+20,x0=k=>L+k*(cw+gap),sx=(k,v)=>x0(k)+(v+5)/10*cw,yB=T+r.length*rh-6;
  svg.setAttribute('viewBox',`0 0 ${W} ${H}`);svg.setAttribute('role','img');svg.setAttribute('aria-label',`${d.name}: who each model named, by round`);
  [0,1,2,3].forEach(k=>{el(svg,'text',{x:x0(k)+cw/2,y:12,'text-anchor':'middle','font-size':11.5,'font-weight':500,fill:C.ink},'Round '+k);
    el(svg,'line',{x1:sx(k,0),x2:sx(k,0),y1:T-8,y2:yB,stroke:C.rule,'stroke-dasharray':'3 3'});
    el(svg,'text',{x:sx(k,-5),y:yB+14,'font-size':9.5,fill:C.a},'A');el(svg,'text',{x:sx(k,5),y:yB+14,'text-anchor':'end','font-size':9.5,fill:C.b},'B')});
  const ov=el(svg,'g',{}),P=new Map(),dots=[];
  r.forEach((a,j)=>{const y=T+j*rh+4;el(svg,'text',{x:L-10,y:y+3.5,'text-anchor':'end','font-size':10,fill:C.ink},lbl(a.model));
    [0,1,2,3].forEach(k=>{el(svg,'line',{x1:x0(k),x2:x0(k)+cw,y1:y,y2:y,stroke:C.faint});const v=a.st[k];if(v==null)return;
      const n=k?(a.cites[k]||[]).length:0,c=el(svg,'circle',{cx:sx(k,v),cy:y,r:4.6,fill:cheap(a.model)?C.bg:labC(a.model),stroke:labC(a.model),'stroke-width':1.8,style:k?'cursor:pointer':''});
      el(c,'title',{},`${short(a.model)} · round ${k}: ${fmt(v)}${k?` · named ${new Set((a.cites[k]||[]).map(x=>x.to)).size} peers`:''}`);
      P.set(a.model+'|'+k,[sx(k,v),y]);dots.push([c,a,k]);
      if(k){c.addEventListener('mouseenter',()=>{if(!PIN)show(a,k)});c.addEventListener('click',()=>{if(PIN&&PIN[0]===a&&PIN[1]===k){PIN=null;clear()}else{PIN=[a,k];show(a,k)}})}})});
  const idle='<span class="note">Hover a dot in rounds 1–3. Click to pin it and read the quotes.</span>';panel.innerHTML=idle;
  function clear(){ov.innerHTML='';dots.forEach(([c])=>c.style.opacity='');panel.innerHTML=idle}
  function show(a,k){ov.innerHTML='';const cs=a.cites[k]||[],to=P.get(a.model+'|'+k),by={};
    cs.forEach(c=>{const b=by[c.to]=by[c.to]||{n:0,priv:false,quotes:[]};b.n++;if(c.where==='private')b.priv=true;if(!b.quotes.includes(c.quote))b.quotes.push(c.quote)});
    Object.entries(by).forEach(([m,b])=>{const fr=P.get(m+'|'+(k-1));if(!fr||!to)return;
      el(ov,'line',{x1:fr[0],y1:fr[1],x2:to[0],y2:to[1],stroke:labC(m),'stroke-width':1.2+Math.min(3,b.n*.7),'stroke-opacity':.8,'stroke-dasharray':b.priv?'none':'4 3'})});
    const on=new Set(Object.keys(by));dots.forEach(([c,aa,kk])=>c.style.opacity=(aa===a&&(kk===k||kk===k-1))||(on.has(aa.model)&&kk===k-1)?'':'.2');
    const prev=a.st[k-1],cur=a.st[k],dd=cur!=null&&prev!=null?cur-prev:null;
    const peers=Object.entries(by).sort((x,y)=>y[1].n-x[1].n);
    panel.innerHTML=`<div><b>${esc(short(a.model))}</b> <span class="tag">round ${k-1} ${fmt(prev)} → round ${k} ${fmt(cur)}${dd?` (${dd>0?'toward B':'toward A'} ${fmt(Math.abs(dd))})`:''}</span>${PIN?' <span class="tag">· pinned, click again to unpin</span>':''}</div>`+
      (peers.length?`<div class="who">${peers.map(([m,b])=>`<span><i style="display:inline-block;width:9px;height:9px;border-radius:50%;background:${labC(m)};margin-right:4px"></i>${esc(lbl(m))} <span class="tag">R${k-1} ${fmt(DATA[S.i].conds.forum.find(x=>x.model===m).st[k-1])} · ${b.n}×${b.priv?'':' (post only)'}</span></span>`).join('')}</div>`+
        [...new Set(cs.map(c=>c.quote+'|'+c.where))].slice(0,5).map(x=>{const [q,w]=x.split('|');return `<blockquote>${esc(q)} <span class="tag">· ${w==='private'?'private answer':'public post'}</span></blockquote>`}).join('')
       :'<div class="note" style="margin-top:4px">Named no peers this round.</div>');
  }
}
// ---- theory radars: one per model, its four rounds overlaid ----
const AX={'neutral':'Neutral','Act Utilitarianism':'Utilitarian','Kantian Deontology':'Kantian','Aristotelian Virtue Ethics':'Virtue','Scanlonian Contractualism':'Scanlonian','Gauthierian Contractarianism':'Gauthierian'};
function radars(){const d=DATA[S.i],host=$('radars');host.innerHTML='';
  if(d.rubrics.length<3){host.innerHTML=`<div class="empty">${d.name} has no theory rubrics in MoReBench (only the neutral rubric), so there are no theory profiles for it. The rubric map below still works.</div>`;$('rnote').textContent='';return}
  $('rnote').textContent='Score under each rubric (% of max). Dashed = round 0; lighter to darker = rounds 1–3.';
  const grid=document.createElement('div');grid.className='radars';host.appendChild(grid);
  const ax=d.rubrics,n=ax.length,cx=90,cy=96,R=56,pt=(i,v)=>{const t=-Math.PI/2+i*2*Math.PI/n;return [cx+Math.cos(t)*R*v/100,cy+Math.sin(t)*R*v/100]},poly=vs=>vs.map((v,i)=>pt(i,Math.max(0,Math.min(100,v??0))).join(',')).join(' ');
  d.conds[S.cond].slice().sort((x,y)=>ORDER.indexOf(short(x.model))-ORDER.indexOf(short(y.model))).forEach(a=>{const cell=document.createElement('div');grid.appendChild(cell);
    const s=document.createElementNS(NS,'svg');s.setAttribute('viewBox','-34 0 248 190');s.setAttribute('role','img');s.setAttribute('aria-label',`${short(a.model)} theory profile by round`);cell.appendChild(s);
    const col=labC(a.model);el(s,'text',{x:cx,y:12,'text-anchor':'middle','font-size':10.5,'font-weight':500,fill:C.ink},lbl(a.model));
    el(s,'text',{x:cx,y:186,'text-anchor':'middle','font-size':9,fill:C.mut},`stance ${a.st.map(v=>v==null?'–':fmt(v)).join(' → ')}`);
    [25,50,75,100].forEach(r=>el(s,'polygon',{points:poly(ax.map(()=>r)),fill:'none',stroke:C.faint}));
    ax.forEach((t,i)=>{const [x,y]=pt(i,100);el(s,'line',{x1:cx,y1:cy,x2:x,y2:y,stroke:C.faint});const [lx,ly]=pt(i,126);el(s,'text',{x:lx,y:ly+3,'text-anchor':Math.abs(lx-cx)<4?'middle':lx>cx?'start':'end','font-size':8,fill:C.mut},AX[t])});
    [0,1,2,3].forEach(k=>{const v=ax.map(t=>(a.sc[k]||{})[t]);if(v.every(x=>x==null))return;
      el(s,'polygon',{points:poly(v),fill:k===3?col:'none','fill-opacity':k===3?.15:0,stroke:k===0?C.mut:col,'stroke-width':k===3?2:1.2,'stroke-opacity':k===0?1:[0,.35,.6,1][k],'stroke-dasharray':k===0?'3 3':'none'})});
    ax.forEach((t,i)=>{const v=(a.sc[3]||{})[t];if(v==null)return;const [x,y]=pt(i,Math.max(0,Math.min(100,v)));const c=el(s,'circle',{cx:x,cy:y,r:2.4,fill:col});
      el(c,'title',{},`${AX[t]}: ${[0,1,2,3].map(k=>{const z=(a.sc[k]||{})[t];return 'R'+k+' '+(z==null?'–':Math.round(z))}).join(' · ')}`)});
  });
}
// ---- maps: MCA of rubric criteria, PCA of theory scores ----
function mapFig(key){const d=DATA[S.i],svg=$(key),info=d[key];svg.innerHTML='';
  if(key==='pca')$('pcabox').style.display=info?'':'none';
  if(!info){return null}
  const all=['forum','control'].flatMap(c=>d.conds[c].flatMap(a=>(a[key]||[]).filter(Boolean)));
  const xs=all.map(p=>p[0]),ys=all.map(p=>p[1]),pad=.08,xr=[Math.min(...xs),Math.max(...xs)],yr=[Math.min(...ys),Math.max(...ys)],dx=(xr[1]-xr[0])*pad||1,dy=(yr[1]-yr[0])*pad||1;
  const W=380,H=330,L=16,R=W-12,T=12,B=H-30,sx=x=>L+(x-xr[0]+dx)/(xr[1]-xr[0]+2*dx)*(R-L),sy=y=>B-(y-yr[0]+dy)/(yr[1]-yr[0]+2*dy)*(B-T);
  svg.setAttribute('viewBox',`0 0 ${W} ${H}`);svg.setAttribute('role','img');svg.setAttribute('aria-label',`${d.name} ${key.toUpperCase()} map`);
  el(svg,'rect',{x:L,y:T,width:R-L,height:B-T,fill:'none',stroke:C.rule});
  if(xr[0]<0&&xr[1]>0)el(svg,'line',{x1:sx(0),x2:sx(0),y1:T,y2:B,stroke:C.rule,'stroke-dasharray':'3 3'});
  if(yr[0]<0&&yr[1]>0)el(svg,'line',{x1:L,x2:R,y1:sy(0),y2:sy(0),stroke:C.rule,'stroke-dasharray':'3 3'});
  el(svg,'text',{x:R,y:B+14,'text-anchor':'end','font-size':10,fill:C.mut},`dim 1 (${info.pct[0]}%) · right ≈ option B`);
  el(svg,'text',{x:L,y:B+14,'font-size':10.5,'font-weight':500,fill:C.ink},key==='mca'?'Rubric map (MCA)':'Theory map (PCA)');
  el(svg,'text',{x:L+4,y:T+11,'font-size':10,fill:C.mut},`dim 2 (${info.pct[1]}%)`);
  all.forEach(p=>el(svg,'circle',{cx:sx(p[0]),cy:sy(p[1]),r:2.2,fill:C.mut,'fill-opacity':.22}));
  if(key==='pca'){const mx=Math.max(...info.load.map(l=>Math.hypot(l[1],l[2]))),sc=Math.min(R-L,B-T)*.32/mx,ox=sx(0),oy=sy(0);
    info.load.forEach(([t,lx,ly])=>{const x=ox+lx*sc,y=oy-ly*sc;el(svg,'line',{x1:ox,y1:oy,x2:x,y2:y,stroke:C.mut,'stroke-width':1.2,'stroke-opacity':.7});
      el(svg,'text',{x:x+(lx>=0?3:-3),y:y+(ly>=0?-3:9),'text-anchor':lx>=0?'start':'end','font-size':9,fill:C.mut},AX[t])})}
  const dots=d.conds[S.cond].map(a=>{const p0=a[key]&&a[key][0];if(p0)el(svg,'circle',{cx:sx(p0[0]),cy:sy(p0[1]),r:4.5,fill:'none',stroke:labC(a.model),'stroke-opacity':.35,'stroke-width':1.4});
    const c=el(svg,'circle',{r:5,fill:cheap(a.model)?C.bg:labC(a.model),stroke:labC(a.model),'stroke-width':2});return [c,el(c,'title',{},''),a]});
  $(key+'note').textContent=key==='mca'?`Which ${info.basis} criteria each answer meets (${info.criteria} criteria that vary; ${info.n} answers). Nearby dots argue similarly.`:`The five theory scores of each answer. Arrows show which theory pulls in which direction.`;
  return {key,sx,sy,dots};
}
render();
matchMedia('(prefers-color-scheme: dark)').addEventListener('change',draw);
new MutationObserver(draw).observe(document.documentElement,{attributes:true,attributeFilter:['data-theme']});
})();
</script>
"""

if __name__ == "__main__":
    main()
