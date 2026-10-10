"""넘버링 기본 자료 검사 — Word 원문 글자가 빠짐없이 들어갔는지(그리고 Word에 없는 글이 생기지 않았는지) Word XML을 따로 읽어 대조 (10-10)
  .venv/bin/python -I tools/num/check_seed.py      # 실패하면 종료 코드 1
· 원문 문단(띄어쓰기 무시)마다 seed의 문제·답·스토리·참고 글 어딘가에 그대로 있어야 함(교정과의 '문제 줄' 오른쪽 사본처럼 같은 글이 두 번인 것은 한 번만 있으면 됨)
· seed 문단마다(앞의 번호 목록 번호를 빼고) 원문 어딘가에 있어야 함
· 그림 수: 원문 그림 참조 수 = seed <img> 수(문제 줄 오른쪽 사본에 든 그림은 빼고 셈)"""
import os, sys, re, json, zipfile, html as H
import xml.etree.ElementTree as ET
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import jblpaths as J
W = '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'
N = lambda s: re.sub(r'[\s ]+', '', s or '')
def seed(sid):
    t = open(os.path.join(J.DOCS, 'num', f'seed.{sid}.js'), encoding='utf-8').read()
    return json.loads(t[t.index(']=') + 2:t.rstrip().rstrip(';').rindex('}') + 1])
def paras(h):
    return [H.unescape(re.sub(r'<[^>]+>', '', x)) for x in re.findall(r'<p[^>]*>(.*?)</p>', h or '', re.S)]
def main():
    src = json.load(open(os.path.join(J.TOOLS, 'num', 'seed_src.json'), encoding='utf-8')); bad = 0
    for S in src:
        sid = S['id']; D = seed(sid)
        z = zipfile.ZipFile(os.path.join(J.ROOT, S['file'])); doc = ET.fromstring(z.read('word/document.xml'))
        allp = []
        for p in doc.iter(W + 'p'):
            t = ''.join(x.text or '' for x in p.iter(W + 't'))
            if t.strip(): allp.append(t)
        sp = []; nimg = 0
        for it in D['items']:
            for k in ('q', 'a', 'st'): sp += paras(it[k]); nimg += len(re.findall(r'<img ', it[k]))
            if it.get('note'): sp += [x for x in it['note'].split(' / ')]
        heads = [l['raw'] for l in D['lecs']] + [D['meta']['src']] + list(D['meta']['legend'].values())
        blob = N(''.join(sp) + ''.join(heads)); docblob = N(''.join(allp))
        miss = [p for p in allp if N(p) and N(p) not in blob and N(p) not in ('문제', '정답', '암기법')]
        # 원문에 없는 글: 번호 목록 번호(앞머리 '1.'·'1)'·'-'·'•') 빼고
        extra = []
        for p in sp:
            q = re.sub(r'^\s*(?:\d{1,2}[.)]|[a-z][.)]|[-•▪◦➢✓■□]|[①-⑳])\s', '', p)
            if N(q) and N(q) not in docblob and N(p) not in docblob: extra.append(p)
        # 그림: 원문에서 쓰인 그림 파일(mc:Fallback 대체 그림 빼고)의 내용 가짓수 = seed가 가리키는 그림 파일 가짓수
        rels = {r.get('Id'): r.get('Target') for r in ET.fromstring(z.read('word/_rels/document.xml.rels'))}
        fbk = set(x for f in doc.iter('{http://schemas.openxmlformats.org/markup-compatibility/2006}Fallback') for x in f.iter())
        dimg = set()
        for b in doc.iter('{http://schemas.openxmlformats.org/drawingml/2006/main}blip'):
            if b in fbk: continue
            t = rels.get(b.get('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}embed'))
            if t: dimg.add(hash(z.read('word/' + t.lstrip('/').replace('word/', '', 1))))
        simg = set(m for it in D['items'] for k in ('q', 'a', 'st') for m in re.findall(r'data-nimg="([^"]+)"', it[k]))
        if len(dimg) != len(simg): print(f'   그림 가짓수 다름: 원문 {len(dimg)} · seed {len(simg)}'); bad += 1
        print(f'{sid}: 원문 문단 {len(allp)} · seed 문단 {len(sp)} · 빠진 원문 {len(miss)} · 원문에 없는 글 {len(extra)} · seed 그림 {nimg}(가짓수 {len(simg)} = 원문 {len(dimg)})')
        for m in miss[:10]: print('   빠짐:', m[:120])
        for m in extra[:10]: print('   없는 글:', m[:120])
        bad += len(miss) + len(extra)
    print('RESULT', 'PASS' if not bad else f'FAIL {bad}')
    return not bad
if __name__ == '__main__':
    sys.exit(0 if main() else 1)
