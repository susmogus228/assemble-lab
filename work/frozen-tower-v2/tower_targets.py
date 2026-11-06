"""Select a visually observed base only when a single candidate is nearby."""
import math

def choose_base_observation(candidates,expected,max_radius):
    nearby=[d for d in candidates if len(d.get('point',[]))>=3 and math.dist(d['point'][:2],expected)<=max_radius]
    return nearby[0] if len(nearby)==1 else None
