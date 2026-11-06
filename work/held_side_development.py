import json,math
from pathlib import Path
from work.held_side_probe import run
r=run(['red','blue'],scene_seed=0,feedback='sensor',retry=True)
obs=r['held_observations'];Path('outputs/held-side-development.json').write_text(json.dumps(obs,indent=2),encoding='utf8')
for color in ('red','blue'):
 for view in ('side_x','side_y','diagonal'):
  subset=[x for x in obs if x['color']==color]; unique=[x for x in subset if len(x['sides'][view])==1];errs=[round(math.dist(x['sides'][view][0]['point'][:2],x['truth'][:2])*1000,1) for x in unique];print(json.dumps({'color':color,'view':view,'seen':len(unique),'total':len(subset),'raw_error_mm':errs}),flush=True)
