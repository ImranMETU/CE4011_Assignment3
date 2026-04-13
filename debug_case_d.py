#!/usr/bin/env python
import json
import sys
from pathlib import Path

# Set up the path the same way main.py does
THIS_DIR = Path(__file__).resolve().parent / 'q2_frame_analysis'
PROJECT_ROOT = THIS_DIR.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from model.structure import Structure

with open('q2_frame_analysis/q3_case_d_unstable_truss.json') as f:
    data = json.load(f)

structure = Structure.from_dict(data)
structure.assign_dofs()
solution = structure.solve()

print('Displacements:', [solution.get(i) for i in range(solution.size)])

reactions = structure.compute_reactions()
for i, r in enumerate(reactions):
    print(f'Node {i}: rx={r.get("rx", 0):.6e}, ry={r.get("ry", 0):.6e}, mz={r.get("mz", 0):.6e}')

member_forces = structure.compute_member_end_forces()
for elem_id, forces in member_forces.items():
    print(f'Element {elem_id}:')
    print(f'  i-end: nx={forces["node_i"].get("nx", 0):.6e}, vy={forces["node_i"].get("vy", 0):.6e}, mz={forces["node_i"].get("mz", 0):.6e}')
    print(f'  j-end: nx={forces["node_j"].get("nx", 0):.6e}, vy={forces["node_j"].get("vy", 0):.6e}, mz={forces["node_j"].get("mz", 0):.6e}')
