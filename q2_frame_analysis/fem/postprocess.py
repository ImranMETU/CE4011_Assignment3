"""
Postprocessing Module
=====================
Computes member forces from nodal displacements.

Step 1: Extract nodal displacements for each element
Step 2: Transform displacements to local (element) coordinates
Step 3: Compute member forces f' = k' * d'

Inputs:
    frame_elements: List of elements
    D: Nodal displacement vector (global frame coordinates)
    E: DOF numbering matrix
    k_local and angle for each element

Outputs:
    Member forces: Axial force, shear force, bending moments at each end

Units:
    Forces: [force]
    Moments: [force × length]

Assumptions:
    - Linear elastic behavior
    - Small deformations
    - Bernoulli-Euler beam theory
"""

import sys
sys.path.insert(0, r"c:\Imran\METU\Coursework\CE4011\Assignment2")

import math
from model.frame_element import (
    compute_local_stiffness,
    compute_global_stiffness,
    compute_rotation_matrix,
    matrix_transpose
)


def extract_element_displacements(node1, node2, D, E):
    """
    Extract nodal displacements for an element.
    
    Args:
        node1 (int): First node index
        node2 (int): Second node index
        D (list): Global displacement vector (from Q1 Vector)
        E (list): DOF numbering matrix
    
    Returns:
        d (list): Element displacements [u1x, u1y, θ1, u2x, u2y, θ2]
    
    Assumptions:
        - D is indexed by 0-based Python indices
        - E[node][dof] gives handout global DOF (0 if constrained)
        - Constrained DOFs contribute zero displacement
    """
    d = []
    
    # Node 1 displacements
    for j in range(3):
        global_dof = E[node1][j]
        if global_dof != 0:
            d.append(D.get(global_dof - 1))
        else:
            d.append(0.0)  # Constrained DOF is zero
    
    # Node 2 displacements
    for j in range(3):
        global_dof = E[node2][j]
        if global_dof != 0:
            d.append(D.get(global_dof - 1))
        else:
            d.append(0.0)  # Constrained DOF is zero
    
    return d


def transform_to_local_coords(d_global, angle):
    """
    Transform nodal displacements from global to local coordinates.
    
    Uses rotation matrix R: d_local = R^T * d_global
    
    Args:
        d_global (list): Displacements in global coordinates [u1x, u1y, θ1, u2x, u2y, θ2]
        angle (float): Element orientation angle [radians]
    
    Returns:
        d_local (list): Displacements in local (element) coordinates
    
    Assumptions:
        - Small rotation angles
        - Counterclockwise positive convention
    """
    # In this codebase, R maps global -> local DOFs, so d_local = R * d_global.
    R = compute_rotation_matrix(angle)
    d_local = [0.0 for _ in range(6)]

    for i in range(6):
        for j in range(6):
            d_local[i] += R[i][j] * d_global[j]

    return d_local


def compute_member_forces(k_prime, d_local):
    """
    Compute member forces from local displacements.
    
    f' = k' * d_local
    
    Args:
        k_prime (list): Local stiffness matrix (6×6)
        d_local (list): Local displacements (6,)
    
    Returns:
        f_local (list): Member forces in local coordinates [f1x, f1y, m1z, f2x, f2y, m2z]
    
    Assumptions:
        - Linear elastic material
        - Small deformations
    """
    f_local = [0.0 for _ in range(6)]
    
    for i in range(6):
        for j in range(6):
            f_local[i] += k_prime[i][j] * d_local[j]
    
    return f_local


def postprocess_element_forces(frame_elements, D, E, geometry):
    """
    Compute and print all member forces.
    
    Args:
        frame_elements (list): List of elements (node1, node2, A, I, E_material)
        D (Vector): Global displacement vector
        E (list): DOF numbering matrix
        geometry (FrameGeometry): Geometry object for length/angle computation
    
    Returns:
        element_forces (list): List of forces for each element
    
    Assumptions:
        - frame_elements are ordered by index
        - D has been solved from K * D = F
    """
    element_forces = []
    
    for elem_idx, element in enumerate(frame_elements):
        node1, node2, A, I, E_material = element
        
        # Get length and angle from geometry
        L = geometry.get_element_length(node1, node2)
        angle = geometry.get_element_angle(node1, node2)
        
        # Extract displacements
        d_global = extract_element_displacements(node1, node2, D, E)
        
        # Transform to local coordinates
        d_local = transform_to_local_coords(d_global, angle)
        
        # Compute local stiffness
        k_prime = compute_local_stiffness(A, I, E_material, L)
        
        # Compute member forces
        f_local = compute_member_forces(k_prime, d_local)
        
        element_forces.append(f_local)
    
    return element_forces


def print_element_forces(element_forces):
    """
    Print member forces for all elements.
    
    Args:
        element_forces (list): List of forces for each element
    
    Returns:
        None
    """
    print("\n" + "="*70)
    print("MEMBER FORCES (LOCAL COORDINATES)")
    print("="*70)
    print("Format: [Axial1, Shear1, Moment1, Axial2, Shear2, Moment2]\n")
    
    for elem_idx, f_local in enumerate(element_forces):
        print(f"Element {elem_idx}:")
        print(f"  Node 1: Axial={f_local[0]:10.4f}, Shear={f_local[1]:10.4f}, Moment={f_local[2]:10.4f}")
        print(f"  Node 2: Axial={f_local[3]:10.4f}, Shear={f_local[4]:10.4f}, Moment={f_local[5]:10.4f}")
        print()
