import re, html, os
import emph
CITE = re.compile(r'(\[\[[A-Z0-9]+:[^\]]+\]\]|\{jb:[^}]+\})')
def inline(s, ctx):
    out = []
    for tok in CITE.split(s):
        if tok.startswith('[['):
            k, p = tok[2:-2].split(':', 1)
            if k == 'DD3': out.append(f'<button class="cite t" data-k="DD3" data-p="">{ctx["LECNAME"][k]} ‘{html.escape(p)}’</button>')
            else:
                if p.isdigit(): ctx['cited'].add((k, int(p)))
                out.append(f'<button class="cite" data-k="{k}" data-p="{p}">{ctx["LECNAME"][k]} p.{p}</button>')
        elif tok.startswith('{jb:'):
            i = tok[4:-1]; q = ctx['QMAP'].get(i)
            if q: out.append(f'<button class="xjb{" rep" if len(q["yrs"]) >= 2 else ""}" data-go="{i}" title="{html.escape(q["short"])}">기출 {"·".join("%02d" % y for y in q["yrs"])}</button>')
        else:
            t = emph.apply(html.escape(tok, quote=False), phrases=False, numbers=False)
            t = re.sub(r'\*\*(.+?)\*\*', r'<b class="term">\1</b>', t)
            t = re.sub(r'==(.+?)==', r'<span class="hl">\1</span>', t)
            t = re.sub(r'\{k:([^{}]+)\}', r'<span class="hk">\1</span>', t)
            t = t.replace('💡', '<b class="bulb">💡</b>').replace('⚠', '<b class="warn">⚠</b>')
            out.append(t)
    return ''.join(out)
def parse(path):
    lec = None; card = None; grp = ''
    for raw in open(path, encoding='utf-8'):
        line = raw.rstrip('\n')
        if not line.strip(): continue
        if line.startswith('#LEC'):
            p = [x.strip() for x in line[4:].split('|')]
            lec = {'k': p[0], 'title': p[1], 'prof': p[2], 'yr': p[3], 'file': p[4], 'pages': int(p[5]), 'notes': [], 'cards': [], 'map': ''}
        elif line.startswith('@MAP'): lec['map'] = line[4:].strip()
        elif line.startswith('@G'): grp = line[2:].strip()
        elif line.startswith('!'): lec['notes'].append(line[1:].strip())
        elif line.startswith('## '):
            p = [x.strip() for x in line[3:].split('|')]; jb = []; tag = ''
            for x in p[3:]:
                if x.startswith('jb='): jb = [j.strip() for j in x[3:].split(',') if j.strip()]
                else: tag = x
            card = {'en': p[0], 'ko': p[1], 'rng': p[2], 'tag': tag, 'jb': jb, 'gist': '', 'body': [], 'figs': [], 'grp': grp, 'recall': []}
            lec['cards'].append(card)
        elif line.startswith('> '): card['gist'] = line[2:].strip()
        elif line.startswith('= '): card['body'].append(('K', line[2:].strip()))
        elif line.startswith('# '): card['body'].append(('h', line[2:].strip()))
        elif line.startswith('|'):
            row = [c.strip() for c in line.strip().strip('|').split('|')]
            if card['body'] and card['body'][-1][0] == 'T': card['body'][-1][1].append(row)
            else: card['body'].append(('T', [row]))
        elif line.startswith('F:'):
            fl = []
            for part in line[2:].split(','):
                part = part.strip()
                if not part: continue
                pg, _, cap = part.partition('=')
                fl.append((int(re.findall(r'\d+', pg)[0]), cap.strip()))
            card['figs'] += [p_ for p_, _ in fl]; card['body'].append(('F', fl))
        elif line.startswith('E:'):
            ids, _, txt = line[2:].partition('|'); card['body'].append(('E', ([i.strip() for i in ids.split(',') if i.strip()], txt.strip())))
        elif line.startswith('M:'): card['recall'].append(line[2:].strip())
        elif line[:2] in ('P:', 'U:'): card['body'].append((line[0], line[2:].strip()))
        elif line.startswith('- '): card['body'].append(('b', line[2:].strip()))
        else: raise ValueError(f'{path}: unknown line: ' + line[:60])
    return lec
HERE = os.path.dirname(os.path.abspath(__file__))
ORDER = ['DD1', 'DD2', 'DD3', 'DX', 'EXT', 'LOAD', 'REP']
def load_all():
    return [parse(os.path.join(HERE, f'lec_{k}.txt')) for k in ORDER if os.path.exists(os.path.join(HERE, f'lec_{k}.txt'))]
if __name__ == '__main__':
    for L in load_all():
        print(L['k'], 'cards', len(L['cards']), 'items', sum(1 for c in L['cards'] for b in c['body'] if b[0] == 'b'), 'tables', sum(1 for c in L['cards'] for b in c['body'] if b[0] == 'T'),
              'exam', sum(1 for c in L['cards'] for b in c['body'] if b[0] == 'E'), 'recall', sum(len(c['recall']) for c in L['cards']), 'figs', sum(len(c['figs']) for c in L['cards']))
