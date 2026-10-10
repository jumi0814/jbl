/* JBL 넘버링 — Word(.docx) 읽기 (10-10)
   브라우저 전용(DOMParser · DecompressionStream · canvas). 허브 '파일 가져오기'가 쓸 때만 불러오고,
   tools/num/build_seed.py가 크롬(playwright)에서 같은 코드로 첨부 Word를 읽어 docs/num/seed.js를 만든다 — 읽는 방법은 한 곳에만.
   JBLDOCX.parse(ArrayBuffer, {img:'inline'|'id', maxW, q, onProgress}) → {title, legend, sections, items, images, flags, layout}
   원칙: 글자는 Word 그대로(번호 목록의 번호도 글자로 넣음) · 서식은 굵게·밑줄·기울임·글자색·형광펜·위/아래 첨자·표·그림만 · 취소선은 글자만 남김
   표 모양 두 가지: ① 머리 줄에 '문제·정답·암기법'이 있는 3칸 표(임상구강내과학) ② 문제 줄(왼·오 같은 글) 뒤에 왼쪽 스토리·오른쪽 답 줄이 오는 2칸 표(교정과)
   어느 쪽도 아니면 '첫 칸 문제 · 둘째 칸 답 · 셋째 칸 스토리'로 읽고 모두 검토 대상으로 둔다. */
(function () {
'use strict';
const LN = e => e.localName;
const kids = (e, n) => { const o = []; if (!e) return o; for (let c = e.firstElementChild; c; c = c.nextElementSibling) if (!n || LN(c) === n) o.push(c); return o; };
const kid = (e, n) => { if (!e) return null; for (let c = e.firstElementChild; c; c = c.nextElementSibling) if (LN(c) === n) return c; return null; };
const attr = (e, n) => { if (!e) return null; for (const a of e.attributes) if (a.localName === n) return a.value; return null; };
const esc = s => String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
const yieldUI = () => new Promise(r => setTimeout(r, 0));
const norm = s => String(s || '').replace(/[\s ]+/g, '').replace(/[(){}\[\].,·:;!?~\-–—'"“”‘’/<>*]/g, '').toLowerCase();
function dice(a, b) { a = norm(a); b = norm(b); if (a === b) return 1; if (a.length < 2 || b.length < 2) return 0; const m = new Map(); for (let i = 0; i < a.length - 1; i++) { const g = a.substr(i, 2); m.set(g, (m.get(g) || 0) + 1); } let n = 0; for (let i = 0; i < b.length - 1; i++) { const g = b.substr(i, 2), c = m.get(g); if (c) { n++; m.set(g, c - 1); } } return 2 * n / (a.length + b.length - 2); }

/* ---------- ZIP ---------- */
async function inflate(u8) {
  if (typeof DecompressionStream === 'undefined') throw new Error('이 브라우저는 Word 파일 읽기(압축 풀기)를 지원하지 않아요 — 최신 Chrome·Safari·Edge에서 해 주세요');
  const s = new Blob([u8]).stream().pipeThrough(new DecompressionStream('deflate-raw'));
  return new Uint8Array(await new Response(s).arrayBuffer());
}
function zipIndex(buf) {
  const u8 = new Uint8Array(buf), dv = new DataView(buf); let e = -1;
  for (let i = u8.length - 22; i >= Math.max(0, u8.length - 66000); i--) if (dv.getUint32(i, true) === 0x06054b50) { e = i; break; }
  if (e < 0) throw new Error('Word(.docx) 파일이 아니에요 — .doc·.hwp·.pdf는 Word에서 .docx로 저장한 뒤 가져와 주세요');
  const n = dv.getUint16(e + 10, true); let p = dv.getUint32(e + 16, true); const out = new Map(), td = new TextDecoder();
  for (let k = 0; k < n; k++) {
    if (dv.getUint32(p, true) !== 0x02014b50) throw new Error('Word 파일 목록이 깨져 있어요');
    const meth = dv.getUint16(p + 10, true), csz = dv.getUint32(p + 20, true), nl = dv.getUint16(p + 28, true), xl = dv.getUint16(p + 30, true), cl = dv.getUint16(p + 32, true), lo = dv.getUint32(p + 42, true);
    const name = td.decode(u8.subarray(p + 46, p + 46 + nl));
    out.set(name, { meth, csz, lo }); p += 46 + nl + xl + cl;
  }
  return { u8, dv, out };
}
async function zipGet(z, name) {
  const f = z.out.get(name); if (!f) return null;
  const nl = z.dv.getUint16(f.lo + 26, true), xl = z.dv.getUint16(f.lo + 28, true), st = f.lo + 30 + nl + xl, raw = z.u8.subarray(st, st + f.csz);
  if (f.meth === 0) return raw.slice();
  if (f.meth === 8) return inflate(raw);
  throw new Error('지원하지 않는 압축 방식(' + f.meth + ')');
}
async function zipXML(z, name) { const b = await zipGet(z, name); if (!b) return null; const d = new DOMParser().parseFromString(new TextDecoder().decode(b), 'application/xml'); if (d.getElementsByTagName('parsererror').length) throw new Error(name + ' 읽기 실패'); return d; }

/* ---------- 번호 목록 ---------- */
const BUL = { '': '•', '': '▪', '': '➢', '': '❖', '': '✓', '': '■', '': '□', '': '➔', 'o': '◦', '': '─' };
function roman(n) { const v = [[1000, 'm'], [900, 'cm'], [500, 'd'], [400, 'cd'], [100, 'c'], [90, 'xc'], [50, 'l'], [40, 'xl'], [10, 'x'], [9, 'ix'], [5, 'v'], [4, 'iv'], [1, 'i']]; let s = ''; for (const [a, r] of v) while (n >= a) { s += r; n -= a; } return s; }
function fmtNum(n, f) {
  switch (f) {
    case 'lowerLetter': return String.fromCharCode(96 + ((n - 1) % 26) + 1);
    case 'upperLetter': return String.fromCharCode(64 + ((n - 1) % 26) + 1);
    case 'lowerRoman': return roman(n);
    case 'upperRoman': return roman(n).toUpperCase();
    case 'decimalEnclosedCircle': case 'decimalEnclosedCircleChinese': return n >= 1 && n <= 20 ? String.fromCharCode(0x2460 + n - 1) : '(' + n + ')';
    case 'ganada': return '가나다라마바사아자차카타파하'[(n - 1) % 14];
    case 'chosung': return 'ㄱㄴㄷㄹㅁㅂㅅㅇㅈㅊㅋㅌㅍㅎ'[(n - 1) % 14];
    case 'decimalZero': return (n < 10 ? '0' : '') + n;
    case 'none': return '';
    default: return String(n);
  }
}
function numbering(doc) {
  const A = {}, N = {};
  if (doc) {
    for (const a of kids(doc.documentElement, 'abstractNum')) { const lv = {}; for (const l of kids(a, 'lvl')) lv[attr(l, 'ilvl')] = { f: attr(kid(l, 'numFmt'), 'val') || 'decimal', t: attr(kid(l, 'lvlText'), 'val'), s: +(attr(kid(l, 'start'), 'val') || 1) }; A[attr(a, 'abstractNumId')] = lv; }
    for (const n of kids(doc.documentElement, 'num')) { const ov = {}; for (const o of kids(n, 'lvlOverride')) { const so = kid(o, 'startOverride'); if (so) ov[attr(o, 'ilvl')] = +attr(so, 'val'); } N[attr(n, 'numId')] = { a: attr(kid(n, 'abstractNumId'), 'val'), ov }; }
  }
  const C = {};
  return function label(numId, ilvl) {
    const d = N[numId]; if (!d || numId === '0') return '';
    const lv = A[d.a] || {}, L = lv[ilvl]; if (!L) return '';
    const c = C[numId] || (C[numId] = {}); const il = +ilvl;
    const st = l => (d.ov[l] != null ? d.ov[l] : ((lv[l] || {}).s || 1));
    c[il] = c[il] == null ? st(il) : c[il] + 1;
    for (const k in c) if (+k > il) delete c[k];
    if (L.f === 'bullet') { const t = L.t || '•'; return [...t].map(ch => BUL[ch] || ch).join(''); }
    if (L.t == null) return '';
    return L.t.replace(/%(\d)/g, (_, k) => { const l = +k - 1; const v = c[l] != null ? c[l] : st(l); return fmtNum(v, ((lv[l] || {}).f) || 'decimal'); });
  };
}

/* ---------- 스타일(굵게·색 등 상속 최소) ---------- */
function styles(doc) {
  const S = {};
  if (doc) for (const s of kids(doc.documentElement, 'style')) S[attr(s, 'styleId')] = { b: attr(kid(s, 'basedOn'), 'val'), r: kid(s, 'rPr'), np: kid(kid(s, 'pPr'), 'numPr') };
  const chain = id => { const o = []; let k = 0; while (id && S[id] && k++ < 8) { o.unshift(S[id]); id = S[id].b; } return o; };
  return { rpr: id => chain(id).map(x => x.r).filter(Boolean), numPr: id => { const c = chain(id).reverse(); for (const x of c) if (x.np) return x.np; return null; } };
}
const HL = { yellow: '#FFFF00', green: '#00FF00', cyan: '#00FFFF', magenta: '#FF00FF', blue: '#0000FF', red: '#FF0000', darkBlue: '#000080', darkCyan: '#008080', darkGreen: '#008000', darkMagenta: '#800080', darkRed: '#800000', darkYellow: '#808000', darkGray: '#808080', lightGray: '#C0C0C0', black: '#000000', white: '#FFFFFF' };
const onoff = e => { if (!e) return null; const v = attr(e, 'val'); return !(v === '0' || v === 'false' || v === 'off'); };
function runFmt(list) {   /* 뒤에 온 것이 이김 */
  const f = { b: false, i: false, u: false, c: '', h: '', v: '', s: false };
  for (const rp of list) {
    if (!rp) continue;
    let x = onoff(kid(rp, 'b')); if (x != null) f.b = x;
    x = onoff(kid(rp, 'i')); if (x != null) f.i = x;
    const u = kid(rp, 'u'); if (u) f.u = (attr(u, 'val') || 'single') !== 'none';
    const c = kid(rp, 'color'); if (c) { const v = attr(c, 'val'); f.c = v && v !== 'auto' && !/^0{6}$/.test(v) ? '#' + v.toUpperCase() : ''; }
    const h = kid(rp, 'highlight'); if (h) { const v = attr(h, 'val'); f.h = v && v !== 'none' ? (HL[v] || '') : ''; f.hn = v; }
    const sh = kid(rp, 'shd'); if (sh && !kid(rp, 'highlight')) { const v = attr(sh, 'fill'); if (v && v !== 'auto' && !/^F{6}$/i.test(v)) { f.h = '#' + v.toUpperCase(); f.hn = 'shd'; } }
    const va = kid(rp, 'vertAlign'); if (va) { const v = attr(va, 'val'); f.v = v === 'superscript' ? 'sup' : v === 'subscript' ? 'sub' : ''; }
    x = onoff(kid(rp, 'strike')); if (x != null) f.s = x; x = onoff(kid(rp, 'dstrike')); if (x) f.s = true;
  }
  return f;
}
function wrap(t, f) {
  let h = esc(t);
  if (f.v) h = '<' + f.v + '>' + h + '</' + f.v + '>';
  if (f.u) h = '<u>' + h + '</u>';
  if (f.i) h = '<i>' + h + '</i>';
  if (f.b) h = '<b>' + h + '</b>';
  const st = (f.c ? 'color:' + f.c + ';' : '') + (f.h ? 'background-color:' + f.h + ';' : '');
  if (st) h = '<span style="' + st + '">' + h + '</span>';
  return h;
}
const isGray = c => /^#(ADADAD|A5A5A5|BFBFBF|7F7F7F|808080|A6A6A6|999999|AAAAAA|8C8C8C|969696|D9D9D9|BEBEBE)$/i.test(c || '');

/* ---------- 본문 → 블록 ---------- */
function Conv(ctx) {
  const { lab, sty, rels, imgs, flags } = ctx;
  function runsOf(p, out) {
    for (let c = p.firstElementChild; c; c = c.nextElementSibling) {
      const n = LN(c);
      if (n === 'r') out.push(c);
      else if (n === 'hyperlink' || n === 'ins' || n === 'smartTag' || n === 'fldSimple' || n === 'customXml' || n === 'dir' || n === 'bdo') runsOf(c, out);
      else if (n === 'sdt') runsOf(kid(c, 'sdtContent') || c, out);
      else if (n === 'AlternateContent') { const ch = kid(c, 'Choice') || kid(c, 'Fallback'); if (ch) runsOf(ch, out); }
    }
    return out;
  }
  function picsIn(e, out) {   /* drawing·pict 안의 그림(묶은 그림 포함) — mc:AlternateContent는 Choice만(대체 그림 두 번 넣지 않게) */
    for (let c = e.firstElementChild; c; c = c.nextElementSibling) {
      const n = LN(c);
      if (n === 'AlternateContent') { const ch = kid(c, 'Choice') || kid(c, 'Fallback'); if (ch) picsIn(ch, out); continue; }
      if (n === 'blip') { const id = attr(c, 'embed') || attr(c, 'link'); if (id) out.push(id); continue; }
      if (n === 'imagedata') { const id = attr(c, 'id'); if (id) out.push(id); continue; }
      if (n === 'txbxContent') { out.push({ txbx: c }); continue; }
      picsIn(c, out);
    }
    return out;
  }
  function ext(e) { const x = e.getElementsByTagNameNS('*', 'extent')[0]; if (!x) return null; const cx = +attr(x, 'cx'), cy = +attr(x, 'cy'); return cx && cy ? { w: Math.round(cx / 9525), h: Math.round(cy / 9525) } : null; }
  function para(p) {
    const pPr = kid(p, 'pPr'), ps = attr(kid(pPr, 'pStyle'), 'val');
    let np = kid(pPr, 'numPr') || sty.numPr(ps), L = '';
    if (np) { const ni = attr(kid(np, 'numId'), 'val'), il = attr(kid(np, 'ilvl'), 'val') || '0'; if (ni) L = lab(ni, il); }
    const base = sty.rpr(ps), runs = runsOf(p, []), parts = [], col = {}, hl = {}; let text = '', ni = 0, last = null, buf = '';
    const flush = () => { if (buf) { parts.push(wrap(buf, last)); buf = ''; } };
    const add = (t, f) => { if (!t) return; if (last && last.b === f.b && last.i === f.i && last.u === f.u && last.c === f.c && last.h === f.h && last.v === f.v) buf += t; else { flush(); last = f; buf = t; } text += t; if (t.trim()) { const k = f.c || 'auto'; col[k] = (col[k] || 0) + t.replace(/\s/g, '').length; if (f.h) hl[f.h] = (hl[f.h] || 0) + t.replace(/\s/g, '').length; } };
    for (const r of runs) {
      const rp = kid(r, 'rPr'), rs = attr(kid(rp, 'rStyle'), 'val');
      const f = runFmt(base.concat(rs ? sty.rpr(rs) : [], [rp]));
      if (f.s) { ctx.strike++; f.s = false; }
      for (let c = r.firstElementChild; c; c = c.nextElementSibling) {
        const n = LN(c);
        if (n === 't') add(c.textContent, f);
        else if (n === 'tab' || n === 'ptab') add('\t', f);
        else if (n === 'br' || n === 'cr') { flush(); parts.push('<br>'); text += '\n'; last = null; }
        else if (n === 'noBreakHyphen') add('-', f);
        else if (n === 'softHyphen') { }
        else if (n === 'sym') { const ch = attr(c, 'char'); if (ch) { const v = String.fromCharCode(parseInt(ch, 16)); add(BUL[v] || v, f); } }
        else if (n === 'drawing' || n === 'pict' || n === 'object' || n === 'AlternateContent') {
          flush(); last = null; const sz = ext(c);
          for (const id of picsIn(c, [])) {
            if (id && id.txbx) { const tx = []; for (const q of id.txbx.getElementsByTagNameNS('*', 'p')) { const b = para(q); if (b.text.trim()) tx.push(b.html); } if (tx.length) { parts.push('<span class="nbox">' + tx.join('') + '</span>'); text += ' '; ctx.txbx++; } continue; }
            const t = rels[id]; if (!t) { flags.push({ k: 'img', m: '그림 연결을 찾지 못함(' + id + ')' }); continue; }
            const k = imgs.ref(t, sz); parts.push(k); ni++; text += ' ';
          }
        }
      }
    }
    flush();
    let inner = parts.join('');
    if (L) { inner = esc(L) + ' ' + inner; text = L + ' ' + text; }
    const jc = attr(kid(pPr, 'jc'), 'val'), il = np ? +(attr(kid(np, 'ilvl'), 'val') || 0) : 0;
    const st = (jc === 'center' ? 'text-align:center;' : jc === 'right' || jc === 'end' ? 'text-align:right;' : '') + (il > 0 ? 'padding-left:' + (il * 1.5) + 'em;' : '');
    const empty = !text.trim() && !ni;
    return { k: 'p', html: '<p' + (st ? ' style="' + st + '"' : '') + '>' + (inner || '<br>') + '</p>', text, col, hl, img: ni, empty };
  }
  function cellBlocks(tc) {
    const out = [];
    for (let c = tc.firstElementChild; c; c = c.nextElementSibling) {
      const n = LN(c);
      if (n === 'p') out.push(para(c));
      else if (n === 'tbl') out.push(table(c));
      else if (n === 'sdt') { const sc = kid(c, 'sdtContent'); if (sc) out.push(...cellBlocks(sc)); }
      else if (n === 'customXml') out.push(...cellBlocks(c));
    }
    return out;
  }
  function trim(bl) { let a = 0, b = bl.length; while (a < b && bl[a].k === 'p' && bl[a].empty) a++; while (b > a && bl[b - 1].k === 'p' && bl[b - 1].empty) b--; return bl.slice(a, b); }
  function rowsOf(tbl) {   /* [{cells:[{blocks, span, vm, shd, col}]}] — 줄 안의 칸(가로 합침 = span, 세로 합침 = vm) */
    const rows = [];
    for (const tr of kids(tbl, 'tr')) {
      const cells = []; let col = 0;
      for (const tc of kids(tr, 'tc')) {
        const pr = kid(tc, 'tcPr'), span = +(attr(kid(pr, 'gridSpan'), 'val') || 1), vmE = kid(pr, 'vMerge'), vm = vmE ? (attr(vmE, 'val') || 'continue') : '', sh = attr(kid(pr, 'shd'), 'fill');
        cells.push({ blocks: cellBlocks(tc), span, vm, col, shd: sh && sh !== 'auto' && !/^F{6}$/i.test(sh) ? '#' + sh.toUpperCase() : '' }); col += span;
      }
      rows.push({ cells });
    }
    return rows;
  }
  function table(tbl) {
    const rows = rowsOf(tbl), rs = new Map();   /* 세로 합침: 시작 칸의 rowspan */
    const live = {};
    rows.forEach((r, ri) => r.cells.forEach(c => { if (c.vm === 'restart') { live[c.col] = c; c.rs = 1; } else if (c.vm === 'continue' && live[c.col]) { live[c.col].rs++; c.skip = true; } else if (!c.vm) delete live[c.col]; }));
    let text = '', img = 0; const col = {};
    const html = '<table>' + rows.map(r => '<tr>' + r.cells.filter(c => !c.skip).map(c => {
      const bl = trim(c.blocks); bl.forEach(b => { text += b.text + '\n'; img += b.img; for (const k in b.col) col[k] = (col[k] || 0) + b.col[k]; });
      return '<td' + (c.span > 1 ? ' colspan="' + c.span + '"' : '') + (c.rs > 1 ? ' rowspan="' + c.rs + '"' : '') + (c.shd ? ' style="background-color:' + c.shd + '"' : '') + '>' + (bl.map(b => b.html).join('') || '<p><br></p>') + '</td>';
    }).join('') + '</tr>').join('') + '</table>';
    return { k: 't', html, text, col, img, empty: false };
  }
  return { para, table, rowsOf, trim };
}

/* ---------- 그림 ---------- */
function fnv(u8) { let h = 0x811c9dc5; for (let i = 0; i < u8.length; i += (u8.length > 400000 ? 7 : 1)) { h ^= u8[i]; h = Math.imul(h, 0x01000193) >>> 0; } h ^= u8.length; return (Math.imul(h, 0x01000193) >>> 0).toString(16).padStart(8, '0'); }
async function shrink(u8, mime, maxW, q) {
  const bmp = await createImageBitmap(new Blob([u8], { type: mime }));
  const sc = Math.min(1, maxW / bmp.width), w = Math.max(1, Math.round(bmp.width * sc)), h = Math.max(1, Math.round(bmp.height * sc));
  const cv = document.createElement('canvas'); cv.width = w; cv.height = h; const g = cv.getContext('2d');
  g.drawImage(bmp, 0, 0, w, h); if (bmp.close) bmp.close();
  let d = cv.toDataURL('image/webp', q);
  if (!/^data:image\/webp/.test(d)) { const c2 = document.createElement('canvas'); c2.width = w; c2.height = h; const g2 = c2.getContext('2d'); g2.fillStyle = '#fff'; g2.fillRect(0, 0, w, h); g2.drawImage(cv, 0, 0); d = c2.toDataURL('image/jpeg', q); }
  return { d, w, h };
}

/* ---------- 연도·꼬리표 ---------- */
const YTOK = /^(?:20)?(\d{2})\s*(?:년도?)?\s*[’']?\s*(탈|짤|매칭|객관식|객|빈칸|서술|기출|~)?\s*(\?)?$/;   /* 24 · 2024 · 24’ · 25탈 · 25 기출 · 20~ */
function yearsTags(text) {   /* 문제 글의 괄호 '(24,22)·(25탈)·(26출제예고,25,…)·(24,과거)'와 줄머리 '25년도:'·'25 빈칸' — 적힌 해만(추측 금지) */
  const yrs = new Set(), tags = new Set(), notes = [];
  const re = /\(([^()]{1,60})\)/g; let m;
  while ((m = re.exec(text))) {
    const toks = m[1].split(/[,，、]\s*/).map(s => s.trim()).filter(Boolean), yy = [], tt = [], nn = [];
    let ok = toks.length > 0;
    for (const t of toks) {
      let x;
      if ((x = /^(\d{2})\s*(?:년도?)?\s*(출제\s*예고|탈\s*대비|수업\s*강조|강조)$/.exec(t))) { tt.push(x[1] + ' ' + x[2].replace(/\s+/g, '').replace('출제예고', '출제 예고').replace('탈대비', '탈 대비').replace('수업강조', '수업 강조')); continue; }
      if ((x = YTOK.exec(t)) && +x[1] >= 5 && +x[1] <= 26) { yy.push(+x[1]); if (x[2] && x[2] !== '~' && x[2] !== '기출') tt.push(x[2] === '객' ? '객관식' : x[2]); if (x[3]) nn.push('연도 뒤 물음표 (' + m[1] + ')'); if (x[2] === '~') nn.push('연도 범위 표기 (' + m[1] + ')'); continue; }
      if (/^(과거|옛날)\s*(기출|객관식|객|서술|필기)?(\s*따옴)?$/.test(t)) { tt.push('과거기출'); continue; }
      if (/^(탈|짤|매칭|탈\s*대비\??)$/.test(t)) { tt.push(t.replace(/\s+/g, '').replace('탈대비', '탈 대비')); continue; }
      ok = false; break;
    }
    if (ok && yy.length === 1 && toks.length === 1 && /^\d{1,2}$/.test(toks[0]) && yy[0] < 12) nn.push("괄호 안 숫자 하나 '(" + m[1] + ")'를 " + (2000 + yy[0]) + '년 출제로 읽음 — 확인');   /* (10) 같은 것 — 연도가 아닐 수도 */
    if (ok && yy.includes(26)) nn.push("'26'을 2026년 출제로 읽음 — 확인(출제 예고면 '26출제예고'로)");
    if (ok) { yy.forEach(y => yrs.add(y)); tt.forEach(t => tags.add(t)); nn.forEach(n => notes.push(n)); }
  }
  for (const ln of text.split('\n')) {
    let x = /^\s*(\d{2})\s*년도\s*[:：]/.exec(ln); if (x && +x[1] >= 5 && +x[1] <= 30) { yrs.add(+x[1]); continue; }
    x = /^\s*(\d{2})\s*(빈칸|객관식|서술|매칭)/.exec(ln); if (x && +x[1] >= 5 && +x[1] <= 30) { yrs.add(+x[1]); notes.push("줄머리 '" + ln.trim().slice(0, 20) + "'를 " + (2000 + +x[1]) + '년 출제로 읽음'); }
  }
  return { yrs: [...yrs].map(y => y < 100 ? 2000 + y : y).sort((a, b) => b - a), tags: [...tags], notes };
}

/* ---------- 머리(강의) 줄 ---------- */
function sectionOf(text, st) {
  let t = text.replace(/\s+/g, ' ').trim(), lab = st.lab || '', prof = '', date = '';
  if (/여기부터/.test(t)) st.from = true;
  if (/(^|[^A-Za-z])(BANK|Bank|bank)([^A-Za-z]|$)|뱅크/.test(t)) { lab = 'BANK'; st.lab = 'BANK'; }
  else if (/(^|[^A-Za-z])JB([^A-Za-z]|$)/.test(t)) { lab = 'JB'; if (!st.from) st.lab = 'JB'; }
  let title = t;
  const ang = /<([^<>]+)>/.exec(t);
  if (ang) title = ang[1].trim();
  else {
    title = t.replace(/^여기부터\s*/, '').replace(/^(?:BANK|Bank|뱅크)\s*[-–—:]\s*/, '').trim();
    const m = /^(?:(\d{4})\s+)?([^_]{1,20}?)_(.+)$/.exec(title);
    if (m && !/JB/.test(m[2])) { date = m[1] || ''; prof = m[2].trim(); title = m[3].trim(); }
    else if (/_/.test(title)) title = title.split('_')[0].trim();
  }
  return { title: title || t, raw: t, lab, prof, date };
}

/* ---------- 문서 해석 ---------- */
async function parse(buf, opt) {
  opt = opt || {};
  const prog = opt.onProgress || (() => {}); prog('압축 풀기');
  const z = zipIndex(buf);
  const doc = await zipXML(z, 'word/document.xml'); if (!doc) throw new Error('word/document.xml이 없어요 — Word 문서가 아닌 것 같아요');
  const numDoc = await zipXML(z, 'word/numbering.xml'), styDoc = await zipXML(z, 'word/styles.xml'), relDoc = await zipXML(z, 'word/_rels/document.xml.rels');
  const rels = {}; if (relDoc) for (const r of kids(relDoc.documentElement, 'Relationship')) if (/image/.test(attr(r, 'Type') || '')) rels[attr(r, 'Id')] = attr(r, 'Target');
  const flags = [], images = {}, pend = [];
  const imgs = {   /* 먼저 자리표(⟦IMGn⟧)만 넣고, 다 읽은 뒤 한꺼번에 줄여서 바꿔 끼움 */
    ref(target, sz) { const i = pend.length; pend.push({ target, sz }); return '⟦IMG' + i + '⟧'; }
  };
  const ctx = { lab: numbering(numDoc), sty: styles(styDoc), rels, imgs, flags, strike: 0, txbx: 0, hlc: {} };
  const C = Conv(ctx), body = kid(doc.documentElement, 'body');
  prog('본문 읽기');
  const top = [];
  for (let c = body.firstElementChild; c; c = c.nextElementSibling) {
    const n = LN(c);
    if (n === 'p') top.push({ k: 'p', b: C.para(c) });
    else if (n === 'tbl') top.push({ k: 't', rows: C.rowsOf(c), grid: kids(kid(c, 'tblGrid'), 'gridCol').length });
    else if (n === 'sdt') { const sc = kid(c, 'sdtContent'); if (sc) for (const x of kids(sc)) { if (LN(x) === 'p') top.push({ k: 'p', b: C.para(x) }); else if (LN(x) === 'tbl') top.push({ k: 't', rows: C.rowsOf(x), grid: kids(kid(x, 'tblGrid'), 'gridCol').length }); } }
  }
  await yieldUI();
  /* 제목·범례(표 앞 문단) */
  let title = '', legend = {}; const pre = [];
  for (const t of top) { if (t.k === 't') break; if (!t.b.empty) pre.push(t.b); }
  if (pre.length) title = pre[0].text.trim();
  for (const b of pre.slice(1)) {   /* '기출  수업시간 강조  과거기출'처럼 형광펜만 다른 짧은 낱말 줄 = 범례 */
    const m = [...b.html.matchAll(/<span style="(?:color:[^;]*;)?background-color:([^;"]+);">([^<]{1,20})<\/span>/g)];
    if (m.length >= 2 && m.map(x => x[2]).join('').length <= 40) m.forEach(x => { legend[x[1].toUpperCase()] = x[2].trim(); });
  }
  const blocksText = bl => bl.map(b => b.text).join('\n');
  const html = bl => bl.map(b => b.html).join('');
  const colOf = bl => { const c = {}; bl.forEach(b => { for (const k in b.col) c[k] = (c[k] || 0) + b.col[k]; }); return c; };
  const major = c => { let k = 'auto', v = -1; for (const x in c) if (c[x] > v) { v = c[x]; k = x; } return v > 0 ? k : ''; };
  const sections = []; const items = []; const sst = { lab: '' }; let sec = null; let layout = '';
  const newSec = (text) => { const s = sectionOf(text, sst); s.k = 'L' + (sections.length + 1); s.n = 0; sections.push(s); sec = s; return s; };
  const ensureSec = () => sec || newSec(title || '가져온 문서');
  const hlTags = (bl) => { const c = {}; for (const b of bl) for (const k in (b.hl || {})) if (legend[k]) c[k] = (c[k] || 0) + b.hl[k]; return Object.keys(c).filter(k => c[k] >= 2).sort((a, b) => c[b] - c[a]).map(k => legend[k]); };   /* 범례(형광펜 색 → 뜻)에 있는 색으로 칠한 문제 글 → 꼬리표(기출·수업시간 강조·과거기출) */
  const mkItem = (o) => { const s = ensureSec(); s.n++; const yt = yearsTags(o.qtext || ''); const it = { lec: s.k, q: o.q, a: o.a || '', st: o.st || '', note: o.note || '', yrs: yt.yrs, tags: [...new Set([...(o.tags || []), ...yt.tags])], lab: s.lab || '', rv: (o.rv || []).concat(yt.notes.map(m => ({ k: 'year', m }))), pos: o.pos }; items.push(it); return it; };

  for (let ti = 0, tn = 0; ti < top.length; ti++) {
    const T = top[ti]; if (T.k !== 't') continue; const tix = tn++;
    const rows = T.rows, ncol = T.grid || Math.max(...rows.map(r => r.cells.reduce((a, c) => a + c.span, 0)));
    /* ① 머리 줄 '문제 | 정답 | 암기법' */
    let hdr = -1, qi = -1, ai = -1, si = -1;
    rows.forEach((r, ri) => { if (hdr >= 0 || r.cells.length < 2) return; const tx = r.cells.map(c => blocksText(c.blocks).replace(/\s+/g, '')); const q = tx.findIndex(t => /^(문제|질문|문항)$/.test(t)), a = tx.findIndex(t => /^(정답|답|답안|해답)$/.test(t)), s = tx.findIndex(t => /^(암기법|스토리|넘버링|암기|넘버링스토리|두문자)$/.test(t)); if (q >= 0 && a >= 0) { hdr = ri; qi = q; ai = a; si = s; } });
    const span1 = r => r.cells.length === 1 || (r.cells.length && r.cells[0].span >= ncol);
    if (hdr >= 0) {
      layout = layout || 'qas';
      rows.forEach((r, ri) => {
        if (ri === hdr) return; const pos = 'T' + tix + 'r' + ri;
        if (span1(r)) { const t = blocksText(r.cells[0].blocks).trim(); if (t) newSec(t); return; }
        const cell = i => i >= 0 && r.cells[i] ? C.trim(r.cells[i].blocks) : [];
        const q = cell(qi), a = cell(ai); let s = cell(si);
        if (!q.length && !a.length && !s.length) return;
        const note = [], st = [];
        for (const b of s) { const mc = major(b.col); if (b.k === 'p' && (isGray(mc) || /^\s*\(?학습부/.test(b.text))) note.push(b); else st.push(b); }
        const rv = [];
        if (!blocksText(q).trim()) rv.push({ k: 'noq', m: '문제 칸이 비어 있음' });
        const at = blocksText(a), stt = blocksText(st);
        if ((/\?\s*$|\(\s*\)|\(\s{2,}\)/m.test(at) || /\(1\)[\s\S]*\(2\)/.test(at)) && /^\s*\(?1[).]/.test(stt) && stt.length < 300) rv.push({ k: 'shift', m: '정답 칸에 문제, 암기법 칸에 답이 있는 것 같음' });
        mkItem({ q: html(q), qtext: blocksText(q), a: html(a), st: html(st), note: note.map(b => b.text.trim()).join(' / '), tags: hlTags(q), rv, pos });
      });
      continue;
    }
    /* ② 2칸 — 문제 줄(왼·오 같은 글) + 내용 줄 */
    const two = rows.filter(r => r.cells.length === 2);
    const dupRows = two.filter(r => { const a = norm(blocksText(r.cells[0].blocks)), b = norm(blocksText(r.cells[1].blocks)); return a && (a === b || dice(a, b) > 0.85 || (b.length > 10 && a.startsWith(b)) || (a.length > 10 && b.startsWith(a))); }).length;
    if (ncol === 2 && (dupRows >= 2 || (layout === 'qrow' && dupRows >= 1))) {
      layout = layout || 'qrow';
      /* 문제 줄 = 왼·오 첫 문단이 같고(띄어쓰기·괄호 무시) 그 글이 문제처럼 보이거나 앞 문제에 이미 내용이 있을 때
         (앞 문제 줄 바로 뒤의 '보기만 있는 왼쪽 + 보기·답이 있는 오른쪽' 줄은 내용 줄 — 교정과 16번) */
      const QL = /(시오|하라|하세요|는가|인가|\?|쓰기|하기|그리기|서술|설명|기술|나열|열거|비교|채우|완성|고르|도해|표시|매칭|가지|이유|목적|방법|원인|특징|정의|종류|차이|단계|순서|기전|분류|적응증|금기|합병증|주의|빈칸|\(\d{2}\s*[,)탈짤]|\(탈)/;
      const firstP = bl => bl.find(x => !x.empty);
      const sameFirst = r => { const fa = firstP(r.cells[0].blocks), fb = firstP(r.cells[1].blocks); return !!(fa && fb && fa.k === 'p' && fb.k === 'p' && norm(fa.text).length >= 6 && (norm(fa.text) === norm(fb.text) || dice(fa.text, fb.text) > 0.88 || (norm(fb.text).length > 10 && norm(fa.text).startsWith(norm(fb.text))) || (norm(fa.text).length > 10 && norm(fb.text).startsWith(norm(fa.text))))); };
      const lc = {}; rows.forEach(r => { if (r.cells.length === 2 && !sameFirst(r)) { const c = colOf(r.cells[0].blocks); for (const k in c) if (k !== 'auto' && !isGray(k)) lc[k] = (lc[k] || 0) + c[k]; } });
      const tot = Object.values(lc).reduce((a, b) => a + b, 0), SC = new Set(Object.keys(lc).filter(k => lc[k] >= tot * 0.15));
      let cur = null;
      const has = c => c && (c.ab.length || c.sb.length || c.nb.length);
      const fin = () => { if (!cur) return; mkItem({ q: html(cur.qb), qtext: blocksText(cur.qb), a: html(cur.ab), st: html(cur.sb), note: cur.nb.map(b => b.text.trim()).join(' / '), tags: hlTags(cur.qb), rv: cur.rv, pos: cur.pos }); cur = null; };
      rows.forEach((r, ri) => {
        const pos = 'T' + tix + 'r' + ri;
        if (span1(r)) { const t = blocksText(r.cells[0].blocks).trim(); if (t) { fin(); newSec(t); } return; }
        if (r.cells.length !== 2) { if (cur) cur.rv.push({ k: 'odd', m: pos + ' 칸 수가 ' + r.cells.length + '개인 줄 — 넣지 않음' }); else flags.push({ k: 'odd', m: pos + ' 칸 수가 ' + r.cells.length + '개인 줄 — 넣지 않음' }); return; }
        const L = C.trim(r.cells[0].blocks), R = C.trim(r.cells[1].blocks);
        if (sameFirst(r) && (QL.test(blocksText(L)) || !cur || has(cur))) {
          fin();
          const lt = blocksText(L), rt = blocksText(R), rv = [];
          const q = L; let ax = [];
          if (norm(lt) !== norm(rt)) {   /* 앞 문단이 같은 데까지 = 문제 · 왼쪽 나머지 = 문제(빈칸·보기) · 오른쪽 나머지 = 답 */
            /* 첫 문단(문제 글)은 띄어쓰기·연도 괄호 차이만 있으면 같은 것으로 · 그 뒤 문단은 글자가 같을 때만 문제 — 다르면 왼쪽 = 문제(빈칸), 오른쪽 = 답(채운 글) — 오른쪽 글은 버리지 않음 */
            let k = 1; while (k < L.length && k < R.length && L[k].k === 'p' && R[k].k === 'p' && norm(L[k].text) === norm(R[k].text)) k++;
            ax = R.slice(k);
            const d = L.slice(0, k).map((b, i) => [b.text.trim(), R[i] && R[i].k === 'p' ? R[i].text.trim() : '']).filter(([x, y]) => norm(x) !== norm(y));
            if (d.length) rv.push({ k: 'qdiff', m: '왼쪽·오른쪽 문제 글이 조금 달라 왼쪽 글로 넣음', d: d.map(([x, y]) => '왼쪽: ' + x + '\n오른쪽: ' + y).join('\n') });
          }
          /* 문제 줄 오른쪽에만 있는 그림(답 그림 — 교정과 Biomechanics 3번)은 답으로: 글이 같아도 그림은 버리지 않음 */
          const ph = b => [...b.html.matchAll(/⟦IMG(\d+)⟧/g)].map(m => +m[1]), lt8 = new Set(L.flatMap(ph).map(i => pend[i].target));
          const ex = R.filter(b => !ax.includes(b)).flatMap(ph).filter(i => !lt8.has(pend[i].target));
          if (ex.length) { ax.unshift({ k: 'p', html: '<p>' + ex.map(i => '⟦IMG' + i + '⟧').join(' ') + '</p>', text: ' ', col: {}, hl: {}, img: ex.length, empty: false }); rv.push({ k: 'qimg', m: '문제 줄 오른쪽 칸에만 있는 그림 ' + ex.length + '개를 답 맨 앞에 넣음' }); }
          cur = { qb: q.slice(), ab: ax.slice(), sb: [], nb: [], rv, pos };
          return;
        }
        if (!cur) cur = { qb: [], ab: [], sb: [], nb: [], rv: [{ k: 'noq', m: '문제 줄 없이 시작한 내용(' + pos + ')' }], pos };
        for (const b of L) {
          if (b.empty) continue; const mc = major(b.col);
          if (b.k === 'p' && !b.img && (/^\s*\(?\s*학습부/.test(b.text) || isGray(mc))) cur.nb.push(b);
          else if (b.k === 't' || b.img) cur.qb.push(b);
          else if (!SC.size || SC.has(mc)) cur.sb.push(b);
          else cur.qb.push(b);
        }
        if (R.length) { const sc = R.filter(b => b.k === 'p' && !b.empty && (SC.has(major(b.col)) || major(b.col) === '#00B050')); if (sc.length) cur.rv.push({ k: 'stans', m: '답 칸에 스토리 색(초록·주황) 글씨가 있어 그대로 답에 둠: ' + sc.map(b => b.text.trim()).join(' / ').slice(0, 140) }); cur.ab.push(...R); }
      });
      fin();
      continue;
    }
    /* ③ 그 밖 — 첫 칸 문제 · 둘째 칸 답 · 셋째 칸 스토리(모두 검토) */
    layout = layout || 'guess';
    rows.forEach((r, ri) => {
      const pos = 'T' + tix + 'r' + ri;
      if (span1(r)) { const t = blocksText(r.cells[0].blocks).trim(); if (t) newSec(t); return; }
      const c = i => r.cells[i] ? C.trim(r.cells[i].blocks) : [];
      const q = c(0), a = c(1), s = c(2); if (!q.length && !a.length) return;
      mkItem({ q: html(q), qtext: blocksText(q), a: html(a), st: html(s), rv: [{ k: 'guess', m: '표 형식을 알아보지 못해 첫 칸=문제·둘째 칸=답·셋째 칸=스토리로 넣음' }], pos });
    });
  }
  /* 그림 줄이기 */
  prog('그림 줄이기 0/' + pend.length);
  const done = [];
  for (let i = 0; i < pend.length; i++) {
    const p = pend[i], path = 'word/' + p.target.replace(/^\/?word\//, '').replace(/^\.\//, '');
    let rep = '';
    try {
      const u8 = await zipGet(z, path);
      if (!u8) throw new Error('없음');
      const ext = (path.split('.').pop() || '').toLowerCase(), mime = { png: 'image/png', jpg: 'image/jpeg', jpeg: 'image/jpeg', gif: 'image/gif', bmp: 'image/bmp', webp: 'image/webp', tif: 'image/tiff', tiff: 'image/tiff' }[ext];
      if (!mime) throw new Error(ext + ' 형식');
      const h = fnv(u8);
      if (!images[h]) images[h] = await shrink(u8, mime, opt.maxW || 1100, opt.q || 0.8);
      const im = images[h], w = p.sz ? Math.min(p.sz.w, im.w) : im.w, hh = Math.round(w * im.h / im.w);
      rep = opt.img === 'id' ? '<img data-nimg="' + h + '" width="' + w + '" height="' + hh + '" alt="">' : '<img src="' + im.d + '" width="' + w + '" height="' + hh + '" alt="">';
    } catch (e) { rep = '<span class="nimgx">[그림을 열지 못함: ' + esc(p.target) + ']</span>'; flags.push({ k: 'img', m: '그림을 열지 못함: ' + p.target + ' (' + e.message + ')' }); }
    done[i] = rep;
    if (i % 3 === 2) { prog('그림 줄이기 ' + (i + 1) + '/' + pend.length); await yieldUI(); }
  }
  const fill = s => String(s || '').replace(/⟦IMG(\d+)⟧/g, (_, i) => done[+i] || '');
  for (const it of items) { it.q = fill(it.q); it.a = fill(it.a); it.st = fill(it.st); }
  if (ctx.strike) flags.push({ k: 'strike', m: '취소선 ' + ctx.strike + '곳 — 글자는 그대로, 취소선만 뺌' });
  const out = { title, legend, sections: sections.map(s => ({ k: s.k, title: s.title, raw: s.raw, lab: s.lab, prof: s.prof, date: s.date, n: s.n })), items, flags, layout, images: {} };
  for (const h in images) out.images[h] = { d: images[h].d, w: images[h].w, h: images[h].h };
  return out;
}

window.JBLDOCX = { parse, yearsTags, norm, dice };
})();
