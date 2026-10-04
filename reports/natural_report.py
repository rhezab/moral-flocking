"""Build reports/natural_report.html from reports/natural.json (run natural_data.py first).

usage: python reports/natural_report.py
"""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
SHORT = {  # short option labels for figures
    "Pandemic research": ("Track A (risky)", "Track B (reliable)"),
    "Covert medication": ("medicate covertly", "refuse"),
    "County services": ("addiction treatment", "child welfare"),
    "Community bank": ("small-business loans", "mortgages"),
}


def main():
    data = json.loads((HERE / "natural.json").read_text())
    for d in data:
        d["short"] = SHORT[d["name"]]
    html = TEMPLATE.replace("__DATA__", json.dumps(data).replace("</", "<\\/"))
    (HERE / "natural_report.html").write_text(html)
    print("wrote reports/natural_report.html")


TEMPLATE = r"""<title>Four Dilemmas, Twelve Models</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,500;12..96,700&family=Source+Serif+4:ital,opsz,wght@0,8..60,400;0,8..60,600;1,8..60,400&family=JetBrains+Mono:wght@400;600&display=swap">
<style>
/* Layout: a reading column (~46rem) with full-width figure panels; findings numbered because they are ordered by importance. */
:root{
  --bg:#f6f7f9; --surface:#ffffff; --ink:#1b2129; --muted:#5d6672; --rule:#dde1e7; --faint:#eef0f4;
  --accent:#3a55c4; --a:#2f6e9e; --b:#b5562b; --ctl:#8a919b;
  --l0:#D97757; --l1:#10A37F; --l2:#1d1d1b; --l3:#C2185B; --l4:#2F6FE4; --l5:#8A6D00;
  --display:"Bricolage Grotesque",ui-sans-serif,system-ui,sans-serif;
  --body:"Source Serif 4",Georgia,"Times New Roman",serif;
  --mono:"JetBrains Mono",ui-monospace,SFMono-Regular,Menlo,monospace;
}
@media (prefers-color-scheme: dark){:root:not([data-theme="light"]){
  --bg:#12151a; --surface:#1a1f26; --ink:#e7eaef; --muted:#9aa3ae; --rule:#2c333d; --faint:#20262f;
  --accent:#8ea2ff; --a:#6aa7d6; --b:#e08a5f; --ctl:#7b838d;
  --l0:#D27350; --l1:#20AE80; --l2:#ecebe6; --l3:#A82E63; --l4:#4F80EC; --l5:#7F6F10; color-scheme:dark}}
:root[data-theme="dark"]{
  --bg:#12151a; --surface:#1a1f26; --ink:#e7eaef; --muted:#9aa3ae; --rule:#2c333d; --faint:#20262f;
  --accent:#8ea2ff; --a:#6aa7d6; --b:#e08a5f; --ctl:#7b838d;
  --l0:#D27350; --l1:#20AE80; --l2:#ecebe6; --l3:#A82E63; --l4:#4F80EC; --l5:#7F6F10; color-scheme:dark}
*{box-sizing:border-box}
body{background:var(--bg);color:var(--ink);font:17px/1.6 var(--body);padding-inline:16px;padding-block:32px 72px}
main{max-width:46rem;margin:0 auto;display:flex;flex-direction:column;gap:12px}
h1,h2,h3{font-family:var(--display);text-wrap:balance;line-height:1.2;margin:0}
h1{font-size:clamp(1.9rem,4.5vw,2.6rem);font-weight:700;letter-spacing:-.01em}
h2{font-size:1.32rem;font-weight:700;margin-top:30px;display:flex;gap:.6rem;align-items:baseline}
h2 .n{font-family:var(--mono);font-size:.85rem;color:var(--accent);font-weight:600}
p,ul,ol{margin:0}
ul,ol{padding-left:1.25rem;display:flex;flex-direction:column;gap:6px}
.eyebrow{font-family:var(--mono);font-size:.75rem;letter-spacing:.08em;text-transform:uppercase;color:var(--muted)}
.meta{color:var(--muted);font-size:.92rem}
.lede{font-size:1.1rem}
.key{background:var(--surface);border:1px solid var(--rule);border-radius:10px;padding:14px 18px;display:flex;flex-direction:column;gap:8px;font-size:.95rem}
.key strong{font-family:var(--display);font-weight:500}
figure{margin:6px 0;background:var(--surface);border:1px solid var(--rule);border-radius:10px;padding:12px 14px;display:flex;flex-direction:column;gap:6px;min-width:0}
figcaption{font-size:.85rem;color:var(--muted)}
svg{width:100%;height:auto;display:block}
svg text{font-family:var(--mono)}
.grid2{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:10px}
@media (max-width:640px){.grid2{grid-template-columns:minmax(0,1fr)}}
.legend{display:flex;flex-wrap:wrap;gap:6px 16px;font-family:var(--mono);font-size:.72rem;color:var(--muted);align-items:center}
.legend i{display:inline-block;vertical-align:middle;margin-right:5px}
.tbl{overflow-x:auto;min-width:0}
table{border-collapse:collapse;width:100%;font-size:.86rem;font-variant-numeric:tabular-nums}
th,td{padding:5px 8px;border-bottom:1px solid var(--rule);text-align:left}
th{font-family:var(--mono);font-weight:600;font-size:.7rem;letter-spacing:.04em;text-transform:uppercase;color:var(--muted)}
td.num,th.num{text-align:right;font-family:var(--mono)}
.neg{color:var(--a)} .pos{color:var(--b)}
code{font-family:var(--mono);font-size:.85em;background:var(--faint);padding:0 4px;border-radius:4px}
hr{border:0;border-top:1px solid var(--rule);margin:24px 0 4px}
footer{color:var(--muted);font-size:.85rem;display:flex;flex-direction:column;gap:8px}
.dil{display:flex;flex-direction:column;gap:10px;padding-top:8px}
.dil h3{font-size:1.18rem;font-weight:700;margin-top:18px}
.dtext{background:var(--surface);border:1px solid var(--rule);border-radius:10px;padding:14px 18px;font-size:.95rem;line-height:1.6;white-space:pre-wrap}
.dtext .q{display:block;margin-top:10px;font-weight:600}
.opts{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:8px}
@media (max-width:640px){.opts{grid-template-columns:minmax(0,1fr)}}
.opt{border:1px solid var(--rule);border-radius:10px;padding:10px 14px;background:var(--surface);display:flex;flex-direction:column;gap:2px;font-size:.93rem}
.opt b{font-family:var(--mono);font-size:.75rem;letter-spacing:.04em}
.opt.A{border-left:4px solid var(--a)} .opt.B{border-left:4px solid var(--b)}
.seg{display:inline-flex;border:1px solid var(--rule);border-radius:99px;overflow:hidden;font-family:var(--mono);font-size:.75rem}
.seg button{font:inherit;border:0;background:var(--surface);color:var(--muted);padding:4px 12px;cursor:pointer}
.seg button.on{background:var(--accent);color:var(--surface)}
.seg button:focus-visible,.play:focus-visible{outline:2px solid var(--accent);outline-offset:2px}
.mv{display:flex;gap:10px;align-items:center}
.play{font:600 .8rem var(--mono);border:1px solid var(--rule);background:var(--surface);color:var(--ink);border-radius:8px;padding:5px 12px;cursor:pointer;min-width:84px}
.mv input[type=range]{flex:1;accent-color:var(--accent)}
.mv .rl{font-family:var(--mono);font-size:.75rem;color:var(--muted);min-width:96px;text-align:right}
.scroll{overflow-x:auto;min-width:0}.scroll svg{min-width:620px}
</style>

<main>
  <header style="display:flex;flex-direction:column;gap:10px">
    <div class="eyebrow">Swarmchasing · natural runs · 4 October 2026</div>
    <h1>Four Dilemmas, Twelve Models</h1>
    <p class="meta">How twelve language models change their minds on moral dilemmas when they discuss them in a shared forum, compared with reflecting alone.</p>
    <p class="lede">Discussion moves models about twice as far as reflection does. Divided groups converge, but not always toward the side that started in the majority. Groups that start out unanimous soften rather than harden. And after discussion, private answers score lower on the MoReBench rubrics.</p>
  </header>

  <div class="key">
    <strong>Setup</strong>
    <p><b>Models:</b> twelve models, two from each of six labs (Anthropic, OpenAI, xAI, Alibaba, DeepSeek, Zhipu).</p>
    <p><b>Round 0:</b> each model answers alone; this is its first round-0 sample. Two conditions then run for three more rounds.</p>
    <ul>
      <li><b>Control:</b> each model re-reads only its own earlier answers.</li>
      <li><b>Forum:</b> each round, all twelve post publicly at the same time, under anonymous “Agent N” labels and seeing the same forum state. Each then writes a private answer that can see the whole forum.</li>
    </ul>
    <p><b>Measures:</b> private answers are stance-coded three times by gpt-6.1-sol, from −5 (option A) to +5 (option B), and scored against MoReBench’s rubrics. One run per dilemma.</p>
  </div>

  <section>
    <h2><span class="n">00</span>The four dilemmas</h2>
    <p>Each dilemma below comes with its two options, the stance of every model in every round, and a movie of the same data. The toggle switches between the forum, where models discussed, and the control, where each model reflected alone.</p>
    <div id="dilemmas"></div>
  </section>

  <section>
    <h2><span class="n">01</span>The starting landscape</h2>
    <p>The four dilemmas were picked from a round-0 screen. Two split the models; two are unanimous. These are the starting views each group carried into discussion.</p>
    <figure><svg id="f1"></svg><div class="legend" id="lab-legend"></div>
      <figcaption>Each dot is one model’s round-0 stance (filled = higher tier, hollow = cheaper tier). Rows sorted by spread.</figcaption></figure>
  </section>

  <section>
    <h2><span class="n">02</span>Discussion moves models further than reflection</h2>
    <p>Averaged over models, the forum shifts each one <b>2.6 points</b> (−5 to +5 scale) by round 3, against <b>1.2</b> for control. The forum moves further in all four dilemmas. In every case the forum also narrows the spread of views more than control does.</p>
    <figure><div class="grid2" id="f2"></div>
      <div class="legend"><span><i style="width:18px;height:3px;background:var(--accent)"></i>forum (private)</span><span><i style="width:18px;height:3px;background:var(--ctl)"></i>control</span><span><i style="width:18px;height:0;border-top:2px dashed var(--accent)"></i>forum public posts</span><span><i style="width:18px;height:10px;background:var(--accent);opacity:.15"></i>±1 SD</span></div>
      <figcaption>Mean stance by round. Public posts are written between private rounds, so they sit halfway between them.</figcaption></figure>
  </section>

  <section>
    <h2><span class="n">03</span>Divided groups converge, but not always to the majority</h2>
    <p><b>Pandemic:</b> the A-side majority won outright, going from 8 : 4 to 12 : 0. Three of the four B-side models crossed in the first round.</p>
    <p><b>Covert medication:</b> the group started at an exact 6 : 6 and ended 1 : 10 for <i>refusing</i>. That is the opposite of control, which drifted slightly toward A. Firm A-holders crossed: grok-4.3 went from −5 to +2 and glm-5.3-flash from −4 to +3. Only qwen3.8-max-prime stayed on A.</p>
    <figure><div class="grid2" id="f3a"></div>
      <div class="legend" id="f3-legend"></div>
      <figcaption>Each row is one model. The hollow dot is its round-0 stance, the arrow runs to its round-3 stance in the forum, and the grey tick marks its round-3 stance in control.</figcaption></figure>
  </section>

  <section>
    <h2><span class="n">04</span>Unanimous groups soften instead of hardening</h2>
    <p>Group-polarization research predicts that like-minded groups grow more extreme as they talk. Here they did the reverse.</p>
    <ul>
      <li><b>County services:</b> the forum moderated from −4.5 to −2.4, while control only reached −3.3.</li>
      <li><b>Community bank:</b> the forum moderated from +4.3 to +2.4, while control stayed at +3.7.</li>
    </ul>
    <p>Nobody crossed sides; models added caveats and conditions. Public posts were milder than the private answers in both, ending at −1.2 and +1.8.</p>
    <figure><div class="grid2" id="f3b"></div>
      <figcaption>Same encoding as above.</figcaption></figure>
  </section>

  <section>
    <h2><span class="n">05</span>After discussion, answers score lower on the rubrics</h2>
    <p>In every dilemma, round-3 forum answers meet fewer rubric criteria than round-0 answers did, while control stays flat. The drop is largest where the group moved most: covert medication fell from 64 to 53 on the neutral rubric. Answers written after discussion seem to cover less of the dilemma, focusing on whatever the forum argued about. The same pattern showed up earlier as rubric checklists collapsing in the smart-home run.</p>
    <figure><svg id="f4"></svg>
      <figcaption>Mean rubric score (% of maximum) over the twelve models. Neutral rubric where available; community bank has only theory rubrics, so its row averages the five.</figcaption></figure>
    <figure><div class="grid2" id="f4r" style="grid-template-columns:repeat(auto-fit,minmax(200px,1fr))"></div>
      <div class="legend"><span><i style="width:18px;height:0;border-top:2px dashed var(--muted)"></i>round 0</span><span><i style="width:18px;height:3px;background:var(--ctl)"></i>control, round 3</span><span><i style="width:18px;height:3px;background:var(--accent)"></i>forum, round 3</span></div>
      <figcaption>Theory profiles (% of maximum under each rubric). Covert medication has only the neutral rubric, so it has no radar.</figcaption></figure>
  </section>

  <section>
    <h2><span class="n">06</span>Who gets named</h2>
    <p>Agents name each other often, 115–149 times per forum, but the most-named model changes with the dilemma. Opus dominates county services; glm-5.3-flash leads in covert medication and the bank; qwen3.8-max-prime, the loudest B-holder, leads in pandemic. Self-mentions, where an agent cites its own post as if a peer wrote it, fell to 3–4 per forum now that agents are told their own label, down from about 14 in the smart-home run.</p>
    <figure><div class="grid2" id="f5"></div>
      <figcaption>Times each model was named by others in posts or private answers (top six per forum).</figcaption></figure>
  </section>

  <section>
    <h2><span class="n">07</span>Who moved toward whom</h2>
    <p>For the transitions where agents crossed sides, the table counts the arguments the movers newly adopted, split by which side already held them. The counts are divided by how many peers sat on each side. The tilt toward the destination side is modest, so read it as a trace, not a causal estimate.</p>
    <div class="tbl" id="f6"></div>
  </section>

  <hr>
  <footer>
    <p><b>Caveats.</b></p>
    <ul>
      <li>One run per dilemma.</li>
      <li>One stance coder.</li>
      <li>Rubric scores use one judge model.</li>
      <li>“Adopted arguments” only means a criterion first appears in the mover’s answer and a peer had met it in the previous round; it is not proof the peer caused it.</li>
      <li>Community bank’s natural run comes from the planted-agent batch; its plant forum isn’t used here.</li>
    </ul>
    <p><b>Still running:</b> planted-agent forums (three Sonnet persuaders) and skewed populations (12 extra copies of models firmly on one side) for covert medication and pandemic.</p>
    <p>Data: <code>experiments/runs/discussion*.jsonl</code>; figures built by <code>reports/natural_report.py</code>.</p>
  </footer>
</main>

<script>
(function(){
const DATA=__DATA__;
const ORDER=['claude-opus-5.5','claude-haiku-4.5','gpt-6.1-sol','gpt-6-luna','grok-4.7','grok-4.3','qwen3.8-max-prime','qwen3.8-flash','deepseek-v4-pro-0813','deepseek-v4.1-flash','glm-5.3-prime','glm-5.3-flash'];
const LABS=['anthropic','openai','x-ai','qwen','deepseek','z-ai'],LABNAME=['Anthropic','OpenAI','xAI','Alibaba','DeepSeek','Zhipu'];
const NS='http://www.w3.org/2000/svg',short=m=>m.split('/').pop(),cheap=m=>ORDER.indexOf(short(m))%2===1;
const mean=a=>a.reduce((x,y)=>x+y,0)/a.length,sd=a=>{const m=mean(a);return Math.sqrt(mean(a.map(x=>(x-m)**2)))},fmt=v=>(v>0?'+':'')+(Math.round(v*10)/10);
let C;const css=()=>{const s=getComputedStyle(document.documentElement),g=n=>s.getPropertyValue(n).trim();C={ink:g('--ink'),mut:g('--muted'),rule:g('--rule'),faint:g('--faint'),acc:g('--accent'),a:g('--a'),b:g('--b'),ctl:g('--ctl'),bg:g('--surface'),lab:[0,1,2,3,4,5].map(i=>g('--l'+i))}};
const labC=m=>C.lab[LABS.indexOf(m.split('/')[0])];
function svgIn(host,w,h,label){const s=document.createElementNS(NS,'svg');s.setAttribute('viewBox',`0 0 ${w} ${h}`);s.setAttribute('role','img');s.setAttribute('aria-label',label);host.appendChild(s);return s}
function el(p,t,a,txt){const e=document.createElementNS(NS,t);for(const k in a)e.setAttribute(k,a[k]);if(txt!=null)e.textContent=txt;p.appendChild(e);return e}
function tip(e,t){el(e,'title',{},t)}
const vals=(d,c,k)=>d.conds[c].map(a=>a.st[k]).filter(v=>v!=null);

function f1(){const s=document.getElementById('f1');s.innerHTML='';const rows=DATA.slice().sort((x,y)=>sd(vals(y,'forum',0))-sd(vals(x,'forum',0)));
  const W=760,L=200,R=W-20,rh=64,T=16,H=T+rows.length*rh+30,sx=v=>L+(v+5)/10*(R-L);s.setAttribute('viewBox',`0 0 ${W} ${H}`);s.setAttribute('role','img');s.setAttribute('aria-label','Round-0 stances by dilemma');
  for(let v=-5;v<=5;v+=5){el(s,'line',{x1:sx(v),x2:sx(v),y1:T,y2:H-28,stroke:C.rule,'stroke-dasharray':v===0?'4 3':'none'});el(s,'text',{x:sx(v),y:H-12,'text-anchor':'middle','font-size':11,fill:C.mut},fmt(v))}
  rows.forEach((d,i)=>{const y=T+i*rh+rh/2,v=vals(d,'forum',0);
    el(s,'text',{x:L-14,y:y-6,'text-anchor':'end','font-size':13,'font-weight':600,fill:C.ink},d.name);
    el(s,'text',{x:L-14,y:y+10,'text-anchor':'end','font-size':10.5,fill:C.mut},`A ${v.filter(x=>x<0).length} : ${v.filter(x=>x>0).length} B · SD ${sd(v).toFixed(1)}`);
    el(s,'text',{x:L+2,y:y-rh/2+12,'font-size':10,fill:C.a},'← '+d.short[0]);el(s,'text',{x:R-2,y:y-rh/2+12,'text-anchor':'end','font-size':10,fill:C.b},d.short[1]+' →');
    const grp={};d.conds.forum.forEach(a=>{const k=Math.round(a.st[0]);(grp[k]=grp[k]||[]).push(a)});
    Object.entries(grp).forEach(([k,as])=>as.forEach((a,j)=>{const col=Math.floor(j/4),r=j%4,n=Math.min(4,as.length-col*4),dir=+k>=0?-1:1;
      const c=el(s,'circle',{cx:sx(a.st[0])+dir*col*11,cy:y+6+(r-(n-1)/2)*9,r:4.5,fill:cheap(a.model)?C.bg:labC(a.model),stroke:labC(a.model),'stroke-width':2});tip(c,`${short(a.model)}: ${fmt(a.st[0])}`)}));
  });
  document.getElementById('lab-legend').innerHTML=LABS.map((l,i)=>`<span><i style="width:10px;height:10px;border-radius:50%;background:${C.lab[i]}"></i>${LABNAME[i]}</span>`).join('');
}
function f2(){const host=document.getElementById('f2');host.innerHTML='';
  DATA.forEach(d=>{const cell=document.createElement('div');host.appendChild(cell);const W=360,H=230,L=40,R=W-14,T=26,B=H-30,sx=k=>L+k/3*(R-L),sy=v=>T+(5-v)/10*(B-T);
    const s=svgIn(cell,W,H,d.name+' mean stance by round');el(s,'text',{x:L,y:16,'font-size':12.5,'font-weight':600,fill:C.ink},d.name);
    [-5,0,5].forEach(v=>{el(s,'line',{x1:L,x2:R,y1:sy(v),y2:sy(v),stroke:C.rule,'stroke-dasharray':v===0?'4 3':'none'});el(s,'text',{x:L-6,y:sy(v)+4,'text-anchor':'end','font-size':10,fill:C.mut},v===5?'+5 B':v===-5?'−5 A':'0')});
    [0,1,2,3].forEach(k=>el(s,'text',{x:sx(k),y:B+18,'text-anchor':'middle','font-size':10,fill:C.mut},'R'+k));
    [['control',C.ctl],['forum',C.acc]].forEach(([c,col])=>{const m=[0,1,2,3].map(k=>mean(vals(d,c,k))),sdv=[0,1,2,3].map(k=>sd(vals(d,c,k)));
      el(s,'polygon',{points:m.map((v,k)=>`${sx(k)},${sy(Math.min(5,v+sdv[k]))}`).concat(m.map((v,k)=>`${sx(k)},${sy(Math.max(-5,v-sdv[k]))}`).reverse()).join(' '),fill:col,'fill-opacity':c==='forum'?.14:.07});
      el(s,'polyline',{points:m.map((v,k)=>`${sx(k)},${sy(v)}`).join(' '),fill:'none',stroke:col,'stroke-width':2.5});
      m.forEach((v,k)=>{const c2=el(s,'circle',{cx:sx(k),cy:sy(v),r:3.5,fill:col});tip(c2,`${c} R${k}: mean ${fmt(v)}, SD ${sdv[k].toFixed(1)}`)});
      el(s,'text',{x:R,y:sy(m[3])+(c==='forum'?(m[3]<m3o(d)?14:-8):(m[3]<m3o(d)?-8:14)),'text-anchor':'end','font-size':10,fill:col},`${fmt(m[3])}`)});
    const P=[1,2,3].map(k=>mean(d.posts.filter(p=>p.round===k).map(p=>p.st)));
    el(s,'polyline',{points:P.map((v,i)=>`${sx(i+.5)},${sy(v)}`).join(' '),fill:'none',stroke:C.acc,'stroke-width':1.5,'stroke-dasharray':'4 3'});
    P.forEach((v,i)=>{const r=el(s,'rect',{x:sx(i+.5)-3,y:sy(v)-3,width:6,height:6,fill:C.bg,stroke:C.acc,'stroke-width':1.5,transform:`rotate(45 ${sx(i+.5)} ${sy(v)})`});tip(r,`posts phase ${i+1}: mean ${fmt(v)}`)});
  });
  function m3o(d){return mean(vals(d,'control',3))}
}
function dumb(hostId,names){const host=document.getElementById(hostId);host.innerHTML='';
  DATA.filter(d=>names.includes(d.name)).forEach(d=>{const cell=document.createElement('div');host.appendChild(cell);
    const ctl=Object.fromEntries(d.conds.control.map(a=>[a.model,a.st[3]])),rows=d.conds.forum.slice().sort((x,y)=>x.st[0]-y.st[0]||ORDER.indexOf(short(x.model))-ORDER.indexOf(short(y.model)));
    const W=360,L=128,R=W-12,rh=19,T=26,H=T+rows.length*rh+40,sx=v=>L+(v+5)/10*(R-L);const s=svgIn(cell,W,H,d.name+' per-model shifts');
    el(s,'text',{x:4,y:15,'font-size':12.5,'font-weight':600,fill:C.ink},d.name);
    el(s,'text',{x:L,y:H-1,'font-size':9,fill:C.a},'← '+d.short[0]);el(s,'text',{x:R,y:H-1,'text-anchor':'end','font-size':9,fill:C.b},d.short[1]+' →');
    for(let v=-5;v<=5;v+=5){el(s,'line',{x1:sx(v),x2:sx(v),y1:T-4,y2:H-34,stroke:C.rule,'stroke-dasharray':v===0?'4 3':'none'});el(s,'text',{x:sx(v),y:H-22,'text-anchor':'middle','font-size':10,fill:C.mut},fmt(v))}
    rows.forEach((a,i)=>{const y=T+i*rh+6,c=labC(a.model),x0=sx(a.st[0]),x3=a.st[3]==null?null:sx(a.st[3]);
      el(s,'text',{x:L-8,y:y+3.5,'text-anchor':'end','font-size':9.5,fill:C.ink},short(a.model).replace('deepseek-','ds-').replace('-0813',''));
      if(ctl[a.model]!=null)el(s,'line',{x1:sx(ctl[a.model]),x2:sx(ctl[a.model]),y1:y-6,y2:y+6,stroke:C.ctl,'stroke-width':2});
      if(x3!=null&&Math.abs(x3-x0)>6){el(s,'line',{x1:x0+(x3>x0?5:-5),x2:x3+(x3>x0?-6:6),y1:y,y2:y,stroke:c,'stroke-width':1.6,'stroke-opacity':.7});
        el(s,'path',{d:`M${x3+(x3>x0?-6:6)},${y-3.5} L${x3+(x3>x0?-1:1)},${y} L${x3+(x3>x0?-6:6)},${y+3.5}`,fill:'none',stroke:c,'stroke-width':1.6,'stroke-opacity':.7})}
      const h=el(s,'circle',{cx:x0,cy:y,r:4,fill:C.bg,stroke:c,'stroke-width':1.8});tip(h,`${short(a.model)} R0 ${fmt(a.st[0])}`);
      if(x3!=null){const f=el(s,'circle',{cx:x3,cy:y,r:4.5,fill:c,stroke:C.bg,'stroke-width':1});tip(f,`${short(a.model)}: forum R3 ${fmt(a.st[3])} · control R3 ${ctl[a.model]==null?'–':fmt(ctl[a.model])}`)}
    });
  });
  document.getElementById('f3-legend').innerHTML=`<span><i style="width:9px;height:9px;border-radius:50%;border:2px solid ${C.ink}"></i>round 0</span><span><i style="width:10px;height:10px;border-radius:50%;background:${C.ink}"></i>forum, round 3</span><span><i style="width:2px;height:12px;background:${C.ctl}"></i>control, round 3</span><span>colour = lab</span>`;
}
const mainScore=(d,a,k)=>{const sc=a.sc[k]||{};if(d.rubrics.includes('neutral'))return sc.neutral;const v=d.rubrics.map(t=>sc[t]).filter(x=>x!=null);return v.length?mean(v):null};
function f4(){const s=document.getElementById('f4');s.innerHTML='';const W=760,L=200,R=W-30,rh=40,T=24,H=T+DATA.length*rh+26,lo=30,hi=70,sx=v=>L+(v-lo)/(hi-lo)*(R-L);
  s.setAttribute('viewBox',`0 0 ${W} ${H}`);s.setAttribute('role','img');s.setAttribute('aria-label','Rubric scores before and after');
  for(let v=lo;v<=hi;v+=10){el(s,'line',{x1:sx(v),x2:sx(v),y1:T-8,y2:H-22,stroke:C.rule});el(s,'text',{x:sx(v),y:H-8,'text-anchor':'middle','font-size':10,fill:C.mut},v)}
  DATA.forEach((d,i)=>{const y=T+i*rh+10,g=(c,k)=>mean(d.conds[c].map(a=>mainScore(d,a,k)).filter(v=>v!=null)),r0=g('forum',0),c3=g('control',3),f3=g('forum',3);
    el(s,'text',{x:L-14,y:y+4,'text-anchor':'end','font-size':12.5,'font-weight':600,fill:C.ink},d.name);
    el(s,'text',{x:L-14,y:y+18,'text-anchor':'end','font-size':9.5,fill:C.mut},d.rubrics.includes('neutral')?'neutral rubric':'mean of 5 theories');
    el(s,'line',{x1:sx(Math.min(r0,f3)),x2:sx(Math.max(r0,f3)),y1:y,y2:y,stroke:C.acc,'stroke-width':6,'stroke-opacity':.15,'stroke-linecap':'round'});
    [[r0,'round 0',C.mut,'hollow'],[c3,'control R3',C.ctl,'fill'],[f3,'forum R3',C.acc,'fill']].forEach(([v,n,col,st])=>{const c=el(s,'circle',{cx:sx(v),cy:y,r:6,fill:st==='hollow'?C.bg:col,stroke:col,'stroke-width':2});tip(c,`${n}: ${v.toFixed(1)}`)});
    el(s,'text',{x:sx(f3),y:y-11,'text-anchor':'middle','font-size':10,fill:C.acc},`${fmt(f3-r0)}`);
  });
  const lg=[[`round 0`,C.mut,1],[`control R3`,C.ctl,0],[`forum R3`,C.acc,0]];lg.forEach(([n,col,h],i)=>{el(s,'circle',{cx:L+i*120+6,cy:10,r:5,fill:h?C.bg:col,stroke:col,'stroke-width':2});el(s,'text',{x:L+i*120+16,y:14,'font-size':10.5,fill:C.mut},n)});
}
function f4r(){const host=document.getElementById('f4r');host.innerHTML='';
  const AX={'neutral':'Neutral','Act Utilitarianism':'Utilitarian','Kantian Deontology':'Kantian','Aristotelian Virtue Ethics':'Virtue','Scanlonian Contractualism':'Scanlonian','Gauthierian Contractarianism':'Gauthierian'};
  DATA.filter(d=>d.rubrics.length>=3).forEach(d=>{const cell=document.createElement('div');host.appendChild(cell);const ax=d.rubrics,n=ax.length,cx=120,cy=118,Rr=70;
    const s=svgIn(cell,240,232,d.name+' theory profile');s.setAttribute('viewBox','-46 0 332 232');el(s,'text',{x:cx,y:14,'text-anchor':'middle','font-size':12,'font-weight':600,fill:C.ink},d.name);
    const pt=(i,v)=>{const t=-Math.PI/2+i*2*Math.PI/n;return [cx+Math.cos(t)*Rr*v/100,cy+Math.sin(t)*Rr*v/100]},poly=vs=>vs.map((v,i)=>pt(i,Math.max(0,Math.min(100,v))).join(',')).join(' ');
    [25,50,75,100].forEach(r=>el(s,'polygon',{points:poly(ax.map(()=>r)),fill:'none',stroke:C.rule}));
    ax.forEach((t,i)=>{const [x,y]=pt(i,100);el(s,'line',{x1:cx,y1:cy,x2:x,y2:y,stroke:C.rule});const [lx,ly]=pt(i,124);el(s,'text',{x:lx,y:ly+3,'text-anchor':Math.abs(lx-cx)<4?'middle':lx>cx?'start':'end','font-size':9,fill:C.mut},AX[t])});
    const prof=(c,k)=>ax.map(t=>mean(d.conds[c].map(a=>(a.sc[k]||{})[t]).filter(v=>v!=null)));
    el(s,'polygon',{points:poly(prof('forum',0)),fill:'none',stroke:C.mut,'stroke-width':1.3,'stroke-dasharray':'4 3'});
    el(s,'polygon',{points:poly(prof('control',3)),fill:'none',stroke:C.ctl,'stroke-width':1.6});
    const f=prof('forum',3);el(s,'polygon',{points:poly(f),fill:C.acc,'fill-opacity':.15,stroke:C.acc,'stroke-width':2});
    f.forEach((v,i)=>{const [x,y]=pt(i,Math.max(0,v));const c=el(s,'circle',{cx:x,cy:y,r:2.6,fill:C.acc});tip(c,`${AX[ax[i]]}: forum R3 ${v.toFixed(0)} · R0 ${prof('forum',0)[i].toFixed(0)} · control R3 ${prof('control',3)[i].toFixed(0)}`)});
  });
}
function f5(){const host=document.getElementById('f5');host.innerHTML='';
  DATA.forEach(d=>{const cell=document.createElement('div');host.appendChild(cell);const items=Object.entries(d.mentions.named).sort((a,b)=>b[1]-a[1]).slice(0,6),mx=Math.max(...items.map(x=>x[1]));
    const W=360,L=132,R=W-34,rh=20,T=26,H=T+items.length*rh+8,s=svgIn(cell,W,H,d.name+' most named');
    el(s,'text',{x:4,y:15,'font-size':12.5,'font-weight':600,fill:C.ink},d.name);el(s,'text',{x:W-4,y:15,'text-anchor':'end','font-size':9.5,fill:C.mut},`${d.mentions.total} mentions · ${d.mentions.self} self`);
    items.forEach(([m,v],i)=>{const y=T+i*rh;el(s,'text',{x:L-8,y:y+12,'text-anchor':'end','font-size':10,fill:C.ink},short(m).replace('deepseek-','ds-').replace('-0813',''));
      const r=el(s,'rect',{x:L,y:y+3,width:Math.max(2,(R-L)*v/mx),height:12,rx:3,fill:labC(m)});tip(r,`${short(m)}: named ${v} times`);
      el(s,'text',{x:L+(R-L)*v/mx+5,y:y+13,'font-size':10,fill:C.mut},v)});
  });
}
function f6(){const rows=[];
  DATA.forEach(d=>d.sides.forEach(s=>{if(!s.crossed)return;const per=(o,k)=>s.avail[k]?((o[k]||0)/s.avail[k]).toFixed(2):'–';
    rows.push(`<tr><td>${d.name}</td><td>R${s.k-1}→R${s.k}</td><td>${s.side==='A'?'<span class="neg">A side</span>':'<span class="pos">B side</span>'}</td><td class="num">${s.n}</td><td class="num">${s.crossed}</td><td class="num">${fmt(s.delta)}</td><td class="num">${per(s.shared,'A')}</td><td class="num">${per(s.shared,'B')}</td><td class="num">${(s.cites.A||0)} / ${(s.cites.B||0)}</td></tr>`)}));
  document.getElementById('f6').innerHTML=`<table><thead><tr><th>Dilemma</th><th>Step</th><th>Movers were</th><th class="num">n</th><th class="num">crossed</th><th class="num">mean change</th><th class="num">args from A peers</th><th class="num">args from B peers</th><th class="num">named A / B</th></tr></thead><tbody>${rows.join('')}</tbody></table>
  <p style="font-size:.82rem;color:var(--muted);margin-top:6px">“Args from A peers” is the number of newly met rubric criteria already held by an A-side peer, per A-side peer available. “Named” counts mentions of peers in the movers’ private answers. Only steps where someone crossed sides are shown.</p>`}

const STATE={};const TIMERS={};
function dilemmas(){const host=document.getElementById('dilemmas');
  if(!host.dataset.built){host.dataset.built=1;
    host.innerHTML=DATA.map((d,i)=>{const q=d.dilemma.trim().split(/\n\s*\n/),last=q.pop();
      return `<div class="dil" id="dil${i}"><h3>${d.name}</h3>
      <div class="dtext">${esc(q.join('\n\n'))}<span class="q">${esc(last)}</span></div>
      <div class="opts"><div class="opt A"><b style="color:var(--a)">A · −5</b>${esc(d.options.option_a)}</div><div class="opt B"><b style="color:var(--b)">B · +5</b>${esc(d.options.option_b)}</div></div>
      <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:8px;margin-top:4px"><span class="eyebrow">Stance by round</span>
        <div class="seg" role="group" aria-label="Condition"><button type="button" data-c="forum" class="on">Forum</button><button type="button" data-c="control">Control</button></div></div>
      <figure><div class="scroll"><svg class="spec"></svg></div><figcaption>One row per model, one column per round. Bottom row: mean (dot) ± SD (bar). Hover a dot for the exact stance.</figcaption></figure>
      <figure><div class="mv"><button type="button" class="play">▶ Play</button><input type="range" min="0" max="3" step="0.01" value="0" aria-label="Round"><span class="rl">Round 0</span></div>
        <svg class="movie"></svg><figcaption>The same data as a movie: each model on the A–B line, gliding between rounds. A faint ring marks where it started.</figcaption></figure></div>`}).join('');
    DATA.forEach((d,i)=>{STATE[i]={cond:'forum',t:0};const box=document.getElementById('dil'+i);
      box.querySelectorAll('.seg button').forEach(b=>b.onclick=()=>{STATE[i].cond=b.dataset.c;box.querySelectorAll('.seg button').forEach(x=>x.classList.toggle('on',x===b));drawDil(i)});
      const sl=box.querySelector('input[type=range]'),btn=box.querySelector('.play');
      sl.oninput=()=>{stop(i);STATE[i].t=+sl.value;moviePos(i)};
      btn.onclick=()=>{if(TIMERS[i]){stop(i);return}let t=STATE[i].t>=3?0:Math.floor(STATE[i].t);const start=performance.now(),from=t,SEG=1400,HOLD=450;btn.textContent='❚❚ Pause';
        TIMERS[i]=setInterval(()=>{const el=performance.now()-start,per=SEG+HOLD,seg=Math.floor(el/per),f=Math.min(1,Math.max(0,(el-seg*per-HOLD)/SEG));
          STATE[i].t=Math.min(3,from+seg+f);moviePos(i);if(STATE[i].t>=3)stop(i)},30)};
    });
  }
  DATA.forEach((d,i)=>drawDil(i));
}
function stop(i){clearInterval(TIMERS[i]);TIMERS[i]=null;const b=document.querySelector(`#dil${i} .play`);if(b)b.textContent='▶ Play'}
const rowsOf=(d,c)=>d.conds[c].slice().sort((x,y)=>x.st[0]-y.st[0]||ORDER.indexOf(short(x.model))-ORDER.indexOf(short(y.model)));
const lbl=m=>short(m).replace('deepseek-','ds-').replace('-0813','');
function drawDil(i){const d=DATA[i],c=STATE[i].cond,box=document.getElementById('dil'+i),rows=rowsOf(d,c);
  // spectrum: columns per round
  const s=box.querySelector('.spec');s.innerHTML='';const W=760,L=124,gap=28,cw=(W-L-8-gap*3)/4,rh=19,T=26,n=rows.length+1,H=T+n*rh+28,x0=k=>L+k*(cw+gap),sx=(k,v)=>x0(k)+(v+5)/10*cw;
  s.setAttribute('viewBox',`0 0 ${W} ${H}`);s.setAttribute('role','img');s.setAttribute('aria-label',`${d.name}: stance of each model by round (${c})`);
  const yB=T+n*rh-6;
  [0,1,2,3].forEach(k=>{el(s,'text',{x:x0(k)+cw/2,y:13,'text-anchor':'middle','font-size':11.5,'font-weight':600,fill:C.ink},'Round '+k);
    el(s,'line',{x1:sx(k,0),x2:sx(k,0),y1:T-8,y2:yB,stroke:C.rule,'stroke-dasharray':'3 3'});
    [-5,0,5].forEach(v=>el(s,'text',{x:sx(k,v),y:yB+14,'text-anchor':'middle','font-size':9.5,fill:v<0?C.a:v>0?C.b:C.mut},v===-5?'A':v===5?'B':'0'))});
  rows.forEach((a,r)=>{const y=T+r*rh+4;el(s,'text',{x:L-8,y:y+3.5,'text-anchor':'end','font-size':9.5,fill:C.ink},lbl(a.model));
    [0,1,2,3].forEach(k=>{el(s,'line',{x1:x0(k),x2:x0(k)+cw,y1:y,y2:y,stroke:C.faint});const v=a.st[k];if(v==null)return;
      const dot=el(s,'circle',{cx:sx(k,v),cy:y,r:4.3,fill:cheap(a.model)?C.bg:labC(a.model),stroke:labC(a.model),'stroke-width':1.8});tip(dot,`${short(a.model)} · R${k}: ${fmt(v)}`)})});
  const y=T+rows.length*rh+4;el(s,'text',{x:L-8,y:y+3.5,'text-anchor':'end','font-size':9.5,'font-weight':600,fill:C.mut},'mean ± SD');
  [0,1,2,3].forEach(k=>{const v=rows.map(a=>a.st[k]).filter(x=>x!=null),m=mean(v),sdv=sd(v);
    el(s,'line',{x1:sx(k,Math.max(-5,m-sdv)),x2:sx(k,Math.min(5,m+sdv)),y1:y,y2:y,stroke:C.mut,'stroke-width':6,'stroke-opacity':.3,'stroke-linecap':'round'});
    const c2=el(s,'circle',{cx:sx(k,m),cy:y,r:3.5,fill:C.ink});tip(c2,`R${k}: mean ${fmt(m)}, SD ${sdv.toFixed(1)} · A ${v.filter(x=>x<0).length} : ${v.filter(x=>x>0).length} B`)});
  // movie
  const mv=box.querySelector('.movie');mv.innerHTML='';const MW=760,ML=124,MR=MW-16,mrh=21,MT=12,MH=MT+rows.length*mrh+40,msx=v=>ML+(v+5)/10*(MR-ML);
  mv.setAttribute('viewBox',`0 0 ${MW} ${MH}`);mv.setAttribute('role','img');mv.setAttribute('aria-label',`${d.name}: animated stances (${c})`);
  el(mv,'line',{x1:msx(0),x2:msx(0),y1:MT-6,y2:MH-34,stroke:C.rule,'stroke-dasharray':'3 3'});
  for(let v=-5;v<=5;v++){el(mv,'line',{x1:msx(v),x2:msx(v),y1:MH-36,y2:MH-31,stroke:C.mut});el(mv,'text',{x:msx(v),y:MH-19,'text-anchor':'middle','font-size':9.5,fill:C.mut},fmt(v))}
  el(mv,'text',{x:ML,y:MH-4,'font-size':10.5,'font-weight':600,fill:C.a},'← A · '+d.short[0]);el(mv,'text',{x:MR,y:MH-4,'text-anchor':'end','font-size':10.5,'font-weight':600,fill:C.b},d.short[1]+' · B →');
  const dots=[];rows.forEach((a,r)=>{const yy=MT+r*mrh+6;el(mv,'line',{x1:ML,x2:MR,y1:yy,y2:yy,stroke:C.faint});
    el(mv,'text',{x:ML-8,y:yy+3.5,'text-anchor':'end','font-size':10,fill:C.ink},lbl(a.model));
    if(a.st[0]!=null)el(mv,'circle',{cx:msx(a.st[0]),cy:yy,r:5,fill:'none',stroke:labC(a.model),'stroke-opacity':.3,'stroke-width':1.5});
    const dot=el(mv,'circle',{cy:yy,r:5.5,fill:cheap(a.model)?C.bg:labC(a.model),stroke:labC(a.model),'stroke-width':2});
    const t2=el(dot,'title',{},'');dots.push([dot,a,t2])});
  box._dots=dots;box._msx=msx;moviePos(i);
}
function moviePos(i){const box=document.getElementById('dil'+i);if(!box._dots)return;const t=STATE[i].t,k=Math.floor(t),f=t-k;
  box._dots.forEach(([dot,a,ti])=>{const p=a.st[k],q=a.st[Math.min(3,k+1)],v=p==null?q:(q==null||f===0?p:p+(q-p)*f);
    dot.style.display=v==null?'none':'';if(v!=null){dot.setAttribute('cx',box._msx(v));ti.textContent=`${short(a.model)}: ${fmt(v)}`}});
  box.querySelector('input[type=range]').value=t;box.querySelector('.rl').textContent=Number.isInteger(t)?`Round ${t}`:`Round ${k} → ${k+1}`;
}
const esc=x=>String(x).replace(/[&<>]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;'}[c]));
function draw(){css();dilemmas();f1();f2();dumb('f3a',['Pandemic research','Covert medication']);dumb('f3b',['County services','Community bank']);f4();f4r();f5();f6()}
draw();
matchMedia('(prefers-color-scheme: dark)').addEventListener('change',draw);
new MutationObserver(draw).observe(document.documentElement,{attributes:true,attributeFilter:['data-theme']});
})();
</script>
"""

if __name__ == "__main__":
    main()
