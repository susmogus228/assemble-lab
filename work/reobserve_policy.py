"""Conservative, simulation-only reobservation waypoint and contact guard."""
import math

def reobserve_target(tool):
    if len(tool)!=3 or not all(math.isfinite(v) for v in tool):return None
    x,y,z=tool
    if z<.18:return None
    target=[x+.02,y+.02,z]
    if not (.30<=target[0]<=.70 and -.4<=target[1]<=.3):return None
    return target

def has_unexpected_contact(contacts,arm,held):
    return any(c['body'] not in (arm,held) for c in contacts)
