import json,math,random
from pathlib import Path
from work.held_visibility_probe import run
rows=[]
for seed,extra in [(0,0),(223,2),(307,0)]:
 rng=random.Random(seed);offset=(round(rng.uniform(-.015,.015),4),round(rng.uniform(-.01,.01),4)) if seed else (0,0)
 r=run(['red','blue'],scene_seed=seed,source_offset=offset,extra_count=extra,feedback='sensor',retry=True)
 row={'seed':seed,'observations':r['held_observations']}; rows.append(row)
 for color in ['red','blue']:
  o=[a for a in row['observations'] if a['color']==color]; unique=[a for a in o if len(a['candidates'])==1];errors=[math.dist(a['candidates'][0]['point'][:2],a['truth'][:2])*1000 for a in unique]
  print(json.dumps({'seed':seed,'color':color,'samples':len(o),'unique':len(unique),'errors_mm':errors}),flush=True)
 Path('outputs/held-visibility-development.json').write_text(json.dumps(rows,indent=2),encoding='utf8')
