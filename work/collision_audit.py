import json
from pathlib import Path
from assemble import run
cases=[]
for shape in ('cube','cylinder','sphere'):
    for x,y in ((.44,-.16),(.48,-.14),(.51,-.10)):
        r=run(source=(x,y),shape=shape)
        frames=r.pop('frames'); r['max_height']=max(f['part'][0][2] for f in frames)
        cases.append(r)
    r=run(shape=shape,miss=True);frames=r.pop('frames');r['max_height']=max(f['part'][0][2] for f in frames);r['negative_control']=True;cases.append(r)
Path('outputs/collision-audit.json').write_text(json.dumps(cases,indent=2),encoding='utf8')
print(json.dumps([{'shape':r['shape'],'source':r['source'],'negative':r.get('negative_control',False),'both':r['contact_steps']['both'],'max_height':round(r['max_height'],3),'placement':r['success']} for r in cases],indent=2))
