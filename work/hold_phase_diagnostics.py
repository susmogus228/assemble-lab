import json,random
from pathlib import Path
from work.hold_phase_probe import run
rows=[]
for seed,extra in [(0,0),(223,2),(503,0),(521,4)]:
 rng=random.Random(seed); offset=(round(rng.uniform(-.015,.015),4),round(rng.uniform(-.01,.01),4)) if seed else (0,0)
 r=run(['red','blue'],scene_seed=seed,source_offset=offset,extra_count=extra,feedback='sensor',retry=True)
 row={'seed':seed,'success':r['success'],'failure':r['failure'],'hold_diagnostics':r['hold_diagnostics'],'checks':r['final_recheck']};rows.append(row);print(json.dumps(row),flush=True);Path('outputs/hold-phase-diagnostics.json').write_text(json.dumps(rows,indent=2),encoding='utf8')
