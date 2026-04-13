"""
OOP Quality Tests for CE4011 Assignment 3 Structural Solver
===========================================================

Tests for object-oriented design, inheritance, polymorphism, and encapsulation.
Verifies that the abstract/concrete class hierarchy and relationship management
work correctly without testing numerical results.

Tolerances used throughout:
  Integer/count checks: exact equality
  Object reference checks: identity verification (is/is not)
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parents[1]))

import pytest
from model import (
    Node, Material, Section, Element, FrameElement, TrussElement, Structure
)


class TestObjectCreation:
    """Verify objects are created in correct initial state."""

    def test_node_creation_minimal(self):
        """Test Node creation with minimal parameters."""
        node = Node(0, 0.0, 0.0)
        assert node.id == 0
        assert node.x == 0.0
        assert node.y == 0.0
        assert node.restraints["ux"] is False
        assert node.restraints["uy"] is False
        assert node.restraints["rz"] is False

    def test_node_creation_with_restraints(self):
        """Test Node creation with explicit restraints."""
        node = Node(1, 1.5, 2.5)
        node.set_restraints(True, False, True)
        assert node.restraints["ux"] is True
        assert node.restraints["uy"] is False
        assert node.restraints["rz"] is True

    def test_material_creation(self):
        """Test Material object creation."""
        mat = Material("steel", 2.1e8)
        assert mat.id == "steel"
        assert mat.E == 2.1e8

    def test_section_creation(self):
        """Test Section object creation."""
        sec = Section("beam_section", 0.5, 0.08)
        assert sec.id == "beam_section"
        assert sec.A == 0.5
        assert sec.I == 0.08

    def test_frame_element_creation(self):
        """Test FrameElement instantiation."""
        node_i = Node(0, 0.0, 0.0)
        node_j = Node(1, 1.0, 0.0)
        mat = Material("m1", 1e8)
        sec = Section("s1", 0.1, 0.001)
        
        elem = FrameElement(1, node_i, node_j, mat, sec)
        assert elem.id == 1
        assert elem.node_i is node_i
        assert elem.node_j is node_j
        assert elem.material is mat
        assert elem.section is sec
        assert elem.release_start is False
        assert elem.release_end is False

    def test_frame_element_with_releases(self):
        """Test FrameElement with end releases."""
        node_i = Node(0, 0.0, 0.0)
        node_j = Node(1, 1.0, 0.0)
        mat = Material("m1", 1e8)
        sec = Section("s1", 0.1, 0.001)
        
        elem = FrameElement(1, node_i, node_j, mat, sec, release_start=True, release_end=True)
        assert elem.release_start is True
        assert elem.release_end is True

    def test_truss_element_creation(self):
        """Test TrussElement instantiation."""
        node_i = Node(0, 0.0, 0.0)
        node_j = Node(1, 1.0, 0.0)
        mat = Material("m1", 1e8)
        sec = Section("s1", 0.01, 0.0)
        
        elem = TrussElement(1, node_i, node_j, mat, sec)
        assert elem.id == 1
        assert elem.node_i is node_i
        assert elem.node_j is node_j


class TestStructureConstruction:
    """Verify Structure.from_dict() correctly builds object graph."""

    def test_structure_from_dict_minimal(self):
        """Test Structure creation from dict with minimal valid data."""
        data = {
            "nodes": [
                {"id": 0, "x": 0.0, "y": 0.0, "restraints": {"ux": True, "uy": True, "rz": True}},
                {"id": 1, "x": 1.0, "y": 0.0},
            ],
            "materials": [
                {"id": "m1", "E": 1e8},
            ],
            "sections": [
                {"id": "s1", "A": 0.01, "I": 0.0},
            ],
            "elements": [
                {"id": 1, "type": "truss", "node_i": 0, "node_j": 1, "material": "m1", "section": "s1"},
            ],
            "nodal_loads": [],
        }
        
        structure = Structure.from_dict(data)
        
        assert len(structure.nodes) == 2
        assert len(structure.materials) == 1
        assert len(structure.sections) == 1
        assert len(structure.elements) == 1

    def test_structure_node_count_matches(self):
        """Verify Structure has correct number of nodes after from_dict."""
        data = {
            "nodes": [
                {"id": i, "x": float(i), "y": 0.0}
                for i in range(5)
            ],
            "materials": [{"id": "m1", "E": 1e8}],
            "sections": [{"id": "s1", "A": 0.01, "I": 0.0}],
            "elements": [],
            "nodal_loads": [],
        }
        
        structure = Structure.from_dict(data)
        assert len(structure.nodes) == 5

    def test_structure_element_count_matches(self):
        """Verify Structure has correct number of elements after from_dict."""
        data = {
            "nodes": [
                {"id": 0, "x": 0.0, "y": 0.0},
                {"id": 1, "x": 1.0, "y": 0.0},
                {"id": 2, "x": 2.0, "y": 0.0},
            ],
            "materials": [{"id": "m1", "E": 1e8}],
            "sections": [{"id": "s1", "A": 0.01, "I": 0.0}],
            "elements": [
                {"id": 1, "type": "truss", "node_i": 0, "node_j": 1, "material": "m1", "section": "s1"},
                {"id": 2, "type": "truss", "node_i": 1, "node_j": 2, "material": "m1", "section": "s1"},
            ],
            "nodal_loads": [],
        }
        
        structure = Structure.from_dict(data)
        assert len(structure.elements) == 2


class TestAssociations:
    """Verify object relationships and shared references."""

    def test_shared_material_reference(self):
        """Test that multiple elements can reference the same Material object."""
        mat = Material("steel", 2e8)
        mat_id = id(mat)  # Store object identity
        
        section = Section("s1", 0.1, 0.001)
        node_i = Node(0, 0.0, 0.0)
        node_j = Node(1, 1.0, 0.0)
        
        elem1 = FrameElement(1, node_i, node_j, mat, section)
        elem2 = FrameElement(2, node_i, node_j, mat, section)
        
        # Verify both elements reference the SAME material object
        assert id(elem1.material) == mat_id
        assert id(elem2.material) == mat_id
        assert elem1.material is elem2.material

    def test_shared_section_reference(self):
        """Test that multiple elements can reference the same Section object."""
        section = Section("beam", 0.2, 0.004)
        section_id = id(section)
        
        mat = Material("m1", 2e8)
        node_i = Node(0, 0.0, 0.0)
        node_j = Node(1, 1.0, 0.0)
        
        elem1 = FrameElement(1, node_i, node_j, mat, section)
        elem2 = FrameElement(2, node_i, node_j, mat, section)
        
        # Verify both elements reference the SAME section object
        assert id(elem1.section) == section_id
        assert id(elem2.section) == section_id
        assert elem1.section is elem2.section

    def test_element_node_references_correct(self):
        """Test that elements hold correct node references."""
        node_i = Node(0, 0.0, 0.0)
        node_j = Node(1, 5.0, 0.0)
        
        mat = Material("m1", 1e8)
        sec = Section("s1", 0.01, 0.001)  # Frame needs nonzero I
        
        elem = FrameElement(1, node_i, node_j, mat, sec)
        
        # Verify element references the exact node objects
        assert elem.node_i is node_i
        assert elem.node_j is node_j
        assert id(elem.node_i) == id(node_i)
        assert id(elem.node_j) == id(node_j)


class TestPolymorphism:
    """Verify abstract and concrete class dispatch."""

    def test_frame_element_is_element_subclass(self):
        """Test that FrameElement is a subclass of Element."""
        assert issubclass(FrameElement, Element)

    def test_truss_element_is_element_subclass(self):
        """Test that TrussElement is a subclass of Element."""
        assert issubclass(TrussElement, Element)

    def test_frame_element_isinstance_check(self):
        """Test isinstance checks for FrameElement."""
        node_i = Node(0, 0.0, 0.0)
        node_j = Node(1, 1.0, 0.0)
        mat = Material("m1", 1e8)
        sec = Section("s1", 0.1, 0.001)
        
        frame_elem = FrameElement(1, node_i, node_j, mat, sec)
        
        assert isinstance(frame_elem, FrameElement)
        assert isinstance(frame_elem, Element)

    def test_truss_element_isinstance_check(self):
        """Test isinstance checks for TrussElement."""
        node_i = Node(0, 0.0, 0.0)
        node_j = Node(1, 1.0, 0.0)
        mat = Material("m1", 1e8)
        sec = Section("s1", 0.01, 0.0)
        
        truss_elem = TrussElement(1, node_i, node_j, mat, sec)
        
        assert isinstance(truss_elem, TrussElement)
        assert isinstance(truss_elem, Element)

    def test_frame_local_stiffness_shape(self):
        """Test that frame local_stiffness() returns 6x6 matrix."""
        node_i = Node(0, 0.0, 0.0)
        node_j = Node(1, 4.0, 0.0)
        mat = Material("m1", 10.0)
        sec = Section("s1", 2.0, 3.0)
        
        frame_elem = FrameElement(1, node_i, node_j, mat, sec)
        k_local = frame_elem.local_stiffness()
        
        assert len(k_local) == 6
        assert all(len(row) == 6 for row in k_local)
        assert isinstance(k_local, list)

    def test_truss_local_stiffness_shape(self):
        """Test that truss local_stiffness() returns 6x6 matrix."""
        node_i = Node(0, 0.0, 0.0)
        node_j = Node(1, 2.0, 0.0)
        mat = Material("m1", 100.0)
        sec = Section("s1", 1.0, 0.0)
        
        truss_elem = TrussElement(1, node_i, node_j, mat, sec)
        k_local = truss_elem.local_stiffness()
        
        assert len(k_local) == 6
        assert all(len(row) == 6 for row in k_local)
        assert isinstance(k_local, list)

    def test_truss_ignores_transverse_loads(self):
        """Test that TrussElement.equivalent_nodal_load_local ignores transverse loads."""
        node_i = Node(0, 0.0, 0.0)
        node_j = Node(1, 2.0, 0.0)
        mat = Material("m1", 100.0)
        sec = Section("s1", 1.0, 0.0)
        
        truss_elem = TrussElement(1, node_i, node_j, mat, sec)
        # Add transverse (local_y) UDL
        truss_elem.member_loads.append({"type": "udl", "direction": "local_y", "w": -100.0})
        
        f_eq = truss_elem.equivalent_nodal_load_local()
        
        # Transverse load components should be zero (indices 1, 4)
        assert f_eq[1] == 0.0
        assert f_eq[4] == 0.0


class TestInheritanceProperties:
    """Verify inherited methods work correctly for both concrete classes."""

    def test_frame_length_method(self):
        """Test that FrameElement.length() works correctly."""
        node_i = Node(0, 0.0, 0.0)
        node_j = Node(1, 3.0, 4.0)  # 3-4-5 triangle
        mat = Material("m1", 1e8)
        sec = Section("s1", 0.1, 0.001)
        
        elem = FrameElement(1, node_i, node_j, mat, sec)
        length = elem.length()
        
        assert 4.99 < length < 5.01  # 5.0 with tolerance

    def test_truss_length_method(self):
        """Test that TrussElement.length() works correctly."""
        node_i = Node(0, 0.0, 0.0)
        node_j = Node(1, 3.0, 0.0)
        mat = Material("m1", 1e8)
        sec = Section("s1", 0.01, 0.0)
        
        elem = TrussElement(1, node_i, node_j, mat, sec)
        length = elem.length()
        
        assert length == 3.0

    def test_frame_angle_method(self):
        """Test that FrameElement.angle() returns correct orientation."""
        import math
        node_i = Node(0, 0.0, 0.0)
        node_j = Node(1, 0.0, 1.0)  # Vertical element
        mat = Material("m1", 1e8)
        sec = Section("s1", 0.1, 0.001)
        
        elem = FrameElement(1, node_i, node_j, mat, sec)
        angle = elem.angle()
        
        # Vertical element should have angle near π/2
        assert abs(angle - math.pi / 2) < 1e-10


class TestMemberLoads:
    """Verify member load handling."""

    def test_frame_member_load_storage(self):
        """Test that member loads are stored on frame elements."""
        node_i = Node(0, 0.0, 0.0)
        node_j = Node(1, 1.0, 0.0)
        mat = Material("m1", 1e8)
        sec = Section("s1", 0.1, 0.001)
        
        elem = FrameElement(1, node_i, node_j, mat, sec)
        elem.member_loads.append({"type": "udl", "direction": "local_y", "w": -10.0})
        
        assert len(elem.member_loads) == 1
        assert elem.member_loads[0]["type"] == "udl"
        assert elem.member_loads[0]["w"] == -10.0

    def test_truss_member_load_storage(self):
        """Test that member loads are stored on truss elements."""
        node_i = Node(0, 0.0, 0.0)
        node_j = Node(1, 2.0, 0.0)
        mat = Material("m1", 1e8)
        sec = Section("s1", 0.01, 0.0)
        
        elem = TrussElement(1, node_i, node_j, mat, sec)
        elem.member_loads.append({"type": "point", "direction": "local_x", "p": 100.0, "a": 1.0})
        
        assert len(elem.member_loads) == 1
        assert elem.member_loads[0]["p"] == 100.0
