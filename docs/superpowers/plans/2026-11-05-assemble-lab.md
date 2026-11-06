# AssembleLab Implementation Plan

**Goal:** Prototype physical assembly and a transparent learned next-action policy with a browser interface.
**Architecture:** Python + Bullet runs isolated scenes and records true body poses; a localhost API exposes replays. Three.js renders those recorded states. A separate policy learns from demonstrations and is evaluated on held-out scenarios.
**Tech Stack:** Python, PyBullet, NumPy, Three.js.
**Spec:** approved Assembly Twin visual and project plan in conversation.

## Tasks
- [ ] Physically grasp, place, release and independently verify stability of an assembly part; preserve failures and negative controls.
- [ ] Build a small demonstration dataset from verified runs, train a policy and compare on disjoint scenarios against a scripted baseline.
- [ ] Implement local API, replay and selected visual direction, clearly distinguish measured results from placeholders.
- [ ] Test physics, model, HTTP, rendering and interaction; document actual limits and reproducible setup.

## Constraints
Simulation only; no fake attachments; no real-world claims; no Github publication without separate authorization. Own project on D:. Existing GripLab remains unchanged.
