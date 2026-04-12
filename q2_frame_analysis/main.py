"""OO entrypoint for CE4011 HW3 Q1 2D structural analysis solver."""

import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from model.structure import Structure


def example_input_data():
    """Built-in structured test model with mixed frame/truss, releases, and member loads."""
    return {
        "nodes": [
            {"id": 0, "x": 0.0, "y": 0.0, "restraints": {"ux": True, "uy": True, "rz": True}},
            {"id": 1, "x": 0.0, "y": 3.0, "restraints": {}},
            {"id": 2, "x": 4.0, "y": 3.0, "restraints": {}},
            {"id": 3, "x": 4.0, "y": 0.0, "restraints": {"uy": True}},
        ],
        "materials": [
            {"id": "steel", "E": 2.0e8},
        ],
        "sections": [
            {"id": "frame_section", "A": 0.02, "I": 0.08},
            {"id": "truss_section", "A": 0.01, "I": 0.0},
        ],
        "elements": [
            {
                "id": 1,
                "type": "frame",
                "node_i": 0,
                "node_j": 1,
                "material": "steel",
                "section": "frame_section",
                "member_loads": [{"type": "udl", "direction": "local_y", "w": -5.0}],
            },
            {
                "id": 2,
                "type": "frame",
                "node_i": 1,
                "node_j": 2,
                "material": "steel",
                "section": "frame_section",
                "releases": {"end": True},
                "member_loads": [{"type": "point", "direction": "local_y", "p": -12.0, "a": 1.5}],
            },
            {
                "id": 3,
                "type": "frame",
                "node_i": 2,
                "node_j": 3,
                "material": "steel",
                "section": "frame_section",
            },
            {
                "id": 4,
                "type": "truss",
                "node_i": 0,
                "node_j": 2,
                "material": "steel",
                "section": "truss_section",
            },
        ],
        "nodal_loads": [
            {"node": 1, "fx": 10.0, "fy": -10.0, "mz": 0.0},
            {"node": 2, "fx": 10.0, "fy": -10.0, "mz": 0.0},
        ],
    }


def q3_case_a_unstable_portal_data():
    """Q3 case (a): portal frame with roller supports at both bases (uy restrained only)."""
    return {
        "nodes": [
            {"id": 0, "x": 0.0, "y": 0.0, "restraints": {"uy": True}},
            {"id": 1, "x": 0.0, "y": 1.0, "restraints": {}},
            {"id": 2, "x": 1.0, "y": 1.0, "restraints": {}},
            {"id": 3, "x": 1.0, "y": 0.0, "restraints": {"uy": True}},
        ],
        "materials": [
            {"id": "rc", "E": 25e9},
        ],
        "sections": [
            {"id": "frame_section", "A": 0.09, "I": 6.75e-4},
        ],
        "elements": [
            {"id": 1, "type": "frame", "node_i": 0, "node_j": 1, "material": "rc", "section": "frame_section"},
            {
                "id": 2,
                "type": "frame",
                "node_i": 1,
                "node_j": 2,
                "material": "rc",
                "section": "frame_section",
                "member_loads": [{"type": "udl", "direction": "local_y", "w": -5000.0}],
            },
            {"id": 3, "type": "frame", "node_i": 2, "node_j": 3, "material": "rc", "section": "frame_section"},
        ],
        "nodal_loads": [],
    }


def load_input(input_path=None):
    if input_path is None:
        return example_input_data()

    p = Path(input_path)
    with p.open("r", encoding="utf-8") as f:
        return json.load(f)


def detect_connected_components(structure):
    """Return connected components as a list of sets of node ids."""
    return structure.connected_components()


def compute_bandwidth(structure):
    """Compute semi-bandwidth and full bandwidth from active equation coupling."""
    if structure.n_active_dofs == 0:
        return 0, 0

    semi_bw = 1
    for element in structure.elements:
        active_eqs = [eq for eq in element.global_dof_numbers() if eq != 0]
        for eq_i in active_eqs:
            for eq_j in active_eqs:
                semi_bw = max(semi_bw, abs(eq_i - eq_j) + 1)

    full_bw = 2 * semi_bw - 1
    return semi_bw, full_bw


def _component_elements(structure, component):
    return [
        element
        for element in structure.elements
        if element.node_i.id in component and element.node_j.id in component
    ]


def _component_type(component_elements):
    if component_elements and all(element.__class__.__name__ == "TrussElement" for element in component_elements):
        return "truss"
    return "frame"


def _node_has_moment_connectivity(node_id, component_elements):
    for element in component_elements:
        if element.__class__.__name__ != "FrameElement":
            continue

        if element.node_i.id == node_id and not getattr(element, "release_start", False):
            return True
        if element.node_j.id == node_id and not getattr(element, "release_end", False):
            return True

    return False


def _count_component_reactions(structure, component, component_elements):
    r = 0
    for node_id in component:
        node = structure.nodes[node_id]

        if node.restraints.get("ux", False):
            r += 1
        if node.restraints.get("uy", False):
            r += 1

        # Count rotational reaction only when the node can transfer frame moment.
        if node.restraints.get("rz", False) and _node_has_moment_connectivity(node_id, component_elements):
            r += 1

    return r


def compute_component_determinacy(structure, component):
    component_elements = _component_elements(structure, component)
    model_type = _component_type(component_elements)

    m = len(component_elements)
    j = len(component)
    r = _count_component_reactions(structure, component, component_elements)

    if model_type == "truss":
        ds = m + r - 2 * j
    else:
        h = 0
        for element in component_elements:
            if element.__class__.__name__ != "FrameElement":
                continue
            if getattr(element, "release_start", False):
                h += 1
            if getattr(element, "release_end", False):
                h += 1
        ds = r + 3 * m - 3 * j - h

    return {
        "type": model_type,
        "ds": ds,
    }


def build_determinacy_summary(structure, components):
    summary = []
    for index, component in enumerate(components, start=1):
        info = compute_component_determinacy(structure, component)
        ds = info["ds"]

        if ds == 0:
            status = "statically determinate"
        elif ds > 0:
            degree_label = "degree" if ds == 1 else "degrees"
            status = f"statically indeterminate by {ds} {degree_label}"
        else:
            unstable = abs(ds)
            degree_label = "degree" if unstable == 1 else "degrees"
            status = f"unstable by {unstable} {degree_label}"

        summary.append(
            {
                "component_index": index,
                "type": info["type"],
                "status": status,
            }
        )

    return summary


def _format_component(component):
    return "{" + ",".join(str(node_id) for node_id in sorted(component)) + "}"


def print_detailed_results(D, reactions, member_forces):
    """Print solved response quantities for engineering reporting."""
    print("Nodal Displacements (active equations):")
    for i in range(D.size):
        print(f"  Eq {i + 1:3d}: {D.get(i): .9e}")

    print("Support Reactions (all nodes, global directions):")
    for node_id in sorted(reactions):
        r = reactions[node_id]
        print(f"  Node {node_id:2d}: Rx={r['rx']: .6e}, Ry={r['ry']: .6e}, Mz={r['mz']: .6e}")

    print("Member-End Forces (local coordinates):")
    for elem_id in sorted(member_forces):
        q = member_forces[elem_id]
        print(
            f"  Element {elem_id:2d} | "
            f"i-end: Nx={q['node_i']['nx']: .6e}, Vy={q['node_i']['vy']: .6e}, Mz={q['node_i']['mz']: .6e} | "
            f"j-end: Nx={q['node_j']['nx']: .6e}, Vy={q['node_j']['vy']: .6e}, Mz={q['node_j']['mz']: .6e}"
        )


def report_analysis(
    structure,
    semi_bw,
    full_bw,
    components,
    determinacy_summary,
    solved,
    case_name,
    D=None,
    reactions=None,
    member_forces=None,
):
    """Print unified, professional Q3 analysis diagnostics."""
    print(f"--- Starting Analysis: {case_name} ---")
    print(f"Nodes: {len(structure.nodes)} | Elements: {len(structure.elements)}")
    print(f"Active Equations: {structure.n_active_dofs}")
    print(f"Semi-bandwidth: {semi_bw} | Full bandwidth: {full_bw}")

    print("Determinacy summary:")
    for item in determinacy_summary:
        print(f"* Component {item['component_index']}: {item['type']}, {item['status']}")

    if len(components) > 1:
        print("WARNING: The model contains disconnected components. Determinacy was assessed per connected component.")
        component_sets = ", ".join(_format_component(comp) for comp in components)
        print(f"WARNING: {len(components)} disconnected sub-structures detected: {component_sets}.")
        print("Each sub-structure is independently supported and solvable.")

    print(f"Processing Load Case: {case_name}...")

    if solved:
        if D is not None and reactions is not None and member_forces is not None:
            print_detailed_results(D, reactions, member_forces)
        print("System solved successfully.")
        print(f"Results written to ./results/{case_name}_results.txt")
    else:
        print("ERROR: Global stiffness matrix is singular or nearly singular.")
        print(
            "The structure may be unstable due to insufficient restraints, "
            "hinge configuration, or disconnected DOFs."
        )


def write_results_file(result_path, structure, D, reactions, member_forces):
    with result_path.open("w", encoding="utf-8") as f:
        f.write("=" * 72 + "\n")
        f.write(f"RESULTS FOR: {result_path.stem}\n")
        f.write("=" * 72 + "\n")
        f.write(f"Nodes: {len(structure.nodes)}\n")
        f.write(f"Elements: {len(structure.elements)}\n")
        f.write(f"Active DOFs: {structure.n_active_dofs}\n")
        f.write(f"||F|| = {structure.F.norm():.6e}\n")
        f.write(f"||D|| = {D.norm():.6e}\n\n")

        f.write("Nodal Displacements (active equations):\n")
        for i in range(D.size):
            f.write(f"  Eq {i + 1:3d}: {D.get(i): .9e}\n")

        f.write("\nSupport Reactions (all nodes, global directions):\n")
        for node_id in sorted(reactions):
            r = reactions[node_id]
            f.write(f"  Node {node_id:2d}: Rx={r['rx']: .6e}, Ry={r['ry']: .6e}, Mz={r['mz']: .6e}\n")

        f.write("\nMember-End Forces (local coordinates):\n")
        for elem_id in sorted(member_forces):
            q = member_forces[elem_id]
            f.write(
                f"  Element {elem_id:2d} | "
                f"i-end: Nx={q['node_i']['nx']: .6e}, Vy={q['node_i']['vy']: .6e}, Mz={q['node_i']['mz']: .6e} | "
                f"j-end: Nx={q['node_j']['nx']: .6e}, Vy={q['node_j']['vy']: .6e}, Mz={q['node_j']['mz']: .6e}\n"
            )


def run_analysis(input_data, case_name, tol=1e-8, max_iter=2000):
    structure = Structure.from_dict(input_data)
    semi_bw, full_bw = compute_bandwidth(structure)
    components = detect_connected_components(structure)
    determinacy_summary = build_determinacy_summary(structure, components)

    try:
        structure.assemble_global_stiffness()
        structure.assemble_global_load_vector()
        D = structure.solve(tol=tol, max_iter=max_iter)
        reactions = structure.compute_reactions()
        member_forces = structure.compute_member_end_forces()

        results_dir = Path(__file__).resolve().parent / "results"
        results_dir.mkdir(parents=True, exist_ok=True)
        result_path = results_dir / f"{case_name}_results.txt"
        write_results_file(result_path, structure, D, reactions, member_forces)

        report_analysis(
            structure,
            semi_bw,
            full_bw,
            components,
            determinacy_summary,
            True,
            case_name,
            D=D,
            reactions=reactions,
            member_forces=member_forces,
        )
        return {
            "success": True,
            "result_path": result_path,
        }
    except (ValueError, RuntimeError):
        report_analysis(structure, semi_bw, full_bw, components, determinacy_summary, False, case_name)
        return {
            "success": False,
        }


def main(input_json_path=None):
    data = load_input(input_json_path)
    case_name = Path(input_json_path).stem if input_json_path else "example_case"
    run_analysis(data, case_name)


if __name__ == "__main__":
    json_path = sys.argv[1] if len(sys.argv) > 1 else None
    main(json_path)
