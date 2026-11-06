import json,math
from work.color_contact_candidate import run
for name,colors,kw in [('blue',['blue'],{}),('red',['red'],{'scene_seed':1,'source_offset':(-.01,.005),'extra_count':2})]:
 r=run(colors,feedback='sensor',retry=True,**kw);frames=r['frames'];idx=r['colors'].index(colors[0]);stages=['verify view','retry grasp','retry lift','retry transfer','retry place','retry release','retry retreat','retry verify view']
 print(name,'verify',r['verification'])
 for stage in stages:
  fs=[f for f in frames if f['stage']==stage]
  if not fs:continue
  point=fs[-1]['parts'][idx][0];print(stage,'xy',round(point[0],4),round(point[1],4),'z',round(point[2],4),'error_mm',round(math.dist(point[:2],[.56,.1])*1000,1))
