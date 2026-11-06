import json,random,math,hashlib
from pathlib import Path
from work.color_camera_candidate import run as baseline
from work.color_tower_v2 import run as candidate
m=json.loads(Path('work/frozen-tower-v2/manifest.json').read_text(encoding='utf8'))
for name,sha in m['sha256'].items():
 path=Path(name) if name=='tower_targets.py' else Path('work',name)
 assert hashlib.sha256(path.read_bytes()).hexdigest()==sha
rows=[]
for c in m['cases']:
 rng=random.Random(c['seed']);offset=(round(rng.uniform(-.015,.015),4),round(rng.uniform(-.01,.01),4))
 for mode,fn in [('baseline',baseline),('v2',candidate)]:
  r=fn(['red','blue'],scene_seed=c['seed'],source_offset=offset,extra_count=c['extra'],same_red=c['same_red'],feedback='sensor',retry=True);frames=r['frames'];before=next((f['parts'][0][0] for f in reversed(frames) if f['part_number']==1),None);after=frames[-1]['parts'][0][0] if frames else None
  row={'scene':c,'offset':offset,'mode':mode,'success':r['success'],'failure':r['failure'],'attempted':[a['color'] for a in r['parts']],'checks':r['final_recheck'],'relative_mm':r['criteria']['relative_offset_mm'],'base_shift_mm':round(math.dist(before[:2],after[:2])*1000,2) if before and after else None,'unselected':r['unselected_displacement_mm'],'base_observations':r.get('base_observations',[])};rows.append(row);print(json.dumps(row),flush=True);Path('outputs/tower-v2-holdout.json').write_text(json.dumps(rows,indent=2),encoding='utf8')
