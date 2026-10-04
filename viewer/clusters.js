// Per-dilemma cluster figures from rubric checklists: a dendrogram and an MCA biplot.
// Input vectors may be fractional (share of judge runs marking a criterion as applying).

// Binary average-linkage clustering on L1 (Hamming for 0/1) distance. Identical vectors
// collapse into one leaf. A merge is "tied" when another equally close pair shares a member,
// i.e. the tie-break decided the structure.
function dendrogram(V) {
  const n = V[0].length, dist = (a, b) => a.reduce((s, x, i) => s + Math.abs(x - b[i]), 0);
  let cl = [];
  const seen = {};
  V.forEach((v, i) => {
    const k = v.join(',');
    if (seen[k]) seen[k].m.push(i); else cl.push(seen[k] = { m: [i], h: 0, kids: [] });
  });
  const avg = (A, B) => { let s = 0; for (const a of A.m) for (const b of B.m) s += dist(V[a], V[b]); return s / (A.m.length * B.m.length); };
  while (cl.length > 1) {
    let mn = Infinity, pairs = [];
    for (let i = 0; i < cl.length; i++) for (let j = i + 1; j < cl.length; j++) {
      const d = avg(cl[i], cl[j]);
      if (d < mn - 1e-9) { mn = d; pairs = [[i, j]]; } else if (Math.abs(d - mn) < 1e-9) pairs.push([i, j]);
    }
    const p = pairs[0];
    const rivals = pairs.slice(1).filter(q => q.includes(p[0]) || q.includes(p[1])).map(q => [cl[q[0]], cl[q[1]]]);
    const node = { m: cl[p[0]].m.concat(cl[p[1]].m), h: mn, kids: [cl[p[0]], cl[p[1]]], rivals };
    cl = cl.filter((_, k) => k !== p[0] && k !== p[1]);
    cl.push(node);
  }
  return cl[0];
}

// Symmetric eigendecomposition (Jacobi). Returns {values, vectors (columns)} sorted descending.
function eigSym(A) {
  const n = A.length, a = A.map(r => r.slice()), v = A.map((_, i) => A.map((_, j) => +(i === j)));
  for (let sweep = 0; sweep < 100; sweep++) {
    let off = 0;
    for (let i = 0; i < n; i++) for (let j = i + 1; j < n; j++) off += a[i][j] ** 2;
    if (off < 1e-20) break;
    for (let p = 0; p < n; p++) for (let q = p + 1; q < n; q++) {
      if (Math.abs(a[p][q]) < 1e-15) continue;
      const th = (a[q][q] - a[p][p]) / (2 * a[p][q]);
      const t = Math.sign(th || 1) / (Math.abs(th) + Math.sqrt(th * th + 1)), c = 1 / Math.sqrt(t * t + 1), s = t * c;
      for (let k = 0; k < n; k++) {
        const akp = a[k][p], akq = a[k][q];
        a[k][p] = c * akp - s * akq; a[k][q] = s * akp + c * akq;
      }
      for (let k = 0; k < n; k++) {
        const apk = a[p][k], aqk = a[q][k];
        a[p][k] = c * apk - s * aqk; a[q][k] = s * apk + c * aqk;
      }
      for (let k = 0; k < n; k++) {
        const vkp = v[k][p], vkq = v[k][q];
        v[k][p] = c * vkp - s * vkq; v[k][q] = s * vkp + c * vkq;
      }
    }
  }
  const idx = a.map((_, i) => i).sort((x, y) => a[y][y] - a[x][x]);
  return { values: idx.map(i => a[i][i]), vectors: v.map(r => idx.map(i => r[i])) };
}

// MCA via correspondence analysis of the (fuzzy) indicator matrix [p, 1-p] per varying criterion.
function mca(V, varying) {
  const n = V.length, Q = varying.length;
  const Z = V.map(v => varying.flatMap(i => [v[i], 1 - v[i]]));
  const tot = n * Q, r = Array(n).fill(1 / n), c = Z[0].map((_, j) => Z.reduce((s, z) => s + z[j], 0) / tot);
  const S = Z.map((z, i) => z.map((x, j) => c[j] > 0 ? (x / tot - r[i] * c[j]) / Math.sqrt(r[i] * c[j]) : 0));
  const SS = S.map(a => S.map(b => a.reduce((s, x, j) => s + x * b[j], 0)));
  const { values, vectors } = eigSym(SS);
  const dims = values.map((l, k) => [l, k]).filter(([l]) => l > 1e-12).slice(0, 2);
  const eig = values.filter(l => l > 1e-12), total = eig.reduce((a, b) => a + b, 0);
  const ben = eig.map(l => l > 1 / Q ? ((Q / (Q - 1)) * (l - 1 / Q)) ** 2 : 0), benTot = ben.reduce((a, b) => a + b, 0);
  // Row principal coordinates F = D_r^-1/2 U Sigma; column coordinates are row centroids / sqrt(eigenvalue).
  const F = V.map((_, i) => dims.map(([l, k]) => vectors[i][k] * Math.sqrt(l) / Math.sqrt(r[i])));
  const G = Z[0].map((_, j) => dims.map(([l], d) => {
    const w = Z.reduce((s, z) => s + z[j], 0);
    return w > 0 ? Z.reduce((s, z, i) => s + z[j] * F[i][d], 0) / w / Math.sqrt(l) : 0;
  }));
  return { F, G, pct: dims.map(([l]) => 100 * l / total), benPct: dims.map((_, d) => benTot ? 100 * ben[d] / benTot : 0) };
}

const SVGNS = 'http://www.w3.org/2000/svg';
function mk(svg, tag, attrs, text) {
  const e = document.createElementNS(SVGNS, tag);
  for (const k in attrs) e.setAttribute(k, attrs[k]);
  if (text != null) e.textContent = text;
  svg.appendChild(e);
  return e;
}
const r2 = v => Math.round(v * 100) / 100;
// Floating tooltip that follows the cursor (shared by all figures).
const floatTip = (() => {
  let d;
  return {
    show(e, t) {
      if (!d) {
        d = document.createElement('div');
        d.style.cssText = 'position:fixed;z-index:50;pointer-events:none;max-width:380px;background:var(--card);color:var(--fg);border:1px solid var(--line);border-radius:6px;padding:6px 9px;font-size:12px;line-height:1.4;box-shadow:0 2px 8px rgba(0,0,0,.25)';
        document.body.appendChild(d);
      }
      d.textContent = t; d.style.display = 'block';
      d.style.left = Math.min(e.clientX + 14, innerWidth - d.offsetWidth - 8) + 'px';
      d.style.top = Math.min(e.clientY + 14, innerHeight - d.offsetHeight - 8) + 'px';
    },
    hide() { if (d) d.style.display = 'none'; },
  };
})();
function hover(el, text) {
  el.addEventListener('mousemove', e => floatTip.show(e, typeof text === 'function' ? text() : text));
  el.addEventListener('mouseleave', () => floatTip.hide());
}
const trunc = (s, n) => s.length > n ? s.slice(0, n - 1) + '…' : s;
function themeColors() {
  const cs = getComputedStyle(document.documentElement);
  return { on: cs.getPropertyValue('--acc').trim(), ink: cs.getPropertyValue('--fg').trim(), mut: cs.getPropertyValue('--mut').trim(), grid: cs.getPropertyValue('--line').trim(), bg: cs.getPropertyValue('--card').trim() };
}

// labels: one per vector; crit/weights: rubric; varying: indices of criteria that differ.
// limit: max heatmap rows; when capped, shows the most variable criteria (closest to an even split).
// The tree always uses every varying criterion.
function renderDendrogram(host, labels, V, crit, weights, varying, tip, limit = Infinity) {
  const T = themeColors(), root = dendrogram(V);
  const spread = ci => { const m = V.reduce((s, v) => s + v[ci], 0) / V.length; return m * (1 - m); };
  const rows = varying.slice().sort((a, b) => spread(b) - spread(a)).slice(0, limit).sort((a, b) => weights[b] - weights[a] || spread(b) - spread(a));
  const leaves = []; (function walk(n) { if (!n.kids.length) leaves.push(n); else n.kids.forEach(walk); })(root);
  const x0 = 260, cw = Math.max(18, Math.min(52, (670 - x0) / leaves.length));
  const leafText = n => n.m.map(i => labels[i]).join(' = ');
  const longest = Math.max(...leaves.map(n => leafText(n).length));
  const rotate = longest * 6.5 > cw;  // rotate whenever horizontal labels would collide
  const top = 30, dh = 120, y0 = top + dh + 8, ch = 26, yL = y0 + rows.length * ch + 12;
  const H = yL + (rotate ? longest * 5.6 : 16) + 8;
  const svg = mk(host, 'svg', { width: '100%', viewBox: `0 0 680 ${H}`, role: 'img', 'aria-label': 'Dendrogram of replies with checklist heatmap' });
  const hy = v => top + dh - (root.h ? v / root.h : 0) * dh;
  const lx = new Map(); leaves.forEach((n, k) => lx.set(n, x0 + k * cw + cw / 2));
  const name = n => n.m.map(i => labels[i]).join(' = ');
  const grp = n => n.kids.length ? `{${n.m.map(i => labels[i]).join(', ')}}` : name(n);
  (function draw(n) {
    if (lx.has(n)) return lx.get(n);
    const xs = n.kids.map(draw), y = hy(n.h), dash = n.rivals.length ? '4 3' : 'none';
    n.kids.forEach((k, i) => mk(svg, 'line', { x1: xs[i], x2: xs[i], y1: y, y2: hy(k.kids.length ? k.h : 0), stroke: T.mut, 'stroke-width': 1.5, 'stroke-dasharray': dash }));
    mk(svg, 'line', { x1: xs[0], x2: xs[1], y1: y, y2: y, stroke: T.mut, 'stroke-width': 1.5, 'stroke-dasharray': dash });
    const hit = mk(svg, 'rect', { x: Math.min(...xs) - 4, y: y - 8, width: Math.abs(xs[1] - xs[0]) + 8, height: 16, fill: 'transparent' });
    const msg = `Merge at ${r2(n.h)}: ${grp(n.kids[0])} + ${grp(n.kids[1])}. ` +
      (n.rivals.length ? `Tie-broken; equally close: ${n.rivals.map(p => grp(p[0]) + ' + ' + grp(p[1])).join('; ')}` : 'Unambiguous.');
    hit.onmouseenter = () => tip(msg); hover(hit, msg);
    if (cw >= 30) mk(svg, 'text', { x: (xs[0] + xs[1]) / 2, y: y - 5, 'text-anchor': 'middle', 'font-size': 11, fill: T.mut }, r2(n.h));
    return (xs[0] + xs[1]) / 2;
  })(root);
  mk(svg, 'text', { x: x0 - 10, y: top - 14, 'text-anchor': 'end', 'font-size': 11, fill: T.mut }, 'average distance');
  const step = Math.max(1, Math.ceil(root.h / 5));  // at most ~6 tick labels
  for (let v = 0; v <= root.h; v += step) mk(svg, 'text', { x: x0 - 10, y: hy(v) + 4, 'text-anchor': 'end', 'font-size': 11, fill: T.mut }, v);
  rows.forEach((ci, r) => {
    const band = mk(svg, 'rect', { x: 0, y: y0 + r * ch, width: x0 + leaves.length * cw, height: ch - 2, fill: 'transparent' });
    hover(band, `#${ci + 1} (${weights[ci] > 0 ? '+' : ''}${weights[ci]}): ${crit[ci]}`);
  });
  leaves.forEach((n, k) => {
    const x = x0 + k * cw + cw / 2, ls = n.m.map(i => labels[i]);
    if (rotate) mk(svg, 'text', { x: x - 3, y: yL, 'text-anchor': 'start', 'font-size': 11, fill: T.ink, transform: `rotate(55 ${x - 3} ${yL})` }, ls.join(' = '));
    else mk(svg, 'text', { x, y: yL + 4, 'text-anchor': 'middle', 'font-size': 11, fill: T.ink }, ls.join(' = '));
    rows.forEach((ci, r) => {
      const f = V[n.m[0]][ci];
      const cell = mk(svg, 'rect', { x: x - cw / 2 + 1, y: y0 + r * ch, width: cw - 2, height: ch - 2, rx: 3, fill: f > 0 ? T.on : 'none', 'fill-opacity': f || 1, stroke: f > 0 ? 'none' : T.grid });
      const msg = `${name(n)} · #${ci + 1} (${weights[ci] > 0 ? '+' : ''}${weights[ci]}): ${f === 1 ? 'applies' : f === 0 ? 'does not apply' : Math.round(f * 100) + '% of judge runs'}\n${crit[ci]}`;
      cell.onmouseenter = () => tip(msg); hover(cell, msg);
    });
  });
  rows.forEach((ci, r) => {
    const t = mk(svg, 'text', { x: x0 - 10, y: y0 + r * ch + ch / 2 + 3, 'text-anchor': 'end', 'font-size': 12, fill: T.ink }, `#${ci + 1} ${trunc(crit[ci], 30)} (${weights[ci] > 0 ? '+' : ''}${weights[ci]})`);
    t.style.pointerEvents = 'none';  // the row band underneath shows the full criterion
  });
}

// nShow: how many criterion points to draw, the ones with the most disagreement across replies.
function renderMCA(host, labels, V, crit, varying, tip, cat, nShow = 4) {
  const T = themeColors(), res = mca(V, varying);
  if (res.F[0].length < 2) { host.insertAdjacentHTML('beforeend', '<p class="note">MCA needs at least two dimensions of variation.</p>'); return; }
  const disagreeAll = q => { const ci = varying[q], m = V.reduce((s, v) => s + v[ci], 0) / V.length; return m * (1 - m); };
  const shown = varying.map((_, q) => q).sort((a, b) => disagreeAll(b) - disagreeAll(a)).slice(0, nShow);
  const pts = res.F.concat(shown.map(q => res.G[2 * q])), xs = pts.map(p => p[0]), ys = pts.map(p => p[1]);
  const pad = 0.15, mnx = Math.min(...xs) - pad, mxx = Math.max(...xs) + pad, mny = Math.min(...ys) - pad, mxy = Math.max(...ys) + pad;
  const L = 60, R = 620, Tp = 24, B = 400, W = 680, H = 450;
  const sx = v => L + (v - mnx) / (mxx - mnx) * (R - L), sy = v => B - (v - mny) / (mxy - mny) * (B - Tp);
  const svg = mk(host, 'svg', { width: '100%', viewBox: `0 0 ${W} ${H}`, role: 'img', 'aria-label': 'MCA biplot of replies and criteria' });
  mk(svg, 'rect', { x: L, y: Tp, width: R - L, height: B - Tp, fill: 'none', stroke: T.grid });
  if (mnx < 0 && mxx > 0) mk(svg, 'line', { x1: sx(0), x2: sx(0), y1: Tp, y2: B, stroke: T.grid });
  if (mny < 0 && mxy > 0) mk(svg, 'line', { x1: L, x2: R, y1: sy(0), y2: sy(0), stroke: T.grid });
  mk(svg, 'text', { x: (L + R) / 2, y: H - 22, 'text-anchor': 'middle', 'font-size': 12, fill: T.mut }, `Dim 1 · ${res.pct[0].toFixed(1)}% of inertia (${res.benPct[0].toFixed(1)}% Benzécri-adjusted)`);
  mk(svg, 'text', { x: 18, y: (Tp + B) / 2, 'text-anchor': 'middle', 'font-size': 12, fill: T.mut, transform: `rotate(-90 18 ${(Tp + B) / 2})` }, `Dim 2 · ${res.pct[1].toFixed(1)}% (${res.benPct[1].toFixed(1)}% adj.)`);
  mk(svg, 'text', { x: (L + R) / 2, y: H - 6, 'text-anchor': 'middle', 'font-size': 11, fill: T.mut }, 'Dots: replies. Diamonds: "criterion applies" centroids for the criteria with most disagreement.');
  // Greedy label placement: try the preferred spot, then nudge vertically until it clears placed labels.
  const placed = [];
  const place = (x, y, text, anchor, size) => {
    const w = text.length * size * 0.58, h = size + 2;
    const box = yy => { const x0 = anchor === 'end' ? x - w : anchor === 'middle' ? x - w / 2 : x; return [x0, yy - h + 3, x0 + w, yy + 3]; };
    const hit = b => placed.some(p => b[0] < p[2] && b[2] > p[0] && b[1] < p[3] && b[3] > p[1]);
    for (let k = 0; k < 14; k++) {
      const yy = y + (k % 2 ? 1 : -1) * Math.ceil(k / 2) * h;
      if (!hit(box(yy)) || k === 13) { placed.push(box(yy)); return yy; }
    }
  };
  // Show only the criteria replies disagree on most (share applying closest to 50%).
  const disagree = q => { const ci = varying[q], m = V.reduce((s, v) => s + v[ci], 0) / V.length; return m * (1 - m); };
  const far = varying.map((_, q) => q).sort((a, b) => disagree(b) - disagree(a)).slice(0, nShow);
  const groups = {};
  res.F.forEach((f, i) => { const k = f.map(v => v.toFixed(6)).join(); (groups[k] = groups[k] || []).push(i); });
  const dots = Object.values(groups).map(g => ({ g, x: sx(res.F[g[0]][0]), y: sy(res.F[g[0]][1]) }));
  dots.forEach(d => placed.push([d.x - 7, d.y - 7, d.x + 7, d.y + 7]));  // keep labels off the dots
  far.forEach(q => {
    const ci = varying[q], g = res.G[2 * q], x = sx(g[0]), y = sy(g[1]);
    mk(svg, 'rect', { x: x - 4, y: y - 4, width: 8, height: 8, transform: `rotate(45 ${x} ${y})`, fill: 'none', stroke: T.ink, 'stroke-width': 1.5 });
    const h = mk(svg, 'circle', { cx: x, cy: y, r: 9, fill: 'transparent' });
    h.onmouseenter = () => tip(`#${ci + 1} applies: "${crit[ci]}"`); hover(h, `#${ci + 1} applies: ${crit[ci]}`);
  });
  dots.forEach(({ g, x, y }) => {
    const label = g.map(i => labels[i]).join(' = '), i0 = g[0];
    const col = cat ? cat.color[i0] : T.on, hollow = cat && cat.hollow[i0];
    mk(svg, 'circle', { cx: x, cy: y, r: (g.length > 1 ? 8 : 6) - (hollow ? 1 : 0), fill: hollow ? T.bg : col, stroke: col, 'stroke-width': 2 });
    if (g.length > 1) mk(svg, 'text', { x, y: y + 3.5, 'text-anchor': 'middle', 'font-size': 9, 'font-weight': 700, fill: hollow ? col : T.bg }, g.length);
    if (!cat) {  // without a provider legend, fall back to text labels
      const right = x > 520, yy = place(right ? x - 10 : x + 10, y + 4, label, right ? 'end' : 'start', 12);
      mk(svg, 'text', { x: right ? x - 10 : x + 10, y: yy, 'text-anchor': right ? 'end' : 'start', 'font-size': 12, fill: T.ink }, label);
    }
    const h = mk(svg, 'circle', { cx: x, cy: y, r: 12, fill: 'transparent' });
    const msg = `${label}${g.length > 1 ? ' · identical checklists' : ''}`;
    h.onmouseenter = () => tip(msg); hover(h, msg);
  });
  if (cat) host.insertAdjacentHTML('afterbegin', legendHTML(cat, 'hover a dot for the model'));
  far.forEach(q => {
    const ci = varying[q], g = res.G[2 * q], x = sx(g[0]), y = sy(g[1]), right = x > 500, text = `#${ci + 1} ${trunc(crit[ci], 22)}`;
    const yy = place(right ? x - 8 : x + 8, y + 4, text, right ? 'end' : 'start', 11);
    mk(svg, 'text', { x: right ? x - 8 : x + 8, y: yy, 'text-anchor': right ? 'end' : 'start', 'font-size': 11, fill: T.mut }, text);
  });
}

// Entry point: replies' vectors from the selected judge. Skips replies without judgments.
function renderClusters(host, labels, V, crit, weights, cat) {
  host.innerHTML = '';
  const tipEl = document.createElement('div');
  tipEl.className = 'note';
  tipEl.textContent = 'Hover a merge, cell or point for details.';
  const tip = t => { tipEl.textContent = t; };
  const varying = crit.map((_, i) => i).filter(i => V.some(v => v[i] !== V[0][i]));
  if (V.length < 3 || varying.length < 2) {
    host.innerHTML = '<p class="note">Need at least 3 judged replies that differ on at least 2 criteria.</p>';
    return;
  }
  host.insertAdjacentHTML('beforeend', `<p class="note">${V.length} replies · ${varying.length} of ${crit.length} criteria vary (only these shown and used). Dashed merges were decided by a tie-break.</p>`);
  const CAP = 15;
  let expanded = false;
  const bar = document.createElement('div'); host.appendChild(bar);
  const d = document.createElement('div'); host.appendChild(d);
  const drawTree = () => {
    d.innerHTML = '';
    renderDendrogram(d, labels, V, crit, weights, varying, tip, expanded ? Infinity : CAP);
    bar.innerHTML = varying.length <= CAP ? '' : `<div class="note" style="display:flex;gap:10px;align-items:center;margin:4px 0">
      <span>${expanded ? `Showing all ${varying.length} varying criteria` : `Showing the ${CAP} most variable of ${varying.length} varying criteria (the tree uses all)`}</span>
      <button type="button">${expanded ? 'Show fewer' : `Show all ${varying.length}`}</button></div>`;
    const b = bar.querySelector('button'); if (b) b.onclick = () => { expanded = !expanded; drawTree(); };
  };
  drawTree();
  let nShow = Math.min(4, varying.length);
  const mbar = document.createElement('div'); host.appendChild(mbar);
  mbar.innerHTML = `<div class="note" style="display:flex;gap:8px;align-items:center;margin:14px 0 2px">MCA: show the
    <input type="number" min="0" max="${varying.length}" value="${nShow}" style="width:52px;font:inherit;color:inherit;background:var(--card);border:1px solid var(--line);border-radius:6px;padding:2px 6px">
    criteria with the most disagreement (of ${varying.length} varying)</div>`;
  const m = document.createElement('div'); host.appendChild(m);
  const drawMCA = () => { m.innerHTML = ''; renderMCA(m, labels, V, crit, varying, tip, cat, nShow); };
  mbar.querySelector('input').oninput = e => { nShow = Math.max(0, Math.min(varying.length, +e.target.value || 0)); drawMCA(); };
  drawMCA();
  host.appendChild(tipEl);
}

// Theory profile: one radar per reply, each axis a rubric's score as % of its maximum,
// over a dashed polygon for the average of all replies.
const RADAR_AXES = [['neutral', 'Neutral'], ['Act Utilitarianism', 'Utilitarian'], ['Kantian Deontology', 'Kantian'],
  ['Aristotelian Virtue Ethics', 'Virtue'], ['Scanlonian Contractualism', 'Scanlonian'], ['Gauthierian Contractarianism', 'Gauthierian']];

// scores: one object per reply, {rubric name: percent or undefined}; stances: per reply, number or null.
// layout (optional): {cols: [header, ...], rows: [{name, idx: [reply index or null per column]}]}
function renderRadar(host, labels, scores, stances, opts, layout) {
  host.innerHTML = '';
  const T = themeColors();
  const axes = RADAR_AXES.filter(([k]) => scores.some(s => s[k] != null));
  if (axes.length < 3) { host.innerHTML = '<p class="note">Theory profile needs at least 3 rubrics judged (only the 30 MoReBench theory dilemmas have theory rubrics).</p>'; return; }
  const avg = axes.map(([k]) => { const v = scores.map(s => s[k]).filter(x => x != null); return v.reduce((a, b) => a + b, 0) / v.length; });
  const tipEl = document.createElement('div'); tipEl.className = 'note'; tipEl.textContent = 'Hover a vertex for the exact score.';
  host.insertAdjacentHTML('beforeend', `<p class="note">Score under each rubric as % of its maximum. Dashed: average of all ${scores.length} replies. Rings at 25/50/75/100%.</p>`);
  const grid = document.createElement('div');
  host.appendChild(grid);
  // Cells in display order: either a provider x tier table, or a plain auto-fill grid.
  let cells = scores.map((_, i) => ({ i, el: grid }));
  if (layout) {
    const nc = layout.cols.length, used = new Set(layout.rows.flatMap(r => r.idx).filter(x => x != null));
    const rows = layout.rows.concat(scores.some((_, i) => !used.has(i)) ? [{ name: 'Other', idx: scores.map((_, i) => i).filter(i => !used.has(i)) }] : []);
    grid.style.cssText = `display:grid;grid-template-columns:110px repeat(${Math.max(nc, ...rows.map(r => r.idx.length))},minmax(0,260px));gap:2px 8px;align-items:center`;
    grid.insertAdjacentHTML('beforeend', '<div></div>' + layout.cols.map(c => `<div class="note" style="text-align:center;font-weight:600">${c}</div>`).join(''));
    cells = [];
    rows.forEach(r => {
      grid.insertAdjacentHTML('beforeend', `<div style="font-weight:600;font-size:13px">${r.name}</div>`);
      r.idx.forEach(i => { const c = document.createElement('div'); grid.appendChild(c); if (i != null) cells.push({ i, el: c }); });
    });
  } else grid.style.cssText = 'display:grid;grid-template-columns:repeat(auto-fill,minmax(230px,1fr));gap:4px';
  host.appendChild(tipEl);
  const n = axes.length, cx = 110, cy = 112, R = 70;
  const pt = (k, v) => { const a = -Math.PI / 2 + k * 2 * Math.PI / n; return [cx + Math.cos(a) * R * v / 100, cy + Math.sin(a) * R * v / 100]; };
  const poly = vals => vals.map((v, k) => pt(k, Math.max(0, v ?? 0)).join(',')).join(' ');
  cells.forEach(({ i, el }) => {
    const s = scores[i];
    const svg = mk(el, 'svg', { viewBox: '-45 0 310 222', width: '100%', role: 'img', 'aria-label': `${labels[i]} theory profile` });
    [25, 50, 75, 100].forEach(r => mk(svg, 'polygon', { points: poly(axes.map(() => r)), fill: 'none', stroke: T.grid }));
    axes.forEach(([, short], k) => {
      const p = pt(k, 100), q = pt(k, 118);
      mk(svg, 'line', { x1: cx, y1: cy, x2: p[0], y2: p[1], stroke: T.grid });
      mk(svg, 'text', { x: q[0], y: q[1] + 4, 'text-anchor': Math.abs(q[0] - cx) < 5 ? 'middle' : q[0] > cx ? 'start' : 'end', 'font-size': 11, fill: T.mut }, short);
    });
    mk(svg, 'polygon', { points: poly(avg), fill: 'none', stroke: T.mut, 'stroke-width': 1.5, 'stroke-dasharray': '3 2' });
    const vals = axes.map(([k]) => s[k]);
    mk(svg, 'polygon', { points: poly(vals), fill: T.on, 'fill-opacity': 0.22, stroke: T.on, 'stroke-width': 2, 'stroke-linejoin': 'round' });
    vals.forEach((v, k) => {
      if (v == null) return;
      const p = pt(k, Math.max(0, v));
      mk(svg, 'circle', { cx: p[0], cy: p[1], r: 3, fill: T.on });
      const h = mk(svg, 'circle', { cx: p[0], cy: p[1], r: 9, fill: 'transparent' });
      h.onmouseenter = () => { tipEl.textContent = `${labels[i]} · ${axes[k][0]} rubric: ${v.toFixed(1)}% of max (average ${avg[k].toFixed(1)}%)`; };
    });
    mk(svg, 'text', { x: cx, y: 14, 'text-anchor': 'middle', 'font-size': 13, 'font-weight': 600, fill: T.ink }, trunc(labels[i], 26));
    if (stances[i] != null) mk(svg, 'text', { x: cx, y: 216, 'text-anchor': 'middle', 'font-size': 11, fill: T.mut }, `stance ${stances[i] > 0 ? '+' : ''}${Math.round(stances[i] * 10) / 10}`);
  });
  const cmp = document.createElement('div');
  cmp.innerHTML = '<h3 style="font-size:14px;margin:18px 0 4px">Pairwise comparison</h3><div></div>';
  host.appendChild(cmp);
  renderRadarCompare(cmp.lastChild, labels, scores, stances, axes, avg, opts);
}

// Pairwise comparison: overlay two replies' hexagons, with a per-axis difference table.
// Defaults to the most different pair (largest L1 distance across axes).
function renderRadarCompare(host, labels, scores, stances, axes, avg, opts) {
  const dark = matchMedia('(prefers-color-scheme: dark)').matches;
  const COL = dark ? ['#3987e5', '#d95926'] : ['#2a78d6', '#eb6834'];  // categorical slots 1 and 2
  const T = themeColors();
  const val = (i, k) => scores[i][axes[k][0]];
  let best = [0, Math.min(1, labels.length - 1)], bestD = -1;
  for (let i = 0; i < labels.length; i++) for (let j = i + 1; j < labels.length; j++) {
    const d = axes.reduce((s, _, k) => s + Math.abs((val(i, k) ?? 0) - (val(j, k) ?? 0)), 0);
    if (d > bestD) { bestD = d; best = [i, j]; }
  }
  const choices = sel => labels.map((l, i) => `<option value="${i}" ${i === sel ? 'selected' : ''}>${l}</option>`).join('');
  const sw = c => `<span style="display:inline-block;width:10px;height:10px;border-radius:2px;background:${c};margin-right:6px"></span>`;
  host.innerHTML = `<div style="display:flex;gap:10px;align-items:center;flex-wrap:wrap;margin:4px 0 6px">
      <span class="note" style="margin:0">Compare</span>${sw(COL[0])}<select data-k="0">${choices(best[0])}</select>
      <span class="note" style="margin:0">with</span>${sw(COL[1])}<select data-k="1">${choices(best[1])}</select>
      <label class="note" style="margin:0"><input type="checkbox" data-avg checked> show average</label>
      <span class="note" style="margin:0">(defaults to the most different pair)</span></div>
    <div style="display:flex;gap:16px;flex-wrap:wrap;align-items:flex-start"><div data-plot style="flex:1 1 300px;max-width:420px"></div><div data-table style="flex:1 1 260px"></div></div>`;
  const pick = [best[0], best[1]];
  const draw = () => {
    const plot = host.querySelector('[data-plot]'), showAvg = host.querySelector('[data-avg]').checked;
    plot.innerHTML = '';
    const n = axes.length, cx = 150, cy = 140, R = 100;
    const pt = (k, v) => { const a = -Math.PI / 2 + k * 2 * Math.PI / n; return [cx + Math.cos(a) * R * v / 100, cy + Math.sin(a) * R * v / 100]; };
    const poly = vals => vals.map((v, k) => pt(k, Math.max(0, v ?? 0)).join(',')).join(' ');
    const svg = mk(plot, 'svg', { viewBox: '-50 0 400 285', width: '100%', role: 'img', 'aria-label': `Theory profiles of ${labels[pick[0]]} and ${labels[pick[1]]}` });
    [25, 50, 75, 100].forEach(r => {
      mk(svg, 'polygon', { points: poly(axes.map(() => r)), fill: 'none', stroke: T.grid });
      mk(svg, 'text', { x: cx + 3, y: cy - R * r / 100 - 2, 'font-size': 10, fill: T.mut }, `${r}%`);
    });
    axes.forEach(([, short], k) => {
      const p = pt(k, 100), q = pt(k, 116);
      mk(svg, 'line', { x1: cx, y1: cy, x2: p[0], y2: p[1], stroke: T.grid });
      mk(svg, 'text', { x: q[0], y: q[1] + 4, 'text-anchor': Math.abs(q[0] - cx) < 5 ? 'middle' : q[0] > cx ? 'start' : 'end', 'font-size': 12, fill: T.mut }, short);
    });
    if (showAvg) mk(svg, 'polygon', { points: poly(avg), fill: 'none', stroke: T.mut, 'stroke-width': 1.5, 'stroke-dasharray': '3 2' });
    pick.forEach((i, c) => {
      const vals = axes.map((_, k) => val(i, k));
      mk(svg, 'polygon', { points: poly(vals), fill: COL[c], 'fill-opacity': 0.15, stroke: COL[c], 'stroke-width': 2, 'stroke-linejoin': 'round' });
      vals.forEach((v, k) => { if (v == null) return; const p = pt(k, Math.max(0, v)); mk(svg, 'circle', { cx: p[0], cy: p[1], r: 4, fill: COL[c], stroke: T.bg, 'stroke-width': 2 }); });
    });
    const f = v => v == null ? '–' : v.toFixed(0) + '%';
    const rows = axes.map(([name], k) => {
      const a = val(pick[0], k), b = val(pick[1], k), d = a != null && b != null ? a - b : null;
      return `<tr><td>${name}</td><td class="c">${f(a)}</td><td class="c">${f(b)}</td><td class="c" style="font-weight:600">${d == null ? '–' : (d > 0 ? '+' : '') + d.toFixed(0)}</td></tr>`;
    }).join('');
    const st = i => stances[i] == null ? '–' : (stances[i] > 0 ? '+' : '') + Math.round(stances[i] * 10) / 10;
    host.querySelector('[data-table]').innerHTML = `<table class="ck"><thead><tr><th style="text-align:left">Rubric</th><th>${sw(COL[0])}${trunc(labels[pick[0]], 14)}</th><th>${sw(COL[1])}${trunc(labels[pick[1]], 14)}</th><th>Diff</th></tr></thead>
      <tbody>${rows}<tr class="foot"><td>Stance (−5 A … +5 B)</td><td class="c">${st(pick[0])}</td><td class="c">${st(pick[1])}</td><td></td></tr></tbody></table>${opts ? `<p class="note">A = ${opts.option_a} · B = ${opts.option_b}</p>` : ''}`;
  };
  host.querySelectorAll('select').forEach(s => s.onchange = () => { pick[+s.dataset.k] = +s.value; draw(); });
  host.querySelector('[data-avg]').onchange = draw;
  draw();
}

// Variation across replies, one row per rubric: each reply's score (% of max) as a dot,
// with the min-max range, mean tick, SD, and checklist disagreement (mean pairwise distance
// between checklists as % of the rubric's criteria).
// pct: per reply {rubric: percent}; vecs: per reply {rubric: checklist vector}; cat as in renderSpectrum.
function renderVariation(host, labels, pct, vecs, cat) {
  host.innerHTML = '';
  const T = themeColors();
  const rubrics = RADAR_AXES.filter(([k]) => pct.filter(p => p[k] != null).length >= 2);
  if (!rubrics.length) { host.innerHTML = '<p class="note">Need at least 2 judged replies per rubric.</p>'; return; }
  const L = 110, R = 480, rowH = 46, top = 26, W = 680, H = top + rubrics.length * rowH + 30;
  const sx = v => L + Math.max(0, Math.min(100, v)) / 100 * (R - L);
  const svg = mk(host, 'svg', { width: '100%', viewBox: `0 0 ${W} ${H}`, role: 'img', 'aria-label': 'Variation of scores across replies by rubric' });
  svg.style.maxWidth = '900px';
  [0, 25, 50, 75, 100].forEach(v => {
    mk(svg, 'line', { x1: sx(v), x2: sx(v), y1: top - 6, y2: H - 26, stroke: T.grid });
    mk(svg, 'text', { x: sx(v), y: H - 12, 'text-anchor': 'middle', 'font-size': 11, fill: T.mut }, `${v}%`);
  });
  mk(svg, 'text', { x: (L + R) / 2, y: 12, 'text-anchor': 'middle', 'font-size': 11, fill: T.mut }, 'score as % of rubric maximum');
  mk(svg, 'text', { x: 500, y: 12, 'font-size': 11, fill: T.mut }, 'SD · range');
  mk(svg, 'text', { x: 590, y: 12, 'font-size': 11, fill: T.mut }, 'checklist');
  mk(svg, 'text', { x: 590, y: 24, 'font-size': 11, fill: T.mut }, 'disagreement');
  rubrics.forEach(([k, short], r) => {
    const y = top + r * rowH + rowH / 2;
    const idx = pct.map((p, i) => i).filter(i => pct[i][k] != null), vals = idx.map(i => pct[i][k]);
    const mean = vals.reduce((a, b) => a + b, 0) / vals.length;
    const sd = Math.sqrt(vals.reduce((a, v) => a + (v - mean) ** 2, 0) / (vals.length - 1));
    const lo = Math.min(...vals), hi = Math.max(...vals);
    // Mean pairwise L1 distance between checklists, as a share of the rubric's criteria.
    const vs = idx.map(i => vecs[i][k]).filter(Boolean);
    let dsum = 0, np = 0;
    for (let a = 0; a < vs.length; a++) for (let b = a + 1; b < vs.length; b++) { dsum += vs[a].reduce((t, x, j) => t + Math.abs(x - vs[b][j]), 0); np++; }
    const dis = np ? 100 * dsum / np / vs[0].length : null;
    mk(svg, 'text', { x: L - 10, y: y + 4, 'text-anchor': 'end', 'font-size': 12, fill: T.ink }, short);
    mk(svg, 'line', { x1: L, x2: R, y1: y, y2: y, stroke: T.grid, 'stroke-opacity': 0.6 });
    mk(svg, 'rect', { x: sx(lo), y: y - 9, width: Math.max(2, sx(hi) - sx(lo)), height: 18, rx: 4, fill: T.on, 'fill-opacity': 0.1 });
    mk(svg, 'line', { x1: sx(mean), x2: sx(mean), y1: y - 12, y2: y + 12, stroke: T.mut, 'stroke-width': 2 });
    const placedX = [];
    idx.forEach(i => {  // nudge overlapping dots vertically
      const x = sx(pct[i][k]); let off = 0;
      for (const o of [0, -7, 7, -14, 14]) { if (!placedX.some(p => Math.abs(p[0] - x) < 7 && p[1] === o)) { off = o; break; } }
      placedX.push([x, off]);
      const col = cat ? cat.color[i] : T.on, hollow = cat && cat.hollow[i];
      const c = mk(svg, 'circle', { cx: x, cy: y + off, r: hollow ? 4 : 4.5, fill: hollow ? T.bg : col, stroke: col, 'stroke-width': 1.8 });
      hover(c, `${labels[i]} · ${k}: ${pct[i][k].toFixed(1)}% (mean ${mean.toFixed(1)}%)`);
    });
    mk(svg, 'text', { x: 500, y: y + 4, 'font-size': 12, fill: T.ink }, `${sd.toFixed(1)} · ${(hi - lo).toFixed(0)}`);
    if (dis != null) mk(svg, 'text', { x: 590, y: y + 4, 'font-size': 12, fill: T.ink }, `${dis.toFixed(0)}%`);
  });
  if (cat) host.insertAdjacentHTML('afterbegin', legendHTML(cat, 'grey tick = mean · shaded band = min to max'));
  host.insertAdjacentHTML('beforeend', '<p class="note">SD and range are in percentage points of the rubric maximum. Checklist disagreement = average share of criteria on which two replies differ (0% = identical checklists).</p>');
}

if (typeof module !== 'undefined') module.exports = { dendrogram, mca, eigSym };

// Stance spectrum: each reply as a dot on the -5 (A) .. +5 (B) line, one row per reply
// (sorted by stance) so labels never collide.
// Provider legend: filled swatch per provider plus a note on tier encoding.
function legendHTML(cat, extra) {
  return `<div class="note" style="display:flex;gap:12px;flex-wrap:wrap;margin:6px 0 2px">${cat.legend.map(([n, c]) =>
    `<span><span style="display:inline-block;width:10px;height:10px;border-radius:50%;background:${c};margin-right:5px;vertical-align:-1px"></span>${n}</span>`).join('')}${cat.note ? `<span>${cat.note}</span>` : ''}${extra ? `<span>· ${extra}</span>` : ''}</div>`;
}
// cat (optional): {color: [per reply], hollow: [per reply], legend: [[name, color]], note}
function renderSpectrum(host, labels, stances, opts, cat) {
  host.innerHTML = '';
  const T = themeColors();
  const items = labels.map((l, i) => ({ l, i, v: stances[i] })).filter(d => d.v != null).sort((a, b) => a.v - b.v);
  if (!items.length) { host.innerHTML = '<p class="note">No stance codes yet (run experiments/stance.py).</p>'; return; }
  const W = 480, L = 24, R = W - 24, row = 17, top = 8;
  const sx = v => L + (v + 5) / 10 * (R - L);
  const axisY = top + items.length * row + 6, H = axisY + 52;
  const svg = mk(host, 'svg', { width: '100%', viewBox: `0 0 ${W} ${H}`, role: 'img', 'aria-label': 'Stance of each reply from -5 (A) to +5 (B)' });
  svg.style.maxWidth = '560px';
  mk(svg, 'line', { x1: sx(0), x2: sx(0), y1: top, y2: axisY, stroke: T.grid, 'stroke-dasharray': '3 3' });
  items.forEach((d, i) => {
    const x = sx(d.v), y = top + i * row + row / 2, right = d.v > 0;
    mk(svg, 'line', { x1: L, x2: R, y1: y, y2: y, stroke: T.grid, 'stroke-opacity': 0.5 });
    const col = cat ? cat.color[d.i] : T.on, hollow = cat && cat.hollow[d.i];
    mk(svg, 'circle', { cx: x, cy: y, r: hollow ? 4.5 : 5, fill: hollow ? T.bg : col, stroke: col, 'stroke-width': 2 });
    mk(svg, 'text', { x: right ? x - 9 : x + 9, y: y + 4, 'text-anchor': right ? 'end' : 'start', 'font-size': 11, fill: T.ink },
      `${trunc(d.l, 24)} ${d.v > 0 ? '+' : ''}${Math.round(d.v * 10) / 10}`);
  });
  mk(svg, 'line', { x1: L, x2: R, y1: axisY, y2: axisY, stroke: T.mut, 'stroke-width': 1.5 });
  for (let v = -5; v <= 5; v++) {
    mk(svg, 'line', { x1: sx(v), x2: sx(v), y1: axisY - 3, y2: axisY + 3, stroke: T.mut });
    mk(svg, 'text', { x: sx(v), y: axisY + 15, 'text-anchor': 'middle', 'font-size': 10, fill: T.mut }, v > 0 ? '+' + v : v);
  }
  mk(svg, 'text', { x: L, y: axisY + 31, 'font-size': 11, 'font-weight': 600, fill: T.ink }, '← A: ' + trunc(opts?.option_a || 'option A', 44));
  mk(svg, 'text', { x: R, y: axisY + 46, 'text-anchor': 'end', 'font-size': 11, 'font-weight': 600, fill: T.ink }, 'B: ' + trunc(opts?.option_b || 'option B', 44) + ' →');
  if (cat) host.insertAdjacentHTML('afterbegin', legendHTML(cat));
}
