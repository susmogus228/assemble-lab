import json,time
from pathlib import Path
from sequence_probe import run
rows=[]
for offset in ((0,0),(-.01,.005),(.01,-.005)):
    started=time.perf_counter();r=run(push=True,source_offset=offset)
    frames=r.pop('frames');rows.append({'offset':offset,'elapsed_seconds':round(time.perf_counter()-started,2),'simulated_seconds':len(frames)/30,'criteria':r['criteria'],'final':r['final_recheck'],'push':r['push']})
Path('outputs/controller-baseline-v2.json').write_text(json.dumps(rows,indent=2),encoding='utf8');print(json.dumps(rows,indent=2))
