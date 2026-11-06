import json,time,sys
from pathlib import Path
sys.path.insert(0,'work')
from controller_v3 import run
rows=[]
for offset in ((0,0),(-.01,.005),(.01,-.005),(-.007,-.006),(.006,.007)):
    start=time.perf_counter();r=run(push=True,source_offset=offset);frames=r.pop('frames')
    rows.append({'offset':offset,'development':offset==(0,0),'elapsed_seconds':round(time.perf_counter()-start,2),'simulated_seconds':len(frames)/30,'criteria':r['criteria'],'final':r['final_recheck'],'push':r['push']})
Path('outputs/controller-candidate-v3.json').write_text(json.dumps(rows,indent=2),encoding='utf8');print(json.dumps(rows,indent=2))
