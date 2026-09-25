import os as _os, sys as _sys; _sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))); import jblpaths as J  # tools/localize.py
import subprocess,os,pymupdf,sys,time
_os.chdir(J.work('IMPL'))   # 강의 PDF·OCR 결과는 work/IMPL/, tesseract는 Homebrew 기본 tessdata
T0=time.time(); BUD=float(sys.argv[1]) if len(sys.argv)>1 else 250
for k in ['I01','I04','I07','I08','I03','I06','I02','I05']:
    if os.path.exists(f'{k}o/DONE'): continue
    doc=pymupdf.open(f'{k}.pdf'); os.makedirs(f'{k}o',exist_ok=True)
    for i,pg in enumerate(doc,1):
        out=f'{k}o/{i}.txt'
        if os.path.exists(out): continue
        if time.time()-T0>BUD: print('budget',k,i); sys.exit(0)
        pix=pg.get_pixmap(matrix=pymupdf.Matrix(1800/pg.rect.width,1800/pg.rect.width)); tmp=f'{k}o/_oi_{k}_{i}.png'; pix.save(tmp)
        r=subprocess.run(['tesseract',tmp,'stdout','-l','kor+eng','--psm','3'],capture_output=True)
        open(out,'w').write(r.stdout.decode('utf-8','replace')); os.remove(tmp)
    open(f'{k}o/DONE','w').write('ok')
print('ALL DONE')
