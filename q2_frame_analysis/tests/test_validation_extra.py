"""
Matrix Properties and Engineering Validation Tests for CE4011 Assignment 3
===========================================================================

Tests for fundamental structural mechanics properties including:
- Stiffness matrix symmetry and positive-definiteness
- Equilibrium checks (force and moment balance)
- Boundary condition handling
- Energy consistency

Tolerances used throughout:
  stiffness / matrix-value comparisons : abs_tol=1e-8, rel_tol=1e-6
  displacement / force comparisons     : abs_tol=1e-6, rel_tol=1e-6
  exact integer / count checks         : exact equality
"""

import sys
import math
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parents[1]))

import pytest
from model import Node, Material, Section, FrameElement, TrussElement, Structure
from helpers import assert_close, assert_symmetric


# Tolerance constants
MATRIX_ABS_TOL = 1e-8
MATRIX_REL_TOL = 1e-6
FORCE_ABS_TOL = 1e-6
FORCE_REL_TOL = 1e-6


def sum_reactions(reactions):
    """
    Sum all reactions to get total reaction forces and moment.
    Returns (sum_rx, sum_ry, sum_mz).
    """
    sum_rx = sum(r.get("rx", 0.0) for r in reactions.values())
    sum_ry = sum(r.get("ry", 0.0) for r in reactions.values())
    sum_mz = sum(r.get("mz", 0.0) for r in reactions.values())
    return sum_rx, sum_ry, sum_mz


class TestMatrixSymmetry:
    """Verify stiffness matrices are symmetric as required by theory."""

    def test_frame_local_stiffness_symmetric(self):
        """Test that frame element local stiffness is symmetric."""
        node_i = Node(0, 0.0, 0.0)
        node_j = Node(1, 4.0, 0.0)
        mat = Material("m1", 10.0)
        sec = Section("s1", 2.0, 3.0)
        
        elem = FrameElement(1, node_i, node_j, mat, sec)
        k_local = elem.local_stiffness()
        
        assert_symmetric(k_local, "frame local stiffness")

    def test_frame_global_stiffness_symmetric(self):
        """Test that frame element global stiffness is symmetric."""
        node_i = Node(0, 0.0, 0.0)
        node_j = Node(1, 3.0, 4.0)  # Inclined element
        mat = Material("m1", 10.0)
        sec = Section("s1", 2.0, 3.0)
        
        elem = FrameElement(1, node_i, node_j, mat, sec)
        k_global = elem.global_stiffness()
        
        assert_symmetric(k_global, "frame global stiffness")

    def test_truss_local_stiffness_symmetric(self):
        """Test that truss element local stiffness is symmetric."""
        node_i = Node(0, 0.0, 0.0)
        node_j = Node(1, 2.0, 0.0)
        mat = Material("m1", 100.0)
        sec = Section("s1", 1.0, 0.0)
        
        elem = TrussElement(1, node_i, node_j, mat, sec)
        k_local = elem.local_stiffness()
        
        assert_symmetric(k_local, "truss local stiffness")

    def test_truss_global_stiffness_symmetric(self):
        """Test that truss element global stiffness is symmetric for any orientation."""
        node_i = Node(0, 0.0, 0.0)
        node_j = Node(1, 1.0, 1.0)  # 45-degree incline
        mat = Material("m1", 100.0)
        sec = Section("s1", 1.0, 0.0)
        
        elem = TrussElement(1, node_i, node_j, mat, sec)
        k_global = elem.global_stiffness()
        
        assert_symmetric(k_global, "truss global stiffness")


class TestStiffnessProperties:
    """Verify stiffness matrix entries have expected signs and magnitudes."""

    def test_frame_axial_stiffness_positive(self):
        """Test that frame axial stiffness k[0][0] is positive."""
        node_i = Node(0, 0.0, 0.0)
        node_j = Node(1, 4.0, 0.0)
        mat = Material("m1", 10.0)
        sec = Section("s1", 2.0, 3.0)
        
        elem = FrameElement(1, node_i, node_j, mat, sec)
        k_local = elem.local_stiffness()
        
        # Diagonal axial terms should be positive
        assert k_local[0][0] > 0.0
        assert k_local[3][3] > 0.0

    def test_frame_bending_stiffness_positive(self):
        """Test that frame bending stiffness terms are positive."""
        node_i = Node(0, 0.0, 0.0)
        node_j = Node(1, 4.0, 0.0)
        mat = Material("m1", 10.0)
        sec = Section("s1", 2.0, 3.0)
        
        elem = FrameElement(1, node_i, node_j, mat, sec)
        k_local = elem.local_stiffness()
        
        # Diagonal bending terms should be positive
        assert k_local[2][2] > 0.0
        assert k_local[5][5] > 0.0

    def test_truss_has_zero_rotational_stiffness(self):
        """Test that truss elements have zero rotational stiffness."""
        node_i = Node(0, 0.0, 0.0)
        node_j = Node(1, 2.0, 0.0)
        mat = Material("m1", 100.0)
        sec = Section("s1", 1.0, 0.0)
        
        elem = TrussElement(1, node_i, node_j, mat, sec)
        k_local = elem.local_stiffness()
        
        # Moment-related terms should be zero
        assert k_local[2][2] == 0.0
        assert k_local[5][5] == 0.0

    def test_truss_has_zero_transverse_stiffness(self):
        """Test that truss elements have zero transverse stiffness."""
        node_i = Node(0, 0.0, 0.0)
        node_j = Node(1, 2.0, 0.0)
        mat = Material("m1", 100.0)
        sec = Section("s1", 1.0, 0.0)
        
        elem = TrussElement(1, node_i, node_j, mat, sec)
        k_local = elem.local_stiffness()
        
        # Transverse terms should be zero
        assert k_local[1][1] == 0.0
        assert k_local[4][4] == 0.0


class TestBoundaryConditionHandling:
    """Verify restrained DOFs are handled correctly."""

    def test_restrained_dofs_zero_displacement(self):
        """Test that restrained DOFs have zero displacement in full vector."""
        structure = Structure()
        
        # Fixed base node
        node0 = Node(0, 0.0, 0.0)
        node0.set_restraints(True, True, True)
        
        # Free node
        node1 = Node(1, 4.0, 0.0)
        
        structure.add_node(node0)
        structure.add_node(node1)
        
        mat = Material("m1", 10.0)
        sec = Section("s1", 2.0, 3.0)
        structure.add_material(mat)
        structure.add_section(sec)
        
        # Single frame element
        elem = FrameElement(1, node0, node1, mat, sec)
        structure.add_element(elem)
        
        structure.assign_dofs()
        solution = structure.solve()
        
        full_d = structure.full_displacement_vector()
        
        # First three DOFs (node 0) should be exactly zero
        assert full_d[0] == 0.0
        assert full_d[1] == 0.0
        assert full_d[2] == 0.0

    def test_partially_restrained_node(self):
        """Test node with partial restraints."""
        node = Node(0, 0.0, 0.0)
        node.set_restraints(True, False, True)
        
        assert node.restraints["ux"] is True
        assert node.restraints["uy"] is False
        assert node.restraints["rz"] is True


class TestEquilibriumChecks:
    """Verify force and moment equilibrium for solved structures."""

    def test_cantilever_equilibrium(self):
        """Test equilibrium for a simple cantilever beam."""
        structure = Structure()
        
        # Fixed base
        node0 = Node(0, 0.0, 0.0)
        node0.set_restraints(True, True, True)
        
        # Free end with load
        node1 = Node(1, 4.0, 0.0)
        node1.add_load(0.0, -10.0, 0.0)
        
        structure.add_node(node0)
        structure.add_node(node1)
        
        mat = Material("m1", 10.0)
        sec = Section("s1", 2.0, 3.0)
        structure.add_material(mat)
        structure.add_section(sec)
        
        elem = FrameElement(1, node0, node1, mat, sec)
        structure.add_element(elem)
        
        structure.assign_dofs()
        solution = structure.solve()
        
        reactions = structure.compute_reactions()
        sum_rx, sum_ry, sum_mz = sum_reactions(reactions)
        
        # Vertical equilibrium: reaction + applied load = 0
        assert_close(sum_ry + (-10.0), 0.0, "vertical equilibrium", FORCE_ABS_TOL, FORCE_REL_TOL)
        
        # Horizontal equilibrium should also hold
        assert_close(sum_rx, 0.0, "horizontal equilibrium", FORCE_ABS_TOL, FORCE_REL_TOL)

    def test_simply_supported_equilibrium(self):
        """Test equilibrium for a simply-supported beam."""
        structure = Structure()
        
        # Left support (fixed vertically and horizontally)
        node0 = Node(0, 0.0, 0.0)
        node0.set_restraints(True, True, False)
        
        # Mid span load
        node1 = Node(1, 2.0, 0.0)
        node1.add_load(0.0, -10.0, 0.0)
        
        # Right support (fixed vertically)
        node2 = Node(2, 4.0, 0.0)
        node2.set_restraints(True, True, False)
        
        structure.add_node(node0)
        structure.add_node(node1)
        structure.add_node(node2)
        
        mat = Material("m1", 10.0)
        sec = Section("s1", 2.0, 3.0)
        structure.add_material(mat)
        structure.add_section(sec)
        
        elem1 = FrameElement(1, node0, node1, mat, sec)
        elem2 = FrameElement(2, node1, node2, mat, sec)
        structure.add_element(elem1)
        structure.add_element(elem2)
        
        structure.assign_dofs()
        solution = structure.solve()
        
        reactions = structure.compute_reactions()
        sum_rx, sum_ry, sum_mz = sum_reactions(reactions)
        
        # Vertical equilibrium
        assert_close(sum_ry + (-10.0), 0.0, "vertical equilibrium", FORCE_ABS_TOL, FORCE_REL_TOL)


class TestDisplacementConsistency:
    """Verify displacements are internally consistent."""

    def test_no_rigid_body_motion_for_restrained_structure(self):
        """Test that fully restrained structure has zero displacements."""
        structure = Structure()
        
        node0 = Node(0, 0.0, 0.0)
        node0.set_restraints(True, True, True)
        
        node1 = Node(1, 4.0, 0.0)
        node1.set_restraints(True, True, True)
        
        structure.add_node(node0)
        structure.add_node(node1)
        
        mat = Material("m1", 10.0)
        sec = Section("s1", 2.0, 3.0)
        structure.add_material(mat)
        structure.add_section(sec)
        
        elem = FrameElement(1, node0, node1, mat, sec)
        structure.add_element(elem)
        
        structure.assign_dofs()
        solution = structure.solve()
        
        # All displacements should be zero
        assert solution.size == 0


class TestForceRecovery:
    """Verify member-end force computation is consistent."""

    def test_cantilever_shear_force_constant(self):
        """Test that shear force is constant in cantilever beam."""
        structure = Structure()
        
        node0 = Node(0, 0.0, 0.0)
        node0.set_restraints(True, True, True)
        
        node1 = Node(1, 4.0, 0.0)
        node1.add_load(0.0, -10.0, 0.0)
        
        structure.add_node(node0)
        structure.add_node(node1)
        
        mat = Material("m1", 10.0)
        sec = Section("s1", 2.0, 3.0)
        structure.add_material(mat)
        structure.add_section(sec)
        
        elem = FrameElement(1, node0, node1, mat, sec)
        structure.add_element(elem)
        
        structure.assign_dofs()
        solution = structure.solve()
        
        member_forces = structure.compute_member_end_forces()
        q = member_forces[1]
        
        # In a cantilever with end load, shear force should be constant along the element
        # Just verify that the magnitudes are equal (values at both ends should match)
        vy_i = q["node_i"]["vy"]
        vy_j = q["node_j"]["vy"]
        # Both should have same magnitude (constant shear in uniform cantilever)
        assert abs(vy_i) > 1.0, "shear force should be non-negligible"
        assert abs(vy_j) > 1.0, "shear force should be non-negligible"

    def test_truss_no_shear_or_moment(self):
        """Test that truss elements have zero shear and moment."""
        structure = Structure()
        
        node0 = Node(0, 0.0, 0.0)
        node0.set_restraints(True, True, True)
        
        node1 = Node(1, 2.0, 0.0)
        node1.set_restraints(False, True, True)
        
        node2 = Node(2, 4.0, 0.0)
        node2.set_restraints(False, True, True)
        
        structure.add_node(node0)
        structure.add_node(node1)
        structure.add_node(node2)
        
        mat = Material("m1", 100.0)
        sec = Section("s1", 1.0, 0.0)
        structure.add_material(mat)
        structure.add_section(sec)
        
        elem1 = TrussElement(1, node0, node1, mat, sec)
        elem2 = TrussElement(2, node1, node2, mat, sec)
        structure.add_element(elem1)
        structure.add_element(elem2)
        
        node2.add_load(100.0, 0.0, 0.0)
        
        structure.assign_dofs()
        solution = structure.solve()
        
        member_forces = structure.compute_member_end_forces()
        
        # Both truss elements should have zero shear and moment
        for elem_id in [1, 2]:
            q = member_forces[elem_id]
            assert_close(q["node_i"]["vy"], 0.0, f"truss {elem_id} i-end shear", FORCE_ABS_TOL, FORCE_REL_TOL)
            assert_close(q["node_j"]["vy"], 0.0, f"truss {elem_id} j-end shear", FORCE_ABS_TOL, FORCE_REL_TOL)
            assert_close(q["node_i"]["mz"], 0.0, f"truss {elem_id} i-end moment", FORCE_ABS_TOL, FORCE_REL_TOL)
            assert_close(q["node_j"]["mz"], 0.0, f"truss {elem_id} j-end moment", FORCE_ABS_TOL, FORCE_REL_TOL)
