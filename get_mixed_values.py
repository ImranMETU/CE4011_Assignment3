#!/usr/bin/env python
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from q2_frame_analysis.main import example_input_data
from model.structure import Structure

# Run the mixed example
data = example_input_data()
structure = Structure.from_dict(data)
structure.assign_dofs()
solution = structure.solve()

print("=== DISPLACEMENTS ===")
print("expected_displacements = [")
for i in range(solution.size):
    print(f"    {solution.get(i)!r},")
print("]")

print("\n=== REACTIONS ===")
reactions = structure.compute_reactions()
print(f"reactions[0]['rx'] = {reactions[0]['rx']!r}")
print(f"reactions[0]['ry'] = {reactions[0]['ry']!r}")
print(f"reactions[0]['mz'] = {reactions[0]['mz']!r}")
print(f"reactions[3]['ry'] = {reactions[3]['ry']!r}")

print("\n=== MEMBER FORCES ===")
member_forces = structure.compute_member_end_forces()
frame_1 = member_forces[1]
truss_4 = member_forces[4]
print(f"frame_1['node_i']['mz'] = {frame_1['node_i']['mz']!r}")
print(f"truss_4['node_i']['nx'] = {truss_4['node_i']['nx']!r}")
print(f"truss_4['node_j']['nx'] = {truss_4['node_j']['nx']!r}")
print(f"truss_4['node_i']['vy'] = {truss_4['node_i']['vy']!r}")
print(f"truss_4['node_i']['mz'] = {truss_4['node_i']['mz']!r}")
