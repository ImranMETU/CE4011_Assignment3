"""Script to run all 5 test cases and collect results."""

import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from model.structure import Structure


def load_input(input_path):
    p = Path(input_path)
    with p.open("r", encoding="utf-8") as f:
        return json.load(f)


def run_analysis_safe(input_data, tol=1e-8, max_iter=2000):
    """Run analysis and return either success payload or error message."""
    try:
        structure = Structure.from_dict(input_data)
        structure.assemble_global_stiffness()
        structure.assemble_global_load_vector()
        D = structure.solve(tol=tol, max_iter=max_iter)
        reactions = structure.compute_reactions()
        member_forces = structure.compute_member_end_forces()
        return {
            "success": True,
            "structure": structure,
            "displacements": D,
            "reactions": reactions,
            "member_forces": member_forces,
        }
    except (ValueError, RuntimeError) as exc:
        return {
            "success": False,
            "error": str(exc),
        }


def print_results(filename, result):
    print(f"\n{'='*72}")
    print(f"ANALYSIS RESULTS FOR: {filename}")
    print('='*72)
    
    if not result["success"]:
        print(f"ERROR: {result['error']}")
        return
    
    structure = result["structure"]
    D = result["displacements"]
    reactions = result["reactions"]
    member_forces = result["member_forces"]
    
    print(f"Nodes: {len(structure.nodes)}")
    print(f"Elements: {len(structure.elements)}")
    print(f"Active DOFs: {structure.n_active_dofs}")
    print(f"K nnz (upper triangle): {len(structure.K.data)}")
    print(f"||F|| = {structure.F.norm():.6e}")
    print(f"||D|| = {D.norm():.6e}")

    print("\nNodal Displacements (active equations):")
    for i in range(D.size):
        print(f"  Eq {i + 1:3d}: {D.get(i): .9e}")

    print("\nSupport Reactions (all nodes, global directions):")
    for node_id in sorted(reactions):
        r = reactions[node_id]
        print(f"  Node {node_id:2d}: Rx={r['rx']: .6e}, Ry={r['ry']: .6e}, Mz={r['mz']: .6e}")

    print("\nMember-End Forces (local coordinates):")
    for elem_id in sorted(member_forces):
        q = member_forces[elem_id]
        print(
            f"  Element {elem_id:2d} | "
            f"i-end: Nx={q['node_i']['nx']: .6e}, Vy={q['node_i']['vy']: .6e}, Mz={q['node_i']['mz']: .6e} | "
            f"j-end: Nx={q['node_j']['nx']: .6e}, Vy={q['node_j']['vy']: .6e}, Mz={q['node_j']['mz']: .6e}"
        )


def run_all_cases():
    cases = [
        "q3_case_a_unstable_portal.json",
        "q3_case_b_disconnected_member.json",
        "q3_case_c_disconnected_substructure.json",
        "q3_case_d_unstable_truss.json",
        "q3_case_e_internal_hinge_beam.json",
    ]
    
    script_dir = Path(__file__).resolve().parent
    
    for case_file in cases:
        case_path = script_dir / case_file
        print(f"\n{'#'*72}")
        print(f"Running: {case_file}")
        print('#'*72)
        
        data = load_input(case_path)
        result = run_analysis_safe(data)
        print_results(case_file, result)


if __name__ == "__main__":
    run_all_cases()
