# 강의자료 PDF OCR — work/CONS/에서 <키>.pdf → <키>o/<쪽>.txt (tesseract는 Homebrew 기본 tessdata 사용, kor+eng)
import subprocess,os,pymupdf,sys,time
sys.path.insert(0,os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import jblpaths as J
os.chdir(J.work('CONS'))
T0=time.time(); BUD=float(sys.argv[1]) if len(sys.argv)>1 else 250
for k in ['C07','C03','C02','C06']:
    if os.path.exists(f'{k}o/DONE'): continue
    doc=pymupdf.open(f'{k}.pdf'); os.makedirs(f'{k}o',exist_ok=True)
    for i,pg in enumerate(doc,1):
        out=f'{k}o/{i}.txt'
        if os.path.exists(out): continue
        if time.time()-T0>BUD: print('budget',k,i); sys.exit(0)
        pix=pg.get_pixmap(matrix=pymupdf.Matrix(1900/pg.rect.width,1900/pg.rect.width)); tmp=f'{k}o/_{i}.png'; pix.save(tmp)
        r=subprocess.run(['tesseract',tmp,'stdout','-l','kor+eng','--psm','3'],capture_output=True)
        open(out,'w').write(r.stdout.decode('utf-8','replace')); os.remove(tmp)
    open(f'{k}o/DONE','w').write('ok')
print('ALL DONE')
