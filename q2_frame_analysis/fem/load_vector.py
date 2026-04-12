"""
Load Vector Module
==================
Constructs the global load vector F from nodal loads.

Nodal loads are applied at nodes and must be mapped to active DOFs using E matrix.
Boundary condition loads (reaction forces at supports) are not included in F directly.

Inputs:
    loads: List of [node, Fx, Fy, Mz] applied forces and moments
    E: DOF numbering matrix
    n_active_dofs: Number of active DOFs

Outputs:
    F: Load vector with size = n_active_dofs

Units:
    Fx, Fy: [force]
    Mz: [moment = force × length]

Assumptions:
    - One load per node (or loads can be accumulated at same node)
    - Supports use zero-displacement BC or reaction extraction
    - Load directions match global coordinate system
"""

import sys
sys.path.insert(0, r"c:\Imran\METU\Coursework\CE4011\Assignment2")

from q1_matrix_library.vector import Vector


def construct_load_vector(loads, E, n_active_dofs):
    """
    Construct global load vector F from nodal loads.
    
    Args:
        loads (list): List of loads, each [node, Fx, Fy, Mz]
                      where Fx, Fy are forces and Mz is moment
        E (list): DOF numbering matrix [n_nodes × 3]
        n_active_dofs (int): Total number of active DOFs
    
    Returns:
        F (Vector): Global load vector [n_active_dofs]
    
    Assumptions:
        - All load nodes are valid (0 ≤ node < n_nodes)
        - DOF values in E are in range [0, n_active_dofs)
        - Multiple loads at same node are accumulated
    """
    # Initialize load vector with zeros
    F = Vector(n_active_dofs)
    for i in range(n_active_dofs):
        F.set(i, 0.0)
    
    # Add loads to appropriate DOFs
    for load in loads:
        node = load[0]
        Fx = load[1]
        Fy = load[2]
        Mz = load[3]
        
        # Map to global DOFs
        dof_ux = E[node][0]  # Horizontal DOF
        dof_uy = E[node][1]  # Vertical DOF
        dof_rz = E[node][2]  # Rotation DOF
        
        # E uses handout convention: 0=restrained, 1-based active numbering.
        if dof_ux != 0:
            F.add(dof_ux - 1, Fx)

        if dof_uy != 0:
            F.add(dof_uy - 1, Fy)

        if dof_rz != 0:
            F.add(dof_rz - 1, Mz)
    
    return F


def print_load_vector(F, name="Load Vector F"):
    """
    Print load vector for verification.
    
    Args:
        F (Vector): Load vector to print
        name (str): Label for output
    
    Returns:
        None
    """
    print(f"\n{name}:")
    for i in range(F.size):
        print(f"  F[{i}] = {F.get(i):12.6f}")
    print()


def get_load_vector_norm(F):
    """
    Compute norm of load vector.
    
    Args:
        F (Vector): Load vector
    
    Returns:
        norm (float): Euclidean norm ||F||
    """
    return F.norm()
