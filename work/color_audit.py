import json
from pathlib import Path
from color_assembly import run
cases=[]
for selected,offset in [(['red'],(0,0)),(['blue'],(.01,-.005)),(['red','blue'],(0,0)),(['red','blue'],(-.01,.005))]:
 r=run(selected,source_offset=offset);cases.append({'selected':selected,'offset':offset,'detected':[{'color':i['color'],'colors_seen':list(i['detections']),'ray':i['laser']} for i in r['inspections']],'completed_actions':[a['color'] for a in r['parts']],'success':r['complete'],'failure':r['failure'],'unselected_displacement_mm':r['unselected_displacement_mm']})
Path('outputs/color-sensor-audit.json').write_text(json.dumps(cases,indent=2),encoding='utf8');print(json.dumps(cases,indent=2))
