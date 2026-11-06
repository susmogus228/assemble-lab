import hashlib,json,math,random
from pathlib import Path
from work.color_tower_multiview_v5 import run as baseline
from work.color_tower_reobserve_v3 import run as candidate
files=['work/color_tower_multiview_v5.py','work/color_tower_reobserve_v3.py','work/reobserve_policy.py','work/reobserve_policy_v2.py','work/held_tracking_geometry.py','work/held_face_geometry.py','work/held_tracking_memory_v2.py','work/held_camera_multiview_v2.py','work/held_camera.py','work/held_camera_visible.py','work/visible_depth_pixel.py','work/hold_guard.py','work/base_camera_highres.py','work/sensors_candidate.py','sensors.py','tower_targets.py','sequence_probe.py']
cases=[{'seed':1103,'extra':0,'same_red':False},{'seed':1109,'extra':2,'same_red':False},{'seed':1117,'extra':4,'same_red':False},{'seed':1123,'extra':1,'same_red':True},{'seed':1129,'extra':3,'same_red':False},{'seed':1151,'extra':2,'same_red':False}]
manifest={'files':{f:hashlib.sha256(Path(f).read_bytes()).hexdigest() for f in files},'cases':cases,'selection':'geometry face gate and up to three bounded collision-checked high observation moves after conflicting upper-lift views, fixed before new scene evaluation','criteria':'unchanged full tower and unselected movement limits; distinguish completion, stop, and camera estimate error','scope':'known 50mm nearly axis-aligned cubes, idealized calibrated simulation cameras and contact identity'}
Path('work/frozen-reobserve-v3').mkdir(exist_ok=True);Path('work/frozen-reobserve-v3/manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf8');rows=[]
for c in cases:
 rng=random.Random(c['seed']);offset=(round(rng.uniform(-.015,.015),4),round(rng.uniform(-.01,.01),4))
 for name,fn in [('previous',baseline),('candidate',candidate)]:
  assert all(hashlib.sha256(Path(f).read_bytes()).hexdigest()==h for f,h in manifest['files'].items())
  r=fn(['red','blue'],scene_seed=c['seed'],source_offset=offset,extra_count=c['extra'],same_red=c['same_red'],feedback='sensor',retry=True)
  checks=r['final_recheck'];tr=[t for t in r['held_tracking'] if t['color']=='blue' and t['estimate'] is not None];errs=[math.dist(t['estimate'],t['truth'][:2])*1000 for t in tr]
  row={'scene':c,'offset':offset,'method':name,'success':r['success'],'failure':r['failure'],'relative_mm':r['criteria']['relative_offset_mm'],'relative_yaw':r['criteria']['relative_yaw_degrees'],'checks':checks,'base_xy_error_mm':math.dist(checks[0]['actual'][:2],(.56,.1))*1000,'upper_height_mm':checks[1]['actual'][2]*1000,'unselected':r['unselected_displacement_mm'],'upper_tracking_count':len(tr),'upper_mean_error_mm':sum(errs)/len(errs) if errs else None,'upper_max_error_mm':max(errs) if errs else None,'reobservations':r.get('reobservations',[]),'hold_last':r['hold_checks'][-1] if r['hold_checks'] else None};rows.append(row);print(json.dumps(row),flush=True);Path('outputs/reobserve-v3-new-scenes.json').write_text(json.dumps(rows,indent=2),encoding='utf8')
