"""Conservative grasp confirmation and bounded XY correction for experiments."""
import math

def stable_grasp(samples):
    if len(samples) < 3:
        return False
    return sum(1 for pair in samples if len(pair)==2 and all(math.isfinite(x) and x >= .1 for x in pair)) >= 2

def bounded_step(estimate, tool, target, gain=.25, limit=.002):
    if estimate is None or len(estimate)!=2 or len(tool)!=2 or len(target)!=2:
        return None
    if not all(math.isfinite(x) for x in (*estimate,*tool,*target)):
        return None
    return tuple(tool[i]+max(-limit,min(limit,gain*(target[i]-estimate[i]))) for i in range(2))
