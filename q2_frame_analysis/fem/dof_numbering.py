"""
DOF Numbering Module
====================
Builds the DOF numbering matrix E that maps global DOFs to active DOFs.

For a 2D frame, each node has 3 DOFs: ux, uy, rz (horizontal, vertical, rotation).
Supported DOFs are removed from the active set.

Inputs:
    n_nodes: Number of nodes
    supports: List of [node, ux, uy, rz] constraints (0=free, 1=restrained)

Outputs:
    E: DOF numbering matrix (n_nodes × 3) with active DOF numbers (0 if constrained)
    n_active_dofs: Number of active (unconstrained) DOFs

Units: None (topology only)

Assumptions:
    - Nodes are numbered 0 to n_nodes-1
    - Each node has exactly 3 DOFs
"""


def build_dof_numbering(n_nodes, supports):
    """
    Build DOF numbering matrix E.
    
    Args:
        n_nodes (int): Number of nodes in the frame.
        supports (list): List of support conditions, each [node, ux, uy, rz]
                         where 0=free, 1=restrained.
    
    Returns:
        E (list): DOF numbering matrix [n_nodes × 3].
                  E[i][j] = global DOF number for node i, direction j
                  E[i][j] = 0 if DOF is constrained
        n_active_dofs (int): Total number of active DOFs.
    
    Assumptions:
        - Nodes numbered 0 to n_nodes-1
        - 3 DOFs per node: [ux, uy, rz]
    """
    # Initialize E matrix with None for not-yet-numbered free DOFs
    E = [[None for _ in range(3)] for _ in range(n_nodes)]

    # Mark constrained DOFs as 0 (handout convention)
    for support in supports:
        node = support[0]
        ux_restrained = support[1]
        uy_restrained = support[2]
        rz_restrained = support[3]
        
        if ux_restrained:
            E[node][0] = 0
        if uy_restrained:
            E[node][1] = 0
        if rz_restrained:
            E[node][2] = 0

    # Number active DOFs sequentially from 1 (handout convention)
    active_dof_number = 1
    for i in range(n_nodes):
        for j in range(3):
            if E[i][j] is None:
                E[i][j] = active_dof_number
                active_dof_number += 1

    n_active_dofs = active_dof_number - 1
    
    return E, n_active_dofs


def build_equation_numbering_array(NumNode, S):
    """
    Build equation-numbering array E for input phase.

    Args:
        NumNode (int): Number of nodes.
        S (list): Support data with rows [node_id, rx, ry, rz],
                  where node_id is 1-based and 1=restrained, 0=free.

    Returns:
        E (list): Equation-numbering array [NumNode x 3] where:
                  - restrained DOFs are 0
                  - active DOFs are numbered rowwise from 1
        NumEq (int): Total number of equations (maximum value in E).
    """
    E = [[0, 0, 0] for _ in range(NumNode)]

    for support in S:
        node_id = support[0]
        node_idx = node_id - 1
        if support[1] == 1:
            E[node_idx][0] = 0
        if support[2] == 1:
            E[node_idx][1] = 0
        if support[3] == 1:
            E[node_idx][2] = 0

    eq = 1
    for i in range(NumNode):
        for j in range(3):
            if E[i][j] == 0:
                is_restrained = False
                for support in S:
                    if support[0] == i + 1 and support[j + 1] == 1:
                        is_restrained = True
                        break
                if not is_restrained:
                    E[i][j] = eq
                    eq += 1

    NumEq = eq - 1
    return E, NumEq


def print_dof_numbering(E, n_active_dofs):
    """
    Print DOF numbering matrix for verification.
    
    Args:
        E (list): DOF numbering matrix.
        n_active_dofs (int): Number of active DOFs.
    
    Returns:
        None
    """
    print("\n" + "="*70)
    print("DOF NUMBERING MATRIX E")
    print("="*70)
    print("Format: E[node][dof] = global_dof_number (0 if constrained)")
    print(f"Total active DOFs: {n_active_dofs}\n")
    
    print("Node | ux   | uy   | rz   |")
    print("-----|------|------|------|")
    for i in range(len(E)):
        ux_str = str(E[i][0])
        uy_str = str(E[i][1])
        rz_str = str(E[i][2])
        print(f"{i:4d} | {ux_str:4s} | {uy_str:4s} | {rz_str:4s} |")
    print()
