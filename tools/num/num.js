/* JBL 내 넘버링 (10-10 · 처음 이름 '넘버링 따기') — 허브(index.html)가 '#/_num' 화면을 열 때만 불러오는 모듈. 홈·과목 화면의 첫 로딩에는 들어가지 않는다.
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
const YTAG = /^\s*(?:(?:20)?\d{2}\s*(?:년도?)?\s*(?:탈|짤|매칭|객관식|객|빈칸|서술|기출|출제\s*예고|탈\s*대비|수업\s*강조|강조)?\s*[’']?\s*\??|과거\s*\S*|옛날\s*\S*|탈|짤|탈\s*대비\??|매칭|NEW|new|짤\s*변형)\s*$/;
const qKey = h => norm(plain(h).replace(/^\s*\d{1,2}(?:-\d)?\s*[.)]\s*/, '').replace(/\(([^()]{0,60})\)/g, (m, x) => x.split(/[,，]/).every(t => YTAG.test(t)) ? '' : m));   /* 번호와 '(24,22)·(25탈)·(과거)'처럼 연도·꼬리표만 있는 괄호만 빼고 비교 — '(10 mm)'·'(전방 탈구)'는 남김 */
const keyOK = k => k && k.length >= 8 && !/미복원|복원불충분|복원부실/.test(k);   /* 너무 짧거나 '미복원' 같은 자리표는 글로 같다고 보지 않음 */
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
      { const pl = /^(\d+(?:\.\d+)?)em$/.exec(sv['padding-left'] || ''); if ((tg === 'P' || tg === 'LI') && pl && +pl[1] <= 12) css += 'padding-left:' + pl[1] + 'em;'; }   /* Word 목록 들여쓰기 */
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
function cfg() { if (!S.cfg) { const c = H.LS.get('num.cfg', null) || {}; S.cfg = { sj: c.sj || '', mode: c.mode === 'all' ? 'all' : 'grp', sort: c.sort || 'lec', f: Object.assign({ lec: '', type: '', st: '', src: '', yr: '' }, c.f || {}), hide: Object.assign({ a: false, st: false }, c.hide || {}), side: c.side === 'c' ? 'c' : '' }; } return S.cfg; }
function cfgSave() { H.LS.set('num.cfg', S.cfg); }
function idx(sj) { const x = H.LS.get('num.x.' + sj, null); return x && typeof x === 'object' ? x : { v: 1, ul: [], lt: {} }; }
function idxPut(sj, x) { x.u = now(); H.LS.set('num.x.' + sj, x); }
function saveState(st, msg) {
  S.saveSt = st; const e = S.root && $('.nm-save', S.root); if (!e) return;
  e.className = 'nm-save ' + st; e.textContent = st === 'ok' ? '저장됨 ✓' : st === 'ing' ? '저장 중…' : st === 'bad' ? '⚠ ' + (msg || '저장 실패') : '';
  if (st === 'ok') { clearTimeout(saveState.t); saveState.t = setTimeout(() => { if (S.saveSt !== 'ok') return; S.saveSt = ''; const e2 = S.root && $('.nm-save', S.root); if (e2) { e2.className = 'nm-save'; e2.textContent = '자동 저장'; } }, 2500); }
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
    if (Object.keys(o).length > 2) o.bq = plain(b.q).replace(/\s+/g, ' ').trim().slice(0, 160);   /* 기본 자료가 바뀌어 id를 못 찾을 때 알아볼 원래 문제 글 */
  } else Object.assign(o, { lec: it.lec, q: it.q, a: it.a, st: it.st, note: it.note, tags: it.tags, yrs: it.yrs, src: it.src, o: it.o, c: it.c }, it.ref ? { ref: it.ref } : {}, it.q0 != null ? { q0: it.q0 } : {}, it.a0 != null ? { a0: it.a0 } : {}, it.rv && it.rv.length ? { rv: it.rv } : {});
  if (it.done) o.done = 1; if (it.del) o.del = 1; if (it.rvok) o.rvok = 1; if (it.prev) o.prev = it.prev;
  o.u = it.u || now(); if (it.c) o.c = it.c;
  return o;
}
function put(it) {
  const o = toRec(it), k = keyI(it.s, it.id);
  if (it.kind === 'seed' && Object.keys(o).every(x => x === 'id' || x === 'k' || x === 'u' || x === 'c' || x === 'bq')) { rawDel(k); saveState('ok'); return true; }   /* 원본과 같아짐 = 작업본 없음 */
  const ok = rawPut(k, o);
  saveState(ok ? 'ok' : 'bad', ok ? '' : '이 기기 저장 공간이 부족해요 — 백업 파일을 받아 두고 [복원] 창에서 공간을 정리해 주세요(쓴 글은 이 창이 열려 있는 동안 남아 있어요)');
  if (!ok) H.toast('넘버링 저장 공간이 부족해요 — 백업 파일을 받아 두세요', { level: 'error', id: 'nmquota' });
  return ok;
}
function touch(it) { it.u = now(); it._t = null; it._k = null; it._qd = null; }
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
  return { id: b.id, s: sj, kind: 'seed', base: b, oi: i, lec: r.lec != null ? r.lec : b.lec, q: r.q != null ? safe(r.q) : b.q, a: r.a != null ? safe(r.a) : b.a, st: r.st != null ? safe(r.st) : (b.st || ''), note: r.note != null ? r.note : (b.note || ''), tags: r.tags || b.tags || [], yrs: r.yrs || b.yrs || [], src: r.src || [{ t: 'seed', s: sj, id: b.id, lab: seedLab(seed, b), yrs: b.yrs || [] }], done: !!r.done, o: r.o != null ? r.o : i, c: r.c || 0, u: r.u || 0, del: !!r.del, rv: b.rv || [], rvok: !!r.rvok, prev: r.prev || null };
}
const RISK = /<(?:script|iframe|object|embed|style|link|meta|svg|math|form|input|textarea|button|select|base|frame)\b|\son[a-z]+\s*=|javascript:|data:(?!image\/(?:png|jpe?g|gif|webp);base64,)/i;
const safe = h => (h && RISK.test(h) ? sanitize(h) : (h || ''));   /* 저장·백업에서 읽은 글은 위험한 꼴이 보이면 정리해서 보여 줌 */
function mkRec(sj, r) { return { id: r.id, s: sj, kind: r.k || 'user', lec: r.lec || '', q: safe(r.q), a: safe(r.a), st: safe(r.st), note: r.note || '', tags: r.tags || [], yrs: r.yrs || [], src: r.src || [], ref: r.ref || null, q0: r.q0, a0: r.a0, done: !!r.done, o: r.o != null ? r.o : 1e6, c: r.c || 0, u: r.u || 0, del: !!r.del, rv: r.rv || [], rvok: !!r.rvok, prev: r.prev || null }; }
function lectures(sj, seed) {
  const L = [], P = H.PACKS[sj], X = idx(sj);
  if (P) P.lect.forEach(l => L.push({ k: l.k, t: l.title, prof: l.prof || '' }));
  if (seed) seed.lecs.forEach(l => L.push({ k: l.k, t: l.t, prof: l.prof || '', lab: l.lab || '' }));
  (X.ul || []).forEach(l => { if (l && l.k && !L.some(x => x.k === l.k)) L.push({ k: l.k, t: l.t, user: 1 }); });
  for (const l of L) if (X.lt && X.lt[l.k]) l.t = X.lt[l.k];
  L.push({ k: '', t: '강의 미분류' });
  return L;
}
function waitPack(sj) {   /* JB 과목이면 그 과목 팩(강의 목록)이 올 때까지 — 주소로 바로 열 때(팩은 허브가 부팅 때 차례로 받음) */
  if (!H.SUBJECTS.some(x => x[0] === sj) || H.PACKS[sj]) return Promise.resolve();
  return new Promise(res => { const t0 = now(), iv = setInterval(() => { if (H.PACKS[sj] || now() - t0 > 15000) { clearInterval(iv); res(); } }, 120); });
}
async function loadSubject(sj) {
  await waitPack(sj);
  const seed = await seedOf(sj).catch(e => { H.toast(e.message, { level: 'error', id: 'nmseed' }); return null; });
  const R = loadRecs(sj), items = [];
  if (seed) seed.items.forEach((b, i) => { items.push(mkSeed(sj, b, R.get(b.id), i, seed)); R.delete(b.id); });
  const orphan = [];
  for (const r of R.values()) { if (/^sd:/.test(r.id)) { if (seed) orphan.push(r); continue; } items.push(mkRec(sj, r)); }   /* 기본 자료를 못 불러왔으면 그 작업본은 화면에만 안 보임(저장은 그대로) */
  for (const r of orphan) { const it = mkRec(sj, Object.assign({}, r, { k: 'user', q: r.q || '<p>' + esc(r.bq || '(원래 문제 글을 찾지 못함)') + '</p>', rv: [{ k: 'orphan', m: '기본 자료(Word)가 바뀌어 원래 문제를 찾지 못했어요 — 내가 쓴 스토리·고친 글은 그대로 남겨 둠' }] })); it.orphan = 1; items.push(it); }
  if (!seed && (window.JBLNUM_INDEX || []).some(x => x.id === sj)) H.toast('Word 기본 자료를 불러오지 못했어요 — 인터넷 연결을 확인하고 새로고침해 주세요(쓴 글은 그대로 있어요)', { level: 'error', id: 'nmseed' });
  S.seed = seed; S.items = items; S.by = new Map(items.map(it => [it.id, it])); S.lecs = lectures(sj, seed);
}
const lecOf = k => S.lecs.find(l => l.k === k) || S.lecs[S.lecs.length - 1];
const lecIdx = k => { const i = S.lecs.findIndex(l => l.k === k); return i < 0 ? S.lecs.length - 1 : i; };
function txt(it) { if (!it._t) it._t = (plain(it.q) + '\n' + plain(it.a) + '\n' + plain(it.st) + '\n' + it.note + '\n' + it.src.map(s => s.lab || '').join(' ') + ' ' + (KIND[it.kind] || '') + '\n' + lecOf(it.lec).t + ' ' + (it.tags || []).join(' ')).toLowerCase(); return it._t; }
function tyOf(it) { if (!it._ty) it._ty = qType(it.q, it.a); return it._ty; }

/* ---------- 화면 ---------- */
/* 10-10 '내 넘버링' 개편: JBL 메뉴 대신 넘버링 전용 사이드바(접기 = 아이콘 줄 · 좁은 화면 = 서랍) · 위 막대 한 줄(검색·필터·보기·가리기·선택 — 상세 필터는 펼칠 때만) · 문제 머리 한 줄(표시 번호 + 문제 · 교수·연도 태그) · 작은 떠 있는 편집 도구(본문을 밀지 않음) */
const ICO = {
  home: '<svg viewBox="0 0 20 20" aria-hidden="true"><path d="M3.5 9.2 10 4l6.5 5.2V16a.8.8 0 0 1-.8.8h-3.4v-4.3H7.7v4.3H4.3a.8.8 0 0 1-.8-.8z"/></svg>',
  plus: '<svg viewBox="0 0 20 20" aria-hidden="true"><path d="M10 4.5v11M4.5 10h11"/></svg>',
  imp: '<svg viewBox="0 0 20 20" aria-hidden="true"><path d="M10 3.5v9m-3.6-3.6L10 12.5l3.6-3.6M4 13.5v2.8h12v-2.8"/></svg>',
  file: '<svg viewBox="0 0 20 20" aria-hidden="true"><path d="M5.2 2.8h6.3L15 6.3v10.9H5.2z"/><path d="M11.5 2.8v3.5H15M7.4 10.2l1 3.9 1.6-3 1.6 3 1-3.9"/></svg>',
  search: '<svg viewBox="0 0 20 20" aria-hidden="true"><circle cx="8.6" cy="8.6" r="5.1"/><path d="m12.6 12.6 4 4"/></svg>',
  filter: '<svg viewBox="0 0 20 20" aria-hidden="true"><path d="M3.5 5.5h13M6 10h8M8.5 14.5h3"/></svg>',
  sel: '<svg viewBox="0 0 20 20" aria-hidden="true"><rect x="3.5" y="3.5" width="13" height="13" rx="2.6"/><path d="m7 10.2 2.1 2.1L13.3 8"/></svg>',
  view: '<svg viewBox="0 0 20 20" aria-hidden="true"><path d="M2.8 10s2.6-5 7.2-5 7.2 5 7.2 5-2.6 5-7.2 5-7.2-5-7.2-5z"/><circle cx="10" cy="10" r="2.2"/></svg>',
};
const STYLE = `
body.v-num #side,body.v-num #sideopen,body.v-num #navbg{display:none!important}
body.v-num #app{grid-template-columns:0 minmax(0,1fr);transition:none}
@media (min-width:861px){body.v-num #top #navbtn{display:none!important}}
body.v-num #home{max-width:none;margin:0;padding:0}
#numv{--nmsw:236px;--nmind:36px;display:grid;grid-template-columns:var(--nmsw) minmax(0,1fr);min-height:calc(100vh - var(--toph,52px));position:relative;color:var(--ink)}
#numv.sidec{--nmsw:56px}
#numv svg{width:18px;height:18px;fill:none;stroke:currentColor;stroke-width:1.7;stroke-linecap:round;stroke-linejoin:round;flex:none}
#numv .nm-side{grid-column:1;grid-row:1;position:sticky;top:var(--toph,52px);align-self:start;height:calc(100vh - var(--toph,52px));height:calc(100dvh - var(--toph,52px));overflow-y:auto;overflow-x:hidden;background:#FBF8F1;border-right:1px solid var(--line);padding:10px 10px 0;display:flex;flex-direction:column;scrollbar-width:thin;overscroll-behavior:contain;z-index:22}
#numv .nm-sh{display:flex;align-items:center;gap:4px;margin:0 0 4px}
#numv .nm-si{display:flex;align-items:center;gap:10px;width:100%;min-height:34px;padding:0 10px;border:0;border-radius:6px;background:none;color:var(--ink);font:inherit;font-size:13.5px;line-height:1.3;text-align:left;cursor:pointer;white-space:nowrap;flex:none}
#numv .nm-si:hover,#numv .nm-si:focus-visible{background:var(--tint,#F2EEE6)}
#numv .nm-si .l{min-width:0;overflow:hidden;text-overflow:ellipsis;flex:1 1 auto}
#numv .nm-si small{color:var(--sub);font-size:12px;font-variant-numeric:tabular-nums;flex:none}
#numv .nm-si.pri{color:var(--acc,#0F5C5A);font-weight:700}
#numv .nm-si.on{font-weight:700}
#numv .nm-sh .nm-si{flex:1 1 auto;width:auto;color:var(--sub)}
#numv .nm-fold{flex:none;width:32px;height:32px;border:1px solid var(--line);border-radius:6px;background:var(--surface,#fff);color:var(--ink);font-size:14px;line-height:1;cursor:pointer;display:inline-flex;align-items:center;justify-content:center;padding:0}
#numv .nm-fold::before{content:'«'}#numv.sidec .nm-fold::before{content:'»'}
#numv .nm-sttl{padding:6px 10px 10px;margin:0 0 6px;border-bottom:1px solid var(--line)}
#numv .nm-sttl b{display:block;font-size:17px;letter-spacing:-.01em}
#numv .nm-sttl span{display:block;font-size:12px;color:var(--faint,#8C857A);margin-top:3px}
#numv .nm-ssec{font-size:12px;color:#6F685D;font-weight:600;letter-spacing:.04em;margin:14px 10px 4px;display:flex;align-items:baseline;gap:6px;flex:none}
#numv .nm-ssec small{font-weight:400;letter-spacing:0;color:var(--faint,#8C857A)}
#numv .nm-si .d{width:8px;height:8px;border-radius:50%;flex:none}
#numv .nm-sjd{flex:none}#numv .nm-sjd>summary{list-style:none;background:var(--surface,#fff);box-shadow:inset 0 0 0 1px var(--line)}#numv .nm-sjd>summary::-webkit-details-marker{display:none}
#numv .nm-sjd .cv{margin-left:auto;color:var(--sub);font-size:11px;transition:transform .15s}#numv .nm-sjd[open] .cv{transform:rotate(180deg)}
#numv .nm-sjl{padding:4px 0 2px}
#numv .nm-sjl .nm-si.on{background:var(--tint,#F2EEE6)}
#numv .nm-ljl{flex:none}
#numv .nm-lj{min-height:32px;padding-top:5px;padding-bottom:5px;white-space:normal;margin:1px 0}
#numv .nm-lj .l{display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;white-space:normal}
#numv .nm-lj.cur{background:var(--surface,#fff);box-shadow:inset 3px 0 0 var(--acc,#0F5C5A),inset 0 0 0 1px var(--line);font-weight:700}
#numv .nm-lj.off{color:var(--faint,#A39B8E)}
#numv .nm-sempty{font-size:12.5px;color:var(--faint,#8C857A);padding:4px 10px}
#numv .nm-sfoot{position:sticky;bottom:0;margin-top:auto;background:#FBF8F1;border-top:1px solid var(--line);padding:10px 10px 12px;font-size:12.5px;color:var(--sub);flex:none}
#numv .nm-sfoot b{color:var(--ink)}
#numv .nm-pg{height:5px;border-radius:3px;background:#E9E3D7;overflow:hidden;margin:6px 0 5px}#numv .nm-pg i{display:block;height:100%;background:#2E7D4F}
#numv .nm-sbg{display:none}
@media (min-width:861px){
 #numv.sidec .nm-side{padding:10px 8px 0;align-items:center}
 #numv.sidec .nm-side .l,#numv.sidec .nm-side small,#numv.sidec .nm-sttl,#numv.sidec .nm-ssec,#numv.sidec .nm-sjd,#numv.sidec .nm-ljl,#numv.sidec .nm-sfoot{display:none}
 #numv.sidec .nm-sh{flex-direction:column-reverse;gap:6px;margin-bottom:8px}
 #numv.sidec .nm-si{width:40px;min-height:40px;padding:0;justify-content:center}
 #numv.sidec .nm-fold{width:40px;height:34px}
}
#numv .nm-main{grid-column:2;grid-row:1;min-width:0;width:100%;max-width:1360px;justify-self:center;padding:0 28px 120px;container:nmm/inline-size}
#numv .nm-stick{position:sticky;top:var(--toph,52px);z-index:18;background:var(--bg,#F7F5F0);margin:0 -28px;padding:10px 28px 8px}
#numv .nm-bar{display:flex;align-items:center;gap:8px;min-height:36px}
#numv .nm-ctx{display:none;align-items:center;gap:6px;flex:0 1 auto;max-width:32%;min-width:0;height:36px;border:1px solid var(--line);background:var(--surface,#fff);border-radius:8px;padding:0 10px;font:inherit;font-size:13px;color:var(--ink);cursor:pointer}
#numv .nm-ctx b{white-space:nowrap;flex:none}#numv .nm-ctx span{color:var(--sub);overflow:hidden;text-overflow:ellipsis;white-space:nowrap;min-width:0}
#numv.sidec .nm-ctx{display:inline-flex}
#numv .nm-sch{flex:1 1 220px;min-width:110px;display:flex;align-items:center;gap:7px;height:36px;border:1px solid var(--line);border-radius:8px;background:var(--surface,#fff);padding:0 10px;color:var(--sub)}
#numv .nm-sch:focus-within{border-color:var(--acc,#0F5C5A);box-shadow:0 0 0 2px rgba(15,92,90,.12)}
#numv .nm-sch svg{width:16px;height:16px}
#numv .nm-sch input{flex:1;min-width:0;border:0;outline:0;background:none;font:inherit;font-size:14px;color:var(--ink);height:100%;padding:0}
#numv .nm-tbtn{display:inline-flex;align-items:center;gap:5px;height:36px;padding:0 11px;border:1px solid var(--line);border-radius:8px;background:var(--surface,#fff);color:var(--ink);font:inherit;font-size:13px;font-weight:600;cursor:pointer;white-space:nowrap;flex:none}
#numv .nm-tbtn svg{width:16px;height:16px}
#numv .nm-tbtn:hover{background:var(--tint,#F2EEE6)}
#numv .nm-tbtn.on{border-color:var(--ink);background:var(--ink);color:var(--card,#fff)}
#numv .nm-tbtn .n{display:inline-block;min-width:18px;height:18px;line-height:18px;border-radius:9px;background:var(--acc,#0F5C5A);color:#fff;font-size:11px;text-align:center;padding:0 5px}
#numv .nm-tbtn.on .n{background:#fff;color:var(--ink)}
#numv .nm-seg{display:inline-flex;border:1px solid var(--line);border-radius:8px;overflow:hidden;flex:none;background:var(--surface,#fff)}
#numv .nm-seg button{border:0;background:none;color:var(--ink);padding:0 10px;font:inherit;font-size:13px;height:34px;cursor:pointer;white-space:nowrap}
#numv .nm-seg button+button{border-left:1px solid var(--line)}
#numv .nm-seg button.on{background:var(--ink);color:var(--card,#fff);font-weight:600}
#numv .nm-vopt{display:flex;align-items:center;gap:8px;flex:none}
#numv .nm-sel{height:34px;padding:0 8px;border:1px solid transparent;border-radius:8px;background:none;color:var(--sub);font:inherit;font-size:12.5px;cursor:pointer;display:inline-flex;align-items:center;gap:4px;white-space:nowrap}
#numv .nm-sel:hover{background:var(--tint,#F2EEE6);color:var(--ink)}
#numv .nm-sel.on{color:var(--acc,#0F5C5A);border-color:var(--acc,#0F5C5A);font-weight:700}
#numv .nm-sel svg{width:15px;height:15px}
#numv .nm-vbtn{display:none}
#numv .nm-save{font-size:12px;color:var(--faint,#8C857A);white-space:nowrap;min-width:5.4em;text-align:right;flex:none}
#numv .nm-save.ing{color:var(--sub)}#numv .nm-save.ok{color:#2E7D4F}#numv .nm-save.bad{color:#B3261E;font-weight:600;white-space:normal;min-width:0;flex:0 1 auto}
#numv .nm-fpan{position:absolute;right:28px;top:calc(100% - 4px);z-index:30;width:min(470px,calc(100vw - 24px));background:var(--card,#fff);border:1px solid var(--line);border-radius:12px;box-shadow:0 12px 36px rgba(0,0,0,.16);padding:12px 14px;display:grid;grid-template-columns:6.5em minmax(0,1fr);gap:8px 10px;align-items:center;font-size:13.5px}
#numv .nm-fpan[hidden]{display:none}
#numv .nm-fpan .k{color:var(--sub);font-size:12.5px;font-weight:600}
#numv .nm-fpan select{font:inherit;font-size:13.5px;height:34px;padding:0 8px;border:1px solid var(--line);border-radius:8px;background:var(--surface,#fff);color:var(--ink);width:100%;min-width:0}
#numv .nm-stg{display:flex;flex-wrap:wrap;gap:4px}
#numv .nm-stg button{border:1px solid var(--line);background:var(--surface,#fff);color:var(--ink);border-radius:999px;padding:0 10px;height:30px;font:inherit;font-size:12.5px;cursor:pointer}
#numv .nm-stg button b{font-weight:700;margin-left:2px;font-variant-numeric:tabular-nums}
#numv .nm-stg button.on{background:var(--ink);border-color:var(--ink);color:var(--card,#fff)}
#numv .nm-fpan .ft{grid-column:1/-1;display:flex;gap:8px;justify-content:flex-end;border-top:1px solid var(--line);padding-top:10px;margin-top:2px}
#numv .nm-info{display:flex;flex-wrap:wrap;align-items:center;gap:6px;font-size:12.5px;color:var(--sub);min-height:26px;margin:0 0 8px}
#numv .nm-info b{color:var(--ink)}
#numv .nm-fchip{display:inline-flex;align-items:center;gap:3px;border:1px solid #C9D9E8;background:#F0F5FA;color:#24466B;border-radius:999px;padding:0 3px 0 10px;height:26px;font:inherit;font-size:12.5px;cursor:pointer;max-width:100%}
#numv .nm-fchip span{overflow:hidden;text-overflow:ellipsis;white-space:nowrap;max-width:22em}
#numv .nm-fchip i{font-style:normal;width:20px;height:20px;border-radius:50%;display:inline-flex;align-items:center;justify-content:center;font-size:11px}
#numv .nm-fchip:hover i,#numv .nm-fchip:focus-visible i{background:rgba(36,70,107,.14)}
#numv .nm-clr{border:0;background:none;color:var(--sub);font:inherit;font-size:12.5px;text-decoration:underline;cursor:pointer;padding:0 4px}
#numv .nm-srt{margin-left:auto;color:var(--faint,#8C857A)}
#numv .nm-btn{border:1px solid var(--line);background:var(--card);color:var(--ink);border-radius:8px;padding:0 11px;font-family:inherit;font-size:13px;min-height:32px;font-weight:600;cursor:pointer}
#numv .nm-btn.pri{background:var(--acc,#0F5C5A);border-color:var(--acc,#0F5C5A);color:#fff}
#numv .nm-btn:disabled{opacity:.5;cursor:default}
#numv .nm-sp{flex:1 1 0}
#numv .nm-batch{display:flex;flex-wrap:wrap;gap:6px;align-items:center;margin:8px 0 0;padding:6px 8px;border:1px solid var(--line);border-radius:10px;background:var(--card,#fff);font-size:13px;box-shadow:0 2px 10px rgba(0,0,0,.06)}
#numv .nm-doc{background:#FFFFFF;color:#1F1D1A;border:1px solid var(--line);border-radius:8px;padding:2px 30px 36px;box-shadow:0 1px 3px rgba(0,0,0,.04)}
#numv .nm-lec{font-family:inherit;font-size:17.5px;font-weight:800;margin:28px 0 0;padding:10px 0 7px;border-bottom:2px solid #1F1D1A;color:#1F1D1A;display:flex;gap:10px;align-items:baseline;flex-wrap:wrap;line-height:1.35;scroll-margin-top:calc(var(--toph,52px) + 62px)}
#numv .nm-lec small{font-size:12.5px;font-weight:500;color:#6A6257}
#numv .nm-lec:first-child{margin-top:14px}
#numv .nm-it{content-visibility:auto;contain-intrinsic-size:auto 260px;padding:15px 0 16px;border-bottom:1px solid #EAE5DB;scroll-margin-top:calc(var(--toph,52px) + 62px)}
#numv .nm-it.flash{animation:nmfl 1.6s ease-out}@keyframes nmfl{0%{background:#FFF3C8}100%{background:transparent}}
#numv .nm-h{display:flex;align-items:flex-start;gap:8px;margin:0 0 8px}
#numv .nm-no{flex:none;min-width:28px;font-weight:800;font-size:15px;line-height:1.5;color:#1F1D1A;font-variant-numeric:tabular-nums;white-space:nowrap}
#numv .nm-it.ok .nm-no{color:#2E7D4F}#numv .nm-it.ok .nm-no::after{content:'✓';font-size:11px;margin-left:2px;vertical-align:2px}
#numv .nm-q{flex:1 1 auto;min-width:0;display:flex;gap:6px;align-items:flex-start;font-weight:650;font-size:15px;line-height:1.5;color:#1F1D1A}
#numv .nm-q>.nm-c{flex:1 1 0;min-width:0;font-size:inherit;line-height:inherit;min-height:0}
#numv .nm-tags{flex:none;display:flex;flex-wrap:wrap;justify-content:flex-end;align-items:center;gap:4px;max-width:40%;padding-top:1px}
#numv .nm-tag{display:inline-block;border:1px solid #E1D9CB;border-radius:5px;padding:0 6px;line-height:19px;font-size:11.5px;font-weight:500;color:#5A5247;background:#FAF7F1;white-space:nowrap}
#numv .nm-tag.yr{border-color:#C9D9E8;background:#F0F5FA;color:#24466B;font-weight:600;font-variant-numeric:tabular-nums}
#numv .nm-edm{font-size:12px;color:#8C857A;line-height:21px;padding:0 1px;cursor:help}
#numv .nm-rvb{border:1px solid #F0C9B0;background:#FFF4EC;color:#9A3412;border-radius:5px;font-size:11.5px;line-height:19px;padding:0 5px;cursor:pointer}
#numv .nm-more{flex:none;border:1px solid transparent;background:none;color:#6A6257;border-radius:6px;padding:0;width:30px;height:24px;font-size:17px;line-height:20px;cursor:pointer}
#numv .nm-more:hover,#numv .nm-more:focus-visible{border-color:#E1D9CB;background:#FAF7F1}
#numv .nm-ck{display:none;align-items:center;padding-top:3px}#numv.selm .nm-ck{display:inline-flex}#numv .nm-ck input{width:17px;height:17px;margin:0}
#numv .nm-edb{flex:none;border:1px solid #E1D9CB;background:#fff;color:#6A6257;border-radius:5px;font-family:inherit;font-size:11.5px;font-weight:500;padding:0 6px;line-height:19px;cursor:pointer;opacity:0;transition:opacity .12s}
#numv .nm-it:hover .nm-edb,#numv .nm-it:focus-within .nm-edb,#numv .nm-edb:focus-visible{opacity:1}
@media (hover:none){#numv .nm-edb{opacity:.75}}
#numv .nm-q>.nm-edb{margin-top:2px}
#numv .nm-body{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1.12fr);border:1px solid #E6E0D5;border-radius:6px;margin-left:var(--nmind)}
#numv .nm-col{min-width:0;padding:6px 12px 9px}
#numv .nm-col+.nm-col{border-left:1px solid #E6E0D5}
#numv .nm-s{background:#FFFEFA;border-radius:0 6px 6px 0}
#numv .nm-lab{display:flex;align-items:center;gap:6px;font-size:11px;font-weight:700;color:#9A9286;letter-spacing:.03em;margin:0 0 3px;min-height:20px}
#numv .nm-c{font-size:14.5px;line-height:1.62;white-space:pre-wrap;word-break:keep-all;overflow-wrap:anywhere;min-height:1.6em;outline:none}
#numv .nm-c p{margin:0}
#numv .nm-c table{border-collapse:collapse;margin:4px 0;max-width:100%;font-size:13.5px;white-space:normal}
#numv .nm-c td,#numv .nm-c th{border:1px solid #BDB5A8;padding:3px 6px;vertical-align:top;min-width:2.5em}
#numv .nm-tw{overflow-x:auto;max-width:100%}
#numv .nm-c img{max-width:100%;height:auto;vertical-align:top;margin:2px 0}
#numv .nm-c ul,#numv .nm-c ol{margin:2px 0;padding-left:1.6em;white-space:normal}
#numv .nm-c li{white-space:pre-wrap}
#numv .nm-s .nm-c{cursor:text;border-radius:4px;transition:background .15s;margin:0 -4px;padding:0 4px}
#numv .nm-s .nm-c:not([contenteditable=true]):hover{background:#FBF5E6}
#numv .nm-ph{color:#A39B8E;font-weight:400}
#numv.hideA .nm-it:not(.revA) .nm-a .nm-c,#numv.hideS .nm-it:not(.revS) .nm-s .nm-c{filter:blur(7px);opacity:.55;user-select:none;cursor:pointer;transition:filter .15s}
#numv.hideA .nm-it:not(.revA) .nm-a .nm-lab::after,#numv.hideS .nm-it:not(.revS) .nm-s .nm-lab::after{content:'가림 · 눌러서 보기';font-weight:600;color:#8A5A00;margin-left:auto;letter-spacing:0}
@media (prefers-reduced-motion:reduce){#numv .nm-c,#numv .nm-edb{transition:none}}
#numv .nm-note{font-size:12px;color:#8C857A;margin:6px 0 0 var(--nmind);white-space:pre-wrap;overflow-wrap:anywhere}
#numv [contenteditable=true]{background:#FFFDF6;outline:1.5px solid #E8C766;outline-offset:3px;border-radius:3px;cursor:text}
#numv .nm-tb{position:fixed;left:0;top:0;z-index:58;display:flex;align-items:center;gap:1px;background:#2F2A24;color:#fff;border-radius:8px;padding:2px;height:32px;box-shadow:0 4px 14px rgba(0,0,0,.22);visibility:hidden;will-change:transform}
#numv .nm-tb button{border:0;background:transparent;color:#fff;border-radius:6px;min-width:28px;height:28px;padding:0 6px;font-family:inherit;font-size:13px;line-height:1;cursor:pointer;display:inline-flex;align-items:center;justify-content:center}
#numv .nm-tb button:hover,#numv .nm-tb button:focus-visible,#numv .nm-tb button.on{background:rgba(255,255,255,.16)}
#numv .nm-tb i.sep{width:1px;height:16px;background:rgba(255,255,255,.22);margin:0 2px}
#numv .nm-tb .done{background:#E8C766;color:#2F2A24;font-weight:700;margin-left:2px;padding:0 8px}
#numv .nm-tb .done:hover{background:#F0D27F}
#numv .nm-pal{position:fixed;z-index:59;background:#fff;color:#1F1D1A;border:1px solid #D8D0C2;border-radius:8px;padding:6px;display:flex;flex-wrap:wrap;gap:4px;width:176px;box-shadow:0 6px 20px rgba(0,0,0,.18)}
#numv .nm-pal button{width:26px;height:26px;border-radius:6px;border:1px solid #D8D0C2;cursor:pointer}
#numv .nm-pal .wide{width:100%;height:30px;text-align:left;padding:0 9px;font-family:inherit;font-size:13px;background:#fff;border:0;border-radius:6px;color:#1F1D1A}
#numv .nm-pal .wide:hover,#numv .nm-pal .wide:focus-visible{background:#F2EEE6}
#numv .nm-pal hr{width:100%;border:0;border-top:1px solid #EEE9E0;margin:2px 0}
#numv .nm-pal.more{width:196px;gap:0;padding:4px}
#numv .nm-pal.more small{color:#8C857A;font-size:11.5px;margin-left:4px}
#numv .nm-menu{position:absolute;z-index:40;background:var(--card);color:var(--ink);border:1px solid var(--line);border-radius:10px;padding:4px;min-width:220px;max-width:min(320px,92vw);max-height:70vh;overflow:auto;box-shadow:0 8px 28px rgba(0,0,0,.18)}
#numv .nm-menu button{display:block;width:100%;text-align:left;border:0;background:none;color:inherit;padding:8px 10px;border-radius:7px;font-family:inherit;font-size:14px;cursor:pointer;min-height:36px}
#numv .nm-menu button:hover,#numv .nm-menu button:focus-visible{background:var(--tint,#F2EEE6)}
#numv .nm-menu hr{border:0;border-top:1px solid var(--line);margin:4px 0}
#numv .nm-menu .warn{color:#B3261E}
#numv .nm-chip{display:inline-block;border:1px solid #E1D9CB;border-radius:999px;padding:0 7px;line-height:19px;font-size:12px;color:#4A4339;background:#FAF7F1;white-space:nowrap}
#numv .nm-chip.yr{border-color:#C9D9E8;background:#F0F5FA;color:#24466B;font-weight:600}
#numv .nm-chip.k-jb{border-color:#D8C9E8;background:#F6F1FB;color:#4F2F78}#numv .nm-chip.k-pred{border-color:#E8D9C1;background:#FBF5EA;color:#6B4A12}#numv .nm-chip.k-seed,#numv .nm-chip.k-word{border-color:#C8DFD3;background:#EFF7F2;color:#1E5A3B}
#numv .nm-chip.s0{color:#8C857A}#numv .nm-chip.s1{color:#8A5A00;border-color:#EBD7A8;background:#FFF8E6}#numv .nm-chip.s2{color:#1E6B3E;border-color:#B9DCC5;background:#EDF8F1;font-weight:700}
#numv .nm-chip.rv{color:#9A3412;border-color:#F0C9B0;background:#FFF4EC}
#numv .nm-det{margin:10px 0 0 var(--nmind);padding:10px 12px;border:1px solid #E4DFD5;border-radius:6px;background:#FCFBF8;font-size:13.5px;display:grid;gap:8px}
#numv .nm-det label{display:grid;grid-template-columns:7.5em 1fr;gap:8px;align-items:center}
#numv .nm-det input{font:inherit;padding:5px 8px;border:1px solid #D8D0C2;border-radius:6px;background:#fff;color:#1F1D1A;min-height:32px}
#numv .nm-det ul{margin:0;padding-left:1.2em}#numv .nm-det li{margin:2px 0}
#numv .nm-det .row{display:flex;gap:6px;flex-wrap:wrap;align-items:center}
#numv .nm-empty{padding:34px 10px;color:#6A6257;text-align:center;font-size:14.5px;line-height:1.6}
#numv .nm-empty .row{display:flex;flex-wrap:wrap;gap:8px;justify-content:center;margin:14px 0 10px}
#numv .nm-empty small{color:#8C857A;font-size:12.5px}
#numv .nm-hid{margin:20px 0 0;font-size:13.5px;color:#6A6257}
#numv .nm-hid summary{cursor:pointer;padding:6px 0}
#numv .nm-hid .row{display:flex;gap:8px;align-items:center;padding:4px 0;border-bottom:1px dashed #E4DFD5}
#numv .nm-ov{position:fixed;inset:0;z-index:60;background:rgba(20,18,15,.45);display:flex;align-items:flex-start;justify-content:center;padding:4vh 12px;overflow:auto}
#numv .nm-dlg{position:relative;background:var(--card);color:var(--ink);border-radius:12px;width:min(1100px,100%);box-shadow:0 18px 60px rgba(0,0,0,.3);display:flex;flex-direction:column}
#numv .nm-dlg>header{display:flex;align-items:center;gap:10px;padding:14px 16px 10px;border-bottom:1px solid var(--line)}
#numv .nm-dlg>header h3{margin:0;font-size:17px;font-family:inherit}
#numv .nm-dlg>header .x{margin-left:auto}
#numv .nm-dlg .bd{padding:12px 16px;display:grid;gap:10px}
#numv .nm-dlg>footer{position:sticky;bottom:0;display:flex;flex-wrap:wrap;gap:8px;align-items:center;padding:10px 16px;border-top:1px solid var(--line);background:var(--card);border-radius:0 0 12px 12px}
#numv .nm-dlg select,#numv .nm-dlg input[type=text],#numv .nm-dlg input[type=search]{font:inherit;font-size:14px;padding:6px 8px;border:1px solid var(--line);border-radius:8px;background:var(--card);color:var(--ink);min-height:34px;max-width:100%}
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
#numv .nm-rich[contenteditable=true]{outline:0}#numv .nm-rich:focus{border-color:#E8C766;box-shadow:0 0 0 2px rgba(232,199,102,.35)}
#numv .nm-rich p{margin:0}#numv .nm-rich img{max-width:100%;height:auto}#numv .nm-rich td{border:1px solid #BDB5A8;padding:3px 6px}#numv .nm-rich table{border-collapse:collapse}
#numv .nm-g2{display:grid;grid-template-columns:1fr 1fr;gap:10px}
#numv .nm-prev{border:1px solid #E4DFD5;border-radius:6px;padding:8px 10px;background:#fff;color:#1F1D1A;margin:4px 0 0}
#numv .nm-prev .nm-body{margin-left:0}#numv .nm-prev .nm-note{margin-left:0}
#numv .nm-warn{color:#9A3412;font-size:13px}
#numv .nm-prog{font-size:14px;color:var(--sub);padding:40px 20px;text-align:center}
#numv .nm-lecin{font:inherit;font-size:14px;padding:4px 8px;border:1px solid #D8D0C2;border-radius:6px;min-width:12em}
@container nmm (max-width:940px){
 #numv .nm-vbtn{display:inline-flex}
 #numv .nm-vopt{display:none;position:absolute;right:28px;top:calc(100% - 4px);z-index:30;flex-direction:column;align-items:stretch;gap:8px;background:var(--card,#fff);border:1px solid var(--line);border-radius:12px;box-shadow:0 12px 36px rgba(0,0,0,.16);padding:10px;width:min(300px,calc(100vw - 24px))}
 #numv .nm-vopt.open{display:flex}
 #numv .nm-vopt .nm-seg{width:100%}#numv .nm-vopt .nm-seg button{flex:1}
 #numv .nm-vopt .nm-sel{justify-content:center;border-color:var(--line)}
}
@container nmm (max-width:640px){
 #numv .nm-doc{padding:0 14px 28px}
 #numv .nm-body{grid-template-columns:minmax(0,1fr);margin-left:0}
 #numv .nm-col+.nm-col{border-left:0;border-top:1px solid #E6E0D5}
 #numv .nm-s{border-radius:0 0 6px 6px}
 #numv .nm-note,#numv .nm-det{margin-left:0}
 #numv .nm-h{display:grid;grid-template-columns:auto auto minmax(0,1fr) auto;column-gap:6px;row-gap:3px}
 #numv .nm-ck{grid-column:1;grid-row:1}#numv .nm-no{grid-column:2;grid-row:1;min-width:0}#numv .nm-q{grid-column:3;grid-row:1}#numv .nm-more{grid-column:4;grid-row:1}
 #numv .nm-tags{grid-column:3;grid-row:2;justify-content:flex-start;max-width:none;padding-top:0}
 #numv .nm-tags:empty{display:none}
 #numv .nm-q>.nm-edb{display:none}
 #numv .nm-g2{grid-template-columns:1fr}
}
@media (max-width:860px){
 #numv{grid-template-columns:minmax(0,1fr)}
 #numv .nm-side{position:fixed;top:var(--toph,52px);bottom:0;left:0;height:auto;align-self:stretch;width:min(300px,86vw);transform:translateX(-102%);visibility:hidden;transition:transform .2s,visibility .2s;z-index:62;box-shadow:6px 0 26px rgba(0,0,0,.18)}
 #numv.sideo .nm-side{transform:none;visibility:visible}
 #numv.sideo .nm-sbg{display:block;position:fixed;left:0;right:0;bottom:0;top:var(--toph,52px);background:rgba(20,16,10,.38);z-index:61}
 #numv .nm-fold::before{content:'✕'}
 #numv .nm-main{grid-column:1;padding:0 12px 100px}
 #numv .nm-stick{margin:0 -12px;padding:8px 12px 6px}
 #numv .nm-si{min-height:42px}
 #numv .nm-fpan,#numv .nm-vopt{right:12px}
 #numv .nm-fpan{left:12px;width:auto;grid-template-columns:5.6em minmax(0,1fr)}
 #numv .nm-tbtn span{display:none}#numv .nm-tbtn{padding:0 9px}
 #numv .nm-save{position:absolute;right:12px;top:100%;min-width:0;font-size:11px;pointer-events:none;background:var(--bg,#F7F5F0);padding:0 4px;border-radius:4px}
 #numv .nm-save:not(.ok):not(.ing):not(.bad){display:none}
 #numv .nm-doc{border-radius:0;border-left:0;border-right:0;margin:0 -12px}
 #numv .nm-irow{grid-template-columns:24px minmax(0,1fr)}#numv .nm-irow .add{grid-column:2;justify-self:start}
 #numv .nm-dlg{border-radius:10px}
}
@media print{#numv{display:block}#numv .nm-side,#numv .nm-stick,#numv .nm-info,#numv .nm-edb,#numv .nm-more{display:none}#numv .nm-it{content-visibility:visible}}
`;
function css() { const o = document.getElementById('nm-css'); if (o && o.dataset.v === H.v) return; if (o) o.remove(); const s = document.createElement('style'); s.id = 'nm-css'; s.dataset.v = H.v; s.textContent = STYLE; document.head.appendChild(s); }

const SORTN = { lec: '강의 순서', own: '사용자 지정 순서', yr: '출제 연도(최근)', freq: '기출 빈도', upd: '최근 수정', st: '제작 상태' };
const yrs2 = y => (y || []).slice().sort((a, b) => b - a).map(x => String(x % 100).padStart(2, '0')).join('·');
const NUMLEAD = /^(\s*)\d{1,3}(?:-\d{1,2})?\s*[.)．]\s*(?!\d)/;
const YPAR = /\s*[(（]\s*((?:20)?\d{2}(?:\s*[,，·]\s*(?:20)?\d{2})*)\s*[)）]/g;
function qDisp(it) {   /* 화면에 보이는 문제 글 — 앞머리의 원래 번호('1.')와, 연도 태그와 똑같은 연도만 든 괄호('(23,24)')만 뺌. 저장된 글은 그대로(수정을 누르면 원문 전체) */
  if (it._qd != null) return it._qd;
  const h = disp(it.q); if (!h) return (it._qd = '');
  const t = document.createElement('template'); t.innerHTML = h;
  let root = t.content; for (const n of t.content.childNodes) { if (n.nodeType === 3 && !n.data.trim()) continue; if (n.nodeType === 1 && n.tagName === 'P') root = n; break; }
  const Y = new Set(it.yrs.map(y => y % 100)), w = document.createTreeWalker(root, NodeFilter.SHOW_TEXT); let first = true;
  for (let n = w.nextNode(); n; n = w.nextNode()) {
    let s = n.data;
    if (first && s.trim()) { s = s.replace(NUMLEAD, '$1'); first = false; }
    if (Y.size) s = s.replace(YPAR, (m, ys) => { const L = ys.split(/[,，·]/).map(x => +x.trim() % 100); return L.length && L.every(y => Y.has(y)) ? '' : m; });
    if (s !== n.data) n.data = s;
  }
  return (it._qd = t.innerHTML);
}
function profOf(it) {   /* 교수 태그 — JB 출처의 교수(여럿이면 모두), 없으면 그 강의 교수 */
  const P = [];
  for (const s of it.src) if (s.t === 'jb' && s.lab) { const m = /·\s*([^·]+)$/.exec(s.lab); const p = m && m[1].trim(); if (p && !P.includes(p)) P.push(p); }
  if (!P.length) { const l = lecOf(it.lec); if (l && l.prof) P.push(l.prof); }
  return P.join('·');
}
function noteTxt(n) { let s = String(n || '').trim(), p; do { p = s; s = s.replace(/^참고\s*[:：]\s*/, ''); } while (s !== p); return /^참고\s*[:：]?$/.test(s) ? '' : s; }   /* '참고: 참고: …' → '참고: …' 한 번 · 빈 '참고'는 안 보임 */
function itemHTML(it, no, hid) {
  const st = stOf(it), rv = it.rv && it.rv.length && !it.rvok, pf = profOf(it), note = noteTxt(it.note);
  const edq = it.kind === 'seed' ? it.q !== it.base.q : it.q0 != null, eda = it.kind === 'seed' ? it.a !== it.base.a : it.a0 != null;
  return `<article class="nm-it${st === 2 ? ' ok' : ''}" data-id="${esc(it.id)}" data-st="${st}"${hid ? ' hidden' : ''}><header class="nm-h"><label class="nm-ck"><input type="checkbox" data-ck="1"${S.sel.has(it.id) ? ' checked' : ''} aria-label="선택"></label><span class="nm-no"${st === 2 ? ' title="완성"' : ''}>${no}.</span>`
    + `<div class="nm-q"><div class="nm-c" data-f="q">${qDisp(it) || '<span class="nm-ph">문제 없음</span>'}</div><button type="button" class="nm-edb" data-act="edit" data-f="q" title="문제 수정(작업본만 — 원본은 그대로 · 원래 번호·연도 괄호까지 원문 전체가 보여요)">수정</button></div>`
    + `<span class="nm-tags">${pf ? `<span class="nm-tag pf" title="교수">${esc(pf)}</span>` : ''}${it.yrs.length ? `<span class="nm-tag yr" title="출제 연도 ${esc(yrsTxt(it.yrs))}">${esc(yrs2(it.yrs))}</span>` : ''}${edq || eda ? `<span class="nm-edm" title="원본에서 고친 작업본(${edq && eda ? '문제·답안' : edq ? '문제' : '답안'}) — ⋯ 메뉴 '원본으로'로 되돌림" aria-label="고친 작업본">✎</span>` : ''}${rv ? `<button type="button" class="nm-rvb" data-act="det" title="${esc(it.rv.map(r => r.m).join('\n'))}" aria-label="검토 필요">⚠</button>` : ''}</span>`
    + `<button type="button" class="nm-more" data-act="more" aria-haspopup="true" title="이 문제 메뉴 — 완성·수정·출처·순서·강의 옮기기·복사·되돌리기·빼기" aria-label="이 문제 메뉴">⋯</button></header>`
    + `<div class="nm-body"><section class="nm-col nm-a"><div class="nm-lab">답안 <button type="button" class="nm-edb" data-act="edit" data-f="a" title="답안 수정(작업본만 — 원본은 그대로)">수정</button></div><div class="nm-c" data-f="a">${disp(it.a) || '<span class="nm-ph">답안 없음 — 수정을 눌러 쓰기</span>'}</div></section>`
    + `<section class="nm-col nm-s"><div class="nm-lab">넘버링 스토리</div><div class="nm-c" data-f="st" tabindex="0" role="textbox" aria-label="넘버링 스토리 — 누르면 바로 편집">${disp(it.st) || '<span class="nm-ph">눌러서 스토리 쓰기</span>'}</div></section></div>`
    + (note ? `<div class="nm-note">참고: ${esc(note)}</div>` : '') + `</article>`;
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
const lecKeys = () => new Set(S.lecs.filter(l => l.k).map(l => l.k));
function lecCounts() { const K = lecKeys(), n = {}; for (const it of S.items) if (!it.del) { const lk = K.has(it.lec) ? it.lec : ''; n[lk] = (n[lk] || 0) + 1; } return n; }
const fKeys = ['lec', 'st', 'type', 'src', 'yr'];
const fCount = () => fKeys.filter(k => S.cfg.f[k] !== '').length;
function sjCounts() {   /* 과목마다 문제 수(뺀 것 빼고) — 저장 글을 풀지 않고 키·글자로만 셈 */
  const c = {}, P = H.NS + 'num.i.';
  for (let i = 0; i < localStorage.length; i++) { const k = localStorage.key(i); if (!k || k.indexOf(P) !== 0) continue; const j = k.indexOf('.', P.length); if (j < 0) continue; const v = localStorage.getItem(k) || ''; if (v.indexOf('"del":1') < 0 && v.indexOf('"del":true') < 0) { const sj = k.slice(P.length, j); c[sj] = (c[sj] || 0) + 1; } }
  return c;
}

function sideHTML() {
  const subs = subjects(), cur = subs.find(s => s.id === S.sj) || { id: S.sj, t: S.sj }, C = S.sjc || {}, k = counts(), ln = lecCounts();
  const dot = id => `<i class="d" style="background:${esc(H.sjColor ? H.sjColor(id) : '#9A9288')}"></i>`;
  const sjl = subs.map(s => { const n = s.id === S.sj ? k.n : (C[s.id] || 0); return `<button type="button" class="nm-si${s.id === S.sj ? ' on' : ''}" data-sj="${esc(s.id)}"${s.id === S.sj ? ' aria-current="true"' : ''}>${dot(s.id)}<span class="l">${esc(s.t)}</span>${n ? `<small>${n}</small>` : ''}</button>`; }).join('') + `<button type="button" class="nm-si" data-sj="__new">${ICO.plus}<span class="l">새 과목 만들기</span></button>`;
  const L = S.lecs.filter(l => ln[l.k]);
  const ljl = L.length ? L.map(l => `<button type="button" class="nm-si nm-lj${S.curLec === l.k ? ' cur' : ''}" data-lj="${esc(l.k)}" title="${esc(l.t + (l.prof ? ' · ' + l.prof : ''))} — 누르면 그 위치로"><span class="l">${esc(l.t)}</span><small>${ln[l.k]}</small></button>`).join('') : '<div class="nm-sempty">아직 문제가 없어요</div>';
  return `<div class="nm-sh"><button type="button" class="nm-si" data-sact="home" title="JBL 홈으로 — 모든 과목">${ICO.home}<span class="l">JBL 홈</span></button><button type="button" class="nm-fold" data-sact="fold" title="메뉴 접기·펼치기 (Shift+M)" aria-label="메뉴 접기·펼치기"></button></div>`
    + `<div class="nm-sttl"><b>내 넘버링</b><span title="다음 업데이트에서 열려요" aria-disabled="true">넘버링 복습 · 추후 업데이트 예정</span></div>`
    + `<button type="button" class="nm-si pri" data-act="new" title="새 문제 만들기">${ICO.plus}<span class="l">새 문제</span></button><button type="button" class="nm-si" data-act="imp" title="JB 기출·강의 예상문제에서 불러오기">${ICO.imp}<span class="l">기존 문제 불러오기</span></button><button type="button" class="nm-si" data-act="file" title="Word(.docx) 넘버링 파일에서 가져오기 — 미리 보고 고른 뒤 넣음">${ICO.file}<span class="l">Word 파일 가져오기</span></button>`
    + `<div class="nm-ssec">과목</div><details class="nm-sjd"${S.sjOpen ? ' open' : ''}><summary class="nm-si on" title="과목 바꾸기">${dot(cur.id)}<span class="l">${esc(cur.t)}</span><span class="cv" aria-hidden="true">▾</span></summary><div class="nm-sjl">${sjl}</div></details>`
    + `<div class="nm-ssec">강의 바로 가기<small>누르면 그 위치로</small></div><div class="nm-ljl">${ljl}</div>`
    + `<div class="nm-sfoot" data-sfoot="1">${footHTML(k)}</div>`;
}
function footHTML(k) { const p = k.n ? Math.round(k.c[2] / k.n * 100) : 0; return `완성 <b>${k.c[2]}</b> / ${k.n}${k.n ? ` · ${p}%` : ''}<div class="nm-pg" aria-hidden="true"><i style="width:${p}%"></i></div>작성 중 ${k.c[1]} · 미작성 ${k.c[0]}`; }
function sideRender() { const a = S.root && $('.nm-side', S.root); if (!a) return; const y = a.scrollTop; a.innerHTML = sideHTML(); a.scrollTop = y; }
function saveTxt() { const st = S.saveSt; return st === 'ok' ? '저장됨 ✓' : st === 'ing' ? '저장 중…' : '자동 저장'; }
function barHTML() {
  const C = S.cfg, nf = fCount(), sub = subjects().find(s => s.id === S.sj), l = S.curLec != null ? lecOf(S.curLec) : null;
  return `<div class="nm-stick"><div class="nm-bar">`
    + `<button type="button" class="nm-ctx" data-act="ctx" title="강의 바로 가기"><b>${esc(sub ? sub.sh : S.sj)}</b><span>${l ? '› ' + esc(l.t) : ''}</span></button>`
    + `<label class="nm-sch">${ICO.search}<input type="search" data-cf="q" placeholder="문제·답안·스토리 검색" value="${esc(S.q)}" aria-label="넘버링 검색"></label>`
    + `<button type="button" class="nm-tbtn${S.fp ? ' on' : ''}" data-act="flt" aria-expanded="${!!S.fp}" aria-haspopup="true" title="필터·정렬 — 강의·제작 상태·유형·출처·연도·정렬">${ICO.filter}<span>필터</span>${nf ? `<b class="n">${nf}</b>` : ''}</button>`
    + `<div class="nm-vopt${S.vo ? ' open' : ''}"><span class="nm-seg" role="group" aria-label="보기"><button type="button" data-mode="grp" class="${C.mode === 'grp' ? 'on' : ''}" aria-pressed="${C.mode === 'grp'}" title="강의마다 머리를 두고 보기">강의별</button><button type="button" data-mode="all" class="${C.mode === 'all' ? 'on' : ''}" aria-pressed="${C.mode === 'all'}" title="강의 머리 없이 한 줄로 이어 보기">전체 목록</button></span>`
    + `<span class="nm-seg" role="group" aria-label="가리고 떠올리기 — 누르면 그 문제만 보임"><button type="button" data-hide="a" class="${C.hide.a ? 'on' : ''}" aria-pressed="${!!C.hide.a}" title="답안을 가려 두고 떠올린 뒤 눌러서 확인">답안 가리기</button><button type="button" data-hide="st" class="${C.hide.st ? 'on' : ''}" aria-pressed="${!!C.hide.st}" title="넘버링 스토리를 가려 두고 떠올린 뒤 눌러서 확인">스토리 가리기</button></span>`
    + `<button type="button" class="nm-sel${S.selMode ? ' on' : ''}" data-act="selm" aria-pressed="${S.selMode}" title="여러 문제를 골라 한 번에 — 완성 표시·강의 옮기기·합치기·빼기">${ICO.sel}${S.selMode ? '선택 끝' : '선택'}</button></div>`
    + `<button type="button" class="nm-tbtn nm-vbtn" data-act="vopt" aria-expanded="${!!S.vo}" aria-haspopup="true" title="보기 — 강의별/전체 목록 · 답안/스토리 가리기 · 여러 개 선택">${ICO.view}<span>보기</span></button>`
    + `<span class="nm-save ${esc(S.saveSt || '')}" aria-live="polite">${saveTxt()}</span></div>`
    + (S.selMode ? `<div class="nm-batch" data-batch="1"></div>` : '') + fpanHTML() + `</div><div class="nm-info" data-cnt="1"></div>`;
}
function stgHTML(k) { const f = S.cfg.f, b = (v, t, n) => `<button type="button" data-stf="${v}" class="${f.st === v ? 'on' : ''}" aria-pressed="${f.st === v}">${t} <b>${n}</b></button>`; return `${b('', '전체', k.n)}${b('0', '미작성', k.c[0])}${b('1', '작성 중', k.c[1])}${b('2', '완성', k.c[2])}${k.rv ? b('rv', '⚠ 검토', k.rv) : ''}`; }
function fpanHTML() {
  const C = S.cfg, f = C.f, ln = lecCounts(), yrs = [...new Set(S.items.filter(i => !i.del).flatMap(i => i.yrs))].sort((a, b) => b - a);
  const opt = (v, t, cur) => `<option value="${esc(v)}"${String(cur) === String(v) ? ' selected' : ''}>${esc(t)}</option>`;
  return `<div class="nm-fpan" data-fpan="1"${S.fp ? '' : ' hidden'} role="group" aria-label="필터·정렬">`
    + `<span class="k">제작 상태</span><div class="nm-stg">${stgHTML(counts())}</div>`
    + `<span class="k">강의만 보기</span><select data-cf="lec" aria-label="강의만 보기(그 강의 문제만)">${opt('', '모든 강의', f.lec)}${S.lecs.filter(l => l.k && ln[l.k]).map(l => opt(l.k, l.t + ' (' + ln[l.k] + ')', f.lec)).join('')}${ln[''] ? opt('__none', '강의 미분류 (' + ln[''] + ')', f.lec) : ''}</select>`
    + `<span class="k">문제 유형</span><select data-cf="type" aria-label="문제 유형">${opt('', '모든 유형', f.type)}${opt('ess', '서술형·넘버링형만', f.type)}${Object.keys(TYPES).map(k => opt(k, TYPES[k], f.type)).join('')}</select>`
    + `<span class="k">출처</span><select data-cf="src" aria-label="출처">${opt('', '모든 출처', f.src)}${Object.keys(KIND).map(k => opt(k, KIND[k], f.src)).join('')}</select>`
    + `<span class="k">출제 연도</span><select data-cf="yr" aria-label="출제 연도">${opt('', '모든 연도', f.yr)}${yrs.map(y => opt(String(y), y + '년 출제', f.yr)).join('')}${opt('none', '연도 없음', f.yr)}</select>`
    + `<span class="k">정렬</span><select data-cf="sort" aria-label="정렬">${Object.keys(SORTN).map(v => opt(v, SORTN[v], C.sort)).join('')}</select>`
    + `<div class="ft"><button type="button" class="nm-btn" data-act="fclr">필터 모두 해제</button><button type="button" class="nm-btn pri" data-act="flt">닫기</button></div></div>`;
}
function infoHTML(vis, k) {
  const C = S.cfg, f = C.f, ch = [];
  const chip = (x, t) => `<button type="button" class="nm-fchip" data-fx="${x}" title="이 조건 풀기"><span>${esc(t)}</span><i aria-hidden="true">✕</i></button>`;
  if (S.q) ch.push(chip('q', '검색: ' + S.q));
  if (f.lec) ch.push(chip('lec', '강의: ' + (f.lec === '__none' ? '강의 미분류' : lecOf(f.lec).t)));
  if (f.st !== '') ch.push(chip('st', '상태: ' + (f.st === 'rv' ? '⚠ 검토 필요' : STN[+f.st] || f.st)));
  if (f.type) ch.push(chip('type', '유형: ' + (f.type === 'ess' ? '서술형·넘버링형' : TYPES[f.type] || f.type)));
  if (f.src) ch.push(chip('src', '출처: ' + (KIND[f.src] || f.src)));
  if (f.yr) ch.push(chip('yr', f.yr === 'none' ? '연도 없음' : f.yr + '년 출제'));
  return `<span>${ch.length ? `보이는 문제 <b>${vis}</b> / ${k.n}` : `<b>${k.n}</b>문제`}</span>${ch.join('')}${ch.length > 1 ? '<button type="button" class="nm-clr" data-act="fclr">모두 해제</button>' : ''}${C.sort !== 'lec' ? `<span class="nm-srt">정렬: ${esc(SORTN[C.sort] || C.sort)}</span>` : ''}`;
}
function batchHTML() { const n = S.sel.size; return `<b>${n}개 선택</b><button type="button" class="nm-btn" data-bat="all">보이는 것 모두 선택</button><button type="button" class="nm-btn" data-bat="none">선택 해제</button><span class="nm-sp"></span><button type="button" class="nm-btn" data-bat="done"${n ? '' : ' disabled'}>완성 표시</button><button type="button" class="nm-btn" data-bat="undone"${n ? '' : ' disabled'}>완성 해제</button><button type="button" class="nm-btn" data-bat="move"${n ? '' : ' disabled'}>강의 옮기기</button><button type="button" class="nm-btn" data-bat="merge"${n > 1 ? '' : ' disabled'} title="같은 문제를 하나로 — 출처·연도를 합침(스토리는 하나만)">합치기</button><button type="button" class="nm-btn" data-bat="del"${n ? '' : ' disabled'}>목록에서 빼기</button>`; }
function refreshCounts(vis) {
  const R = S.root; if (!R) return; const k = counts(); if (vis == null) vis = S.visN != null ? S.visN : $$('.nm-it:not([hidden])', R).length;
  const c = $('[data-cnt]', R); if (c) c.innerHTML = infoHTML(vis, k);
  const g = $('.nm-stg', R); if (g) g.innerHTML = stgHTML(k);
  const ft = $('[data-sfoot]', R); if (ft) ft.innerHTML = footHTML(k);
  const bt = $('[data-batch]', R); if (bt) bt.innerHTML = batchHTML();
  const fb = $('.nm-tbtn[data-act=flt]', R); if (fb) { const n = fCount(); let e = fb.querySelector('.n'); if (n) { if (!e) { e = document.createElement('b'); e.className = 'n'; fb.appendChild(e); } e.textContent = n; } else if (e) e.remove(); }
}
function vClass() { return (S.selMode ? 'selm ' : '') + (S.cfg.hide.a ? 'hideA ' : '') + (S.cfg.hide.st ? 'hideS ' : '') + (S.cfg.side === 'c' ? 'sidec ' : '') + (S.drawer ? 'sideo' : ''); }
function frame() {   /* #numv 뼈대 — 사이드바·본문(대화창·메뉴는 #numv 바로 아래에 붙어 다시 그려도 남음) */
  let V = document.getElementById('numv');
  if (!V || !S.root.contains(V) || !$('.nm-main', V)) { S.root.innerHTML = '<div id="numv"><aside class="nm-side" aria-label="내 넘버링 메뉴"></aside><div class="nm-sbg" data-sact="close"></div><div class="nm-main"></div></div>'; V = document.getElementById('numv'); }
  V.className = vClass(); return V;
}
function emptyHTML() { return `<div class="nm-empty">아직 이 과목에 넘버링 문제가 없어요.<div class="row"><button type="button" class="nm-btn pri" data-act="imp">기존 문제 불러오기</button><button type="button" class="nm-btn" data-act="new">+ 새 문제</button><button type="button" class="nm-btn" data-act="file">Word 파일 가져오기</button></div><small>JB 기출·강의 예상문제를 골라 넣거나, 직접 만들거나, 내 Word(.docx)에서 가져올 수 있어요.</small></div>`; }

function render(o) {
  o = o || {}; const tok = ++S.tok, R = S.root; if (!R) return;
  endEdit(true);
  const L = ordered(), C = S.cfg, K = lecKeys();
  const chunks = [];   /* [html, ...] — 첫 묶음은 바로, 나머지는 쉬는 틈에 */
  let cur = '', curLec = null, n = 0;
  const flush = () => { if (cur) { chunks.push(cur); cur = ''; } };
  for (const it of L) {
    if (C.mode === 'grp') { const lk = K.has(it.lec) ? it.lec : ''; if (lk !== curLec) { curLec = lk; const l = lecOf(lk); cur += `<h2 class="nm-lec" data-lec="${esc(lk)}">${esc(l.t)}<small>${esc([l.prof, l.lab].filter(Boolean).join(' · '))}</small></h2>`; } }
    const v = visible(it); cur += itemHTML(it, 0, !v); n++;
    if (n % 40 === 0) flush();
  }
  flush();
  const hid = S.items.filter(it => it.del);
  const V = frame(), main = $('.nm-main', V);
  main.innerHTML = `${barHTML()}<div class="nm-doc" data-doc="1">${chunks[0] || ''}${L.length ? '' : emptyHTML()}</div>${hid.length ? hidHTML(hid) : ''}`;
  sideRender();
  const doc = $('[data-doc]', R);
  const rest = chunks.slice(1);
  const done = () => { if (tok !== S.tok) return; applyFilter(); if (o.pos) restorePos(o.pos); else if (o.y != null) window.scrollTo(0, o.y); if (o.flash) flash(o.flash); spy(); };
  applyFilter(true);
  if (!rest.length) { done(); return; }
  let i = 0; const step = () => { if (tok !== S.tok || !doc.isConnected) return; doc.insertAdjacentHTML('beforeend', rest[i++]); if (i < rest.length) setTimeout(step, 0); else done(); };
  setTimeout(step, 0);
}
function hidHTML(hid) { return `<details class="nm-hid"><summary>목록에서 뺀 문제 ${hid.length}개 — 다시 넣을 수 있어요(원본은 그대로)</summary>${hid.map(it => `<div class="row" data-id="${esc(it.id)}"><span class="nm-chip k-${esc(it.kind)}">${esc(KIND[it.kind] || it.kind)}</span><span style="flex:1;min-width:0;overflow:hidden;text-overflow:ellipsis;white-space:nowrap">${esc(plain(it.q).slice(0, 90))}</span><button type="button" class="nm-btn" data-act="undel">다시 넣기</button></div>`).join('')}</details>`; }
function applyFilter(initial) {   /* 숨김·표시 번호(지금 보이는 순서대로 1, 2, 3…)·강의 머리·개수만 고침 — 다시 그리지 않음 */
  const R = S.root; if (!R) return;
  const arts = $$('.nm-it', R), K = lecKeys(), vl = {}; let no = 0;
  for (const a of arts) { const it = S.by.get(a.dataset.id); const v = !!it && visible(it); if (a.hidden === v) a.hidden = !v; if (v) { const nb = a.querySelector('.nm-no'); const t = (++no) + '.'; if (nb.textContent !== t) nb.textContent = t; vl[K.has(it.lec) ? it.lec : ''] = 1; } }
  $$('.nm-lec', R).forEach(h => { const any = !!vl[h.dataset.lec]; if (h.hidden === any) h.hidden = !any; });
  $$('.nm-lj', R).forEach(b => b.classList.toggle('off', !vl[b.dataset.lj]));
  S.visN = no; refreshCounts(no);
  if (!initial) { const e = $('.nm-empty2', R); if (e) e.remove(); if (!no && S.items.some(it => !it.del)) $('[data-doc]', R).insertAdjacentHTML('beforeend', '<div class="nm-empty nm-empty2">조건에 맞는 문제가 없어요 — 위의 조건(✕)을 풀거나 검색어를 바꿔 보세요.</div>'); }
}
function rerenderItem(it) {
  const a = S.root && $(`.nm-it[data-id="${CSS.escape(it.id)}"]`, S.root); if (!a) return;
  const no = parseInt(a.querySelector('.nm-no').textContent, 10) || 0; const t = document.createElement('div'); t.innerHTML = itemHTML(it, no, a.hidden); const n = t.firstElementChild; ['revA', 'revS'].forEach(c => { if (a.classList.contains(c)) n.classList.add(c); }); a.replaceWith(n);
  refreshCounts();
}
function toph() { return parseFloat(getComputedStyle(document.documentElement).getPropertyValue('--toph')) || 52; }
function stuckBottom() { const s = S.root && $('.nm-stick', S.root); if (!s) return toph(); return Math.max(s.getBoundingClientRect().bottom, toph()); }
function flash(id) { const a = S.root && $(`.nm-it[data-id="${CSS.escape(id)}"]`, S.root); if (!a) return; a.hidden = false; a.scrollIntoView({ block: 'center' }); a.classList.remove('flash'); void a.offsetWidth; a.classList.add('flash'); }
function topItem() { const y = stuckBottom(), arts = $$('.nm-it:not([hidden])', S.root); for (const a of arts) { const r = a.getBoundingClientRect(); if (r.bottom > y + 4) return { id: a.dataset.id, off: Math.round(r.top) }; } return null; }
function restorePos(p) { const a = S.root && $(`.nm-it[data-id="${CSS.escape(p.id)}"]`, S.root); if (!a) return; a.scrollIntoView({ block: 'start' }); window.scrollBy(0, -(p.off || 0) + 0); requestAnimationFrame(() => { const r = a.getBoundingClientRect(); if (Math.abs(r.top - (p.off || 0)) > 4) window.scrollBy(0, r.top - (p.off || 0)); }); }
/* 강의 바로 가기(문서는 그대로 두고 그 강의 첫 자리로) — '강의만 보기'(필터)와 다름 */
function jumpLec(k) {
  const R = S.root; if (!R) return; let el = null;
  if (S.cfg.mode === 'grp') { el = $(`.nm-lec[data-lec="${CSS.escape(k)}"]`, R); if (el && el.hidden) el = null; }
  if (!el) { const K = lecKeys(); el = $$('.nm-it:not([hidden])', R).find(a => { const it = S.by.get(a.dataset.id); return it && (K.has(it.lec) ? it.lec : '') === k; }) || null; }
  if (S.drawer) drawer(false);
  if (!el) { H.toast('이 강의 문제는 지금 필터·검색에 걸려 안 보여요 — 위의 조건(✕)을 풀어 보세요'); return; }
  const s = S.root && $('.nm-stick', S.root), y = el.getBoundingClientRect().top + scrollY - toph() - (s ? s.offsetHeight : 0) - 6;
  window.scrollTo(0, Math.max(0, y)); setCur(k);
}
function setCur(k) {
  if (k === S.curLec) return; S.curLec = k; const R = S.root; if (!R) return;
  $$('.nm-lj.cur', R).forEach(b => b.classList.remove('cur'));
  const b = $(`.nm-lj[data-lj="${CSS.escape(k)}"]`, R); if (b) { b.classList.add('cur'); const sd = b.closest('.nm-side'); if (sd && sd.scrollHeight > sd.clientHeight) { const t = b.offsetTop, h = sd.clientHeight; if (t < sd.scrollTop + 40 || t > sd.scrollTop + h - 120) sd.scrollTop = Math.max(0, t - h / 2); } }
  const c = $('.nm-ctx span', R); if (c) { const l = lecOf(k); c.textContent = l ? '› ' + l.t : ''; }
}
function spy() {   /* 지금 화면 맨 위 문제의 강의 → 사이드바 '강의 바로 가기'에 표시(스크롤 중 0.12초마다 한 번 · 한 점만 짚어 봄) */
  spyT = 0; const R = S.root; if (!R || !document.getElementById('numv')) return;
  const doc = $('[data-doc]', R); if (!doc) return; const r = doc.getBoundingClientRect(), y = stuckBottom() + 16;
  if (r.top > y) { const f = $('.nm-lec:not([hidden]),.nm-it:not([hidden])', doc); if (f) pickLec(f); return; }
  const el = document.elementFromPoint(Math.max(r.left + 48, 0), y), a = el && el.closest && (el.closest('.nm-it') || el.closest('.nm-lec'));
  if (a && doc.contains(a)) pickLec(a);
}
function pickLec(a) { if (a.classList.contains('nm-lec')) { setCur(a.dataset.lec); return; } const it = S.by.get(a.dataset.id); if (it) setCur(lecKeys().has(it.lec) ? it.lec : ''); }
let spyT = 0;
function side(on) {   /* 넓은 화면 = 접기·펼치기(기억) · 좁은 화면(≤860) = 서랍 열기·닫기 */
  const V = S.root && document.getElementById('numv'); if (!V) return;
  if (innerWidth <= 860) { drawer(on == null ? !S.drawer : !!on); return; }
  const c = on == null ? S.cfg.side !== 'c' : !on; S.cfg.side = c ? 'c' : ''; cfgSave(); V.classList.toggle('sidec', c); tbKick();
}
function drawer(on) { S.drawer = !!on; const V = document.getElementById('numv'); if (V) V.classList.toggle('sideo', S.drawer); if (on) { const f = V && $('.nm-side .nm-lj.cur, .nm-side [data-act=new]', V); if (f) f.focus({ preventScroll: true }); } }
function fpOpen(on) { S.fp = !!on; if (on) S.vo = false; const R = S.root; if (!R) return; const p = $('[data-fpan]', R); if (p) p.hidden = !S.fp; const b = $('.nm-tbtn[data-act=flt]', R); if (b) { b.classList.toggle('on', S.fp); b.setAttribute('aria-expanded', String(S.fp)); } const v = $('.nm-vopt', R); if (v && on) v.classList.remove('open'); }
function voOpen(on) { S.vo = !!on; if (on) fpOpen(false); S.vo = !!on; const R = S.root; if (!R) return; const v = $('.nm-vopt', R); if (v) v.classList.toggle('open', S.vo); const b = $('[data-act=vopt]', R); if (b) b.setAttribute('aria-expanded', String(S.vo)); }
function fClear(x) {   /* 조건 하나(x) 또는 모두 풀기 — 검색 포함 */
  const C = S.cfg;
  if (!x || x === 'q') { S.q = ''; const i = S.root && $('[data-cf=q]', S.root); if (i) i.value = ''; }
  if (!x) fKeys.forEach(k => { C.f[k] = ''; }); else if (x !== 'q') C.f[x] = '';
  cfgSave(); if (S.root) $$('.nm-fpan select[data-cf]', S.root).forEach(s => { const k = s.dataset.cf; if (k !== 'sort' && C.f[k] != null) s.value = C.f[k]; });
  applyFilter();
}

/* ---------- 편집기(누른 칸 하나만) — 작은 떠 있는 도구 막대: 자주 쓰는 것(굵게·밑줄·글자색·형광펜·번호·글머리표)만, 나머지는 ⋯ ---------- */
const COLORS = ['#000000', '#C00000', '#E36C09', '#BF4E14', '#00B050', '#0070C0', '#7030A0', '#7F7F7F'];
const HILITE = ['#FFFF00', '#00FF00', '#00FFFF', '#FF99CC', '#FFD966', '#C6E0B4'];
const curEd = () => S.ed || S.formEd;
function tbHTML(form) {
  return `<div class="nm-tb" role="toolbar" aria-label="서식">`
    + `<button type="button" data-cmd="bold" title="굵게 (⌘/Ctrl B)"><b>B</b></button><button type="button" data-cmd="underline" title="밑줄 (⌘/Ctrl U)"><u>U</u></button>`
    + `<button type="button" data-pal="fc" title="글자색" aria-label="글자색"><span style="border-bottom:2.5px solid #F05252;line-height:1.05;font-weight:700">가</span></button><button type="button" data-pal="hl" title="형광펜" aria-label="형광펜"><span style="background:#FFF066;color:#1F1D1A;padding:1px 4px;border-radius:3px;font-size:12px;font-weight:600">형</span></button><i class="sep"></i>`
    + `<button type="button" data-cmd="insertOrderedList" title="번호 목록">1.</button><button type="button" data-cmd="insertUnorderedList" title="글머리표">•</button>`
    + `<button type="button" data-pal="more" title="더보기 — 기울임·서식 지우기·표·그림·실행 취소" aria-label="서식 더보기">⋯</button>`
    + (form ? '' : `<button type="button" class="done" data-cmd="done" title="편집 끝 (Esc) — 자동 저장됨">완료</button>`) + `</div>`;
}
let tbRaf = 0;
function tbKick() { if (!tbRaf) tbRaf = requestAnimationFrame(() => { tbRaf = 0; tbPlace(); palPlace(); }); }
function tbWatch(on) { if (on) { addEventListener('scroll', tbKick, { capture: true, passive: true }); addEventListener('resize', tbKick); } else { removeEventListener('scroll', tbKick, { capture: true }); removeEventListener('resize', tbKick); } }
function tbMount(E, box) {
  const t = document.createElement('div'); t.innerHTML = tbHTML(!!E.form); const tb = t.firstElementChild; box.appendChild(tb); E.tb = tb;
  tb.addEventListener('mousedown', e => e.preventDefault());
  tb.addEventListener('click', e => { const c = e.target.closest('[data-cmd]'), p = e.target.closest('[data-pal]'); if (c) runCmd(c.dataset.cmd); else if (p) palOpen(p, p.dataset.pal); });
  tbPlace(); tbWatch(true);
}
function tbPlace() {   /* 편집 칸 오른쪽 위(문제 칸은 오른쪽 아래 — 비어 있는 '넘버링 스토리' 머리 줄 위) · 위 막대 아래로만 · 칸이 화면 밖이면 숨김 */
  const E = curEd(); if (!E || !E.tb || !E.tb.isConnected) return;
  if (!E.el.isConnected) { E.tb.style.visibility = 'hidden'; return; }
  const tb = E.tb, fr = E.el.getBoundingClientRect(), w = tb.offsetWidth, h = tb.offsetHeight, minT = E.form ? 8 : stuckBottom() + 4;
  const art = E.f === 'q' && E.el.closest('.nm-it'), right = art ? art.getBoundingClientRect().right : fr.right;
  let y = E.f === 'q' ? fr.bottom + 4 : fr.top - h - 6; if (y < minT) y = minT;
  const vis = fr.bottom > minT + 4 && fr.top < innerHeight - 10;
  const x = Math.max(8, Math.min(right - w, innerWidth - w - 8));
  tb.style.transform = `translate(${Math.round(x)}px,${Math.round(y)}px)`; tb.style.visibility = vis ? 'visible' : 'hidden';
}
function palClose() { $$('.nm-pal').forEach(p => p.remove()); S.palBtn = null; }
function palOpen(btn, kind) {
  const was = $('.nm-pal'), same = was && was.dataset.k === kind && S.palBtn === btn; palClose(); if (same) return;
  const E = curEd(); if (!E) return; const box = E.tb && E.tb.parentNode; if (!box) return;
  const p = document.createElement('div'); p.className = 'nm-pal' + (kind === 'more' ? ' more' : ''); p.dataset.k = kind; p.setAttribute('role', 'menu');
  if (kind === 'fc') p.innerHTML = COLORS.map(c => `<button type="button" data-fc="${c}" title="${c}" style="background:${c}"></button>`).join('') + `<button type="button" class="wide" data-fc="">기본색</button>`;
  else if (kind === 'hl') p.innerHTML = HILITE.map(c => `<button type="button" data-hl="${c}" title="${c}" style="background:${c}"></button>`).join('') + `<button type="button" class="wide" data-hl="">형광펜 지우기</button>`;
  else p.innerHTML = [['cmd', 'italic', '<i>기울임</i><small>⌘/Ctrl I</small>'], ['cmd', 'removeFormat', '서식 지우기'], '-', ['tb', 'ins2', '표 넣기 2×2'], ['tb', 'ins3', '표 넣기 3×3'], ['tb', 'row', '표: 아래에 줄 더하기'], ['tb', 'col', '표: 오른쪽에 칸 더하기'], ['tb', 'drow', '표: 이 줄 빼기'], ['tb', 'dcol', '표: 이 칸 빼기'], ['tb', 'dtbl', '표 지우기'], '-', ['cmd', 'img', '그림 넣기'], '-', ['cmd', 'undo', '↶ 실행 취소<small>⌘/Ctrl Z</small>'], ['cmd', 'redo', '↷ 다시 실행']].map(x => x === '-' ? '<hr>' : `<button type="button" class="wide" data-${x[0]}="${x[1]}">${x[2]}</button>`).join('');
  box.appendChild(p); S.palBtn = btn; palPlace();
  p.addEventListener('mousedown', e => e.preventDefault());
  p.addEventListener('click', e => {
    const E2 = curEd(); if (!E2) return; const fc = e.target.closest('[data-fc]'), hl = e.target.closest('[data-hl]'), tb = e.target.closest('[data-tb]'), c = e.target.closest('[data-cmd]');
    if (fc) { E2.el.focus({ preventScroll: true }); document.execCommand('foreColor', false, fc.dataset.fc || '#000000'); palClose(); edChanged(); }
    else if (hl) { E2.el.focus({ preventScroll: true }); document.execCommand('hiliteColor', false, hl.dataset.hl || 'transparent'); palClose(); edChanged(); }
    else if (tb) { E2.el.focus({ preventScroll: true }); palClose(); tblOp(tb.dataset.tb); }
    else if (c) { palClose(); runCmd(c.dataset.cmd); }
  });
}
function palPlace() { const p = $('.nm-pal'), b = S.palBtn; if (!p || !b || !b.isConnected) return; const r = b.getBoundingClientRect(), w = p.offsetWidth, h = p.offsetHeight; let y = r.bottom + 4; if (y + h > innerHeight - 8) y = Math.max(8, r.top - h - 4); p.style.left = Math.round(Math.max(8, Math.min(r.right - w, innerWidth - w - 8))) + 'px'; p.style.top = Math.round(y) + 'px'; }
function edChanged() { if (S.ed) edInput(); tbKick(); }
function startEdit(el, it, f, ev) {
  if (S.ed && S.ed.el === el) return;
  { const art = el.closest && el.closest('.nm-it'); if (art) art.classList.add(f === 'st' ? 'revS' : 'revA'); }
  endEdit();
  if (!el.isConnected) { el = S.root && $(`.nm-it[data-id="${CSS.escape(it.id)}"] .nm-c[data-f="${f}"]`, S.root); if (!el) return; }   /* 같은 문제의 다른 칸을 고치다 왔으면 그 문제가 새로 그려짐 */
  const orig = it[f] || '';
  el.innerHTML = disp(orig) || '<p><br></p>';
  el.contentEditable = 'true'; el.spellcheck = false;
  let o0 = toStore(el.innerHTML); if (isEmpty(o0)) o0 = '';
  const base = isEmpty(orig) ? '' : o0;   /* 브라우저·정리를 한 번 거친 같은 글 — 열었다 닫기만 하면 '고침'이 생기지 않게 */
  S.ed = { el, it, f, orig: orig, norm0: base, t: 0, saved: base, tb: null };
  tbMount(S.ed, document.getElementById('numv'));
  try { document.execCommand('styleWithCSS', false, true); document.execCommand('defaultParagraphSeparator', false, 'p'); } catch (e) {}
  el.focus({ preventScroll: true });
  const sel = getSelection();
  let r = null;
  if (ev && ev.clientX != null) { if (document.caretRangeFromPoint) r = document.caretRangeFromPoint(ev.clientX, ev.clientY); else if (document.caretPositionFromPoint) { const p = document.caretPositionFromPoint(ev.clientX, ev.clientY); if (p) { r = document.createRange(); r.setStart(p.offsetNode, p.offset); } } }
  if (!r || !el.contains(r.startContainer)) { r = document.createRange(); r.selectNodeContents(el); r.collapse(false); }
  sel.removeAllRanges(); sel.addRange(r);
}
function edInput() { const E = S.ed; if (!E) return; saveState('ing'); clearTimeout(E.t); E.t = setTimeout(edSave, 700); if (E.f === 'q') tbKick(); }
function edSave() {
  const E = S.ed; if (!E) return; clearTimeout(E.t); E.t = 0;
  let h = toStore(E.el.innerHTML); if (isEmpty(h)) h = '';
  if (h === E.saved) { saveState('ok'); return; }
  const it = E.it;
  if (E.saved === E.norm0 && h !== E.norm0) it.prev = { f: E.f, h: E.orig, at: now() };   /* 이번 편집 전 글 = 되돌리기 한 칸 */
  if ((E.f === 'q' || E.f === 'a') && it.kind !== 'seed' && it.kind !== 'user' && it[E.f + '0'] == null) it[E.f + '0'] = E.orig;   /* JB·예상·Word 가져온 원본 사본(처음 고칠 때) */
  it[E.f] = h === E.norm0 ? E.orig : h; touch(it); E.saved = h; it._ty = null;   /* 원래 글로 되돌려 쓰면 원본 그대로(작업본 아님) */
  put(it);
}
function endEdit(silent) {
  const E = S.ed; if (!E) return; edSave(); S.ed = null;
  try { E.el.contentEditable = 'false'; E.el.removeAttribute('contenteditable'); } catch (e) {}
  if (E.tb && E.tb.isConnected) E.tb.remove(); palClose(); if (!S.formEd) tbWatch(false);
  if (!silent && E.el.isConnected) rerenderItem(E.it);
}
function cellAt() { const s = getSelection(), E = curEd(); if (!s.rangeCount || !E) return null; let n = s.anchorNode; while (n && n !== E.el) { if (n.nodeType === 1 && (n.tagName === 'TD' || n.tagName === 'TH')) return n; n = n.parentNode; } return null; }
function replaceNode(node, html) { const r = document.createRange(); r.selectNode(node); const s = getSelection(); s.removeAllRanges(); s.addRange(r); document.execCommand('insertHTML', false, html); }
function tblOp(k) {
  const E = curEd(); if (!E) return;
  if (k === 'ins2' || k === 'ins3') { const n = k === 'ins2' ? 2 : 3; document.execCommand('insertHTML', false, '<table>' + Array.from({ length: n }, () => '<tr>' + Array.from({ length: n }, () => '<td><p><br></p></td>').join('') + '</tr>').join('') + '</table><p><br></p>'); edChanged(); return; }
  const td = cellAt(); if (!td) { H.toast('표 안의 칸을 먼저 누르세요'); return; }
  const tr = td.parentNode, tb = td.closest('table'), ci = [...tr.children].indexOf(td), t2 = tb.cloneNode(true), rows = [...t2.querySelectorAll('tr')], ri = [...tb.querySelectorAll('tr')].indexOf(tr);
  if (k === 'row') { const nr = document.createElement('tr'); for (let i = 0; i < rows[ri].children.length; i++) { const c = document.createElement('td'); c.innerHTML = '<p><br></p>'; nr.appendChild(c); } rows[ri].after(nr); }
  else if (k === 'col') rows.forEach(r => { const c = document.createElement('td'); c.innerHTML = '<p><br></p>'; const ref = r.children[Math.min(ci, r.children.length - 1)]; if (ref) ref.after(c); else r.appendChild(c); });
  else if (k === 'drow') { if (rows.length <= 1) { tblOp('dtbl'); return; } rows[ri].remove(); }
  else if (k === 'dcol') { rows.forEach(r => { const c = r.children[Math.min(ci, r.children.length - 1)]; if (c) c.remove(); }); if (!t2.querySelector('td,th')) { tblOp('dtbl'); return; } }
  else if (k === 'dtbl') { replaceNode(tb, '<p><br></p>'); edChanged(); return; }
  replaceNode(tb, t2.outerHTML); edChanged();
}
async function shrinkFile(file, maxW) {
  const bmp = await createImageBitmap(file); const sc = Math.min(1, (maxW || 1000) / bmp.width), w = Math.max(1, Math.round(bmp.width * sc)), h = Math.max(1, Math.round(bmp.height * sc));
  const cv = document.createElement('canvas'); cv.width = w; cv.height = h; const g = cv.getContext('2d'); g.fillStyle = '#fff'; g.fillRect(0, 0, w, h); g.drawImage(bmp, 0, 0, w, h); if (bmp.close) bmp.close();
  let d = cv.toDataURL('image/webp', 0.8); if (!/^data:image\/webp/.test(d)) d = cv.toDataURL('image/jpeg', 0.82);
  return { d, w: Math.min(w, 640), h: Math.round(Math.min(w, 640) * h / w) };
}
function pickImage(cb) { const i = document.createElement('input'); i.type = 'file'; i.accept = 'image/*'; i.onchange = async () => { const f = i.files && i.files[0]; if (!f) return; try { cb(await shrinkFile(f)); } catch (e) { H.toast('그림을 열지 못했어요 — 다른 형식(png·jpg)으로 해 주세요', { level: 'error', id: 'nmimg' }); } }; i.click(); }
function runCmd(c) {
  const E = curEd(); if (!E) return; E.el.focus({ preventScroll: true });
  if (c === 'done') { if (S.ed) endEdit(); return; }
  if (c === 'img') { const sel = getSelection(), r = sel.rangeCount ? sel.getRangeAt(0).cloneRange() : null; E.busy = true;
    const back = () => { removeEventListener('focus', back); setTimeout(() => { if (curEd() === E && E.busy === true) { E.busy = false; E.el.focus({ preventScroll: true }); } }, 900); }; addEventListener('focus', back);
    pickImage(im => { E.busy = false; if (curEd() !== E) return; E.el.focus({ preventScroll: true }); if (r) { sel.removeAllRanges(); sel.addRange(r); } document.execCommand('insertHTML', false, `<img src="${im.d}" width="${im.w}" height="${im.h}" alt="">`); edChanged(); }); return; }
  try { document.execCommand(c, false, null); } catch (e) {}
  edChanged();
}
async function onPaste(e) {
  const E = curEd(); if (!E) return; const cd = e.clipboardData; if (!cd) return;
  const files = [...(cd.files || [])].filter(f => /^image\//.test(f.type)), h = cd.getData('text/html'), t = cd.getData('text/plain');
  e.preventDefault();
  if (h) { S.pasteLost = 0; const c = sanitize(h, { paste: true }); document.execCommand('insertHTML', false, c); if (S.pasteLost && !files.length) H.toast('Word 안의 그림은 글과 함께 복사되지 않아요 — 그림만 따로 복사해 붙여 넣거나 ⋯ → [그림 넣기]로 넣어 주세요', { level: 'result' }); }
  else if (files.length) { for (const f of files) { try { const im = await shrinkFile(f); if (curEd() !== E) return; E.el.focus({ preventScroll: true }); document.execCommand('insertHTML', false, `<img src="${im.d}" width="${im.w}" height="${im.h}" alt="">`); } catch (_) {} } }
  else if (t) document.execCommand('insertText', false, t);
  if (curEd() === E) edChanged();
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
  const L = [[it.done ? 'undone' : 'done', it.done ? '완성 해제' : '✓ 완성으로 표시'], ['editq', '문제 수정'], ['edita', '답안 수정'], ['det', '출처·연도·태그·참고 보기/고치기'], '-',
    ['up', '위로 옮기기' + (canMove ? '' : ' (정렬: 사용자 지정으로)')], ['down', '아래로 옮기기' + (canMove ? '' : ' (정렬: 사용자 지정으로)')], ['lec', '다른 강의로 옮기기'], ['copy', '복사해서 새 문제로'], '-'];
  if (it.prev) L.push(['prev', '마지막 수정 전으로 되돌리기 (' + ({ q: '문제', a: '답안', st: '스토리' }[it.prev.f] || '') + ' · ' + new Date(it.prev.at).toLocaleTimeString('ko-KR', { hour: '2-digit', minute: '2-digit' }) + ')']);
  if (orig) L.push(['orig', '문제·답안을 원본으로 되돌리기']);
  const s0 = it.src.find(s => s.t === 'jb' || s.t === 'pred'); if (s0 && H.PACKS[s0.s]) L.push(['open', s0.t === 'jb' ? 'JB 기출 원본 열기' : '예상문제 원본 열기']);
  L.push('-', ['del', '목록에서 빼기(원본은 그대로)', 'warn']);
  const m = menuOpen(btn, L); if (!m) return;
  m.addEventListener('click', e => { const b = e.target.closest('[data-mi]'); if (!b) return; menuClose(); itemAct(b.dataset.mi, it, btn); });
}
function itemAct(k, it, btn) {
  if (S.ed && S.ed.it === it) endEdit(true);   /* 고치던 글을 먼저 저장(다시 그릴 때 사라지지 않게) */
  if (k === 'done' || k === 'undone') { it.done = k === 'done'; touch(it); put(it); rerenderItem(it); applyFilter(); return; }
  if (k === 'det') { detOpen(it); return; }
  if (k === 'editq' || k === 'edita') { const f = k === 'editq' ? 'q' : 'a', el = S.root && $(`.nm-it[data-id="${CSS.escape(it.id)}"] .nm-c[data-f="${f}"]`, S.root); if (el) startEdit(el, it, f); return; }
  if (k === 'up' || k === 'down') { moveItem(it, k === 'up' ? -1 : 1); return; }
  if (k === 'lec') { lecPick(btn, l => { it.lec = l; touch(it); put(it); render({ flash: it.id }); }); return; }
  if (k === 'copy') { const n = newItem({ s: it.s, lec: it.lec, q: it.q, a: it.a, st: it.st, note: it.note, tags: it.tags.slice(), yrs: it.yrs.slice(), src: it.src.map(s => Object.assign({}, s)), o: it.o + 0.5 }); renumber(); render({ flash: n.id }); H.toast('복사했어요 — 바로 아래에 새 문제로'); return; }
  if (k === 'prev') { const p = it.prev; const cur = it[p.f]; if ((p.f === 'q' || p.f === 'a') && it.kind !== 'seed' && it.kind !== 'user' && it[p.f + '0'] == null) it[p.f + '0'] = cur;   /* 원본으로 → 되돌리기: 원본 사본을 다시 남김 */ it[p.f] = p.h; it.prev = { f: p.f, h: cur, at: now() }; touch(it); it._ty = null; put(it); rerenderItem(it); H.toast('되돌렸어요 — 한 번 더 누르면 다시 앞으로'); return; }
  if (k === 'orig') { ask('이 문제의 문제·답안을 원본 글로 되돌릴까요?\n(넘버링 스토리는 그대로예요)', { ok: '원본으로' }).then(y => { if (y) itemAct('orig!', it, btn); }); return; }
  if (k === 'orig!') { const oq = it.q, oa = it.a; if (it.kind === 'seed') { it.q = it.base.q; it.a = it.base.a; } else { if (it.q0 != null) { it.q = it.q0; it.q0 = undefined; } if (it.a0 != null) { it.a = it.a0; it.a0 = undefined; } } it.prev = oq !== it.q ? { f: 'q', h: oq, at: now() } : oa !== it.a ? { f: 'a', h: oa, at: now() } : it.prev; touch(it); it._ty = null; put(it); rerenderItem(it); H.toast('원본으로 되돌렸어요 — ⋯ 메뉴 \'마지막 수정 전으로\'로 고친 글을 다시 볼 수 있어요'); return; }
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
  m.addEventListener('click', async e => { const b = e.target.closest('[data-mi]'); if (!b) return; menuClose(); let k = b.dataset.mi; if (k === '__new') { k = await newLecture(); if (k == null) return; } cb(k); });
}
async function newLecture(name) {
  const t = name != null ? name : await ask('새 강의 이름', { input: '', ph: '예: Space closure', ok: '만들기' });
  if (!t || !t.trim()) return null;
  const x = idx(S.sj); x.ul = x.ul || []; const k = 'U' + now().toString(36); x.ul.push({ k, t: t.trim() }); idxPut(S.sj, x); S.lecs = lectures(S.sj, S.seed); return k;
}
function detOpen(it) {
  if (S.ed && S.ed.it === it) endEdit();
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
    if (k === 'unsrc') { ask('이 출처 연결을 끊을까요? (원본 문제는 그대로)', { ok: '끊기' }).then(y => { if (!y) return; it.src.splice(i, 1); touch(it); put(it); refreshItem(it, true); }); return; }
    if (k === 'srcadd') { const inp = d.querySelector('[data-det-in=srcadd]'); const v = inp.value.trim(); if (!v) return; it.src.push({ t: 'user', s: it.s, lab: v, yrs: [] }); touch(it);   /* 출처 이름의 숫자는 출제 연도로 넣지 않음(연도는 '출제 연도' 칸에서만) */ put(it); refreshItem(it, true); return; }
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
function dlgClose() { formEnd(); $$('.nm-ov').forEach(o => o.remove()); document.body.style.overflow = ''; }
/* 화면 안 확인·입력 창 — 브라우저 confirm/prompt는 쓰지 않음(미리보기 틀·앱 보기에서 막힘) · Enter = 확인 · Esc = 취소 */
function ask(msg, o) {
  o = o || {}; const R = $('#numv'); if (!R) return Promise.resolve(o.input != null ? null : false);
  return new Promise(res => {
    const box = document.createElement('div'); box.className = 'nm-ov'; box.style.zIndex = 90; box.setAttribute('role', 'alertdialog'); box.setAttribute('aria-modal', 'true');
    box.innerHTML = `<div class="nm-dlg" style="width:min(520px,100%)"><div class="bd"><div style="white-space:pre-wrap;font-size:15px;line-height:1.55">${esc(msg)}</div>${o.input != null ? `<input type="text" data-ask-in="1" value="${esc(o.input)}" placeholder="${esc(o.ph || '')}" aria-label="${esc(o.ph || msg)}">` : ''}</div><footer><span style="flex:1"></span>${o.only ? '' : `<button type="button" class="nm-btn" data-ask="0">${esc(o.no || '취소')}</button>`}<button type="button" class="nm-btn pri" data-ask="1">${esc(o.ok || '확인')}</button></footer></div>`;
    const fin = v => { box.remove(); res(v); };
    box.addEventListener('click', e => { const b = e.target.closest('[data-ask]'); if (b) { const inp = box.querySelector('[data-ask-in]'); fin(b.dataset.ask === '1' ? (inp ? inp.value : true) : (inp ? null : false)); } else if (e.target === box) fin(o.input != null ? null : false); });
    box.addEventListener('keydown', e => { if (e.key === 'Escape') { e.preventDefault(); e.stopPropagation(); fin(o.input != null ? null : false); } else if (e.key === 'Enter' && !e.isComposing) { e.preventDefault(); const inp = box.querySelector('[data-ask-in]'); fin(inp ? inp.value : true); } });
    R.appendChild(box); const f = box.querySelector('[data-ask-in]') || box.querySelector('[data-ask="1"]'); if (f) f.focus();
  });
}
function newForm(pre) {
  pre = pre || {};
  const subs = subjects(), sj = pre.s || S.sj;
  const lecOpts = sjv => { const L = sjv === S.sj ? S.lecs : lectures(sjv, (window.JBLNUM_SEED || {})[sjv]); return L.filter(l => l.k).map(l => `<option value="${esc(l.k)}"${l.k === (pre.lec != null ? pre.lec : S.cfg.f.lec) ? ' selected' : ''}>${esc(l.t)}</option>`).join('') + '<option value="">강의 미분류</option><option value="__new">+ 새 강의 만들기…</option>'; };
  const ov = dlg('새 문제 만들기', `<div class="nm-g2"><label class="nm-fld"><span>과목</span><select data-nf="s">${subs.map(s => `<option value="${esc(s.id)}"${s.id === sj ? ' selected' : ''}>${esc(s.t)}</option>`).join('')}</select></label><label class="nm-fld"><span>강의</span><select data-nf="lec">${lecOpts(sj)}</select></label></div>`
    + richField('q', '문제', pre.q, '예: ○○의 적응증 4가지를 쓰시오.') + `<div class="nm-g2">${richField('a', '답안', pre.a)}${richField('st', '넘버링 스토리 (비워 둬도 저장돼요)', pre.st)}</div>`
    + `<div class="nm-g2"><label class="nm-fld"><span>출처</span><input type="text" data-nf="src" value="직접 추가" placeholder="예: 25 수업 강조, 스터디 예상"></label><label class="nm-fld"><span>출제 연도(있으면)</span><input type="text" data-nf="yrs" placeholder="예: 25, 23"></label></div>`
    + `<div class="nm-g2"><label class="nm-fld"><span>태그</span><input type="text" data-nf="tags" placeholder="쉼표로 나눔"></label><label class="nm-fld"><span>참고사항</span><input type="text" data-nf="note"></label></div><div class="nm-warn" data-nf-msg="1"></div>`,
    `<span style="font-size:13px;color:var(--sub)">칸을 누르면 작은 서식 도구가 떠요(⋯에 표·그림·실행 취소)</span><span style="flex:1"></span><button type="button" class="nm-btn" data-x="1">취소</button><button type="button" class="nm-btn pri" data-nfsave="1">저장</button>`);
  if (!ov) return;
  const sel = ov.querySelector('[data-nf=s]'), lsel = ov.querySelector('[data-nf=lec]');
  sel.addEventListener('change', async () => { if (sel.value !== S.sj) await seedOf(sel.value).catch(() => null); lsel.innerHTML = lecOpts(sel.value); });
  lsel.addEventListener('change', async () => { if (lsel.value === '__new') { const t = await ask('새 강의 이름', { input: '', ph: '예: Space closure', ok: '만들기' }); if (t && t.trim()) { const x = idx(sel.value); x.ul = x.ul || []; const k = 'U' + now().toString(36); x.ul.push({ k, t: t.trim() }); idxPut(sel.value, x); if (sel.value === S.sj) S.lecs = lectures(S.sj, S.seed); lsel.innerHTML = lecOpts(sel.value); lsel.value = k; } else lsel.value = ''; } });
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
function formRich(ov) {   /* 대화창 안 서식 칸: 누른 칸 위에 같은 작은 떠 있는 도구 막대(완료 단추 없음 — 저장은 대화창의 [저장]) */
  ov.addEventListener('focusin', e => { const el = e.target.closest && e.target.closest('[data-rich]'); if (!el) return; if (S.formEd && S.formEd.el === el) return; formEnd(); S.formEd = { el, form: true }; tbMount(S.formEd, ov); try { document.execCommand('styleWithCSS', false, true); document.execCommand('defaultParagraphSeparator', false, 'p'); } catch (_) {} });
  ov.addEventListener('focusout', e => { const F = S.formEd; if (!F || e.target !== F.el) return; setTimeout(() => { if (S.formEd !== F || F.busy) return; const ae = document.activeElement; if (ae && (F.el.contains(ae) || (F.tb && F.tb.contains(ae)) || (ae.closest && ae.closest('.nm-pal')))) return; formEnd(); }, 150); });
  ov.addEventListener('input', e => { if (S.formEd && S.formEd.el.contains(e.target)) tbKick(); });
  ov.addEventListener('paste', e => { if (e.target.closest && e.target.closest('[data-rich]')) onPaste(e); });
}
function formEnd() { const F = S.formEd; if (!F) return; S.formEd = null; if (F.tb) F.tb.remove(); palClose(); if (!S.ed) tbWatch(false); }

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
function dupOf(c, items) {   /* 같은 출처 = 이미 있음(뺀 문제면 다시 넣기) · 문제 글이 같음 = 같은 문제(출처만 잇기) · 비슷함(0.75↑) = 사용자 확인 */
  for (const it of items) if (it.src.some(s => s.t === c.t && s.id === c.id)) return { k: it.del ? 'back' : 'have', it };
  if (!keyOK(c.key)) return null;
  for (const it of items) if (!it.del && kOf(it) === c.key) return { k: 'same', it };
  let best = null, bs = 0; for (const it of items) { if (it.del) continue; const k2 = kOf(it); if (!keyOK(k2)) continue; if (Math.abs(k2.length - c.key.length) > Math.max(k2.length, c.key.length) * 0.5) continue; const d = dice(k2, c.key); if (d > bs) { bs = d; best = it; } }
  if (bs >= 0.75) return { k: 'sim', it: best, d: bs };
  return null;
}
function planOf(L, target) {   /* 고른 순서대로 — 앞에서 새로 넣기로 한 문제도 뒤의 같은 문제와 비교(한 묶음 안 중복 방지) */
  const pool = target.slice(), plan = [];
  for (const x of L) { const d = dupOf(x, pool), p = { x, d }; if (!d) { p.ni = { id: (x.t === 'jb' ? 'jb:' : 'pr:') + x.id, q: x.q, _k: x.key, src: [{ t: x.t, id: x.id }], del: false, yrs: [], _plan: true }; pool.push(p.ni); } plan.push(p); }
  return plan;
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
    box.innerHTML = list.length ? list.map(x => { const d = dupOf(x, target); x.dup = d; return `<div class="nm-irow${d && (d.k === 'have' || d.k === 'same') ? ' dup' : ''}" data-ix="${esc(x.id)}"><input type="checkbox" data-ick="1"${st.chk.has(x.id) ? ' checked' : ''}${d && d.k === 'have' ? ' disabled' : ''} aria-label="고르기"><div><div class="t">${esc(plain(x.q))}</div><div class="m"><span class="nm-chip k-${x.t}">${x.t === 'jb' ? 'JB 기출' + (x.prof ? ' · ' + esc(x.prof) : '') : '예상문제'}</span>${x.yrs.length ? `<span class="nm-chip yr">${esc(yrsTxt(x.yrs))}</span>` : ''}<span class="nm-chip">${esc(TYPES[x.ty])}</span><span class="nm-chip">${esc(lecT(x.lec))}</span>${d ? `<span class="nm-chip ${d.k === 'sim' ? 'rv' : 's2'}" title="${esc(plain(d.it.q).slice(0, 200))}">${d.k === 'have' ? '이미 있음' : d.k === 'back' ? '뺀 문제 → 다시 넣기' : d.k === 'same' ? '같은 문제 있음 → 출처만 연결' : '비슷한 문제 있음(' + Math.round(d.d * 100) + '%)'}</span>` : ''}</div></div><button type="button" class="nm-btn add" data-iadd="1"${d && d.k === 'have' ? ' disabled' : ''}>${d && d.k === 'same' ? '출처 연결' : d && d.k === 'back' ? '다시 넣기' : '추가'}</button></div>`; }).join('') : '<div class="nm-empty">조건에 맞는 문제가 없어요.</div>';
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
    const plan = planOf(L, target);
    const nNew = plan.filter(p => !p.d || p.d.k === 'back').length, nHave = plan.filter(p => p.d && p.d.k === 'have').length, nSame = plan.filter(p => p.d && p.d.k === 'same').length, sim = plan.filter(p => p.d && p.d.k === 'sim');
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
function addMany(plan, sim, simMerge, sj) {   /* 한 번에 — 기록은 사본에 먼저 만들고, 쓰다가 실패하면 이번에 쓴 키를 모두 쓰기 전 값으로(기존 문제 손상 없음) */
  const t = now(), live = sj === S.sj, before = new Map(), apply = []; let add = 0, link = 0, skip = 0;
  let o = (live ? S.items.reduce((m, it) => Math.max(m, it.o || 0), -1) : 1e6) + 1;
  const lab = x => x.t === 'jb' ? 'JB 기출' + (x.prof ? ' · ' + x.prof : '') : '예상문제';
  const out = new Map();   /* id → {rec, fin} — 같은 문제에 출처를 여럿 이을 때도 사본 하나 */
  const made = new Map();  /* 계획 자리표 → 새 문제 */
  const srcOf = x => ({ t: x.t, s: x.s, id: x.id, lec: x.lec, yrs: x.yrs, lab: lab(x) });
  const linkTo = (it, x) => {
    const e = out.get(it.id), c = e ? e.c : Object.assign({}, it, { src: it.src.map(z => Object.assign({}, z)), yrs: it.yrs.slice() });
    if (c.src.some(z => z.t === x.t && z.id === x.id)) return false;
    c.src.push(srcOf(x)); c.yrs = [...new Set(c.yrs.concat(x.yrs))].sort((p1, p2) => p2 - p1); c.u = t;
    out.set(it.id, { c, fin: e ? e.fin : () => { if (it !== c && !it._new) Object.assign(it, { src: c.src, yrs: c.yrs, u: t, _t: null, _qd: null }); } }); return true;
  };
  for (const p of plan) {
    const x = p.x, d = p.d, si = sim.indexOf(p);
    if (d && d.k === 'have') { skip++; continue; }
    if (d && d.k === 'back') { const it = d.it, c = Object.assign({}, it, { del: false, u: t }); out.set(it.id, { c, fin: () => { it.del = false; it.u = t; } }); add++; continue; }   /* 뺐던 문제 = 다시 넣기(스토리 그대로) */
    if (d && (d.k === 'same' || (d.k === 'sim' && simMerge.has(si)))) { const tg = d.it._plan ? made.get(d.it) : d.it; if (tg && linkTo(tg, x)) link++; else skip++; continue; }
    const it = { id: (x.t === 'jb' ? 'jb:' : 'pr:') + x.id, s: sj, kind: x.t, lec: x.lec, q: x.q, a: x.a, st: '', note: x.note || '', tags: [], yrs: x.yrs.slice(), src: [srcOf(x)], ref: { t: x.t, s: x.s, id: x.id }, done: false, o: o++, c: t, u: t, del: false, rv: [], rvok: false, prev: null, _new: 1 };
    if (p.ni) made.set(p.ni, it);
    out.set(it.id, { c: it, fin: () => { delete it._new; if (live && !S.by.has(it.id)) { S.items.push(it); S.by.set(it.id, it); } } }); add++;
  }
  try {
    for (const [id, e] of out) { const k = keyI(sj, id); if (!before.has(k)) before.set(k, localStorage.getItem(H.NS + k)); const r = toRec(e.c); delete r._new; localStorage.setItem(H.NS + k, JSON.stringify(r)); if (H.LSQ) H.LSQ.delete(k); }
  } catch (e) {
    for (const [k, v] of before) { try { if (v == null) localStorage.removeItem(H.NS + k); else localStorage.setItem(H.NS + k, v); } catch (_) {} }
    return { err: e && (e.name === 'QuotaExceededError' || e.code === 22) ? '이 기기 저장 공간이 부족해요' : String(e && e.message || e) };
  }
  for (const e of out.values()) e.fin();
  if (live && S.root && document.getElementById('numv')) render({ pos: topItem() });
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
    const t = now(), before = new Map(), subjBefore = localStorage.getItem(H.NS + 'num.subj');
    try {
      if (sj === '__new') { const L = H.LS.get('num.subj', []) || []; sj = 'U' + t.toString(36).toUpperCase(); L.push({ id: sj, t: title.slice(0, 40) }); localStorage.setItem(H.NS + 'num.subj', JSON.stringify(L)); }
      const target = await itemsOfSubject(sj), pool = target.filter(it => !it.del), x = JSON.parse(JSON.stringify(idx(sj))); x.ul = x.ul || []; const lmap = {};
      const exist = lectures(sj, (window.JBLNUM_SEED || {})[sj]);
      for (const s of secs) { const nm = names[s.k]; const hit = exist.find(l => l.t === nm) || x.ul.find(l => l.t === nm); if (hit) lmap[s.k] = hit.k; else { const k = 'U' + t.toString(36) + s.k; x.ul.push({ k, t: nm }); lmap[s.k] = k; } }
      let o = target.reduce((m, it) => Math.max(m, it.o || 0), -1) + 1, add = 0, link = 0; const recs = new Map();   /* id → 쓸 기록(기존 문제는 사본에) */
      const kq = it => it._k != null ? it._k : (it._k = qKey(it.q));
      for (const y of pick) {
        const q = sanitize(y.q), a = sanitize(sw ? y.st : y.a), st = sanitize(sw ? y.a : y.st), key = qKey(q), okKey = key.length >= 8 && !/미복원|복원불충분/.test(key);
        const aKey = norm(plain(a)), same0 = okKey && pool.find(it => kq(it) === key && norm(plain(it.a)) === aKey), qOnly = !same0 && okKey && pool.find(it => kq(it) === key);   /* 문제·답이 모두 같을 때만 출처 연결 — 문제만 같고 답이 다르면 따로 넣고 검토 표시 */
        const src = { t: 'word', s: sj, lab: 'Word: ' + fname.replace(/\.docx$/i, '') + (y.lab ? ' · ' + y.lab : ''), yrs: y.yrs };
        if (same0) {
          const c = recs.get(same0.id) ? recs.get(same0.id).it : Object.assign({}, same0, { src: same0.src.map(z => Object.assign({}, z)), yrs: same0.yrs.slice() });
          if (!c.src.some(s2 => s2.t === 'word' && s2.lab === src.lab)) { c.src.push(src); c.yrs = [...new Set(c.yrs.concat(y.yrs))].sort((p1, p2) => p2 - p1); c.u = t; recs.set(c.id, { it: c, orig: same0 }); link++; }
          continue;
        }
        const it = { id: 'w:' + t.toString(36) + ':' + y.i, s: sj, kind: 'word', lec: lmap[y.lec] || '', q, a, st, note: y.note || '', tags: y.tags || [], yrs: y.yrs || [], src: [src], ref: null, done: false, o: o++, c: t, u: t, del: false, rv: (y.rv || []).concat(qOnly ? [{ k: 'qsame', m: '문제 글이 같은 문제가 이미 있지만 답이 달라 따로 넣음 — 같은 문제면 \'여러 개 선택 → 합치기\'' }] : []), rvok: false, prev: null };
        recs.set(it.id, { it }); pool.push(it); add++;
      }
      for (const [id, r] of recs) { const k = keyI(sj, id); if (!before.has(k)) before.set(k, localStorage.getItem(H.NS + k)); localStorage.setItem(H.NS + k, JSON.stringify(toRec(r.it))); if (H.LSQ) H.LSQ.delete(k); }
      const xk = 'num.x.' + sj; before.set(xk, localStorage.getItem(H.NS + xk)); x.u = now(); localStorage.setItem(H.NS + xk, JSON.stringify(x));
      dlgClose(); H.toast(`가져왔어요 — 새 문제 ${add}${link ? ' · 같은 문제 출처 연결 ' + link : ''}`, { level: 'result' });
      await switchSubject(sj, { force: sj === S.sj });
    } catch (e) {   /* 이번에 쓴 키는 쓰기 전 값으로 되돌림(기존 문제는 그대로) */
      for (const [k, v] of before) { try { if (v == null) localStorage.removeItem(H.NS + k); else localStorage.setItem(H.NS + k, v); } catch (_) {} }
      try { if (subjBefore == null) localStorage.removeItem(H.NS + 'num.subj'); else localStorage.setItem(H.NS + 'num.subj', subjBefore); } catch (_) {}
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
  if (k === 'del') { ask(L.length + '개 문제를 목록에서 뺄까요?\n(원본은 그대로 · 맨 아래 \'목록에서 뺀 문제\'에서 다시 넣을 수 있어요)', { ok: '빼기' }).then(y => { if (!y) return; L.forEach(it => { it.del = true; touch(it); put(it); }); S.sel.clear(); render({ pos: topItem() }); }); return; }
  if (k === 'move') { lecPick(btn, l => { L.forEach(it => { it.lec = l; touch(it); put(it); }); render({ pos: topItem() }); H.toast(L.length + '개를 옮겼어요'); }); return; }
  if (k === 'merge') {
    const tgt = L.slice().sort((a, b) => a.o - b.o)[0], rest = L.filter(x => x !== tgt);
    const withSt = L.filter(x => !isEmpty(x.st)); if (withSt.length > 1) { ask('스토리가 있는 문제가 ' + withSt.length + '개라 합칠 수 없어요 — 한 문제에는 스토리 하나만 둬요.\n하나만 남기고 다시 해 주세요.', { only: true, ok: '알겠어요' }); return; }
    ask(`${L.length}개를 첫 문제(${plain(tgt.q).slice(0, 40)}…) 하나로 합칠까요?\n출처·연도·태그를 모으고, 나머지는 목록에서 빼요(원본은 그대로).`, { ok: '합치기' }).then(y => { if (!y) return;
    rest.forEach(x => { x.src.forEach(s => { if (!tgt.src.some(z => z.t === s.t && z.id === s.id && z.lab === s.lab)) tgt.src.push(s); }); tgt.yrs = [...new Set(tgt.yrs.concat(x.yrs))].sort((a, b) => b - a); tgt.tags = [...new Set((tgt.tags || []).concat(x.tags || []))]; if (isEmpty(tgt.st) && !isEmpty(x.st)) tgt.st = x.st; x.del = true; touch(x); put(x); });
    touch(tgt); put(tgt); S.sel.clear(); render({ flash: tgt.id }); }); return;
  }
}

/* ---------- 열기·과목 바꾸기 ---------- */
async function switchSubject(sj, o) {
  o = o || {};
  if (!S.root || !document.getElementById('numv')) { location.hash = '#/_num/' + sj; return; }   /* 넘버링 화면을 떠난 뒤(알림의 '보기') = 그 과목으로 다시 열기 */
  endEdit(true); const tok = S.swTok = (S.swTok || 0) + 1, R0 = S.root;
  if (S.sj && S.sj !== sj) H.LS.set('num.pos.' + S.sj, topItem());
  S.sj = sj; S.cfg.sj = sj; if (!o.keepF && !o.force) S.cfg.f.lec = ''; cfgSave(); S.sel.clear(); S.curLec = null; S.fp = false; S.vo = false; if (S.drawer) drawer(false);
  const V = frame(); $('.nm-main', V).innerHTML = '<div class="nm-prog">넘버링 불러오는 중…</div>';
  await loadSubject(sj);
  if (tok !== S.swTok || S.root !== R0 || !S.root) return;   /* 기다리는 사이 다른 과목·화면으로 옮겼으면 그만 */
  if (S.cfg.f.lec && !S.lecs.some(l => l.k === S.cfg.f.lec) && S.cfg.f.lec !== '__none') S.cfg.f.lec = '';
  S.sjc = sjCounts();
  H.histSet({ num: 1, sj }, '#/_num/' + sj, false);
  render({ pos: o.flash ? null : (o.pos || H.LS.get('num.pos.' + sj, null)), flash: o.flash });
}
function newSubject() { ask('새 과목 이름', { input: '', ph: '예: 교정학 2', ok: '만들기' }).then(t => { if (!t || !t.trim()) return; const L = H.LS.get('num.subj', []) || []; const id = 'U' + now().toString(36).toUpperCase(); L.push({ id, t: t.trim() }); H.LS.set('num.subj', L); switchSubject(id); }); }
function lecMenu(btn) {   /* 사이드바를 접었을 때 위 막대의 '과목 › 강의'를 누르면 — 강의 바로 가기 */
  const n = lecCounts(), L = S.lecs.filter(l => n[l.k]).map(l => [l.k, l.t + ' (' + n[l.k] + ')']);
  if (!L.length) { H.toast('아직 이 과목에 문제가 없어요'); return; }
  const m = menuOpen(btn, L); if (!m) return; m.style.left = Math.max(0, btn.getBoundingClientRect().left - document.getElementById('numv').getBoundingClientRect().left) + 'px';
  m.addEventListener('click', e => { const b = e.target.closest('[data-mi]'); if (!b) return; menuClose(); jumpLec(b.dataset.mi); });
}
let bound = false;
function bind() {
  if (bound) return; bound = true;
  document.addEventListener('click', e => {
    if (!S.root || !S.root.isConnected || !document.getElementById('numv')) return;
    const t = e.target; if (!t.closest) return;
    if (!t.closest('.nm-menu') && !t.closest('[data-act=more]') && !t.closest('[data-act=ctx]') && !t.closest('[data-mi]')) menuClose();
    if (!t.closest('.nm-pal') && !t.closest('[data-pal]')) palClose();
    if (S.fp && !t.closest('[data-fpan]') && !t.closest('[data-act=flt]') && S.root.contains(t) && !t.closest('.nm-ov')) fpOpen(false);
    if (S.vo && !t.closest('.nm-vopt') && !t.closest('[data-act=vopt]')) voOpen(false);
    if (!S.root.contains(t)) return;
    if (t.closest('.nm-ov') || t.closest('.nm-tb') || t.closest('.nm-pal')) return;   /* 대화창·도구 막대는 따로 */
    const sa = t.closest('[data-sact]'); if (sa) { const k = sa.dataset.sact; if (k === 'home') { const g = document.getElementById('gohome'); if (g) g.click(); else location.hash = '#/'; } else if (k === 'fold') side(); else if (k === 'close') drawer(false); return; }
    const sj = t.closest('[data-sj]'); if (sj) { const id = sj.dataset.sj; S.sjOpen = false; if (id === '__new') newSubject(); else if (id !== S.sj) switchSubject(id); else { const d = t.closest('details'); if (d) d.open = false; if (S.drawer) drawer(false); } return; }
    if (t.closest('.nm-sjd > summary')) { setTimeout(() => { const d = $('.nm-sjd', S.root); S.sjOpen = !!(d && d.open); }, 0); return; }
    const lj = t.closest('[data-lj]'); if (lj) { jumpLec(lj.dataset.lj); return; }
    const fx = t.closest('[data-fx]'); if (fx) { fClear(fx.dataset.fx); return; }
    const md = t.closest('[data-mode]'); if (md) { S.cfg.mode = md.dataset.mode; cfgSave(); render({ pos: topItem() }); return; }
    const hd = t.closest('[data-hide]'); if (hd) { const k = hd.dataset.hide; S.cfg.hide[k] = !S.cfg.hide[k]; cfgSave(); $$('.nm-it.revA,.nm-it.revS', S.root).forEach(a => a.classList.remove('revA', 'revS')); const V = document.getElementById('numv'); V.classList.toggle('hideA', !!S.cfg.hide.a); V.classList.toggle('hideS', !!S.cfg.hide.st); $$('[data-hide]', S.root).forEach(b => { const on = !!S.cfg.hide[b.dataset.hide]; b.classList.toggle('on', on); b.setAttribute('aria-pressed', String(on)); }); return; }
    { const hc = t.closest('.nm-a .nm-c, .nm-s .nm-c'), art = hc && hc.closest('.nm-it'), isA = hc && !!hc.closest('.nm-a');   /* 가린 칸을 누르면 그 문제 그 칸만 보임(편집은 한 번 더 누를 때) */
      if (art && (isA ? S.cfg.hide.a && !art.classList.contains('revA') : S.cfg.hide.st && !art.classList.contains('revS'))) { art.classList.add(isA ? 'revA' : 'revS'); return; } }
    const sf = t.closest('[data-stf]'); if (sf) { S.cfg.f.st = sf.dataset.stf; cfgSave(); applyFilter(); return; }
    const bt = t.closest('[data-bat]'); if (bt) { batch(bt.dataset.bat, bt); return; }
    const a = t.closest('[data-act]');
    if (a) {
      const k = a.dataset.act, art = a.closest('.nm-it'), it = art && S.by.get(art.dataset.id);
      if (k === 'more' && it) { itemMenu(a, it); return; }
      if (k === 'det' && it) { detOpen(it); return; }
      if (k === 'edit' && it) { const el = art.querySelector(`.nm-c[data-f="${a.dataset.f}"]`); if (el) startEdit(el, it, a.dataset.f); return; }
      if (k === 'flt') { fpOpen(!S.fp); return; }
      if (k === 'vopt') { voOpen(!S.vo); return; }
      if (k === 'fclr') { fClear(); return; }
      if (k === 'ctx') { if (innerWidth <= 860) drawer(true); else lecMenu(a); return; }
      if (S.drawer && (k === 'new' || k === 'imp' || k === 'file')) drawer(false);
      if (k === 'new') { newForm(); return; }
      if (k === 'imp') { importDlg(); return; }
      if (k === 'file') { fileImport(); return; }
      if (k === 'selm') { S.selMode = !S.selMode; S.vo = false; if (!S.selMode) S.sel.clear(); render({ pos: topItem() }); return; }
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
    if (c === 'sort') { S.cfg.sort = e.target.value; cfgSave(); render({ pos: topItem() }); return; }
    S.cfg.f[c] = e.target.value; cfgSave(); applyFilter();
    if (c === 'lec' && S.cfg.f.lec) { const d = $('[data-doc]', S.root); if (d) window.scrollTo(0, Math.max(0, d.getBoundingClientRect().top + scrollY - stuckBottom() - 8)); }
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
  document.addEventListener('keydown', e => {
    if (!S.root || !document.getElementById('numv')) return;
    if (!S.ed) { if (e.key === 'Escape' && !$('.nm-ov') && (S.fp || S.vo || S.drawer || $('.nm-menu'))) { e.preventDefault(); e.stopPropagation(); menuClose(); if (S.fp) fpOpen(false); if (S.vo) voOpen(false); if (S.drawer) drawer(false); } return; }
    if (e.key === 'Escape') { e.preventDefault(); e.stopPropagation(); endEdit(); return; } const mod = e.metaKey || e.ctrlKey; if (mod && e.shiftKey && (e.key === 'x' || e.key === 'X' || e.key === '5')) { e.preventDefault(); }
  }, true);
  addEventListener('scroll', () => { if (!spyT && S.root) spyT = setTimeout(spy, 120); }, { passive: true });
  addEventListener('resize', () => { if (S.drawer && innerWidth > 860) drawer(false); });
  addEventListener('pagehide', flush); document.addEventListener('visibilitychange', () => { if (document.hidden) flush(); });
  addEventListener('storage', e => {   /* 다른 창에서 고친 문제 — 모았다가 한 번에(고치는 중인 문제는 건드리지 않음) */
    if (!S.root || !document.getElementById('numv') || !e.key || e.key.indexOf(H.NS + 'num.i.' + S.sj + '.') !== 0) return;
    SQ.add(e.key.slice((H.NS + 'num.i.' + S.sj + '.').length)); clearTimeout(sqT); sqT = setTimeout(syncOther, 400);
  });
}
const SQ = new Set(); let sqT = 0;
function syncOther() {
  const ids = [...SQ]; SQ.clear(); if (!S.root || !document.getElementById('numv')) return;
  let added = false; const re = [];
  for (const id of ids) {
    if (S.ed && S.ed.it.id === id) { H.toast('다른 창에서 지금 고치는 문제를 바꿨어요 — 편집을 끝낸 뒤 새로고침하면 그 글이 보여요', { level: 'result', id: 'nmother' }); continue; }
    let r = null; try { const v = localStorage.getItem(H.NS + keyI(S.sj, id)); r = v ? JSON.parse(v) : null; } catch (_) {}
    const it = S.by.get(id);
    if (it && it.kind === 'seed') { Object.assign(it, mkSeed(S.sj, it.base, r, it.oi, S.seed), { _t: null, _ty: null, _k: null, _qd: null }); re.push(it); }
    else if (r) { const n = mkRec(S.sj, r); if (it) { Object.assign(it, n, { _t: null, _ty: null, _k: null, _qd: null }); re.push(it); } else { S.items.push(n); S.by.set(n.id, n); added = true; } }
  }
  if (added || re.length > 20) { if (!S.ed) render({ pos: topItem() }); return; }
  re.forEach(rerenderItem); applyFilter();
}
function flush() { if (S.ed) edSave(); }
function leave() { if (!S.root) return; try { endEdit(true); formEnd(); if (S.sj && document.getElementById('numv')) H.LS.set('num.pos.' + S.sj, topItem()); } catch (e) {} menuClose(); dlgClose(); palClose(); tbWatch(false); S.fp = false; S.vo = false; S.drawer = false; document.body.classList.remove('v-num'); S.root = null; }
async function open(root, o, host) {
  H = host; css(); bind(); cfg(); S.root = root; document.body.classList.add('v-num');
  S.drawer = false; S.fp = false; S.vo = false; S.curLec = null;
  root.innerHTML = ''; frame(); $('.nm-main', root).innerHTML = '<div class="nm-prog">넘버링 불러오는 중…</div>';
  await index();
  const subs = subjects(), has = new Set(); for (let i = 0; i < localStorage.length; i++) { const k = localStorage.key(i), m = k && /^jblhub\.v1\.num\.i\.([^.]+)\./.exec(k); if (m) has.add(m[1]); }
  let sj = o.sj && subs.some(s => s.id === o.sj) ? o.sj : (S.cfg.sj && subs.some(s => s.id === S.cfg.sj) ? S.cfg.sj : (subs.find(s => has.has(s.id)) || subs.find(s => s.seed) || subs[0]).id);   /* 주소 → 마지막 과목 → 문제가 있는 과목 → 첫 과목 */
  if (S.root !== root) return;
  S.sj = sj; S.cfg.sj = sj; cfgSave();
  await loadSubject(sj);
  if (S.root !== root) return;
  if (S.cfg.f.lec && !S.lecs.some(l => l.k === S.cfg.f.lec) && S.cfg.f.lec !== '__none') S.cfg.f.lec = '';
  S.sjc = sjCounts();
  H.histSet({ num: 1, sj }, '#/_num/' + sj, !!o.push);
  render({ pos: o.y != null ? null : H.LS.get('num.pos.' + sj, null), y: o.y });
}
window.JBLNUM = { open, leave, flush, side, state: () => ({ num: 1, sj: S.sj }), _S: S, _H: () => H, _qType: qType, _sanitize: sanitize, _plain: plain, _qKey: qKey, _qDisp: qDisp };
})();
