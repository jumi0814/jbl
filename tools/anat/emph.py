import re
# HUB의 isRed 판정(r>=110, g<=95, b<=95)을 만족하는 색을 CSS에서 .k 에 지정 → HUB '자동 빈칸(빨간 글씨)'이 그대로 동작
PHRASES = [
 # DD I
 'WR Proffit', 'Congenital deformities', 'Developmental origin', 'Trauma', 'Tumors', 'Paul Tessier',
 'Intrinsic bone malformation', 'Fetal head constraint', 'Intrinsic brain malformation', 'Multifactorial',
 'Developmental delay', 'Increased ICP', 'Restriction of cerebral growth', 'Visual impairments', 'Psychosocial issue',
 'Growth disturbance', 'Abnormal function', 'Distorted appearance', 'trigonocephaly', 'scaphocephaly', 'brachycephaly',
 'Scaphocephaly', 'Trigonocephaly', 'Hypertelorism', 'Hypotelorism', 'Epicanthal folds', 'Frontal bossing', 'strip craniectomy',
 'Frontal plagiocephaly', 'Posterior plagiocephaly', 'floating forehead', 'Prevention is the best treatment',
 'Ventriculoperitoneal shunting', 'beaten copper', 'Papilledema', 'TWIST1', 'TWIST, MSX2', 'RAB23', 'TCOF1', 'Autosomal recessive',
 'FGFR3 P250R', 'FGFR2 signaling pathway mutation', 'Cutis gyrate', 'cloverleaf skull', 'Cloverleaf skull',
 'Acrocephalosyndactyly type I', 'mandibulofacial dysostosis', 'down slanting', 'Class II malocclusion', 'Steep maxillary occlusal plane',
 'Macrostomia (Tessier #7 cleft)', 'Goldenhar-Gorlin syndrome', 'Kaban class IIB or III', 'Sporadic',
 'Allow deformation during descent through vaginal canal', 'Accommodate head expansion',
 # DD II
 'Trichion', 'Glabella', 'Subnasale', 'Gnathion', 'Tr-G-Sn-Gn', 'Stomion', 'rete pegs', 'primary determinant', 'Dermal elastosis',
 'Delayed healing', 'tear trough', 'gold standard', 'Jaws in CR', 'Lips relaxed', 'Teeth in lightly touching', 'FH plane parallel to the floor',
 'Cone beam technology', 'Transcranial', 'Prediction tracing', 'normal facial appearance', 'only an aid', 'Not be used as a sole diagnostic tool',
 'CO-CR', 'Tooth wear', 'Parafunctional habit', 'Postoperative stability', 'Le Fort I level',
 # DD III
 'intermediate splint', 'steep', 'N-perp', 'condylar positioning device', 'Real time navigation', 'Cost efficient', 'Easy planning',
 # DX
 '티타늄', '지르코니아', '나사형', '절대적 금기증', '상대적 금기증', '혈소판감소성자반병', '조기 발치', '협설 X', '상이 겹쳐짐',
 '대합치 정출', '변연골 소실', '연결 나사 풀림', '전치부와 구치부 분리', '이공 사이', 'All-on-4', 'top-down treatment concept',
 '각화치은', 'Flapless', '감염의 가능성', '치료기간 단축',
 # EXT
 'Tooth-dependent structure', 'buccal > lingual', 'loss in width > height', 'Class 3 관계', 'Socket preservation', 'Space maintenance',
 'Osteogenic materials', 'DFDBA', 'Bovine', 'Hydroxyapatite', 'cross-linked', 'Atraumatic extraction', 'overfilling', 'Membrane으로 상방 커버',
 'thick wall phenotype', 'Thick gingival biotype', 'tension-free primary closure',
 # LOAD
 '치근막', '치조정에 집중', '층판골', '즉시부하', '조기 부하', '전통 부하', 'Non-submerged', 'cross-arch splinting', 'A-P spread',
 'osseodensification', 'self-tapping implant', 'axial load',
 # REP
 '탈구치아재식술', '의도적 발치 후 재식술', '치아 자가이식술', '이인자형 치아이식술', 'tetracycline', '기능력에 의한 자극', '환자의 연령',
 '치주인대와 백악질', '치근 2/3', 'PDL 재부착', 'MTA',
]
PHRASES = sorted(set(PHRASES), key=len, reverse=True)
NUM = re.compile(
 r'(?<![\w.#/])(?:\d+(?:\.\d+)?\s?±\s?\d+(?:\.\d+)?\s?(?:°|mm|도)?'
 r'|(?:\d+(?:\.\d+)?-)?1\s?[/:]\s?\d{1,3}(?:,\d{3})+(?:-\d{1,3}(?:,\d{3})+)?|1/\d{3,5}'
 r'|(?:\d{1,3}(?:,\d{3})+|\d+(?:\.\d+)?)(?:\s?[-~–]\s?\d+(?:\.\d+)?)?\s?(?:%|mm|Ms\b|months?\b|weeks?\b|years?\b|주|개월|세\b|도\b|°|Ncm|N/cm2|μm|rads|ys\b|YO\b|Y\b))')
def apply(t, phrases=True, numbers=True):
    # 1) 수동 표기 {r:...}
    marks = []
    def keep(m):
        marks.append('<span class="k">' + m.group(1) + '</span>'); return '\x00%d\x00' % (len(marks) - 1)
    t = re.sub(r'\{r:([^{}]+)\}', keep, t)
    # 2) 핵심어 사전 (한 줄에서 구절당 첫 1회)
    for ph in (PHRASES if phrases else []):
        e = re.escape(ph)
        m = re.search(r'(?<![\w가-힣])' + e if re.match(r'\w', ph) else e, t)
        if m and '\x00' not in t[max(0, m.start() - 1):m.end() + 1]:
            marks.append('<span class="k">' + m.group(0) + '</span>')
            t = t[:m.start()] + '\x00%d\x00' % (len(marks) - 1) + t[m.end():]
    # 3) 수치 + 단위
    def num(m):
        marks.append('<span class="k">' + m.group(0) + '</span>'); return '\x00%d\x00' % (len(marks) - 1)
    if numbers: t = NUM.sub(num, t)
    # 4) "p.N" 쪽 표기는 흐리게
    t = re.sub(r'(?<![\w])(p\.\d+(?:[~\-–,]\s?\d+)*)', r'<span class="pg">\1</span>', t)
    return re.sub(r'\x00(\d+)\x00', lambda m: marks[int(m.group(1))], t)
if __name__ == '__main__':
    for s in ['p.8 Fontanel closure — Anterior: 9-12 Ms · Posterior: 3-6 Ms. 1/2000 live births, 85% of craniosynostosis',
              'Maxillary depth 90 ±3 / Occlusal plane 8 ±4° / {r:steep} mounting, 1:150,000, 0.8-1/10,000, 5000 rads, 2-5 Y, M 18 ys']:
        print(apply(s))
