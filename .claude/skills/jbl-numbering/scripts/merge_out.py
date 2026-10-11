"""여러 세션의 결과 JSON(nb export)을 JBL '결과 가져오기' 파일 하나로 합친다(강의 순서 = 첫 파일이 아니라 --order 원본 순).
같은 id가 두 번 나오면 멈춤 · sid가 다르면 멈춤. 각 파일은 미리 nb verify를 통과한 것.
쓰기: .venv/bin/python -I .claude/skills/jbl-numbering/scripts/merge_out.py a.json b.json … --out 합본.json [--order 원본.json]"""
import argparse, json, sys


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('files', nargs='+'); ap.add_argument('--out', required=True); ap.add_argument('--order')
    a = ap.parse_args(); base = None; byid = {}; lec_of = {}
    for f in a.files:
        d = json.load(open(f, encoding='utf-8'))
        if d.get('format') != 'jbl-numbering': sys.exit(f'형식 아님: {f}')
        if base is None: base = d
        if d['sid'] != base['sid']: sys.exit(f"과목이 다름: {f} ({d['sid']} ≠ {base['sid']})")
        for g in d['lecs']:
            for it in g['items']:
                if it['id'] in byid: sys.exit(f"같은 문제가 두 번: {it['id']} ({f})")
                byid[it['id']] = it; lec_of[it['id']] = g['lec']
    order = []
    if a.order:
        src = json.load(open(a.order, encoding='utf-8'))
        order = [(g['lec'], it['id']) for g in src['lecs'] for it in g['items'] if it['id'] in byid]
    seen = {i for _, i in order}; order += [(lec_of[i], i) for i in byid if i not in seen]
    lecs = []
    for lec, i in order:
        if not lecs or lecs[-1]['lec'] != lec: lecs.append({'lec': lec, 'items': []})
        lecs[-1]['items'].append(byid[i])
    o = {k: base[k] for k in ('format', 'v', 'sid', 'subject', 'batch') if k in base}
    o.update(part='1/1', n=len(byid), made_by='claude:jbl-numbering', note=f'세션 {len(a.files)}개 합본 · 검수 통과 스토리만', lecs=lecs)
    json.dump(o, open(a.out, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print(f'{a.out} · 문제 {len(byid)} · 강의 {len({g["lec"] for g in lecs})}')


if __name__ == '__main__':
    main()
