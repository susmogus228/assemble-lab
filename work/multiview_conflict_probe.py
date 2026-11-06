import random,json
from unittest.mock import patch
from work.held_tracking_memory import HeldTracker
from work.color_tower_multiview_v3 import run
orig=HeldTracker.update;events=[]
def debug(self,x,y,t):
 v=orig(self,x,y,t)
 if v[1] in ('conflict','unavailable'):events.append({'mode':v[1],'x':x,'y':y,'tool':list(t)})
 return v
rng=random.Random(911);off=(round(rng.uniform(-.015,.015),4),round(rng.uniform(-.01,.01),4))
with patch.object(HeldTracker,'update',debug):r=run(['red','blue'],scene_seed=911,source_offset=off,extra_count=2,feedback='sensor',retry=True)
print(json.dumps({'failure':r['failure'],'events':events}))
