import hashlib,json,math,random
from pathlib import Path
from work.color_tower_held_v2 import run as baseline
from work.color_tower_guarded_v1 import run as candidate
files=['work/color_tower_held_v2.py','work/color_tower_guarded_v1.py','work/hold_guard.py','work/held_camera.py','work/sensors_candidate.py','sensors.py','tower_targets.py','sequence_probe.py']
cases=[{'seed':601,'extra':0,'same_red':False},{'seed':607,'extra':2,'same_red':False},{'seed':613,'extra':4,'same_red':False},{'seed':617,'extra':1,'same_red':True}]
manifest={'files':{f:hashlib.sha256(Path(f).read_bytes()).hexdigest() for f in files},'cases':cases,'scope':'simulated 50 mm cubes, idealized camera and finger contact body identity; guarded before release, sampled at stage checkpoints','frozen':'candidate and scenes fixed before paired new-scene evaluation'}
Path('work/frozen-guarded-v1').mkdir(exist_ok=True);Path('work/frozen-guarded-v1/manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf8')
rows=[]
for c in cases:
 rng=random.Random(c['seed']);offset=(round(rng.uniform(-.015,.015),4),round(rng.uniform(-.01,.01),4))
 for name,run in [('previous_tracking',baseline),('guarded',candidate)]:
  assert all(hashlib.sha256(Path(f).read_bytes()).hexdigest()==h for f,h in manifest['files'].items())
  r=run(['red','blue'],scene_seed=c['seed'],source_offset=offset,extra_count=c['extra'],same_red=c['same_red'],feedback='sensor',retry=True)
  tr=r.get('held_tracking',[]);valid=[x for x in tr if x['estimate'] is not None];errors=[math.dist(x['estimate'],x['truth'][:2])*1000 for x in valid]
  row={'scene':c,'offset':offset,'method':name,'success':r['success'],'failure':r['failure'],'relative_mm':r['criteria']['relative_offset_mm'],'relative_yaw':r['criteria']['relative_yaw_degrees'],'checks':r['final_recheck'],'unselected':r['unselected_displacement_mm'],'tracking_count':len(tr),'tracking_valid':len(valid),'tracking_mean_error_mm':sum(errors)/len(errors) if errors else None,'tracking_max_error_mm':max(errors) if errors else None,'hold_checks':r.get('hold_checks',[]),'diagnostics':r['diagnostics']};rows.append(row);summary={**row,'hold_checks':len(row['hold_checks']),'diagnostics':None};print(json.dumps(summary),flush=True);Path('outputs/guarded-descent-new-scenes.json').write_text(json.dumps(rows,indent=2),encoding='utf8')
