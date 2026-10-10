/* JBL 넘버링 따기 (10-10) — 허브(index.html)가 '#/_num' 화면을 열 때만 불러오는 모듈. 홈·과목 화면의 첫 로딩에는 들어가지 않는다.
   화면: Word 문서처럼 한 과목의 문제가 모두 펼쳐진 채 위에서 아래로 — 문제 머리(번호·출처·연도) → 문제 → 왼쪽 답안 | 오른쪽 넘버링 스토리.
   저장: 허브와 같은 localStorage 이름 공간(jblhub.v1.) — 문제마다 한 키 'num.i.<과목>.<id>'(고친 문제만 다시 씀) · 과목 정보 'num.x.<과목>' · 보기 설정 'num.cfg' · 내가 만든 과목 'num.subj'
     → 허브 백업 파일·자동 백업(dumpAll)에 그대로 들어가고, 백업 합치기(mergeData)는 문제마다 더 최근 것(u)이 이김.
   원본 보존: JB 기출·예상문제·Word 기본 자료(docs/num/seed.*.js)는 읽기만 — 고친 글은 작업본으로만 저장, '원본으로'로 언제든 되돌림. 목록에서 빼도 원본은 그대로.
   빠르게: 읽을 때는 가벼운 HTML만(content-visibility로 화면 밖 문제는 그리지 않음) · 편집기는 누른 칸 하나만 · 저장은 입력이 멈춘 뒤(0.7초) 그 문제만 · 검색은 0.2초 기다렸다가 숨김만 바꿈. */
(function () {
'use strict';
let H = null;   /* 허브가 넘겨 줌: LS·NS·LSQ·toast·PACKS·SUBJECTS·sjColor·openDoc·histSet·base·plStat */
const $ = (s, e) => (e || document).querySelector(s), $$ = (s, e) => [...(e || document).querySelectorAll(s)];
const esc = s => String(s == null ? '' : s).replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
const now = () => Date.now();
const TYPES = { num: '넘버링형', essay: '서술형', blank: '빈칸형', mc: '객관식', short: '단답형' };
const STN = ['미작성', '작성 중', '완성'];
const KIND = { seed: 'Word 자료', jb: 'JB 기출', pred: '예상문제', user: '직접 추가', word: 'Word 가져옴' };
const S = { root: null, sj: '', cfg: null, items: [], by: new Map(), lecs: [], seed: null, ed: null, q: '', sel: new Set(), selMode: false, tok: 0, saveSt: '', idxLoaded: null };

/* ---------- 글 ---------- */
const ENT = { amp: '&', lt: '<', gt: '>', quot: '"', nbsp: ' ', '#39': "'" };
const plain = h => String(h || '').replace(/<br\s*\/?>/gi, '\n').replace(/<\/(p|div|li|tr)>/gi, '\n').replace(/<\/t[dh]>/gi, ' ').replace(/<[^>]+>/g, '').replace(/&(#?\w+);/g, (m, k) => ENT[k] != null ? ENT[k] : k[0] === '#' ? String.fromCharCode(k[1] === 'x' ? parseInt(k.slice(2), 16) : +k.slice(1)) : m);
const norm = s => String(s || '').replace(/[\s ]+/g, '').replace(/[(){}\[\].,·:;!?~\-–—'"“”‘’/<>*]/g, '').toLowerCase();
const qKey = h => norm(plain(h).replace(/^\s*\d{1,2}\s*[.)]\s*/, '').replace(/\((?:\s*\d{2}[^)]*|[^)]*(?:기출|과거|탈|짤|출제|예고|강조)[^)]*)\)/g, ''));
const isEmpty = h => !/<img\b/i.test(h || '') && !plain(h).replace(/\s/g, '');
function bigrams(s) { const m = new Map(); for (let i = 0; i < s.length - 1; i++) { const g = s.substr(i, 2); m.set(g, (m.get(g) || 0) + 1); } return m; }
function dice(a, b) { if (a === b) return 1; if (a.length < 2 || b.length < 2) return 0; const A = bigrams(a); let n = 0; for (let i = 0; i < b.length - 1; i++) { const g = b.substr(i, 2), c = A.get(g); if (c) { n++; A.set(g, c - 1); } } return 2 * n / (a.length + b.length - 2); }
const yrsTxt = y => (y || []).slice().sort((a, b) => b - a).join(' · ');
const parseYrs = s => [...new Set((String(s || '').match(/\d{2,4}/g) || []).map(x => +x < 100 ? 2000 + +x : +x).filter(y => y >= 2005 && y <= 2035))].sort((a, b) => b - a);
const stOf = it => it.done ? 2 : isEmpty(it.st) ? 0 : 1;
/* 문제 유형 — 기존 자료에 유형 정보가 없어(예상문제 v/n은 짤 변형·미출제) 문제 글과 답 모양으로 판정. 불러오기에서는 '전체 보기'로 직접 고를 수 있음 */
function qType(q, a) {
  const Q = plain(q).trim(), A = plain(a).trim(), L = Q.split('\n'), head = L[0] || '', rest = L.slice(1).join('\n');
  const opts = (rest.match(/^\s*(?:\(?\d{1,2}\)|\d{1,2}\s*[.)]|[①-⑳]|[ㄱ-ㅎ]\s*[-.)]|[a-e]\s*[.)])\s*\S/gm) || []).length;   /* 둘째 줄부터의 보기 */
  const write = /서술하|설명하시오|설명하라|설명하세요|기술하|논하|쓰시오|쓰고|적으시오|그리시오|도해|나열하|열거하/.test(Q);
  if (/고르시오|고르면|고르고|고르세요|골라|옳은\s*것|옳지\s*않은|틀린\s*것|맞는\s*것|T\s*\/\s*F|O\s*\/\s*X|참\s*\/\s*거짓|선지|객관식|\[객\]/.test(Q) && !write) return 'mc';
  if (opts >= 3 && !write && (/\?\s*(?:\(|\[|$)|다음\s*중|것은|것을|적합한|해당하는/.test(head) || A.replace(/\s/g, '').length < 80)) return 'mc';
  const n = (A.match(/^\s*(?:\d{1,2}\s*[.)]|[①-⑳]|\(\d{1,2}\)|[a-zA-Z]\s*[.)]|[-•▪◦➢*]|[가-하]\s*[.)])\s*\S/gm) || []).length;
  if (/빈칸|채우시오|채워\s*넣|완성하시오|\(\s{0,3}\)|_{3,}/.test(Q) && !/\d+\s*가지/.test(Q)) return 'blank';
  if (/\d+\s*가지|몇\s*가지|나열|열거|모두\s*(?:쓰|적|기술)|종류|분류|단계|순서|요소|조건|원인|증상|소견|합병증|적응증|금기|부작용|주의\s*사항|특징|방법|목표|이유|목적|고려\s*사항|변화/.test(Q) && n >= 2 || n >= 3) return 'num';
  if (write || /비교|이유|목적|기전|차이|정의|의의|어떻게|왜/.test(Q) || A.replace(/\s/g, '').length >= 150) return 'essay';
  return 'short';
}
const essayish = t => t === 'num' || t === 'essay';

/* ---------- 붙여넣기·저장 전 정리(허용: 문단·줄바꿈·굵게·기울임·밑줄·위아래 첨자·글자색·형광펜·목록·표·그림 / 취소선은 글자만) ---------- */
const OKT = new Set(['P', 'BR', 'B', 'I', 'U', 'SUP', 'SUB', 'SPAN', 'TABLE', 'TBODY', 'THEAD', 'TR', 'TD', 'TH', 'UL', 'OL', 'LI', 'IMG']);
const REN = { STRONG: 'B', EM: 'I', DIV: 'P', H1: 'P', H2: 'P', H3: 'P', H4: 'P', H5: 'P', H6: 'P', BLOCKQUOTE: 'P', INS: 'U', TFOOT: 'TBODY', CAPTION: 'P', DT: 'P', DD: 'P', PRE: 'P', SECTION: 'P', ARTICLE: 'P', HEADER: 'P', FOOTER: 'P' };
const DROP = new Set(['SCRIPT', 'STYLE', 'INPUT', 'SELECT', 'TEXTAREA', 'IFRAME', 'OBJECT', 'EMBED', 'SVG', 'CANVAS', 'VIDEO', 'AUDIO', 'LINK', 'META', 'TITLE', 'HEAD', 'NOSCRIPT', 'TEMPLATE', 'COLGROUP', 'COL']);
const HLN = { yellow: '#FFFF00', green: '#00FF00', cyan: '#00FFFF', magenta: '#FF00FF', blue: '#0000FF', red: '#FF0000', darkblue: '#000080', darkcyan: '#008080', darkgreen: '#008000', darkmagenta: '#800080', darkred: '#800000', darkyellow: '#808000', darkgray: '#808080', lightgray: '#C0C0C0', black: '#000000', white: '#FFFFFF' };
function hexc(v) {
  v = String(v || '').trim().toLowerCase(); if (!v || v === 'transparent' || v === 'inherit' || v === 'initial' || v === 'auto' || v === 'windowtext' || v === 'none') return '';
  let m = /^#([0-9a-f]{3})$/.exec(v); if (m) return '#' + m[1].split('').map(c => c + c).join('').toUpperCase();
  m = /^#([0-9a-f]{6})$/.exec(v); if (m) return '#' + m[1].toUpperCase();
  m = /^rgba?\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)(?:\s*,\s*([\d.]+))?\s*\)$/.exec(v); if (m) { if (m[4] != null && +m[4] < 0.1) return ''; return '#' + [m[1], m[2], m[3]].map(x => (+x).toString(16).padStart(2, '0')).join('').toUpperCase(); }
  if (HLN[v]) return HLN[v];
  return /^[a-z]+$/.test(v) && v.length < 20 ? v : '';
}
function sanitize(html, opt) {
  opt = opt || {};
  const t = document.createElement('template'); t.innerHTML = String(html || '');
  const walk = (el) => {
    for (let c = el.firstChild; c;) {
      const nx = c.nextSibling;
      if (c.nodeType === 8) { c.remove(); c = nx; continue; }
      if (c.nodeType === 3) { if (opt.paste) c.data = c.data.replace(/[\r\n\t ]*\n[\r\n\t ]*/g, ' '); c = nx; continue; }
      if (c.nodeType !== 1) { c.remove(); c = nx; continue; }
      let tg = c.tagName.toUpperCase();
      if (DROP.has(tg)) { c.remove(); c = nx; continue; }
      if (tg === 'IMG') {
        const src = c.getAttribute('src') || '', ni = c.getAttribute('data-nimg');
        if (!(ni && /^[\w.-]+$/.test(ni)) && !/^data:image\/(png|jpe?g|gif|webp);base64,/i.test(src)) { if (opt.paste && src) S.pasteLost = (S.pasteLost || 0) + 1; c.remove(); c = nx; continue; }
        const w = +c.getAttribute('width') || 0, h = +c.getAttribute('height') || 0;
        for (const a of [...c.attributes]) c.removeAttribute(a.name);
        if (ni && /^[\w.-]+$/.test(ni)) c.setAttribute('data-nimg', ni); else c.setAttribute('src', src);
        if (w) c.setAttribute('width', String(Math.round(w))); if (h) c.setAttribute('height', String(Math.round(h))); c.setAttribute('alt', '');
        c = nx; continue;
      }
      if ((tg === 'OL' || tg === 'UL') && /\bcirc\b/.test(c.className || '')) {   /* 예상문제 답의 ①②③ 목록(번호가 글자에 이미 있음) → 문단 */
        const f = document.createDocumentFragment(); for (const li of [...c.children]) { const p = document.createElement('p'); while (li.firstChild) p.appendChild(li.firstChild); f.appendChild(p); }
        c.replaceWith(f); c = nx; continue;
      }
      if (/:/.test(c.tagName) || tg === 'FONT' && false) { walk(c); c.replaceWith(...c.childNodes); c = nx; continue; }   /* o:p·v:shape 등 Word 이름표 */
      if (REN[tg]) { const n = document.createElement(REN[tg]); for (const a of [...c.attributes]) if (a.name === 'style') n.setAttribute('style', a.value); while (c.firstChild) n.appendChild(c.firstChild); c.replaceWith(n); c = n; tg = REN[tg]; }
      walk(c);
      /* 모양(style) → 굵게·기울임·밑줄·글자색·형광펜만 */
      const st = c.getAttribute('style') || '', sv = {};
      st.split(';').forEach(d => { const i = d.indexOf(':'); if (i > 0) sv[d.slice(0, i).trim().toLowerCase()] = d.slice(i + 1).trim(); });
      const col = hexc(sv['color']), bg = hexc(sv['mso-highlight'] || sv['background-color'] || (sv['background'] && !/url\(/i.test(sv['background']) ? sv['background'].split(/\s+/)[0] : ''));
      const fw = sv['font-weight'] || '', bold = /bold|[6-9]00/.test(fw), ital = /italic/.test(sv['font-style'] || ''), und = /underline/.test(sv['text-decoration'] || sv['text-decoration-line'] || ''), al = /^(center|right)$/.test(sv['text-align'] || '') ? sv['text-align'] : '';
      if (tg === 'S' || tg === 'STRIKE' || tg === 'DEL') { c.replaceWith(...c.childNodes); c = nx; continue; }
      if (tg === 'FONT') { const fc = hexc(c.getAttribute('color')); const sp = document.createElement('span'); if (fc) sp.style.color = fc; while (c.firstChild) sp.appendChild(c.firstChild); c.replaceWith(sp); c = sp; tg = 'SPAN'; }
      if (!OKT.has(tg)) { c.replaceWith(...c.childNodes); c = nx; continue; }
      const keep = {};
      if (tg === 'TD' || tg === 'TH') { const cs = +c.getAttribute('colspan') || 0, rs = +c.getAttribute('rowspan') || 0; if (cs > 1) keep.colspan = String(cs); if (rs > 1) keep.rowspan = String(rs); }
      for (const a of [...c.attributes]) c.removeAttribute(a.name);
      for (const k in keep) c.setAttribute(k, keep[k]);
      let css = '';
      if (tg === 'SPAN' || tg === 'TD' || tg === 'TH' || tg === 'P' || tg === 'LI' || tg === 'B' || tg === 'U' || tg === 'I') { if (col && col !== '#000000') css += 'color:' + col + ';'; if (bg && bg !== '#FFFFFF') css += 'background-color:' + bg + ';'; }
      if ((tg === 'P' || tg === 'TD' || tg === 'TH') && al) css += 'text-align:' + al + ';';
      if (css) c.setAttribute('style', css);
      let host = c;
      if (bold && tg !== 'B' && !(tg === 'TH')) { const b = document.createElement('b'); while (host.firstChild) b.appendChild(host.firstChild); host.appendChild(b); }
      if (ital && tg !== 'I') { const b = document.createElement('i'); while (host.firstChild) b.appendChild(host.firstChild); host.appendChild(b); }
      if (und && tg !== 'U') { const b = document.createElement('u'); while (host.firstChild) b.appendChild(host.firstChild); host.appendChild(b); }
      if (tg === 'SPAN' && !c.getAttribute('style')) { c.replaceWith(...c.childNodes); }
      c = nx;
    }
  };
  walk(t.content);
  /* 표 밖 맨글자 덩어리는 문단으로 묶음 */
  const d = document.createElement('div'); d.appendChild(t.content);
  let out = d.innerHTML.replace(/<p><\/p>/g, '<p><br></p>');
  return out;
}
const toStore = h => sanitize(h);
const disp = h => String(h || '').replace(/<img data-nimg="([\w.-]+)"/g, (m, k) => '<img data-nimg="' + k + '" src="' + H.base + 'num/img/' + k + '" loading="lazy" decoding="async"');

/* ---------- 저장 ---------- */
const keyI = (sj, id) => 'num.i.' + sj + '.' + id;
function cfg() { if (!S.cfg) { const c = H.LS.get('num.cfg', null) || {}; S.cfg = { sj: c.sj || '', mode: c.mode === 'all' ? 'all' : 'grp', sort: c.sort || 'lec', f: Object.assign({ lec: '', type: '', st: '', src: '', yr: '' }, c.f || {}) }; } return S.cfg; }
function cfgSave() { H.LS.set('num.cfg', S.cfg); }
function idx(sj) { const x = H.LS.get('num.x.' + sj, null); return x && typeof x === 'object' ? x : { v: 1, ul: [], lt: {} }; }
function idxPut(sj, x) { x.u = now(); H.LS.set('num.x.' + sj, x); }
function saveState(st, msg) {
  S.saveSt = st; const e = S.root && $('.nm-save', S.root); if (!e) return;
  e.className = 'nm-save ' + st; e.textContent = st === 'ok' ? '저장됨 ✓' : st === 'ing' ? '저장 중…' : st === 'bad' ? '⚠ ' + (msg || '저장 실패') : '';
  if (st === 'ok') { clearTimeout(saveState.t); saveState.t = setTimeout(() => { if (S.saveSt === 'ok' && e.isConnected) e.textContent = '자동 저장'; }, 2500); }
}
function rawPut(k, v) {   /* 바로 쓰고 결과를 돌려줌(실패하면 허브 LS 대기열 — 다음에 다시 씀 · IndexedDB 비춤) */
  const s = JSON.stringify(v);
  try { localStorage.setItem(H.NS + k, s); if (H.LSQ && H.LSQ.has(k)) H.LSQ.delete(k); return true; }
  catch (e) { try { H.LS.set(k, v); } catch (_) {} return false; }
}
function rawDel(k) { try { localStorage.removeItem(H.NS + k); } catch (e) {} if (H.LSQ && H.LSQ.has(k)) H.LSQ.delete(k); }
const same = (a, b) => JSON.stringify(a || []) === JSON.stringify(b || []);
function toRec(it) {
  const o = { id: it.id, k: it.kind };
  if (it.kind === 'seed') {
    const b = it.base;
    if (it.lec !== b.lec) o.lec = it.lec; if (it.q !== b.q) o.q = it.q; if (it.a !== b.a) o.a = it.a; if (it.st !== (b.st || '')) o.st = it.st; if (it.note !== (b.note || '')) o.note = it.note;
    if (!same(it.tags, b.tags)) o.tags = it.tags; if (!same(it.yrs, b.yrs)) o.yrs = it.yrs; if (it.src.length !== 1 || it.src[0].t !== 'seed') o.src = it.src; if (it.o !== it.oi) o.o = it.o;
  } else Object.assign(o, { lec: it.lec, q: it.q, a: it.a, st: it.st, note: it.note, tags: it.tags, yrs: it.yrs, src: it.src, o: it.o, c: it.c }, it.ref ? { ref: it.ref } : {}, it.q0 != null ? { q0: it.q0 } : {}, it.a0 != null ? { a0: it.a0 } : {}, it.rv && it.rv.length ? { rv: it.rv } : {});
  if (it.done) o.done = 1; if (it.del) o.del = 1; if (it.rvok) o.rvok = 1; if (it.prev) o.prev = it.prev;
  o.u = it.u || now(); if (it.c) o.c = it.c;
  return o;
}
function put(it) {
  const o = toRec(it), k = keyI(it.s, it.id);
  if (it.kind === 'seed' && Object.keys(o).every(x => x === 'id' || x === 'k' || x === 'u' || x === 'c')) { rawDel(k); saveState('ok'); return true; }   /* 원본과 같아짐 = 작업본 없음 */
  const ok = rawPut(k, o);
  saveState(ok ? 'ok' : 'bad', ok ? '' : '이 기기 저장 공간이 부족해요 — 백업 파일을 받아 두고 [복원] 창에서 공간을 정리해 주세요(쓴 글은 이 창이 열려 있는 동안 남아 있어요)');
  if (!ok) H.toast('넘버링 저장 공간이 부족해요 — 백업 파일을 받아 두세요', { level: 'error', id: 'nmquota' });
  return ok;
}
function touch(it) { it.u = now(); it._t = null; it._k = null; }
const kOf = it => (it._k != null ? it._k : (it._k = qKey(it.q)));

/* ---------- 자료 ---------- */
function loadScript(src) { return new Promise((res, rej) => { const s = document.createElement('script'); s.src = src; s.onload = () => res(); s.onerror = () => { s.remove(); rej(new Error('불러오지 못했어요: ' + src.split('?')[0])); }; document.head.appendChild(s); }); }
async function index() { if (!window.JBLNUM_INDEX) { try { await loadScript(H.base + 'num/seed.js?v=' + H.v); } catch (e) { window.JBLNUM_INDEX = []; } } return window.JBLNUM_INDEX || []; }
async function seedOf(sj) { const x = (window.JBLNUM_INDEX || []).find(o => o.id === sj); if (!x) return null; window.JBLNUM_SEED = window.JBLNUM_SEED || {}; if (!window.JBLNUM_SEED[sj]) await loadScript(H.base + 'num/seed.' + sj + '.js?v=' + x.v); return window.JBLNUM_SEED[sj] || null; }
function subjects() {
  const out = [], X = window.JBLNUM_INDEX || [];
  for (const [id, ko, sh] of H.SUBJECTS) out.push({ id, t: ko, sh: sh || ko, jbl: true });
  for (const x of X) if (!out.some(o => o.id === x.id)) out.push({ id: x.id, t: x.t, sh: x.short || x.t, seed: x });
  for (const x of (H.LS.get('num.subj', []) || [])) if (x && x.id && !out.some(o => o.id === x.id)) out.push({ id: x.id, t: x.t, sh: x.t, user: true });
  return out;
}
const subjT = sj => { const x = subjects().find(o => o.id === sj); return x ? x.t : sj; };
function loadRecs(sj) {
  const P = H.NS + 'num.i.' + sj + '.', out = new Map();
  for (let i = 0; i < localStorage.length; i++) { const k = localStorage.key(i); if (k && k.indexOf(P) === 0) { try { const r = JSON.parse(localStorage.getItem(k)); if (r && r.id) out.set(r.id, r); } catch (e) {} } }
  if (H.LSQ) for (const [k, v] of H.LSQ) if (k.indexOf('num.i.' + sj + '.') === 0) { try { const r = JSON.parse(v); if (r && r.id) out.set(r.id, r); } catch (e) {} }
  return out;
}
function seedLab(seed, b) { const m = seed.meta || {}; return (m.short || m.t) + ' Word' + (b.lab ? ' · ' + b.lab : ''); }
function mkSeed(sj, b, r, i, seed) {
  r = r || {};
  return { id: b.id, s: sj, kind: 'seed', base: b, oi: i, lec: r.lec != null ? r.lec : b.lec, q: r.q != null ? r.q : b.q, a: r.a != null ? r.a : b.a, st: r.st != null ? r.st : (b.st || ''), note: r.note != null ? r.note : (b.note || ''), tags: r.tags || b.tags || [], yrs: r.yrs || b.yrs || [], src: r.src || [{ t: 'seed', s: sj, id: b.id, lab: seedLab(seed, b), yrs: b.yrs || [] }], done: !!r.done, o: r.o != null ? r.o : i, c: r.c || 0, u: r.u || 0, del: !!r.del, rv: b.rv || [], rvok: !!r.rvok, prev: r.prev || null };
}
function mkRec(sj, r) { return { id: r.id, s: sj, kind: r.k || 'user', lec: r.lec || '', q: r.q || '', a: r.a || '', st: r.st || '', note: r.note || '', tags: r.tags || [], yrs: r.yrs || [], src: r.src || [], ref: r.ref || null, q0: r.q0, a0: r.a0, done: !!r.done, o: r.o != null ? r.o : 1e6, c: r.c || 0, u: r.u || 0, del: !!r.del, rv: r.rv || [], rvok: !!r.rvok, prev: r.prev || null }; }
function lectures(sj, seed) {
  const L = [], P = H.PACKS[sj], X = idx(sj);
  if (P) P.lect.forEach(l => L.push({ k: l.k, t: l.title, prof: l.prof || '' }));
  if (seed) seed.lecs.forEach(l => L.push({ k: l.k, t: l.t, prof: l.prof || '', lab: l.lab || '' }));
  (X.ul || []).forEach(l => { if (l && l.k && !L.some(x => x.k === l.k)) L.push({ k: l.k, t: l.t, user: 1 }); });
  for (const l of L) if (X.lt && X.lt[l.k]) l.t = X.lt[l.k];
  L.push({ k: '', t: '강의 미분류' });
  return L;
}
async function loadSubject(sj) {
  const seed = await seedOf(sj).catch(e => { H.toast(e.message, { level: 'error', id: 'nmseed' }); return null; });
  const R = loadRecs(sj), items = [];
  if (seed) seed.items.forEach((b, i) => { items.push(mkSeed(sj, b, R.get(b.id), i, seed)); R.delete(b.id); });
  for (const r of R.values()) if (!/^sd:/.test(r.id) || !seed) items.push(mkRec(sj, r));
  S.seed = seed; S.items = items; S.by = new Map(items.map(it => [it.id, it])); S.lecs = lectures(sj, seed);
}
const lecOf = k => S.lecs.find(l => l.k === k) || S.lecs[S.lecs.length - 1];
const lecIdx = k => { const i = S.lecs.findIndex(l => l.k === k); return i < 0 ? S.lecs.length - 1 : i; };
function txt(it) { if (!it._t) it._t = (plain(it.q) + '\n' + plain(it.a) + '\n' + plain(it.st) + '\n' + it.note + '\n' + it.src.map(s => s.lab || '').join(' ') + ' ' + (KIND[it.kind] || '') + '\n' + lecOf(it.lec).t + ' ' + (it.tags || []).join(' ')).toLowerCase(); return it._t; }
function tyOf(it) { if (!it._ty) it._ty = qType(it.q, it.a); return it._ty; }

/* ---------- 화면 ---------- */
const STYLE = `
#numv{--nmw:1360px;max-width:var(--nmw);margin:0 auto}
body.v-num #home{max-width:1440px}
#numv .nm-tabs{display:flex;gap:6px;align-items:center;flex-wrap:wrap;margin:0 0 10px}
#numv .nm-tab{border:1px solid var(--line);background:var(--card);color:var(--ink);border-radius:999px;padding:6px 14px;font-size:14px;font-weight:600}
#numv .nm-tab.on{background:var(--acc,#0F5C5A);border-color:var(--acc,#0F5C5A);color:#fff}
#numv .nm-tab[aria-disabled=true]{color:var(--sub);background:transparent;border-style:dashed;cursor:not-allowed;font-weight:500}
#numv .nm-tab small{font-weight:500;font-size:12px}
#numv .nm-save{margin-left:auto;font-size:13px;color:var(--sub)}#numv .nm-save.ing{color:var(--sub)}#numv .nm-save.ok{color:#2E7D4F}#numv .nm-save.bad{color:#B3261E;font-weight:600}
#numv .nm-bar{display:flex;flex-wrap:wrap;gap:6px 8px;align-items:center;margin:0 0 6px}
#numv .nm-bar select,#numv .nm-bar input[type=search],#numv .nm-dlg select,#numv .nm-dlg input[type=text],#numv .nm-dlg input[type=search]{font:inherit;font-size:14px;padding:6px 8px;border:1px solid var(--line);border-radius:8px;background:var(--card);color:var(--ink);min-height:34px;max-width:100%}
#numv .nm-bar input[type=search]{flex:1 1 220px;min-width:160px}
#numv .nm-bar .nm-sp{flex:1 1 0}
#numv .nm-seg{display:inline-flex;border:1px solid var(--line);border-radius:8px;overflow:hidden}
#numv .nm-seg button{border:0;background:var(--card);color:var(--ink);padding:6px 10px;font-size:13px;min-height:34px}#numv .nm-seg button.on{background:var(--ink);color:var(--card)}
#numv .nm-btn{border:1px solid var(--line);background:var(--card);color:var(--ink);border-radius:8px;padding:6px 11px;font-size:13.5px;min-height:34px;font-weight:600;cursor:pointer}
#numv .nm-btn.pri{background:var(--acc,#0F5C5A);border-color:var(--acc,#0F5C5A);color:#fff}
#numv .nm-btn:disabled{opacity:.5;cursor:default}
#numv .nm-cnt{display:flex;flex-wrap:wrap;gap:4px 12px;font-size:13px;color:var(--sub);margin:4px 0 12px;align-items:center}
#numv .nm-cnt button{border:0;background:none;color:inherit;font:inherit;padding:2px 0;cursor:pointer;border-bottom:1px dashed transparent}#numv .nm-cnt button.on{color:var(--ink);font-weight:700;border-bottom-color:var(--ink)}
#numv .nm-cnt b{color:var(--ink)}
#numv .nm-batch{position:sticky;top:calc(var(--toph,52px) + 4px);z-index:6;display:flex;flex-wrap:wrap;gap:6px;align-items:center;background:var(--card);border:1px solid var(--line);border-radius:10px;padding:8px 10px;margin:0 0 10px;box-shadow:0 2px 10px rgba(0,0,0,.08)}
#numv .nm-doc{background:#FFFFFF;color:#1F1D1A;border:1px solid var(--line);border-radius:6px;padding:8px 28px 40px;box-shadow:0 1px 3px rgba(0,0,0,.04)}
#numv .nm-lec{font-family:inherit;font-size:19px;font-weight:800;margin:26px 0 4px;padding:10px 0 8px;border-bottom:2px solid #1F1D1A;color:#1F1D1A;display:flex;gap:10px;align-items:baseline;flex-wrap:wrap}
#numv .nm-lec small{font-size:13px;font-weight:500;color:#6A6257}
#numv .nm-lec:first-child{margin-top:8px}
#numv .nm-it{content-visibility:auto;contain-intrinsic-size:auto 420px;padding:16px 0 18px;border-bottom:1px solid #E4DFD5}
#numv .nm-it.flash{animation:nmfl 1.6s ease-out}@keyframes nmfl{0%{background:#FFF3C8}100%{background:transparent}}
#numv .nm-h{display:flex;flex-wrap:wrap;gap:4px 8px;align-items:center;font-size:12.5px;color:#6A6257;margin:0 0 6px}
#numv .nm-no{font-weight:800;color:#1F1D1A;font-size:14px;min-width:1.6em}
#numv .nm-chip{display:inline-block;border:1px solid #E1D9CB;border-radius:999px;padding:0 7px;line-height:19px;font-size:12px;color:#4A4339;background:#FAF7F1;white-space:nowrap}
#numv .nm-chip.yr{border-color:#C9D9E8;background:#F0F5FA;color:#24466B;font-weight:600}
#numv .nm-chip.k-jb{border-color:#D8C9E8;background:#F6F1FB;color:#4F2F78}#numv .nm-chip.k-pred{border-color:#E8D9C1;background:#FBF5EA;color:#6B4A12}#numv .nm-chip.k-seed,#numv .nm-chip.k-word{border-color:#C8DFD3;background:#EFF7F2;color:#1E5A3B}
#numv .nm-chip.s0{color:#8C857A}#numv .nm-chip.s1{color:#8A5A00;border-color:#EBD7A8;background:#FFF8E6}#numv .nm-chip.s2{color:#1E6B3E;border-color:#B9DCC5;background:#EDF8F1;font-weight:700}
#numv .nm-chip.rv{color:#9A3412;border-color:#F0C9B0;background:#FFF4EC;cursor:pointer}
#numv .nm-chip.ed{color:#6A6257;border-style:dashed}
#numv .nm-h .nm-gap{flex:1 1 auto}
#numv .nm-more{border:1px solid transparent;background:none;color:#6A6257;border-radius:6px;padding:0 8px;font-size:18px;line-height:26px;cursor:pointer;min-width:34px;min-height:30px}
#numv .nm-more:hover,#numv .nm-more:focus-visible{border-color:#E1D9CB;background:#FAF7F1}
#numv .nm-ck{display:none;align-items:center}#numv.selm .nm-ck{display:inline-flex}#numv .nm-ck input{width:18px;height:18px}
#numv .nm-q{font-weight:600;font-size:15.5px;line-height:1.6;margin:0 0 10px;display:flex;flex-wrap:wrap;gap:4px 8px;align-items:flex-start}
#numv .nm-q>.nm-c{flex:1 1 0;min-width:0}
#numv .nm-q>.nm-tb{flex:1 1 100%}
#numv .nm-ql{font-size:11.5px;font-weight:700;color:#fff;background:#3A342D;border-radius:4px;padding:0 6px;line-height:19px;margin-top:3px;flex:none}
#numv .nm-q>.nm-edb{margin-top:3px;flex:none}
#numv .nm-body{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1fr);gap:0;border:1px solid #E4DFD5;border-radius:4px}
#numv .nm-col{min-width:0;padding:8px 12px 10px}
#numv .nm-col+.nm-col{border-left:1px solid #E4DFD5}
#numv .nm-lab{display:flex;align-items:center;gap:6px;font-size:11.5px;font-weight:700;color:#8C857A;letter-spacing:.02em;margin:0 0 4px;min-height:22px}
#numv .nm-edb{border:1px solid #E1D9CB;background:#fff;color:#6A6257;border-radius:6px;font-size:11.5px;padding:0 7px;line-height:20px;cursor:pointer;opacity:.75}
#numv .nm-it:hover .nm-edb,#numv .nm-edb:focus-visible{opacity:1}
#numv .nm-c{font-size:14.5px;line-height:1.62;white-space:pre-wrap;word-break:keep-all;overflow-wrap:anywhere;min-height:1.6em;outline:none}
#numv .nm-c p,#numv .nm-q p{margin:0}
#numv .nm-q .nm-c{font-size:inherit;line-height:inherit}
#numv .nm-c table,#numv .nm-q table{border-collapse:collapse;margin:4px 0;max-width:100%;font-size:13.5px;white-space:normal}
#numv .nm-c td,#numv .nm-c th,#numv .nm-q td,#numv .nm-q th{border:1px solid #BDB5A8;padding:3px 6px;vertical-align:top;min-width:2.5em}
#numv .nm-tw{overflow-x:auto;max-width:100%}
#numv .nm-c img,#numv .nm-q img{max-width:100%;height:auto;vertical-align:top;margin:2px 0}
#numv .nm-c ul,#numv .nm-c ol{margin:2px 0;padding-left:1.6em;white-space:normal}
#numv .nm-c li{white-space:pre-wrap}
#numv .nm-s .nm-c{cursor:text;border-radius:4px;transition:background .15s}
#numv .nm-s .nm-c:not([contenteditable=true]):hover{background:#FBF8F2}
#numv .nm-ph{color:#A39B8E;font-weight:400}
#numv .nm-note{font-size:12.5px;color:#6A6257;margin:8px 0 0;white-space:pre-wrap}
#numv [contenteditable=true]{background:#FFFDF6;box-shadow:inset 0 0 0 2px #E8C766;border-radius:4px;padding:2px 4px;cursor:text}
#numv .nm-tb{position:sticky;top:calc(var(--toph,52px) + 2px);z-index:8;display:flex;flex-wrap:wrap;gap:3px;align-items:center;background:#2F2A24;color:#fff;border-radius:8px;padding:4px 6px;margin:0 0 6px;box-shadow:0 3px 12px rgba(0,0,0,.18)}
#numv .nm-tb button{border:0;background:transparent;color:#fff;border-radius:5px;min-width:32px;height:30px;padding:0 7px;font-size:14px;cursor:pointer}
#numv .nm-tb button:hover,#numv .nm-tb button:focus-visible,#numv .nm-tb button.on{background:rgba(255,255,255,.16)}
#numv .nm-tb i.sep{width:1px;height:20px;background:rgba(255,255,255,.25);margin:0 3px}
#numv .nm-tb .done{margin-left:auto;background:#E8C766;color:#2F2A24;font-weight:700}
#numv .nm-pal{position:absolute;z-index:40;background:#fff;color:#1F1D1A;border:1px solid #D8D0C2;border-radius:8px;padding:6px;display:flex;flex-wrap:wrap;gap:4px;width:188px;box-shadow:0 6px 20px rgba(0,0,0,.18)}
#numv .nm-pal button{width:28px;height:28px;border-radius:6px;border:1px solid #D8D0C2;cursor:pointer}
#numv .nm-pal .wide{width:auto;padding:0 8px;font-size:12.5px;background:#fff}
#numv .nm-menu{position:absolute;z-index:40;background:var(--card);color:var(--ink);border:1px solid var(--line);border-radius:10px;padding:4px;min-width:220px;max-width:min(320px,92vw);box-shadow:0 8px 28px rgba(0,0,0,.18)}
#numv .nm-menu button{display:block;width:100%;text-align:left;border:0;background:none;color:inherit;padding:8px 10px;border-radius:7px;font-size:14px;cursor:pointer;min-height:36px}
#numv .nm-menu button:hover,#numv .nm-menu button:focus-visible{background:var(--tint,#F2EEE6)}
#numv .nm-menu hr{border:0;border-top:1px solid var(--line);margin:4px 0}
#numv .nm-menu .warn{color:#B3261E}
#numv .nm-det{margin:10px 0 0;padding:10px 12px;border:1px solid #E4DFD5;border-radius:6px;background:#FCFBF8;font-size:13.5px;display:grid;gap:8px}
#numv .nm-det label{display:grid;grid-template-columns:7.5em 1fr;gap:8px;align-items:center}
#numv .nm-det input{font:inherit;padding:5px 8px;border:1px solid #D8D0C2;border-radius:6px;background:#fff;color:#1F1D1A;min-height:32px}
#numv .nm-det ul{margin:0;padding-left:1.2em}#numv .nm-det li{margin:2px 0}
#numv .nm-det .row{display:flex;gap:6px;flex-wrap:wrap;align-items:center}
#numv .nm-empty{padding:30px 10px;color:#6A6257;text-align:center;font-size:14.5px}
#numv .nm-hid{margin:20px 0 0;font-size:13.5px;color:#6A6257}
#numv .nm-hid summary{cursor:pointer;padding:6px 0}
#numv .nm-hid .row{display:flex;gap:8px;align-items:center;padding:4px 0;border-bottom:1px dashed #E4DFD5}
#numv .nm-ov{position:fixed;inset:0;z-index:60;background:rgba(20,18,15,.45);display:flex;align-items:flex-start;justify-content:center;padding:4vh 12px;overflow:auto}
#numv .nm-dlg{position:relative;background:var(--card);color:var(--ink);border-radius:12px;width:min(1100px,100%);max-height:none;box-shadow:0 18px 60px rgba(0,0,0,.3);display:flex;flex-direction:column}
#numv .nm-dlg>header{display:flex;align-items:center;gap:10px;padding:14px 16px 10px;border-bottom:1px solid var(--line)}
#numv .nm-dlg>header h3{margin:0;font-size:17px;font-family:inherit}
#numv .nm-dlg>header .x{margin-left:auto}
#numv .nm-dlg .bd{padding:12px 16px;display:grid;gap:10px}
#numv .nm-dlg>footer{position:sticky;bottom:0;display:flex;flex-wrap:wrap;gap:8px;align-items:center;padding:10px 16px;border-top:1px solid var(--line);background:var(--card);border-radius:0 0 12px 12px}
#numv .nm-dlg .flt{display:flex;flex-wrap:wrap;gap:6px 8px;align-items:center}
#numv .nm-ilist{border:1px solid var(--line);border-radius:8px;max-height:56vh;overflow:auto;background:#fff;color:#1F1D1A}
#numv .nm-irow{display:grid;grid-template-columns:28px minmax(0,1fr) auto;gap:8px;align-items:start;padding:8px 10px;border-bottom:1px solid #EEE9E0;content-visibility:auto;contain-intrinsic-size:auto 64px}
#numv .nm-irow input{width:18px;height:18px;margin-top:2px}
#numv .nm-irow .t{font-size:14px;line-height:1.5;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden;overflow-wrap:anywhere}
#numv .nm-irow .m{display:flex;flex-wrap:wrap;gap:4px;margin:3px 0 0;font-size:12px}
#numv .nm-irow.dup{background:#F6F4EF}#numv .nm-irow.dup .t{color:#6A6257}
#numv .nm-irow .add{font-size:12.5px;padding:3px 9px;min-height:30px}
#numv .nm-fld{display:grid;gap:4px}#numv .nm-fld>span{font-size:12.5px;font-weight:700;color:var(--sub)}
#numv .nm-rich{border:1px solid #D8D0C2;border-radius:6px;background:#fff;color:#1F1D1A;padding:6px 8px;min-height:3.2em;font-size:14.5px;line-height:1.6;white-space:pre-wrap;overflow-wrap:anywhere}
#numv .nm-rich p{margin:0}#numv .nm-rich img{max-width:100%;height:auto}#numv .nm-rich td{border:1px solid #BDB5A8;padding:3px 6px}#numv .nm-rich table{border-collapse:collapse}
#numv .nm-g2{display:grid;grid-template-columns:1fr 1fr;gap:10px}
#numv .nm-prev{border:1px solid #E4DFD5;border-radius:6px;padding:8px 10px;background:#fff;color:#1F1D1A;margin:4px 0 0}
#numv .nm-warn{color:#9A3412;font-size:13px}
#numv .nm-prog{font-size:14px;color:var(--sub);padding:20px;text-align:center}
#numv .nm-lecin{font:inherit;font-size:14px;padding:4px 8px;border:1px solid #D8D0C2;border-radius:6px;min-width:12em}
@media (max-width:760px){
 #numv .nm-doc{padding:4px 12px 30px;border-radius:0;border-left:0;border-right:0;margin:0 -16px}
 #numv .nm-body{grid-template-columns:minmax(0,1fr)}
 #numv .nm-col+.nm-col{border-left:0;border-top:1px solid #E4DFD5}
 #numv .nm-g2{grid-template-columns:1fr}
 #numv .nm-irow{grid-template-columns:24px minmax(0,1fr)}#numv .nm-irow .add{grid-column:2;justify-self:start}
 #numv .nm-dlg{border-radius:10px}
 #numv .nm-bar select{flex:1 1 calc(50% - 8px);min-width:0}
}
@media print{#numv .nm-bar,#numv .nm-tabs,#numv .nm-cnt,#numv .nm-edb,#numv .nm-more{display:none}#numv .nm-it{content-visibility:visible}}
`;
function css() { if (!document.getElementById('nm-css')) { const s = document.createElement('style'); s.id = 'nm-css'; s.textContent = STYLE; document.head.appendChild(s); } }

function srcChips(it) {
  const k = it.src[0] ? it.src[0].t : it.kind, more = it.src.length > 1 ? ' 외 ' + (it.src.length - 1) : '';
  const lab = it.src[0] ? (it.src[0].lab || KIND[k] || k) : (KIND[it.kind] || '');
  return `<span class="nm-chip k-${esc(k)}" title="${esc(it.src.map(s => (s.lab || KIND[s.t] || s.t) + (s.yrs && s.yrs.length ? ' ' + yrsTxt(s.yrs) : '')).join('\n'))}">${esc(lab + more)}</span>`;
}
function itemHTML(it, no, hid) {
  const st = stOf(it), rv = it.rv && it.rv.length && !it.rvok, ty = tyOf(it);
  const edq = it.kind === 'seed' ? it.q !== it.base.q : it.q0 != null, eda = it.kind === 'seed' ? it.a !== it.base.a : it.a0 != null;
  return `<article class="nm-it" data-id="${esc(it.id)}"${hid ? ' hidden' : ''}><header class="nm-h"><label class="nm-ck"><input type="checkbox" data-ck="1"${S.sel.has(it.id) ? ' checked' : ''} aria-label="선택"></label><span class="nm-no">${no}</span>${srcChips(it)}${it.yrs.length ? `<span class="nm-chip yr" title="출제 연도">${esc(yrsTxt(it.yrs))}</span>` : ''}<span class="nm-chip">${esc(TYPES[ty])}</span>${(it.tags || []).map(t => `<span class="nm-chip">${esc(t)}</span>`).join('')}<span class="nm-chip s${st}">${STN[st]}</span>${rv ? `<button type="button" class="nm-chip rv" data-act="det" title="${esc(it.rv.map(r => r.m).join('\n'))}">⚠ 검토</button>` : ''}${edq || eda ? `<span class="nm-chip ed" title="원본에서 고친 작업본 — ⋯ 메뉴 '원본으로'로 되돌림">${edq && eda ? '문제·답 고침' : edq ? '문제 고침' : '답 고침'}</span>` : ''}<span class="nm-gap"></span><button type="button" class="nm-more" data-act="more" aria-haspopup="true" title="이 문제 메뉴 — 완성·출처·순서·강의 옮기기·복사·되돌리기·빼기" aria-label="이 문제 메뉴">⋯</button></header>`
    + `<div class="nm-q"><span class="nm-ql" aria-hidden="true">문제</span><div class="nm-c" data-f="q">${disp(it.q) || '<span class="nm-ph">문제 없음</span>'}</div><button type="button" class="nm-edb" data-act="edit" data-f="q" title="문제 고치기(작업본만 — 원본은 그대로)">수정</button></div>`
    + `<div class="nm-body"><section class="nm-col nm-a"><div class="nm-lab">답안 <button type="button" class="nm-edb" data-act="edit" data-f="a" title="답안 고치기(작업본만 — 원본은 그대로)">수정</button></div><div class="nm-c" data-f="a">${disp(it.a) || '<span class="nm-ph">답안 없음 — 수정을 눌러 쓰기</span>'}</div></section>`
    + `<section class="nm-col nm-s"><div class="nm-lab">넘버링 스토리</div><div class="nm-c" data-f="st" tabindex="0" role="textbox" aria-label="넘버링 스토리 — 누르면 바로 편집">${disp(it.st) || '<span class="nm-ph">눌러서 스토리 쓰기</span>'}</div></section></div>`
    + (it.note ? `<div class="nm-note">참고: ${esc(it.note)}</div>` : '') + `</article>`;
}
function visible(it) {
  const f = S.cfg.f;
  if (it.del) return false;
  if (f.lec) { const known = S.lecs.some(l => l.k && l.k === it.lec); if (f.lec === '__none' ? known : it.lec !== f.lec) return false; }
  if (f.type) { const t = tyOf(it); if (f.type === 'ess' ? !essayish(t) : t !== f.type) return false; }
  if (f.st !== '') { if (f.st === 'rv') { if (!(it.rv && it.rv.length && !it.rvok)) return false; } else if (String(stOf(it)) !== f.st) return false; }
  if (f.src && !it.src.some(s => s.t === f.src) && it.kind !== f.src) return false;
  if (f.yr) { if (f.yr === 'none' ? it.yrs.length : !it.yrs.includes(+f.yr)) return false; }
  if (S.q) { const ws = S.q.toLowerCase().split(/\s+/).filter(Boolean), t = txt(it); if (!ws.every(w => t.indexOf(w) >= 0)) return false; }
  return true;
}
function cmp() {
  const s = S.cfg.sort, L = it => lecIdx(it.lec), Y = it => it.yrs.length ? Math.max(...it.yrs) : 0;
  const by = { lec: (a, b) => L(a) - L(b) || a.o - b.o, own: (a, b) => a.o - b.o, yr: (a, b) => Y(b) - Y(a) || b.yrs.length - a.yrs.length || L(a) - L(b) || a.o - b.o, freq: (a, b) => b.yrs.length - a.yrs.length || Y(b) - Y(a) || L(a) - L(b) || a.o - b.o, upd: (a, b) => (b.u || 0) - (a.u || 0) || a.o - b.o, st: (a, b) => stOf(a) - stOf(b) || L(a) - L(b) || a.o - b.o };
  return by[s] || by.lec;
}
function ordered() { const live = S.items.filter(it => !it.del); return live.sort(cmp()); }
function counts() { const c = [0, 0, 0], live = S.items.filter(it => !it.del); live.forEach(it => c[stOf(it)]++); return { n: live.length, c, rv: live.filter(it => it.rv && it.rv.length && !it.rvok).length }; }

function barHTML() {
  const C = S.cfg, f = C.f, subs = subjects(), x = idx(S.sj);
  const yrs = [...new Set(S.items.filter(i => !i.del).flatMap(i => i.yrs))].sort((a, b) => b - a);
  const lecN = {}; S.items.forEach(it => { if (!it.del) lecN[it.lec || ''] = (lecN[it.lec || ''] || 0) + 1; });
  const opt = (v, t, cur) => `<option value="${esc(v)}"${String(cur) === String(v) ? ' selected' : ''}>${esc(t)}</option>`;
  return `<div class="nm-tabs" role="tablist" aria-label="넘버링 메뉴"><button type="button" class="nm-tab on" role="tab" aria-selected="true">넘버링 따기</button><button type="button" class="nm-tab" role="tab" aria-selected="false" aria-disabled="true" title="넘버링 복습은 다음 업데이트에서 열려요">넘버링 복습 <small>· 추후 업데이트 예정</small></button><span class="nm-save" aria-live="polite">자동 저장</span></div>`
    + `<div class="nm-bar"><select data-cf="sj" aria-label="과목">${subs.map(s => opt(s.id, s.t + (s.jbl ? '' : s.seed ? ' (Word 자료)' : ' (내 과목)'), S.sj)).join('')}<option value="__new">+ 새 과목 만들기…</option></select>`
    + `<select data-cf="lec" aria-label="강의">${opt('', '모든 강의', f.lec)}${S.lecs.filter(l => l.k && lecN[l.k]).map(l => opt(l.k, l.t + ' (' + lecN[l.k] + ')', f.lec)).join('')}${lecN[''] ? opt('__none', '강의 미분류 (' + lecN[''] + ')', f.lec) : ''}</select>`
    + `<input type="search" data-cf="q" placeholder="문제·답안·스토리·출처·강의 검색" value="${esc(S.q)}" aria-label="넘버링 검색">`
    + `<span class="nm-seg" role="group" aria-label="보기"><button type="button" data-mode="grp" class="${C.mode === 'grp' ? 'on' : ''}" aria-pressed="${C.mode === 'grp'}">강의별</button><button type="button" data-mode="all" class="${C.mode === 'all' ? 'on' : ''}" aria-pressed="${C.mode === 'all'}">전체 목록</button></span></div>`
    + `<div class="nm-bar"><select data-cf="type" aria-label="문제 유형">${opt('', '모든 유형', f.type)}${opt('ess', '서술형·넘버링형만', f.type)}${Object.keys(TYPES).map(k => opt(k, TYPES[k], f.type)).join('')}</select>`
    + `<select data-cf="st" aria-label="제작 상태">${opt('', '모든 상태', f.st)}${STN.map((t, i) => opt(String(i), t, f.st)).join('')}${opt('rv', '⚠ 검토 필요', f.st)}</select>`
    + `<select data-cf="src" aria-label="출처">${opt('', '모든 출처', f.src)}${Object.keys(KIND).map(k => opt(k, KIND[k], f.src)).join('')}</select>`
    + `<select data-cf="yr" aria-label="출제 연도">${opt('', '모든 연도', f.yr)}${yrs.map(y => opt(String(y), y + '년 출제', f.yr)).join('')}${opt('none', '연도 없음', f.yr)}</select>`
    + `<select data-cf="sort" aria-label="정렬">${[['lec', '강의 순서'], ['own', '사용자 지정 순서'], ['yr', '출제 연도(최근)'], ['freq', '기출 빈도'], ['upd', '최근 수정'], ['st', '제작 상태']].map(([v, t]) => opt(v, '정렬: ' + t, C.sort)).join('')}</select>`
    + `<span class="nm-sp"></span><button type="button" class="nm-btn pri" data-act="new">+ 새 문제</button><button type="button" class="nm-btn" data-act="imp">기존 문제 불러오기</button><button type="button" class="nm-btn" data-act="file" title="Word(.docx) 넘버링 파일에서 문제 가져오기 — 미리 보고 고른 뒤 넣음">파일 가져오기</button><button type="button" class="nm-btn" data-act="selm" aria-pressed="${S.selMode}">${S.selMode ? '선택 끝' : '여러 개 선택'}</button></div>`
    + `<div class="nm-cnt" data-cnt="1"></div>`
    + (S.selMode ? `<div class="nm-batch" data-batch="1"></div>` : '');
}
function cntHTML() {
  const k = counts(), f = S.cfg.f, vis = $$('.nm-it:not([hidden])', S.root).length;
  const b = (v, t, n) => `<button type="button" data-stf="${v}" class="${f.st === v ? 'on' : ''}">${t} <b>${n}</b></button>`;
  return `${b('', '전체', k.n)}${b('0', '미작성', k.c[0])}${b('1', '작성 중', k.c[1])}${b('2', '완성', k.c[2])}${k.rv ? b('rv', '⚠ 검토', k.rv) : ''}<span>· 보이는 문제 <b>${vis}</b></span>${S.seed ? `<span title="${esc(S.seed.meta.src)}">· 기본 자료: ${esc(S.seed.meta.file || S.seed.meta.src)}</span>` : ''}`;
}
function batchHTML() { const n = S.sel.size; return `<b>${n}개 선택</b><button type="button" class="nm-btn" data-bat="all">보이는 것 모두 선택</button><button type="button" class="nm-btn" data-bat="none">선택 해제</button><span class="nm-sp"></span><button type="button" class="nm-btn" data-bat="done"${n ? '' : ' disabled'}>완성 표시</button><button type="button" class="nm-btn" data-bat="undone"${n ? '' : ' disabled'}>완성 해제</button><button type="button" class="nm-btn" data-bat="move"${n ? '' : ' disabled'}>강의 옮기기</button><button type="button" class="nm-btn" data-bat="merge"${n > 1 ? '' : ' disabled'} title="같은 문제를 하나로 — 출처·연도를 합침(스토리는 하나만)">합치기</button><button type="button" class="nm-btn" data-bat="del"${n ? '' : ' disabled'}>목록에서 빼기</button>`; }

function render(o) {
  o = o || {}; const tok = ++S.tok, R = S.root; if (!R) return;
  endEdit(true);
  const L = ordered(), C = S.cfg;
  const chunks = [];   /* [html, ...] — 첫 묶음은 바로, 나머지는 쉬는 틈에 */
  let cur = '', no = 0, curLec = null, n = 0;
  const flush = () => { if (cur) { chunks.push(cur); cur = ''; } };
  for (const it of L) {
    if (C.mode === 'grp') { const lk = S.lecs.some(l => l.k === it.lec) ? it.lec : ''; if (lk !== curLec) { curLec = lk; const l = lecOf(lk); cur += `<h2 class="nm-lec" data-lec="${esc(lk)}">${esc(l.t)}<small>${esc([l.prof, l.lab].filter(Boolean).join(' · '))}</small></h2>`; } }
    const v = visible(it); cur += itemHTML(it, v ? ++no : 0, !v); n++;
    if (n % 40 === 0) flush();
  }
  flush();
  const hid = S.items.filter(it => it.del);
  let V = document.getElementById('numv'), main = V && R.contains(V) && $('.nm-main', V);   /* 대화창·메뉴(#numv 바로 아래)는 그대로 두고 본문만 다시 */
  if (!main) { R.innerHTML = '<div id="numv"><div class="nm-main"></div></div>'; V = document.getElementById('numv'); main = $('.nm-main', V); }
  V.className = S.selMode ? 'selm' : '';
  main.innerHTML = `${barHTML()}<div class="nm-doc" data-doc="1">${chunks[0] || ''}${L.length ? '' : `<div class="nm-empty">아직 이 과목에 넘버링 문제가 없어요.<br><b>기존 문제 불러오기</b>로 JB 기출·예상문제를 넣거나 <b>+ 새 문제</b>로 직접 만들어 보세요.</div>`}</div>${hid.length ? hidHTML(hid) : ''}`;
  const doc = $('[data-doc]', R);
  const rest = chunks.slice(1);
  const done = () => { if (tok !== S.tok) return; applyFilter(); if (o.pos) restorePos(o.pos); else if (o.y != null) window.scrollTo(0, o.y); if (o.flash) flash(o.flash); };
  { const c = $('[data-cnt]', R); if (c) c.innerHTML = cntHTML(); const bt = $('[data-batch]', R); if (bt) bt.innerHTML = batchHTML(); }
  if (!rest.length) { done(); return; }
  let i = 0; const step = () => { if (tok !== S.tok || !doc.isConnected) return; doc.insertAdjacentHTML('beforeend', rest[i++]); if (i < rest.length) setTimeout(step, 0); else done(); };
  setTimeout(step, 0);
}
function hidHTML(hid) { return `<details class="nm-hid"><summary>목록에서 뺀 문제 ${hid.length}개 — 다시 넣을 수 있어요(원본은 그대로)</summary>${hid.map(it => `<div class="row" data-id="${esc(it.id)}"><span class="nm-chip k-${esc(it.kind)}">${esc(KIND[it.kind] || it.kind)}</span><span style="flex:1;min-width:0;overflow:hidden;text-overflow:ellipsis;white-space:nowrap">${esc(plain(it.q).slice(0, 90))}</span><button type="button" class="nm-btn" data-act="undel">다시 넣기</button></div>`).join('')}</details>`; }
function applyFilter(initial) {
  const R = S.root; if (!R) return;
  const arts = $$('.nm-it', R); let no = 0;
  for (const a of arts) { const it = S.by.get(a.dataset.id); const v = !!it && visible(it); if (a.hidden === v) a.hidden = !v; if (v) { const nb = a.querySelector('.nm-no'); const t = String(++no); if (nb.textContent !== t) nb.textContent = t; } }
  $$('.nm-lec', R).forEach(h => { let n = h.nextElementSibling, any = false; while (n && !n.classList.contains('nm-lec')) { if (n.classList.contains('nm-it') && !n.hidden) { any = true; break; } n = n.nextElementSibling; } h.hidden = !any; });
  const c = $('[data-cnt]', R); if (c) c.innerHTML = cntHTML();
  const bt = $('[data-batch]', R); if (bt) bt.innerHTML = batchHTML();
  if (!initial) { const e = $('.nm-empty2', R); if (e) e.remove(); if (!no && S.items.some(it => !it.del)) $('[data-doc]', R).insertAdjacentHTML('beforeend', '<div class="nm-empty nm-empty2">조건에 맞는 문제가 없어요 — 검색어·거르기를 바꿔 보세요.</div>'); }
}
function rerenderItem(it) {
  const a = S.root && $(`.nm-it[data-id="${CSS.escape(it.id)}"]`, S.root); if (!a) return;
  const no = a.querySelector('.nm-no').textContent; const t = document.createElement('div'); t.innerHTML = itemHTML(it, no, a.hidden); const n = t.firstElementChild; a.replaceWith(n);
  const c = $('[data-cnt]', S.root); if (c) c.innerHTML = cntHTML();
}
function flash(id) { const a = S.root && $(`.nm-it[data-id="${CSS.escape(id)}"]`, S.root); if (!a) return; a.hidden = false; a.scrollIntoView({ block: 'center' }); a.classList.remove('flash'); void a.offsetWidth; a.classList.add('flash'); }
function topItem() { const arts = $$('.nm-it:not([hidden])', S.root); for (const a of arts) { const r = a.getBoundingClientRect(); if (r.bottom > 80) return { id: a.dataset.id, off: Math.round(r.top) }; } return null; }
function restorePos(p) { const a = S.root && $(`.nm-it[data-id="${CSS.escape(p.id)}"]`, S.root); if (!a) return; a.scrollIntoView({ block: 'start' }); window.scrollBy(0, -(p.off || 0) + 0); requestAnimationFrame(() => { const r = a.getBoundingClientRect(); if (Math.abs(r.top - (p.off || 0)) > 4) window.scrollBy(0, r.top - (p.off || 0)); }); }

/* ---------- 편집기(누른 칸 하나만) ---------- */
const COLORS = ['#000000', '#C00000', '#E36C09', '#BF4E14', '#00B050', '#0070C0', '#7030A0', '#7F7F7F'];
const HILITE = ['#FFFF00', '#00FF00', '#00FFFF', '#FF99CC', '#FFD966', '#C6E0B4'];
function tbHTML() {
  return `<div class="nm-tb" role="toolbar" aria-label="서식">`
    + `<button type="button" data-cmd="bold" title="굵게 (⌘/Ctrl B)"><b>B</b></button><button type="button" data-cmd="underline" title="밑줄 (⌘/Ctrl U)"><u>U</u></button>`
    + `<button type="button" data-pal="fc" title="글자색"><span style="border-bottom:3px solid #C00000">가</span> ▾</button><button type="button" data-pal="hl" title="형광펜"><span style="background:#FFFF00;color:#1F1D1A;padding:0 3px">형광</span> ▾</button><i class="sep"></i>`
    + `<button type="button" data-cmd="insertOrderedList" title="번호 목록">1.</button><button type="button" data-cmd="insertUnorderedList" title="글머리표">•</button><button type="button" data-pal="tbl" title="표 넣기·줄/칸 더하기·빼기">표 ▾</button><button type="button" data-cmd="img" title="그림 넣기(이 기기에 줄여서 저장)">그림</button><i class="sep"></i>`
    + `<button type="button" data-cmd="undo" title="실행 취소 (⌘/Ctrl Z)">↶</button><button type="button" data-cmd="redo" title="다시 실행 (⌘/Ctrl Shift Z)">↷</button>`
    + `<button type="button" class="done" data-cmd="done" title="편집 끝 (Esc) — 자동 저장됨">완료</button></div>`;
}
function startEdit(el, it, f, ev) {
  if (S.ed && S.ed.el === el) return;
  endEdit();
  if (!el.isConnected) { el = S.root && $(`.nm-it[data-id="${CSS.escape(it.id)}"] .nm-c[data-f="${f}"]`, S.root); if (!el) return; }   /* 같은 문제의 다른 칸을 고치다 왔으면 그 문제가 새로 그려짐 */
  const orig = it[f] || '';
  el.innerHTML = disp(orig) || '<p><br></p>';
  el.contentEditable = 'true'; el.spellcheck = false;
  const host = f === 'q' ? el.closest('.nm-q') : el.closest('.nm-col');
  host.insertAdjacentHTML('afterbegin', tbHTML());
  S.ed = { el, it, f, orig, t: 0, saved: orig, tb: host.firstElementChild };
  try { document.execCommand('styleWithCSS', false, true); document.execCommand('defaultParagraphSeparator', false, 'p'); } catch (e) {}
  el.focus({ preventScroll: true });
  const sel = getSelection();
  let r = null;
  if (ev && ev.clientX != null) { if (document.caretRangeFromPoint) r = document.caretRangeFromPoint(ev.clientX, ev.clientY); else if (document.caretPositionFromPoint) { const p = document.caretPositionFromPoint(ev.clientX, ev.clientY); if (p) { r = document.createRange(); r.setStart(p.offsetNode, p.offset); } } }
  if (!r || !el.contains(r.startContainer)) { r = document.createRange(); r.selectNodeContents(el); r.collapse(false); }
  sel.removeAllRanges(); sel.addRange(r);
}
function edInput() { const E = S.ed; if (!E) return; saveState('ing'); clearTimeout(E.t); E.t = setTimeout(edSave, 700); }
function edSave() {
  const E = S.ed; if (!E) return; clearTimeout(E.t); E.t = 0;
  let h = toStore(E.el.innerHTML); if (isEmpty(h)) h = '';
  if (h === E.saved) { saveState('ok'); return; }
  const it = E.it;
  if (E.saved === E.orig && h !== E.orig) it.prev = { f: E.f, h: E.orig, at: now() };   /* 이번 편집 전 글 = 되돌리기 한 칸 */
  if ((E.f === 'q' || E.f === 'a') && it.kind !== 'seed' && it.kind !== 'user' && it.kind !== 'word' && it[E.f + '0'] == null) it[E.f + '0'] = E.orig;   /* JB·예상 원본 사본(처음 고칠 때) */
  it[E.f] = h; touch(it); E.saved = h; it._ty = null;
  put(it);
}
function endEdit(silent) {
  const E = S.ed; if (!E) return; edSave(); S.ed = null;
  try { E.el.contentEditable = 'false'; E.el.removeAttribute('contenteditable'); } catch (e) {}
  if (E.tb && E.tb.isConnected) E.tb.remove(); palClose();
  if (!silent && E.el.isConnected) rerenderItem(E.it);
}
function palClose() { $$('.nm-pal', S.root || document).forEach(p => p.remove()); }
function palOpen(btn, kind) {
  palClose(); const R = btn.closest('.nm-dlg') || $('#numv'); if (!R) return;
  const p = document.createElement('div'); p.className = 'nm-pal'; p.setAttribute('role', 'menu');
  if (kind === 'fc') p.innerHTML = COLORS.map(c => `<button type="button" data-fc="${c}" title="${c}" style="background:${c}"></button>`).join('') + `<button type="button" class="wide" data-fc="">기본색</button>`;
  else if (kind === 'hl') p.innerHTML = HILITE.map(c => `<button type="button" data-hl="${c}" title="${c}" style="background:${c}"></button>`).join('') + `<button type="button" class="wide" data-hl="">형광펜 지우기</button>`;
  else p.innerHTML = [['ins2', '표 넣기 2×2'], ['ins3', '표 넣기 3×3'], ['row', '아래에 줄 더하기'], ['col', '오른쪽에 칸 더하기'], ['drow', '이 줄 빼기'], ['dcol', '이 칸 빼기'], ['dtbl', '표 지우기']].map(([k, t]) => `<button type="button" class="wide" data-tb="${k}">${t}</button>`).join('');
  if (kind === 'tbl') p.style.width = '170px';
  const r = btn.getBoundingClientRect(), rr = R.getBoundingClientRect();
  p.style.left = Math.max(0, Math.min(r.left - rr.left, rr.width - 200)) + 'px'; p.style.top = (r.bottom - rr.top + 4) + 'px';
  R.style.position = 'relative'; R.appendChild(p);
}
function cellAt() { const s = getSelection(); if (!s.rangeCount) return null; let n = s.anchorNode; while (n && n !== (S.ed && S.ed.el)) { if (n.nodeType === 1 && (n.tagName === 'TD' || n.tagName === 'TH')) return n; n = n.parentNode; } return null; }
function replaceNode(node, html) { const r = document.createRange(); r.selectNode(node); const s = getSelection(); s.removeAllRanges(); s.addRange(r); document.execCommand('insertHTML', false, html); }
function tblOp(k) {
  const E = S.ed; if (!E) return;
  if (k === 'ins2' || k === 'ins3') { const n = k === 'ins2' ? 2 : 3; document.execCommand('insertHTML', false, '<table>' + Array.from({ length: n }, () => '<tr>' + Array.from({ length: n }, () => '<td><p><br></p></td>').join('') + '</tr>').join('') + '</table><p><br></p>'); edInput(); return; }
  const td = cellAt(); if (!td) { H.toast('표 안의 칸을 먼저 누르세요'); return; }
  const tr = td.parentNode, tb = td.closest('table'), ci = [...tr.children].indexOf(td), t2 = tb.cloneNode(true), rows = [...t2.querySelectorAll('tr')], ri = [...tb.querySelectorAll('tr')].indexOf(tr);
  if (k === 'row') { const nr = document.createElement('tr'); for (let i = 0; i < rows[ri].children.length; i++) { const c = document.createElement('td'); c.innerHTML = '<p><br></p>'; nr.appendChild(c); } rows[ri].after(nr); }
  else if (k === 'col') rows.forEach(r => { const c = document.createElement('td'); c.innerHTML = '<p><br></p>'; const ref = r.children[Math.min(ci, r.children.length - 1)]; if (ref) ref.after(c); else r.appendChild(c); });
  else if (k === 'drow') { if (rows.length <= 1) { tblOp('dtbl'); return; } rows[ri].remove(); }
  else if (k === 'dcol') { rows.forEach(r => { const c = r.children[Math.min(ci, r.children.length - 1)]; if (c) c.remove(); }); if (!t2.querySelector('td,th')) { tblOp('dtbl'); return; } }
  else if (k === 'dtbl') { replaceNode(tb, '<p><br></p>'); edInput(); return; }
  replaceNode(tb, t2.outerHTML); edInput();
}
async function shrinkFile(file, maxW) {
  const bmp = await createImageBitmap(file); const sc = Math.min(1, (maxW || 1000) / bmp.width), w = Math.max(1, Math.round(bmp.width * sc)), h = Math.max(1, Math.round(bmp.height * sc));
  const cv = document.createElement('canvas'); cv.width = w; cv.height = h; const g = cv.getContext('2d'); g.fillStyle = '#fff'; g.fillRect(0, 0, w, h); g.drawImage(bmp, 0, 0, w, h); if (bmp.close) bmp.close();
  let d = cv.toDataURL('image/webp', 0.8); if (!/^data:image\/webp/.test(d)) d = cv.toDataURL('image/jpeg', 0.82);
  return { d, w: Math.min(w, 640), h: Math.round(Math.min(w, 640) * h / w) };
}
function pickImage(cb) { const i = document.createElement('input'); i.type = 'file'; i.accept = 'image/*'; i.onchange = async () => { const f = i.files && i.files[0]; if (!f) return; try { cb(await shrinkFile(f)); } catch (e) { H.toast('그림을 열지 못했어요 — 다른 형식(png·jpg)으로 해 주세요', { level: 'error', id: 'nmimg' }); } }; i.click(); }
function edCmd(c) {
  const E = S.ed; if (!E) return; E.el.focus({ preventScroll: true });
  if (c === 'done') { endEdit(); return; }
  if (c === 'img') { const sel = getSelection(), r = sel.rangeCount ? sel.getRangeAt(0).cloneRange() : null; E.busy = true;
    const back = () => { removeEventListener('focus', back); setTimeout(() => { if (S.ed === E && E.busy === true) { E.busy = false; E.el.focus({ preventScroll: true }); } }, 900); }; addEventListener('focus', back);
    pickImage(im => { E.busy = false; if (S.ed !== E) return; E.el.focus({ preventScroll: true }); if (r) { sel.removeAllRanges(); sel.addRange(r); } document.execCommand('insertHTML', false, `<img src="${im.d}" width="${im.w}" height="${im.h}" alt="">`); edInput(); }); return; }
  try { document.execCommand(c, false, null); } catch (e) {}
  edInput();
}
async function onPaste(e) {
  const E = S.ed || S.formEd; if (!E) return; const cd = e.clipboardData; if (!cd) return;
  const files = [...(cd.files || [])].filter(f => /^image\//.test(f.type)), h = cd.getData('text/html'), t = cd.getData('text/plain');
  e.preventDefault();
  if (h) { S.pasteLost = 0; const c = sanitize(h, { paste: true }); document.execCommand('insertHTML', false, c); if (S.pasteLost && !files.length) H.toast('Word 안의 그림은 글과 함께 복사되지 않아요 — 그림만 따로 복사해 붙여 넣거나 [그림] 버튼으로 넣어 주세요', { level: 'result' }); }
  else if (files.length) { for (const f of files) { try { const im = await shrinkFile(f); document.execCommand('insertHTML', false, `<img src="${im.d}" width="${im.w}" height="${im.h}" alt="">`); } catch (_) {} } }
  else if (t) document.execCommand('insertText', false, t);
  if (S.ed) edInput();
}

/* ---------- 메뉴(⋯) ---------- */
function menuClose() { $$('.nm-menu', document).forEach(m => m.remove()); }
function menuOpen(btn, items) {
  menuClose(); const R = $('#numv'); if (!R) return;
  const m = document.createElement('div'); m.className = 'nm-menu'; m.setAttribute('role', 'menu');
  m.innerHTML = items.map(x => x === '-' ? '<hr>' : `<button type="button" role="menuitem" data-mi="${esc(x[0])}"${x[2] ? ` class="${x[2]}"` : ''}>${esc(x[1])}</button>`).join('');
  R.style.position = 'relative'; R.appendChild(m);
  const r = btn.getBoundingClientRect(), rr = R.getBoundingClientRect(), mw = m.offsetWidth;
  m.style.left = Math.max(0, Math.min(r.right - rr.left - mw, rr.width - mw)) + 'px'; m.style.top = (r.bottom - rr.top + 4) + 'px';
  const f = m.querySelector('button'); if (f) f.focus({ preventScroll: true });
  return m;
}
function itemMenu(btn, it) {
  const orig = it.kind === 'seed' ? (it.q !== it.base.q || it.a !== it.base.a) : (it.q0 != null || it.a0 != null);
  const canMove = S.cfg.sort === 'lec' || S.cfg.sort === 'own';
  const L = [[it.done ? 'undone' : 'done', it.done ? '완성 해제' : '✓ 완성으로 표시'], ['det', '출처·연도·태그·참고 보기/고치기'], '-',
    ['up', '위로 옮기기' + (canMove ? '' : ' (정렬: 사용자 지정으로)')], ['down', '아래로 옮기기' + (canMove ? '' : ' (정렬: 사용자 지정으로)')], ['lec', '다른 강의로 옮기기'], ['copy', '복사해서 새 문제로'], '-'];
  if (it.prev) L.push(['prev', '마지막 수정 전으로 되돌리기 (' + ({ q: '문제', a: '답안', st: '스토리' }[it.prev.f] || '') + ' · ' + new Date(it.prev.at).toLocaleTimeString('ko-KR', { hour: '2-digit', minute: '2-digit' }) + ')']);
  if (orig) L.push(['orig', '문제·답안을 원본으로 되돌리기']);
  const s0 = it.src.find(s => s.t === 'jb' || s.t === 'pred'); if (s0 && H.PACKS[s0.s]) L.push(['open', s0.t === 'jb' ? 'JB 기출 원본 열기' : '예상문제 원본 열기']);
  L.push('-', ['del', '목록에서 빼기(원본은 그대로)', 'warn']);
  const m = menuOpen(btn, L); if (!m) return;
  m.addEventListener('click', e => { const b = e.target.closest('[data-mi]'); if (!b) return; menuClose(); itemAct(b.dataset.mi, it, btn); });
}
function itemAct(k, it, btn) {
  if (k === 'done' || k === 'undone') { it.done = k === 'done'; touch(it); put(it); rerenderItem(it); applyFilter(); return; }
  if (k === 'det') { detOpen(it); return; }
  if (k === 'up' || k === 'down') { moveItem(it, k === 'up' ? -1 : 1); return; }
  if (k === 'lec') { lecPick(btn, l => { it.lec = l; touch(it); put(it); render({ flash: it.id }); }); return; }
  if (k === 'copy') { const n = newItem({ s: it.s, lec: it.lec, q: it.q, a: it.a, st: it.st, note: it.note, tags: it.tags.slice(), yrs: it.yrs.slice(), src: it.src.map(s => Object.assign({}, s)), o: it.o + 0.5 }); renumber(); render({ flash: n.id }); H.toast('복사했어요 — 바로 아래에 새 문제로'); return; }
  if (k === 'prev') { const p = it.prev; const cur = it[p.f]; it[p.f] = p.h; it.prev = { f: p.f, h: cur, at: now() }; touch(it); it._ty = null; put(it); rerenderItem(it); H.toast('되돌렸어요 — 한 번 더 누르면 다시 앞으로'); return; }
  if (k === 'orig') { if (!confirm('이 문제의 문제·답안을 원본 글로 되돌릴까요? (넘버링 스토리는 그대로)')) return; const oq = it.q, oa = it.a; if (it.kind === 'seed') { it.q = it.base.q; it.a = it.base.a; } else { if (it.q0 != null) { it.q = it.q0; it.q0 = undefined; } if (it.a0 != null) { it.a = it.a0; it.a0 = undefined; } } it.prev = oq !== it.q ? { f: 'q', h: oq, at: now() } : oa !== it.a ? { f: 'a', h: oa, at: now() } : it.prev; touch(it); it._ty = null; put(it); rerenderItem(it); H.toast('원본으로 되돌렸어요 — ⋯ 메뉴 \'마지막 수정 전으로\'로 고친 글을 다시 볼 수 있어요'); return; }
  if (k === 'open') { const s0 = it.src.find(s => s.t === 'jb' || s.t === 'pred'); jumpOrig(s0); return; }
  if (k === 'del') { it.del = true; touch(it); put(it); S.sel.delete(it.id); render({ pos: topItem() }); H.toast('목록에서 뺐어요 — 맨 아래 \'목록에서 뺀 문제\'에서 다시 넣을 수 있어요', { level: 'result', action: { label: '되돌리기', fn: () => { it.del = false; touch(it); put(it); render({ flash: it.id }); } } }); }
}
function jumpOrig(s0) { if (!s0) return; leave(); if (s0.t === 'jb') H.openDoc(s0.s, '_jb', null, s0.id); else H.openDoc(s0.s, s0.lec || (H.PACKS[s0.s].lect[0] || {}).k, 'pred', s0.id); }
function renumber() { /* o 값이 겹치거나 소수가 쌓이면 정수로 다시 매김(바뀐 문제만 저장) */ const L = S.items.slice().sort((a, b) => a.o - b.o); L.forEach((it, i) => { if (it.o !== i) { it.o = i; it.u = it.u || now(); put(it); } }); }
function moveItem(it, d) {
  if (S.cfg.sort !== 'lec' && S.cfg.sort !== 'own') { S.cfg.sort = 'own'; cfgSave(); }
  const L = ordered().filter(x => visible(x) && (S.cfg.mode !== 'grp' || S.cfg.sort !== 'lec' || x.lec === it.lec)); const i = L.indexOf(it), j = i + d;
  if (i < 0 || j < 0 || j >= L.length) { H.toast(d < 0 ? '맨 위예요' : '맨 아래예요'); return; }
  const o = L[j]; const t = it.o; it.o = o.o; o.o = t; if (it.o === o.o) { it.o += d * 0.5; }
  touch(it); touch(o); put(it); put(o); render({ flash: it.id });
}
function lecPick(btn, cb) {
  const L = S.lecs.filter(l => l.k).map(l => [l.k, l.t]).concat([['__new', '+ 새 강의 만들기…'], ['', '강의 미분류']]);
  const m = menuOpen(btn, L); if (!m) return;
  m.addEventListener('click', e => { const b = e.target.closest('[data-mi]'); if (!b) return; menuClose(); let k = b.dataset.mi; if (k === '__new') { k = newLecture(); if (k == null) return; } cb(k); });
}
function newLecture(name) {
  const t = name != null ? name : prompt('새 강의 이름');
  if (!t || !t.trim()) return null;
  const x = idx(S.sj); x.ul = x.ul || []; const k = 'U' + now().toString(36); x.ul.push({ k, t: t.trim() }); idxPut(S.sj, x); S.lecs = lectures(S.sj, S.seed); return k;
}
function detOpen(it) {
  const a = $(`.nm-it[data-id="${CSS.escape(it.id)}"]`, S.root); if (!a) return;
  const old = a.querySelector('.nm-det'); if (old) { old.remove(); return; }
  const rv = it.rv && it.rv.length ? `<div><b>Word 반영 검토</b><ul>${it.rv.map(r => `<li>${esc(r.m)}${r.d ? `<br><small style="white-space:pre-wrap">${esc(r.d)}</small>` : ''}</li>`).join('')}</ul>${it.rvok ? '<span class="nm-chip s2">검토 끝</span> <button type="button" class="nm-btn" data-det="rvundo">다시 검토 필요로</button>' : '<button type="button" class="nm-btn" data-det="rvok">✓ 확인했어요(검토 끝)</button>'}</div>` : '';
  const src = `<div><b>출처</b><ul>${it.src.map((s, i) => `<li>${esc(s.lab || KIND[s.t] || s.t)}${s.yrs && s.yrs.length ? ' · ' + esc(yrsTxt(s.yrs)) : ''}${s.id && (s.t === 'jb' || s.t === 'pred') ? ` <small>(${esc(s.id)})</small>` : ''} ${(s.t === 'jb' || s.t === 'pred') && H.PACKS[s.s] ? `<button type="button" class="nm-btn" data-det="open" data-i="${i}">원본 열기</button>` : ''}${it.src.length > 1 ? ` <button type="button" class="nm-btn" data-det="unsrc" data-i="${i}">연결 끊기</button>` : ''}</li>`).join('')}</ul><div class="row"><input type="text" data-det-in="srcadd" placeholder="출처 더하기(예: 25 수업 강조, 스터디 자료)" aria-label="출처 더하기"><button type="button" class="nm-btn" data-det="srcadd">더하기</button></div></div>`;
  a.insertAdjacentHTML('beforeend', `<div class="nm-det"><label>출제 연도<input type="text" data-det-in="yrs" value="${esc(it.yrs.map(y => String(y).slice(2)).join(', '))}" placeholder="예: 25, 23, 16"></label><label>태그<input type="text" data-det-in="tags" value="${esc((it.tags || []).join(', '))}" placeholder="쉼표로 나눔"></label><label>참고사항<input type="text" data-det-in="note" value="${esc(it.note)}"></label>${src}${rv}<div class="row"><span style="color:#6A6257;font-size:12.5px">${esc(KIND[it.kind] || it.kind)} · 만든 때 ${it.c ? new Date(it.c).toLocaleString('ko-KR') : '—'} · 고친 때 ${it.u ? new Date(it.u).toLocaleString('ko-KR') : '—'}</span><span class="nm-sp" style="flex:1"></span><button type="button" class="nm-btn" data-det="close">닫기</button></div></div>`);
  const d = a.querySelector('.nm-det');
  d.addEventListener('change', e => { const k = e.target.dataset.detIn; if (!k || k === 'srcadd') return; const v = e.target.value; if (k === 'yrs') it.yrs = parseYrs(v); else if (k === 'tags') it.tags = v.split(/[,，]/).map(s => s.trim()).filter(Boolean); else if (k === 'note') it.note = v.trim(); touch(it); put(it); refreshItem(it, true); });
  d.addEventListener('click', e => { const b = e.target.closest('[data-det]'); if (!b) return; const k = b.dataset.det, i = +b.dataset.i;
    if (k === 'close') { d.remove(); return; }
    if (k === 'open') { jumpOrig(it.src[i]); return; }
    if (k === 'unsrc') { if (!confirm('이 출처 연결을 끊을까요? (원본 문제는 그대로)')) return; it.src.splice(i, 1); touch(it); put(it); refreshItem(it, true); return; }
    if (k === 'srcadd') { const inp = d.querySelector('[data-det-in=srcadd]'); const v = inp.value.trim(); if (!v) return; it.src.push({ t: 'user', s: it.s, lab: v, yrs: parseYrs(v) }); it.yrs = [...new Set(it.yrs.concat(parseYrs(v)))].sort((p, q) => q - p); touch(it); put(it); refreshItem(it, true); return; }
    if (k === 'rvok' || k === 'rvundo') { it.rvok = k === 'rvok'; touch(it); put(it); refreshItem(it, true); applyFilter(); } });
}
function refreshItem(it, keepDet) { const open = keepDet && $(`.nm-it[data-id="${CSS.escape(it.id)}"] .nm-det`, S.root); it._t = null; rerenderItem(it); if (open) detOpen(it); }

/* ---------- 새 문제·복사 ---------- */
function uid() { return 'u:' + now().toString(36) + Math.random().toString(36).slice(2, 6); }
function maxO(sj) { return S.sj === sj ? S.items.reduce((m, it) => Math.max(m, it.o || 0), -1) : 1e6 + now() / 1e7; }
function newItem(o) {
  const t = now(), it = { id: o.id || uid(), s: o.s, kind: o.kind || 'user', lec: o.lec || '', q: o.q || '', a: o.a || '', st: o.st || '', note: o.note || '', tags: o.tags || [], yrs: o.yrs || [], src: o.src || [{ t: 'user', s: o.s, lab: '직접 추가' }], ref: o.ref || null, done: false, o: o.o != null ? o.o : maxO(o.s) + 1, c: t, u: t, del: false, rv: o.rv || [], rvok: false, prev: null };
  if (!put(it)) H.toast('저장 공간이 부족해 이 기기에 바로 쓰지 못했어요 — 창을 닫기 전에 백업하세요', { level: 'error', id: 'nmquota' });
  if (S.sj === o.s) { S.items.push(it); S.by.set(it.id, it); }
  bumpIdx(o.s); return it;
}
function bumpIdx(sj) { const x = idx(sj); idxPut(sj, x); }
function richField(name, label, html, ph) { return `<label class="nm-fld"><span>${esc(label)}</span><div class="nm-rich" contenteditable="true" data-rich="${name}" data-ph="${esc(ph || '')}">${disp(html || '') || '<p><br></p>'}</div></label>`; }
function dlg(title, body, foot) {
  const R = $('#numv'); if (!R) return null; dlgClose();
  R.insertAdjacentHTML('beforeend', `<div class="nm-ov" data-ov="1" role="dialog" aria-modal="true" aria-label="${esc(title)}"><div class="nm-dlg"><header><h3>${esc(title)}</h3><button type="button" class="nm-btn x" data-x="1" aria-label="닫기">✕ 닫기</button></header><div class="bd">${body}</div><footer>${foot || ''}</footer></div></div>`);
  const ov = $('.nm-ov', R); document.body.style.overflow = 'hidden';
  ov.addEventListener('click', e => { if (e.target === ov || e.target.closest('[data-x]')) dlgClose(); });
  ov.addEventListener('keydown', e => { if (e.key === 'Escape') { e.stopPropagation(); dlgClose(); } });
  return ov;
}
function dlgClose() { $$('.nm-ov').forEach(o => o.remove()); document.body.style.overflow = ''; S.formEd = null; }
function newForm(pre) {
  pre = pre || {};
  const subs = subjects(), sj = pre.s || S.sj;
  const lecOpts = sjv => { const L = sjv === S.sj ? S.lecs : lectures(sjv, (window.JBLNUM_SEED || {})[sjv]); return L.filter(l => l.k).map(l => `<option value="${esc(l.k)}"${l.k === (pre.lec != null ? pre.lec : S.cfg.f.lec) ? ' selected' : ''}>${esc(l.t)}</option>`).join('') + '<option value="">강의 미분류</option><option value="__new">+ 새 강의 만들기…</option>'; };
  const ov = dlg('새 문제 만들기', `<div class="nm-g2"><label class="nm-fld"><span>과목</span><select data-nf="s">${subs.map(s => `<option value="${esc(s.id)}"${s.id === sj ? ' selected' : ''}>${esc(s.t)}</option>`).join('')}</select></label><label class="nm-fld"><span>강의</span><select data-nf="lec">${lecOpts(sj)}</select></label></div>`
    + richField('q', '문제', pre.q, '예: ○○의 적응증 4가지를 쓰시오.') + `<div class="nm-g2">${richField('a', '답안', pre.a)}${richField('st', '넘버링 스토리 (비워 둬도 저장돼요)', pre.st)}</div>`
    + `<div class="nm-g2"><label class="nm-fld"><span>출처</span><input type="text" data-nf="src" value="직접 추가" placeholder="예: 25 수업 강조, 스터디 예상"></label><label class="nm-fld"><span>출제 연도(있으면)</span><input type="text" data-nf="yrs" placeholder="예: 25, 23"></label></div>`
    + `<div class="nm-g2"><label class="nm-fld"><span>태그</span><input type="text" data-nf="tags" placeholder="쉼표로 나눔"></label><label class="nm-fld"><span>참고사항</span><input type="text" data-nf="note"></label></div><div class="nm-warn" data-nf-msg="1"></div>`,
    `<span style="font-size:13px;color:var(--sub)">문제 칸을 누르면 서식 도구(굵게·밑줄·색·형광펜·목록·표·그림)가 나와요</span><span style="flex:1"></span><button type="button" class="nm-btn" data-x="1">취소</button><button type="button" class="nm-btn pri" data-nfsave="1">저장</button>`);
  if (!ov) return;
  const sel = ov.querySelector('[data-nf=s]'), lsel = ov.querySelector('[data-nf=lec]');
  sel.addEventListener('change', async () => { if (sel.value !== S.sj) await seedOf(sel.value).catch(() => null); lsel.innerHTML = lecOpts(sel.value); });
  lsel.addEventListener('change', () => { if (lsel.value === '__new') { const t = prompt('새 강의 이름'); if (t && t.trim()) { const x = idx(sel.value); x.ul = x.ul || []; const k = 'U' + now().toString(36); x.ul.push({ k, t: t.trim() }); idxPut(sel.value, x); if (sel.value === S.sj) S.lecs = lectures(S.sj, S.seed); lsel.innerHTML = lecOpts(sel.value); lsel.value = k; } else lsel.value = ''; } });
  formRich(ov);
  ov.querySelector('[data-nfsave]').addEventListener('click', () => {
    const g = n => ov.querySelector(`[data-rich=${n}]`), val = n => { const h = toStore(g(n).innerHTML); return isEmpty(h) ? '' : h; };
    const q = val('q'); if (!q) { ov.querySelector('[data-nf-msg]').textContent = '문제를 써 주세요.'; g('q').focus(); return; }
    const sjv = sel.value, srcl = ov.querySelector('[data-nf=src]').value.trim() || '직접 추가', yrs = parseYrs(ov.querySelector('[data-nf=yrs]').value);
    const it = newItem({ s: sjv, lec: lsel.value === '__new' ? '' : lsel.value, q, a: val('a'), st: val('st'), note: ov.querySelector('[data-nf=note]').value.trim(), tags: ov.querySelector('[data-nf=tags]').value.split(/[,，]/).map(s => s.trim()).filter(Boolean), yrs, src: [{ t: 'user', s: sjv, lab: srcl, yrs }] });
    dlgClose();
    if (sjv !== S.sj) switchSubject(sjv, { flash: it.id }); else render({ flash: it.id });
    H.toast('새 문제를 넣었어요');
  });
  setTimeout(() => { const q = ov.querySelector('[data-rich=q]'); if (q) q.focus(); }, 30);
}
function formRich(ov) {   /* 대화창 안 서식 칸: 누른 칸 위에 같은 도구 막대 */
  ov.addEventListener('focusin', e => { const el = e.target.closest && e.target.closest('[data-rich]'); if (!el) return; if (S.formEd && S.formEd.el === el) return; $$('.nm-tb', ov).forEach(t => t.remove()); el.insertAdjacentHTML('beforebegin', tbHTML().replace('nm-tb"', 'nm-tb" style="position:static"').replace(/<button type="button" class="done"[^<]*<\/button>/, '')); S.formEd = { el, tb: el.previousElementSibling }; try { document.execCommand('styleWithCSS', false, true); document.execCommand('defaultParagraphSeparator', false, 'p'); } catch (_) {} });
  ov.addEventListener('mousedown', e => { if (e.target.closest('.nm-tb,.nm-pal')) e.preventDefault(); });
  ov.addEventListener('click', e => {
    const F = S.formEd; if (!F) return;
    const c = e.target.closest('.nm-tb [data-cmd]'), p = e.target.closest('.nm-tb [data-pal]'), fc = e.target.closest('[data-fc]'), hl = e.target.closest('[data-hl]'), tb = e.target.closest('[data-tb]');
    if (c) { F.el.focus(); if (c.dataset.cmd === 'img') { const s = getSelection(), r = s.rangeCount ? s.getRangeAt(0).cloneRange() : null; pickImage(im => { F.el.focus(); if (r) { s.removeAllRanges(); s.addRange(r); } document.execCommand('insertHTML', false, `<img src="${im.d}" width="${im.w}" height="${im.h}" alt="">`); }); } else document.execCommand(c.dataset.cmd, false, null); }
    else if (p) palOpen(p, p.dataset.pal);
    else if (fc) { F.el.focus(); document.execCommand('foreColor', false, fc.dataset.fc || '#000000'); palClose(); }
    else if (hl) { F.el.focus(); document.execCommand('hiliteColor', false, hl.dataset.hl || 'transparent'); palClose(); }
    else if (tb) { const keep = S.ed; S.ed = { el: F.el }; tblOp(tb.dataset.tb); S.ed = keep; palClose(); }
  });
  ov.addEventListener('paste', e => { if (e.target.closest && e.target.closest('[data-rich]')) onPaste(e); });
}

/* ---------- 기존 문제 불러오기(JB 기출·강의 예상문제) ---------- */
function pickHTML(root, sel) { const e = root.querySelector(sel); return e ? e : null; }
function lnHTML(box, skip) {
  if (!box) return '';
  const c = box.cloneNode(true); $$(skip || '.lab0', c).forEach(x => x.remove()); $$('button:not(.cite),.noann summary,details.srcd', c).forEach(x => x.remove());
  if (c.children.length && [...c.children].every(x => x.classList.contains('ln'))) return [...c.children].map(x => { const h = sanitize(x.innerHTML); return '<p>' + (x.classList.contains('hd') ? '<b>' + h + '</b>' : h) + '</p>'; }).join('');
  return sanitize(c.innerHTML);
}
const PARSED = new Map();
function jbList(sj) {
  if (PARSED.has(sj)) return PARSED.get(sj);
  const P = H.PACKS[sj]; if (!P) return [];
  const out = [], tpl = document.createElement('template');
  for (const id in P.cards) {
    tpl.innerHTML = P.cards[id]; const a = tpl.content.querySelector('article'); if (!a) continue;
    const lines = a.querySelector('section.ab.jbans .lines'), srcl = lines && lines.querySelector('.lab-src');
    const q = lnHTML(a.querySelector('.qtext')), an = lnHTML(lines, '.lab0,.lab-src');
    out.push({ t: 'jb', s: sj, id: a.dataset.aid || (sj + ':' + id), lec: a.dataset.lec || '', yrs: (a.dataset.yrs || '').split(/\s+/).filter(Boolean).map(y => +y < 100 ? 2000 + +y : +y), prof: a.dataset.prof || '', q, a: an, note: srcl ? srcl.textContent.replace(/^\s*참고:\s*/, '참고: ').trim() : '' });
  }
  (P.preds || []).forEach(p => {
    tpl.innerHTML = p.html; const a = tpl.content.querySelector('article'); if (!a) return;
    const q = lnHTML(a.querySelector('.pq')), box = a.querySelector('section.ab.jbans .pre2') || a.querySelector('section.ab.jbans');
    const kind = (a.querySelector('.ybadge i') || {}).textContent || '';
    out.push({ t: 'pred', s: sj, id: a.dataset.aid, lec: p.k, yrs: [], prof: '', q, a: box ? lnHTML(box, 'h5') : '', note: kind ? '예상문제 · ' + kind : '예상문제' });
  });
  out.forEach(x => { x.ty = qType(x.q, x.a); x.key = qKey(x.q); x.txt = (plain(x.q) + ' ' + plain(x.a)).toLowerCase(); });
  PARSED.set(sj, out); return out;
}
async function itemsOfSubject(sj) {   /* 다른 과목에 넣을 때의 중복 확인용 */
  if (sj === S.sj) return S.items;
  const seed = await seedOf(sj).catch(() => null), R = loadRecs(sj), L = [];
  if (seed) seed.items.forEach((b, i) => { L.push(mkSeed(sj, b, R.get(b.id), i, seed)); R.delete(b.id); });
  for (const r of R.values()) L.push(mkRec(sj, r));
  return L;
}
function dupOf(c, items) {   /* 같은 출처 = 이미 있음 · 문제 글이 같음 = 같은 문제(출처만 잇기) · 비슷함(0.75↑) = 사용자 확인 */
  for (const it of items) if (it.src.some(s => s.t === c.t && s.id === c.id)) return { k: 'have', it };
  for (const it of items) if (!it.del && c.key && kOf(it) === c.key) return { k: 'same', it };
  let best = null, bs = 0; for (const it of items) { if (it.del) continue; const k2 = kOf(it); if (!k2 || !c.key) continue; if (Math.abs(k2.length - c.key.length) > Math.max(k2.length, c.key.length) * 0.5) continue; const d = dice(k2, c.key); if (d > bs) { bs = d; best = it; } }
  if (bs >= 0.75) return { k: 'sim', it: best, d: bs };
  return null;
}
async function importDlg() {
  const jbl = subjects().filter(s => s.jbl && H.PACKS[s.id]);
  if (!jbl.length) { H.toast('과목 자료(JB)를 아직 불러오는 중이에요 — 잠시 뒤 다시 눌러 주세요'); return; }
  let sj = jbl.some(s => s.id === S.sj) ? S.sj : jbl[0].id;
  const st = { sj, lec: '', src: '', yr: '', ty: 'ess', q: '', chk: new Set() };
  const ov = dlg('기존 문제 불러오기 — JB 기출 · 강의 예상문제', `<div class="flt"><select data-if="sj" aria-label="과목">${jbl.map(s => `<option value="${s.id}"${s.id === sj ? ' selected' : ''}>${esc(s.t)}</option>`).join('')}</select><select data-if="lec" aria-label="강의"></select><select data-if="src" aria-label="출처"><option value="">JB 기출 + 예상문제</option><option value="jb">JB 기출만</option><option value="pred">강의 예상문제만</option></select><select data-if="yr" aria-label="출제 연도"></select><select data-if="ty" aria-label="문제 유형"><option value="ess" selected>서술형·넘버링형만</option><option value="">전체 문제</option>${Object.keys(TYPES).map(k => `<option value="${k}">${TYPES[k]}만</option>`).join('')}</select><input type="search" data-if="q" placeholder="문제·답 검색" aria-label="검색"></div><div class="nm-warn" data-if-info="1"></div><div class="nm-ilist" data-ilist="1"></div>`,
    `<span data-if-sum="1" style="font-size:13.5px"></span><span style="flex:1"></span><button type="button" class="nm-btn" data-ib="sel">고른 것 추가</button><button type="button" class="nm-btn" data-ib="lec">이 강의 전체</button><button type="button" class="nm-btn" data-ib="flt">거른 결과 전체</button><button type="button" class="nm-btn" data-ib="all">과목 전체</button>`);
  if (!ov) return;
  let target = await itemsOfSubject(st.sj), list = [];
  const P = () => H.PACKS[st.sj];
  const fill = () => {
    const L = jbList(st.sj), lecs = P().lect;
    ov.querySelector('[data-if=lec]').innerHTML = `<option value="">모든 강의</option>` + lecs.map(l => `<option value="${esc(l.k)}"${l.k === st.lec ? ' selected' : ''}>${esc(l.title)}</option>`).join('');
    const ys = [...new Set(L.flatMap(x => x.yrs))].sort((a, b) => b - a);
    ov.querySelector('[data-if=yr]').innerHTML = `<option value="">모든 연도</option>` + ys.map(y => `<option value="${y}"${String(y) === st.yr ? ' selected' : ''}>${y}년 출제</option>`).join('');
  };
  const lecT = k => { const l = P().lect.find(x => x.k === k); return l ? l.title : k; };
  const filt = () => { const ws = st.q.toLowerCase().split(/\s+/).filter(Boolean); return jbList(st.sj).filter(x => (!st.lec || x.lec === st.lec) && (!st.src || x.t === st.src) && (!st.yr || x.yrs.includes(+st.yr)) && (!st.ty || (st.ty === 'ess' ? essayish(x.ty) : x.ty === st.ty)) && ws.every(w => x.txt.indexOf(w) >= 0)); };
  const draw = () => {
    list = filt();
    const box = ov.querySelector('[data-ilist]');
    box.innerHTML = list.length ? list.map(x => { const d = dupOf(x, target); x.dup = d; return `<div class="nm-irow${d && d.k !== 'sim' ? ' dup' : ''}" data-ix="${esc(x.id)}"><input type="checkbox" data-ick="1"${st.chk.has(x.id) ? ' checked' : ''}${d && d.k === 'have' ? ' disabled' : ''} aria-label="고르기"><div><div class="t">${esc(plain(x.q))}</div><div class="m"><span class="nm-chip k-${x.t}">${x.t === 'jb' ? 'JB 기출' + (x.prof ? ' · ' + esc(x.prof) : '') : '예상문제'}</span>${x.yrs.length ? `<span class="nm-chip yr">${esc(yrsTxt(x.yrs))}</span>` : ''}<span class="nm-chip">${esc(TYPES[x.ty])}</span><span class="nm-chip">${esc(lecT(x.lec))}</span>${d ? `<span class="nm-chip ${d.k === 'sim' ? 'rv' : 's2'}" title="${esc(plain(d.it.q).slice(0, 200))}">${d.k === 'have' ? '이미 있음' : d.k === 'same' ? '같은 문제 있음 → 출처만 연결' : '비슷한 문제 있음(' + Math.round(d.d * 100) + '%)'}</span>` : ''}</div></div><button type="button" class="nm-btn add" data-iadd="1"${d && d.k === 'have' ? ' disabled' : ''}>${d && d.k === 'same' ? '출처 연결' : '추가'}</button></div>`; }).join('') : '<div class="nm-empty">조건에 맞는 문제가 없어요.</div>';
    sum();
  };
  const sum = () => { const n = list.length, nh = list.filter(x => x.dup && x.dup.k === 'have').length; ov.querySelector('[data-if-sum]').innerHTML = `보이는 ${n}문제(이미 있음 ${nh}) · 고른 것 <b>${st.chk.size}</b>`; ov.querySelector('[data-if-info]').textContent = st.ty === 'ess' ? '서술형·넘버링형만 보는 중 — 판정은 문제 글(서술·설명·~가지 등)과 답 모양으로 해요. 빠진 문제가 있으면 유형을 \'전체 문제\'로 바꿔 직접 고르세요.' : ''; };
  fill(); draw();
  const on = (sel, ev, f) => ov.querySelector(sel).addEventListener(ev, f);
  on('[data-if=sj]', 'change', async e => { st.sj = e.target.value; st.lec = ''; st.yr = ''; st.chk.clear(); target = await itemsOfSubject(st.sj); fill(); draw(); });
  on('[data-if=lec]', 'change', e => { st.lec = e.target.value; draw(); });
  on('[data-if=src]', 'change', e => { st.src = e.target.value; draw(); });
  on('[data-if=yr]', 'change', e => { st.yr = e.target.value; draw(); });
  on('[data-if=ty]', 'change', e => { st.ty = e.target.value; draw(); });
  let qt = 0; on('[data-if=q]', 'input', e => { clearTimeout(qt); qt = setTimeout(() => { st.q = e.target.value; draw(); }, 200); });
  ov.querySelector('[data-ilist]').addEventListener('change', e => { const r = e.target.closest('[data-ix]'); if (!r || !e.target.matches('[data-ick]')) return; if (e.target.checked) st.chk.add(r.dataset.ix); else st.chk.delete(r.dataset.ix); sum(); });
  ov.querySelector('[data-ilist]').addEventListener('click', e => { const b = e.target.closest('[data-iadd]'); if (!b) return; const r = b.closest('[data-ix]'); const x = list.find(y => y.id === r.dataset.ix); if (x) confirmAdd([x], st.sj, ov, async () => { target = await itemsOfSubject(st.sj); draw(); }); });
  ov.querySelector('footer').addEventListener('click', e => { const b = e.target.closest('[data-ib]'); if (!b) return; const k = b.dataset.ib, all = jbList(st.sj);
    const L = k === 'sel' ? all.filter(x => st.chk.has(x.id)) : k === 'lec' ? (st.lec ? all.filter(x => x.lec === st.lec && (!st.ty || (st.ty === 'ess' ? essayish(x.ty) : x.ty === st.ty))) : null) : k === 'flt' ? list : all;
    if (L == null) { H.toast('강의를 먼저 고르세요(강의 선택 칸)'); return; }
    if (!L.length) { H.toast(k === 'sel' ? '고른 문제가 없어요 — 왼쪽 네모를 눌러 고르세요' : '넣을 문제가 없어요'); return; }
    confirmAdd(L, st.sj, ov, async () => { st.chk.clear(); target = await itemsOfSubject(st.sj); draw(); }); });
}
function confirmAdd(L, sj, ov, after) {
  itemsOfSubject(sj).then(target => {
    const plan = L.map(x => ({ x, d: dupOf(x, target) }));
    const nNew = plan.filter(p => !p.d).length, nHave = plan.filter(p => p.d && p.d.k === 'have').length, nSame = plan.filter(p => p.d && p.d.k === 'same').length, sim = plan.filter(p => p.d && p.d.k === 'sim');
    const box = document.createElement('div'); box.className = 'nm-ov'; box.style.zIndex = 70;
    box.innerHTML = `<div class="nm-dlg" style="width:min(760px,100%)"><header><h3>${esc(subjT(sj))} 넘버링에 넣기 — 확인</h3></header><div class="bd"><div>고른 문제 <b>${L.length}</b> · 새로 넣을 문제 <b>${nNew + sim.length}</b> · 이미 있음(건너뜀) <b>${nHave}</b> · 같은 문제(출처·연도만 연결) <b>${nSame}</b>${sim.length ? ` · 비슷한 문제 <b>${sim.length}</b>` : ''}</div>${sim.length ? `<div class="nm-warn">비슷한 문제는 기본으로 따로 넣어요. 같은 문제라면 체크해 출처만 연결하세요.</div><div class="nm-ilist" style="max-height:40vh">${sim.map((p, i) => `<label class="nm-irow" style="grid-template-columns:28px minmax(0,1fr)"><input type="checkbox" data-sim="${i}"><div><div class="t">${esc(plain(p.x.q))}</div><div class="m"><span class="nm-chip rv">비슷 ${Math.round(p.d.d * 100)}%</span><span class="t" style="-webkit-line-clamp:1">이미 있는 문제: ${esc(plain(p.d.it.q))}</span></div></div></label>`).join('')}</div>` : ''}</div><footer><span style="flex:1"></span><button type="button" class="nm-btn" data-cf2="no">취소</button><button type="button" class="nm-btn pri" data-cf2="ok"${nNew + sim.length + nSame ? '' : ' disabled'}>넣기</button></footer></div>`;
    (ov || $('#numv')).appendChild(box);
    box.addEventListener('click', e => { const b = e.target.closest('[data-cf2]'); if (!b) return; if (b.dataset.cf2 === 'no') { box.remove(); return; }
      const simMerge = new Set($$('[data-sim]:checked', box).map(c => +c.dataset.sim));
      const r = addMany(plan, sim, simMerge, sj); box.remove();
      if (r.err) { H.toast('넣다가 멈췄어요 — 기존 넘버링은 그대로예요: ' + r.err, { level: 'error', id: 'nmimp' }); return; }
      H.toast(`${subjT(sj)} — 새 문제 ${r.add} · 출처 연결 ${r.link}${r.skip ? ' · 건너뜀 ' + r.skip : ''}`, { level: 'result', action: sj !== S.sj ? { label: '보기', fn: () => { dlgClose(); switchSubject(sj); } } : null });
      if (after) after(); });
  });
}
function addMany(plan, sim, simMerge, sj) {   /* 한 번에 — 기록은 사본에 먼저 쓰고, 중간에 실패하면 이번에 쓴 키를 모두 되돌림(기존 문제 손상 없음) */
  const t = now(), live = sj === S.sj, before = new Map(), recs = [], apply = []; let add = 0, link = 0, skip = 0;
  let o = (live ? S.items.reduce((m, it) => Math.max(m, it.o || 0), -1) : 1e6) + 1;
  const lab = x => x.t === 'jb' ? 'JB 기출' + (x.prof ? ' · ' + x.prof : '') : '예상문제';
  const linked = new Map();   /* 같은 문제에 여러 출처를 이을 때 사본 하나에 모음 */
  for (const p of plan) {
    const x = p.x, d = p.d, si = sim.indexOf(p);
    if (d && d.k === 'have') { skip++; continue; }
    if (d && (d.k === 'same' || (d.k === 'sim' && simMerge.has(si)))) {
      const it = d.it, c = linked.get(it) || { src: it.src.map(z => Object.assign({}, z)), yrs: it.yrs.slice() };
      if (c.src.some(z => z.t === x.t && z.id === x.id)) { skip++; continue; }
      c.src.push({ t: x.t, s: x.s, id: x.id, lec: x.lec, yrs: x.yrs, lab: lab(x) }); c.yrs = [...new Set(c.yrs.concat(x.yrs))].sort((p1, p2) => p2 - p1); linked.set(it, c); link++; continue;
    }
    const id = (x.t === 'jb' ? 'jb:' : 'pr:') + x.id, old = live && S.by.get(id);
    if (old && old.del) { apply.push(() => { old.del = false; old.u = t; }); recs.push([keyI(sj, id), Object.assign(toRec(old), { del: undefined, u: t })]); add++; continue; }   /* 뺐던 문제 = 다시 넣기 */
    const it = { id, s: sj, kind: x.t, lec: x.lec, q: x.q, a: x.a, st: '', note: x.note || '', tags: [], yrs: x.yrs.slice(), src: [{ t: x.t, s: x.s, id: x.id, lec: x.lec, yrs: x.yrs, lab: lab(x) }], ref: { t: x.t, s: x.s, id: x.id }, done: false, o: o++, c: t, u: t, del: false, rv: [], rvok: false, prev: null };
    recs.push([keyI(sj, id), toRec(it)]); apply.push(() => { if (live && !S.by.has(it.id)) { S.items.push(it); S.by.set(it.id, it); } }); add++;
  }
  for (const [it, c] of linked) { const r = Object.assign(toRec(Object.assign({}, it, { src: c.src, yrs: c.yrs, u: t }))); recs.push([keyI(sj, it.id), r]); apply.push(() => { it.src = c.src; it.yrs = c.yrs; it.u = t; it._t = null; }); }
  try {
    for (const [k, r] of recs) { if (!before.has(k)) before.set(k, localStorage.getItem(H.NS + k)); localStorage.setItem(H.NS + k, JSON.stringify(r)); }
  } catch (e) {
    for (const [k, v] of before) { try { if (v == null) localStorage.removeItem(H.NS + k); else localStorage.setItem(H.NS + k, v); } catch (_) {} }
    return { err: e && (e.name === 'QuotaExceededError' || e.code === 22) ? '이 기기 저장 공간이 부족해요' : String(e && e.message || e) };
  }
  apply.forEach(f => f());
  if (live) render({ pos: topItem() });
  bumpIdx(sj); saveState('ok');
  return { add, link, skip };
}

/* ---------- Word 파일 가져오기(미리 보고 고른 뒤) ---------- */
async function fileImport() {
  const inp = document.createElement('input'); inp.type = 'file'; inp.accept = '.docx,application/vnd.openxmlformats-officedocument.wordprocessingml.document';
  inp.onchange = async () => {
    const f = inp.files && inp.files[0]; if (!f) return;
    if (!/\.docx$/i.test(f.name)) { H.toast('Word(.docx) 파일만 가져올 수 있어요 — .doc·.hwp·.pdf는 Word에서 .docx로 저장해 주세요', { level: 'error', id: 'nmfile' }); return; }
    const ov = dlg('파일 가져오기 — ' + f.name, `<div class="nm-prog" data-prog="1">Word 읽는 중…</div>`, '');
    try {
      if (!window.JBLDOCX) await loadScript(H.base + 'num/docx.js?v=' + H.v);
      const r = await window.JBLDOCX.parse(await f.arrayBuffer(), { img: 'inline', maxW: 900, q: 0.72, onProgress: m => { const p = ov && ov.querySelector('[data-prog]'); if (p) p.textContent = m + '…'; } });
      if (!$('.nm-ov')) return;
      filePreview(f.name, r);
    } catch (e) { const p = ov && ov.querySelector('[data-prog]'); if (p) p.innerHTML = '⚠ ' + esc(e.message || String(e)) + '<br><small>기존 넘버링은 바뀌지 않았어요.</small>'; }
  };
  inp.click();
}
function filePreview(fname, r) {
  const subs = subjects(), title = (r.title || fname.replace(/\.docx$/i, '')).trim();
  const guess = subs.find(s => title.indexOf(s.t) >= 0 || title.indexOf(s.sh) >= 0);
  const secs = r.sections.filter(s => s.n);
  const bytes = JSON.stringify(r.items).length;
  const it2 = r.items.map((x, i) => Object.assign(x, { i, on: true }));
  const ov = dlg('파일 가져오기 — 미리 보기', `<div class="nm-g2"><label class="nm-fld"><span>넣을 과목</span><select data-fp="s">${subs.map(s => `<option value="${esc(s.id)}"${guess && guess.id === s.id ? ' selected' : ''}>${esc(s.t)}</option>`).join('')}<option value="__new"${guess ? '' : ' selected'}>+ 새 과목: ${esc(title.slice(0, 30))}</option></select></label><label class="nm-fld"><span>칸 읽기</span><select data-fp="swap"><option value="">답안 = ${r.layout === 'qrow' ? '오른쪽 칸' : '정답 칸'} · 스토리 = ${r.layout === 'qrow' ? '왼쪽 칸' : '암기법 칸'}(자동)</option><option value="1">답안 ↔ 스토리 바꾸기</option></select></label></div>`
    + `<div>형식: <b>${r.layout === 'qas' ? '문제|정답|암기법 3칸 표' : r.layout === 'qrow' ? '문제 줄 + 스토리|답 2칸 표' : '알아보지 못함(첫 칸=문제·둘째=답·셋째=스토리로 읽음)'}</b> · 강의 ${secs.length} · 문제 ${r.items.length} · 그림 ${Object.keys(r.images || {}).length || (JSON.stringify(r.items).match(/<img /g) || []).length} · 검토 표시 ${r.items.filter(x => x.rv && x.rv.length).length} · 저장 크기 약 ${(bytes / 1e6).toFixed(1)}MB${bytes > 2.5e6 ? ' <span class="nm-warn">— 그림이 많아 이 기기 저장 공간을 많이 써요</span>' : ''}</div>`
    + (r.flags.length ? `<div class="nm-warn">${r.flags.map(x => esc(x.m)).join('<br>')}</div>` : '')
    + `<div class="nm-ilist" style="max-height:58vh" data-fplist="1">${secs.map(s => `<div style="padding:8px 10px;background:#F6F4EF;border-bottom:1px solid #E4DFD5;display:flex;gap:8px;align-items:center;flex-wrap:wrap"><b>강의</b><input class="nm-lecin" data-lecname="${esc(s.k)}" value="${esc(s.title)}" aria-label="강의 이름"><small>${esc([s.prof, s.lab].filter(Boolean).join(' · '))} · ${s.n}문제</small></div>` + it2.filter(x => x.lec === s.k).map(x => `<div class="nm-irow" data-fi="${x.i}"><input type="checkbox" checked data-fck="1" aria-label="넣기"><div><div class="t">${esc(plain(x.q))}</div><div class="m">${x.yrs.length ? `<span class="nm-chip yr">${esc(yrsTxt(x.yrs))}</span>` : ''}${x.tags.map(t => `<span class="nm-chip">${esc(t)}</span>`).join('')}${isEmpty(x.st) ? '<span class="nm-chip s0">스토리 없음</span>' : '<span class="nm-chip s1">스토리 있음</span>'}${x.rv && x.rv.length ? `<span class="nm-chip rv" title="${esc(x.rv.map(v => v.m).join('\n'))}">⚠ 검토</span>` : ''}</div></div><button type="button" class="nm-btn add" data-fview="1">자세히</button></div>`).join('')).join('')}</div>`,
    `<span data-fpsum="1" style="font-size:13.5px"></span><span style="flex:1"></span><button type="button" class="nm-btn" data-x="1">취소</button><button type="button" class="nm-btn pri" data-fpgo="1">가져오기</button>`);
  if (!ov) return;
  const sum = () => { const n = $$('[data-fck]:checked', ov).length; ov.querySelector('[data-fpsum]').textContent = `넣을 문제 ${n} / ${r.items.length} — 같은 문제가 이미 있으면 출처만 연결해요`; };
  sum();
  ov.querySelector('[data-fplist]').addEventListener('change', e => { if (e.target.matches('[data-fck]')) { it2[+e.target.closest('[data-fi]').dataset.fi].on = e.target.checked; sum(); } });
  ov.querySelector('[data-fplist]').addEventListener('click', e => { const b = e.target.closest('[data-fview]'); if (!b) return; const row = b.closest('[data-fi]'), x = it2[+row.dataset.fi]; const nx = row.nextElementSibling; if (nx && nx.classList.contains('nm-prev')) { nx.remove(); return; } const sw = ov.querySelector('[data-fp=swap]').value === '1'; row.insertAdjacentHTML('afterend', `<div class="nm-prev"><div class="nm-q"><div class="nm-c">${sanitize(x.q)}</div></div><div class="nm-body"><section class="nm-col"><div class="nm-lab">답안</div><div class="nm-c">${sanitize(sw ? x.st : x.a) || '<span class="nm-ph">없음</span>'}</div></section><section class="nm-col"><div class="nm-lab">넘버링 스토리</div><div class="nm-c">${sanitize(sw ? x.a : x.st) || '<span class="nm-ph">없음</span>'}</div></section></div>${x.note ? `<div class="nm-note">참고: ${esc(x.note)}</div>` : ''}${x.rv && x.rv.length ? `<div class="nm-warn">${x.rv.map(v => esc(v.m)).join('<br>')}</div>` : ''}</div>`); });
  ov.querySelector('[data-fpgo]').addEventListener('click', async () => {
    let sj = ov.querySelector('[data-fp=s]').value; const sw = ov.querySelector('[data-fp=swap]').value === '1';
    const names = {}; $$('[data-lecname]', ov).forEach(i => { names[i.dataset.lecname] = i.value.trim() || i.dataset.lecname; });
    const pick = it2.filter(x => x.on); if (!pick.length) { H.toast('넣을 문제를 하나 이상 고르세요'); return; }
    const keysWritten = []; const t = now();
    try {
      if (sj === '__new') { const L = H.LS.get('num.subj', []) || []; sj = 'U' + t.toString(36).toUpperCase(); L.push({ id: sj, t: title.slice(0, 40) }); H.LS.set('num.subj', L); }
      const target = await itemsOfSubject(sj); const x = idx(sj); x.ul = x.ul || []; const lmap = {};
      const exist = lectures(sj, (window.JBLNUM_SEED || {})[sj]);
      for (const s of secs) { const nm = names[s.k]; const hit = exist.find(l => l.t === nm) || x.ul.find(l => l.t === nm); if (hit) lmap[s.k] = hit.k; else { const k = 'U' + t.toString(36) + s.k; x.ul.push({ k, t: nm }); lmap[s.k] = k; } }
      let o = target.reduce((m, it) => Math.max(m, it.o || 0), -1) + 1, add = 0, link = 0; const live = sj === S.sj; const changed = [];
      for (const y of pick) {
        const q = sanitize(y.q), a = sanitize(sw ? y.st : y.a), st = sanitize(sw ? y.a : y.st), key = qKey(q);
        const aKey = norm(plain(a)), same0 = key && target.find(it => !it.del && kOf(it) === key && norm(plain(it.a)) === aKey), qOnly = !same0 && key && target.find(it => !it.del && kOf(it) === key);   /* 문제·답이 모두 같을 때만 출처 연결 — 문제만 같고 답이 다르면 따로 넣고 검토 표시 */
        const src = { t: 'word', s: sj, lab: 'Word: ' + fname.replace(/\.docx$/i, '') + (y.lab ? ' · ' + y.lab : ''), yrs: y.yrs };
        if (same0) { if (!same0.src.some(s2 => s2.t === 'word' && s2.lab === src.lab)) { same0.src.push(src); same0.yrs = [...new Set(same0.yrs.concat(y.yrs))].sort((p, q2) => q2 - p); same0.u = t; changed.push(same0); link++; } continue; }
        const it = { id: 'w:' + t.toString(36) + ':' + y.i, s: sj, kind: 'word', lec: lmap[y.lec] || '', q, a, st, note: y.note || '', tags: y.tags || [], yrs: y.yrs || [], src: [src], ref: null, done: false, o: o++, c: t, u: t, del: false, rv: (y.rv || []).concat(qOnly ? [{ k: 'qsame', m: '문제 글이 같은 문제가 이미 있지만 답이 달라 따로 넣음 — 같은 문제면 \'여러 개 선택 → 합치기\'' }] : []), rvok: false, prev: null };
        changed.push(it); target.push(it); add++;
      }
      for (const it of changed) { localStorage.setItem(H.NS + keyI(sj, it.id), JSON.stringify(toRec(it))); keysWritten.push(keyI(sj, it.id)); }
      idxPut(sj, x);
      dlgClose(); H.toast(`가져왔어요 — 새 문제 ${add}${link ? ' · 같은 문제 출처 연결 ' + link : ''}`, { level: 'result' });
      if (live) await switchSubject(sj, { force: true }); else await switchSubject(sj);
    } catch (e) {
      for (const k of keysWritten) { try { localStorage.removeItem(H.NS + k); } catch (_) {} }
      H.toast('가져오지 못했어요 — 기존 넘버링은 그대로예요: ' + (e && (e.name === 'QuotaExceededError' || e.code === 22) ? '이 기기 저장 공간이 부족해요(그림이 많은 파일은 나눠서)' : String(e && e.message || e)), { level: 'error', id: 'nmfile' });
    }
  });
}

/* ---------- 여러 개 선택 ---------- */
function batch(k, btn) {
  const L = [...S.sel].map(id => S.by.get(id)).filter(Boolean);
  if (k === 'all') { $$('.nm-it:not([hidden])', S.root).forEach(a => S.sel.add(a.dataset.id)); $$('.nm-it:not([hidden]) [data-ck]', S.root).forEach(c => c.checked = true); applyFilter(); return; }
  if (k === 'none') { S.sel.clear(); $$('[data-ck]', S.root).forEach(c => c.checked = false); applyFilter(); return; }
  if (!L.length) return;
  if (k === 'done' || k === 'undone') { L.forEach(it => { it.done = k === 'done'; touch(it); put(it); }); render({ pos: topItem() }); return; }
  if (k === 'del') { if (!confirm(L.length + '개 문제를 목록에서 뺄까요? (원본은 그대로 · 맨 아래에서 다시 넣을 수 있어요)')) return; L.forEach(it => { it.del = true; touch(it); put(it); }); S.sel.clear(); render({ pos: topItem() }); return; }
  if (k === 'move') { lecPick(btn, l => { L.forEach(it => { it.lec = l; touch(it); put(it); }); render({ pos: topItem() }); H.toast(L.length + '개를 옮겼어요'); }); return; }
  if (k === 'merge') {
    const tgt = L.slice().sort((a, b) => a.o - b.o)[0], rest = L.filter(x => x !== tgt);
    const withSt = L.filter(x => !isEmpty(x.st)); if (withSt.length > 1) { alert('스토리가 있는 문제가 ' + withSt.length + '개라 합칠 수 없어요 — 한 문제에는 스토리 하나만 둬요. 하나만 남기고 다시 해 주세요.'); return; }
    if (!confirm(`${L.length}개를 첫 문제(${plain(tgt.q).slice(0, 40)}…) 하나로 합칠까요?\n출처·연도·태그를 모으고, 나머지는 목록에서 빼요(원본은 그대로).`)) return;
    rest.forEach(x => { x.src.forEach(s => { if (!tgt.src.some(z => z.t === s.t && z.id === s.id && z.lab === s.lab)) tgt.src.push(s); }); tgt.yrs = [...new Set(tgt.yrs.concat(x.yrs))].sort((a, b) => b - a); tgt.tags = [...new Set((tgt.tags || []).concat(x.tags || []))]; if (isEmpty(tgt.st) && !isEmpty(x.st)) tgt.st = x.st; x.del = true; touch(x); put(x); });
    touch(tgt); put(tgt); S.sel.clear(); render({ flash: tgt.id }); return;
  }
}

/* ---------- 열기·과목 바꾸기 ---------- */
async function switchSubject(sj, o) {
  o = o || {}; endEdit(true);
  if (S.sj && S.sj !== sj) H.LS.set('num.pos.' + S.sj, topItem());
  S.sj = sj; S.cfg.sj = sj; if (!o.keepF && !o.force) S.cfg.f.lec = ''; cfgSave(); S.sel.clear();
  S.root.innerHTML = '<div id="numv"><div class="nm-prog">넘버링 불러오는 중…</div></div>';
  await loadSubject(sj);
  if (S.cfg.f.lec && !S.lecs.some(l => l.k === S.cfg.f.lec) && S.cfg.f.lec !== '__none') S.cfg.f.lec = '';
  H.histSet({ num: 1, sj }, '#/_num/' + sj, false);
  render({ pos: o.flash ? null : (o.pos || H.LS.get('num.pos.' + sj, null)), flash: o.flash });
}
let bound = false;
function bind() {
  if (bound) return; bound = true;
  document.addEventListener('click', e => {
    if (!S.root || !S.root.isConnected || !document.getElementById('numv')) return;
    const t = e.target; if (!t.closest) return;
    if (!t.closest('.nm-menu') && !t.closest('[data-act=more]') && !t.closest('[data-mi]')) menuClose();
    if (!t.closest('.nm-pal') && !t.closest('[data-pal]')) palClose();
    if (!S.root.contains(t)) return;
    if (t.closest('.nm-ov')) return;   /* 대화창은 따로 */
    const tb = t.closest('.nm-tb'); if (tb) { const c = t.closest('[data-cmd]'), p = t.closest('[data-pal]'); if (c) edCmd(c.dataset.cmd); else if (p) palOpen(p, p.dataset.pal); return; }
    const fc = t.closest('[data-fc]'), hl = t.closest('[data-hl]'), tbo = t.closest('[data-tb]');
    if (fc && S.ed) { S.ed.el.focus(); document.execCommand('foreColor', false, fc.dataset.fc || '#000000'); palClose(); edInput(); return; }
    if (hl && S.ed) { S.ed.el.focus(); document.execCommand('hiliteColor', false, hl.dataset.hl || 'transparent'); palClose(); edInput(); return; }
    if (tbo && S.ed) { S.ed.el.focus(); tblOp(tbo.dataset.tb); palClose(); return; }
    const md = t.closest('[data-mode]'); if (md) { S.cfg.mode = md.dataset.mode; cfgSave(); render({ pos: topItem() }); return; }
    const sf = t.closest('[data-stf]'); if (sf) { S.cfg.f.st = sf.dataset.stf; cfgSave(); const s = $('[data-cf=st]', S.root); if (s) s.value = S.cfg.f.st; applyFilter(); return; }
    const bt = t.closest('[data-bat]'); if (bt) { batch(bt.dataset.bat, bt); return; }
    const a = t.closest('[data-act]');
    if (a) {
      const k = a.dataset.act, art = a.closest('.nm-it'), it = art && S.by.get(art.dataset.id);
      if (k === 'more' && it) { itemMenu(a, it); return; }
      if (k === 'det' && it) { detOpen(it); return; }
      if (k === 'edit' && it) { const el = art.querySelector(`.nm-c[data-f="${a.dataset.f}"]`); if (el) startEdit(el, it, a.dataset.f); return; }
      if (k === 'new') { newForm(); return; }
      if (k === 'imp') { importDlg(); return; }
      if (k === 'file') { fileImport(); return; }
      if (k === 'selm') { S.selMode = !S.selMode; if (!S.selMode) S.sel.clear(); render({ pos: topItem() }); return; }
      if (k === 'undel') { const id = a.closest('[data-id]').dataset.id, x = S.by.get(id); if (x) { x.del = false; touch(x); put(x); render({ flash: x.id }); } return; }
    }
    const st = t.closest('.nm-s .nm-c[data-f=st]');
    if (st && !(S.ed && S.ed.el === st) && !t.closest('a')) { const art = st.closest('.nm-it'), it = S.by.get(art.dataset.id); if (it) startEdit(st, it, 'st', e); return; }
  });
  document.addEventListener('mousedown', e => { if (S.ed && e.target.closest && (e.target.closest('.nm-tb') || e.target.closest('.nm-pal'))) e.preventDefault(); }, true);
  document.addEventListener('change', e => {
    if (!S.root || !S.root.contains(e.target) || e.target.closest('.nm-ov')) return;
    const c = e.target.dataset.cf;
    if (e.target.matches('[data-ck]')) { const id = e.target.closest('.nm-it').dataset.id; if (e.target.checked) S.sel.add(id); else S.sel.delete(id); const b = $('[data-batch]', S.root); if (b) b.innerHTML = batchHTML(); return; }
    if (!c || c === 'q') return;
    if (c === 'sj') { if (e.target.value === '__new') { const t = prompt('새 과목 이름(예: 교정학 2)'); if (!t || !t.trim()) { e.target.value = S.sj; return; } const L = H.LS.get('num.subj', []) || []; const id = 'U' + now().toString(36).toUpperCase(); L.push({ id, t: t.trim() }); H.LS.set('num.subj', L); switchSubject(id); return; } switchSubject(e.target.value); return; }
    if (c === 'sort') { S.cfg.sort = e.target.value; cfgSave(); render({ pos: topItem() }); return; }
    S.cfg.f[c] = e.target.value; cfgSave(); applyFilter();
    if (c === 'lec' && S.cfg.f.lec) window.scrollTo(0, Math.max(0, S.root.getBoundingClientRect().top + scrollY - 60));
  });
  let qt = 0;
  document.addEventListener('input', e => {
    if (!S.root || !S.root.contains(e.target)) return;
    if (S.ed && S.ed.el.contains(e.target)) { edInput(); return; }
    if (e.target.dataset && e.target.dataset.cf === 'q') { clearTimeout(qt); qt = setTimeout(() => { S.q = e.target.value.trim(); applyFilter(); }, 200); }
  });
  document.addEventListener('paste', e => { if (S.ed && S.ed.el.contains(e.target)) onPaste(e); });
  document.addEventListener('pointerdown', e => { if (S.ed && e.target.closest && (e.target.closest('.nm-tb') || e.target.closest('.nm-pal'))) S.tbAt = now(); }, true);
  document.addEventListener('focusout', e => { const E = S.ed; if (!E || e.target !== E.el) return; setTimeout(() => { if (S.ed !== E || E.busy || now() - (S.tbAt || 0) < 600) return; const ae = document.activeElement; if (ae && (E.el.contains(ae) || (E.tb && E.tb.contains(ae)) || ae.closest && ae.closest('.nm-pal'))) return; if (document.hidden) { edSave(); return; } endEdit(); }, 150); });
  document.addEventListener('keydown', e => { if (!S.ed) return; if (e.key === 'Escape') { e.preventDefault(); e.stopPropagation(); endEdit(); return; } const mod = e.metaKey || e.ctrlKey; if (mod && e.shiftKey && (e.key === 'x' || e.key === 'X' || e.key === '5')) { e.preventDefault(); } }, true);
  addEventListener('pagehide', flush); document.addEventListener('visibilitychange', () => { if (document.hidden) flush(); });
  addEventListener('storage', e => {   /* 다른 창에서 고친 문제 */
    if (!S.root || !document.getElementById('numv') || !e.key || e.key.indexOf(H.NS + 'num.i.' + S.sj + '.') !== 0) return;
    const id = e.key.slice((H.NS + 'num.i.' + S.sj + '.').length), it = S.by.get(id); if (S.ed && S.ed.it.id === id) return;
    let r = null; try { r = e.newValue ? JSON.parse(e.newValue) : null; } catch (_) {}
    if (it && it.kind === 'seed') { const n = mkSeed(S.sj, it.base, r, it.oi, S.seed); Object.assign(it, n, { _t: null, _ty: null }); }
    else if (r) { const n = mkRec(S.sj, r); if (it) Object.assign(it, n, { _t: null, _ty: null }); else { S.items.push(n); S.by.set(n.id, n); render({ pos: topItem() }); return; } }
    if (it) rerenderItem(it); applyFilter();
  });
}
function flush() { if (S.ed) edSave(); }
function leave() { if (!S.root) return; try { endEdit(true); if (S.sj && document.getElementById('numv')) H.LS.set('num.pos.' + S.sj, topItem()); } catch (e) {} menuClose(); dlgClose(); document.body.classList.remove('v-num'); S.root = null; }
async function open(root, o, host) {
  H = host; css(); bind(); cfg(); S.root = root; document.body.classList.add('v-num');
  root.innerHTML = '<div id="numv"><div class="nm-prog">넘버링 불러오는 중…</div></div>';
  await index();
  const subs = subjects(); let sj = o.sj && subs.some(s => s.id === o.sj) ? o.sj : (S.cfg.sj && subs.some(s => s.id === S.cfg.sj) ? S.cfg.sj : (subs.find(s => s.seed) || subs[0]).id);
  if (S.root !== root) return;
  S.sj = sj; S.cfg.sj = sj; cfgSave();
  await loadSubject(sj);
  if (S.root !== root) return;
  if (S.cfg.f.lec && !S.lecs.some(l => l.k === S.cfg.f.lec) && S.cfg.f.lec !== '__none') S.cfg.f.lec = '';
  H.histSet({ num: 1, sj }, '#/_num/' + sj, !!o.push);
  render({ pos: o.y != null ? null : H.LS.get('num.pos.' + sj, null), y: o.y });
}
window.JBLNUM = { open, leave, flush, state: () => ({ num: 1, sj: S.sj }), _S: S, _H: () => H, _qType: qType, _sanitize: sanitize, _plain: plain };
})();
