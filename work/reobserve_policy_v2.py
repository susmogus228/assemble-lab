"""A small fixed set of high-altitude simulation-only observation poses."""
import math
from work.reobserve_policy import has_unexpected_contact

def reobserve_targets(tool):
    if len(tool)!=3 or not all(math.isfinite(v) for v in tool):return []
    x,y,z=tool
    if z<.18:return []
    targets=[[x+dx,y+dy,z] for dx,dy in ((.02,.02),(-.02,.02),(0.,-.02))]
    return [p for p in targets if .30<=p[0]<=.70 and -.4<=p[1]<=.3]
