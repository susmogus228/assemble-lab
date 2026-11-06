import hashlib,json
from pathlib import Path
from work.single_grasp_coupling_probe import run
files=['work/single_grasp_coupling_probe.py'];cases=[{'source':[.445,-.135],'path':'forward'},{'source':[.475,-.155],'path':'diagonal'},{'source':[.505,-.145],'path':'turn'},{'source':[.455,-.115],'path':'turn'},{'source':[.495,-.165],'path':'forward'},{'source':[.47,-.125],'path':'diagonal'}]
manifest={'files':{f:hashlib.sha256(Path(f).read_bytes()).hexdigest() for f in files},'cases':cases,'comparison':'independent finger joints versus Panda fingers coupled using Bullet gear constraint; no constraint to cube; peak change in object position in grasp-target coordinates, sampled every 8 physics steps','heldout':'frozen before running'}
Path('work/frozen-single-coupling').mkdir(exist_ok=True);Path('work/frozen-single-coupling/manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf8')
rows=[]
for c in cases:
 for coupled in (False,True):
  assert all(hashlib.sha256(Path(f).read_bytes()).hexdigest()==h for f,h in manifest['files'].items())
  r=run(tuple(c['source']),c['path'],False,coupled);rows.append(r);print(json.dumps({k:v for k,v in r.items() if k!='trace'}),flush=True);Path('outputs/single-grasp-coupling-new.json').write_text(json.dumps(rows,indent=2),encoding='utf8')
