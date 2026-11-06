import json
from pathlib import Path
from sequence_probe import run
scenes=[]
for layout in ('tower','row'):
    for offset in ((0,0),(-.015,.01),(.015,-.01)):
        r=run(layout=layout,source_offset=offset)
        scenes.append({'layout':layout,'source_offset':offset,'success':r['complete'],'criteria':r['criteria'],'parts':r['final_recheck']})
Path('outputs/figure-audit.json').write_text(json.dumps(scenes,indent=2),encoding='utf8')
print(json.dumps(scenes,indent=2))
