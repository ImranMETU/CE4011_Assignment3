"""
Assembly Module
===============
Assembles the global stiffness matrix from element stiffness matrices.

Direct Stiffness Method (DSM):
    1. For each element:
        a. Compute element stiffness k
        b. Map local DOFs to global DOFs using E matrix
        c. Add element stiffness to global K

Inputs:
    frame_elements: List of elements with (node1, node2, A, I, E, angle)
    E: DOF numbering matrix
    K: SymmetricSparseMatrix for accumulation

Outputs:
    K: Assembled global stiffness matrix (sparse)

Units:
    K: [force/length] and [moment/radian]

Assumptions:
    - Elements are ordered by (node1, node2) pairs
    - E matrix maps all DOFs
    - K is SymmetricSparseMatrix from Q1 library
"""

import sys
sys.path.insert(0, r"c:\Imran\METU\Coursework\CE4011\Assignment2")

from q1_matrix_library.symmetric_sparse_matrix import SymmetricSparseMatrix
from model.frame_element import compute_global_stiffness, compute_local_stiffness


def assemble_global_stiffness(frame_elements, E, K, geometry):
    """
    Assemble global stiffness matrix using Direct Stiffness Method.
    
    Args:
        frame_elements (list): List of elements, each with:
                               (node1, node2, A, I, E_material)
        E (list): DOF numbering matrix [n_nodes × 3]
        K (SymmetricSparseMatrix): Global stiffness matrix to accumulate into
        geometry (FrameGeometry): Geometry object for length/angle computation
    
    Returns:
        K (SymmetricSparseMatrix): Assembled global stiffness matrix
    
    Assumptions:
        - Elements ordered by pair indices
        - All nodes in E matrix are valid (0 ≤ node < n_nodes)
        - SymmetricSparseMatrix supports .add(i, j, value)
    """
    for elem_idx, element in enumerate(frame_elements):
        node1, node2, A, I, E_material = element
        
        # Compute element length and angle from geometry
        L = geometry.get_element_length(node1, node2)
        angle = geometry.get_element_angle(node1, node2)
        
        # Compute local stiffness
        k_prime = compute_local_stiffness(A, I, E_material, L)
        
        # Compute global stiffness
        k_global = compute_global_stiffness(k_prime, angle)
        
        # Map local DOFs to global DOFs
        # Element has 6 DOFs: node1(3) + node2(3)
        global_dofs = []
        for dof_idx in range(3):
            global_dofs.append(E[node1][dof_idx])  # Node1's DOFs
        for dof_idx in range(3):
            global_dofs.append(E[node2][dof_idx])  # Node2's DOFs
        
        # Add element contributions to global K
        # Only iterate upper triangle to avoid double-adding due to symmetry
        for i in range(6):
            for j in range(i, 6):  # j starts from i, not 0
                global_i = global_dofs[i]
                global_j = global_dofs[j]
                
                # E uses handout convention: 0=restrained, 1-based active numbering.
                if global_i != 0 and global_j != 0:
                    K.add(global_i - 1, global_j - 1, k_global[i][j])
    
    return K


def print_assembly_info(frame_elements, n_active_dofs, K=None):
    """
    Print information about assembly process.
    
    Args:
        frame_elements (list): List of frame elements
        n_active_dofs (int): Total number of active DOFs
        K (SymmetricSparseMatrix): Assembled stiffness matrix (optional)
    
    Returns:
        None
    """
    print("\n" + "="*70)
    print("ASSEMBLY INFORMATION")
    print("="*70)
    print(f"Number of elements: {len(frame_elements)}")
    print(f"Number of active DOFs: {n_active_dofs}")
    print(f"Global stiffness matrix size: {n_active_dofs} × {n_active_dofs}")
    
    if K is not None:
        print(f"\nAssembled K matrix (non-zero entries):")
        print(f"  Storage entries: {len(K.data)}")
        
        # Show diagonal terms (should be positive for SPD)
        print(f"\n  Diagonal terms:")
        for i in range(min(n_active_dofs, 6)):
            val = K.get(i, i)
            print(f"    K[{i},{i}] = {val:12.6f}")
    print()
