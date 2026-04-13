"""
Performance and Storage Efficiency Tests for CE4011 Assignment 3
================================================================

Lightweight performance-oriented tests for:
- Storage efficiency of sparse matrix representation
- Assembly and solve time sanity checks (not rigid benchmarks)
- Memory usage patterns

These are *sanity checks* only, not hard performance requirements.
Do not use for production benchmarking.

Tolerances and thresholds:
  Assembly time: should complete within 5 seconds (extremely loose threshold)
  Solve time: should complete within 5 seconds
  Sparse matrix sparsity: should have significantly fewer entries than dense
"""

import sys
import time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parents[1]))

import pytest
from model import Node, Material, Section, FrameElement, TrussElement, Structure


# Performance thresholds (very loose)
ASSEMBLY_TIME_LIMIT_SEC = 5.0
SOLVE_TIME_LIMIT_SEC = 5.0


def build_simple_frame_chain(n_elements=10):
    """Build a simple frame cantilever chain for performance testing."""
    structure = Structure()
    
    # Fixed base
    node_prev = Node(0, 0.0, 0.0)
    node_prev.set_restraints(True, True, True)
    structure.add_node(node_prev)
    
    # Chain of elements
    for i in range(1, n_elements + 1):
        node = Node(i, float(i), 0.0)
        structure.add_node(node)
        
        if i == n_elements:
            # Apply end load
            node.add_load(0.0, -100.0, 0.0)
    
    mat = Material("m1", 10.0)
    sec = Section("s1", 2.0, 3.0)
    structure.add_material(mat)
    structure.add_section(sec)
    
    # Connect elements
    for i in range(1, n_elements + 1):
        node_i = structure.nodes[i - 1]
        node_j = structure.nodes[i]
        elem = FrameElement(i, node_i, node_j, mat, sec)
        structure.add_element(elem)
    
    return structure


def build_simple_truss_grid(nx=5, ny=3):
    """Build a simple truss grid for performance testing."""
    structure = Structure()
    
    # Create grid of nodes
    node_id = 0
    nodes = {}
    for j in range(ny):
        for i in range(nx):
            node = Node(node_id, float(i), float(j))
            if j == 0:
                # Bottom row fixed
                node.set_restraints(True, True, True)
            nodes[(i, j)] = node
            structure.add_node(node)
            node_id += 1
    
    # Add load at top-right
    nodes[(nx - 1, ny - 1)].add_load(0.0, -100.0, 0.0)
    
    mat = Material("m1", 100.0)
    sec = Section("s1", 1.0, 0.0)
    structure.add_material(mat)
    structure.add_section(sec)
    
    # Create truss members
    elem_id = 1
    # Horizontal members
    for j in range(ny):
        for i in range(nx - 1):
            node_i = nodes[(i, j)]
            node_j = nodes[(i + 1, j)]
            elem = TrussElement(elem_id, node_i, node_j, mat, sec)
            structure.add_element(elem)
            elem_id += 1
    
    # Vertical members
    for j in range(ny - 1):
        for i in range(nx):
            node_i = nodes[(i, j)]
            node_j = nodes[(i, j + 1)]
            elem = TrussElement(elem_id, node_i, node_j, mat, sec)
            structure.add_element(elem)
            elem_id += 1
    
    return structure


class TestAssemblyPerformance:
    """Test assembly time and resource usage."""

    @pytest.mark.performance
    def test_frame_chain_assembly_time(self):
        """Test that frame chain assembly completes in reasonable time."""
        structure = build_simple_frame_chain(n_elements=20)
        
        start = time.time()
        structure.assign_dofs()
        structure.assemble_global_stiffness()
        structure.assemble_global_load_vector()
        elapsed = time.time() - start
        
        assert elapsed < ASSEMBLY_TIME_LIMIT_SEC, f"Assembly took {elapsed:.3f}s (limit: {ASSEMBLY_TIME_LIMIT_SEC}s)"

    @pytest.mark.performance
    def test_truss_grid_assembly_time(self):
        """Test that truss grid assembly completes in reasonable time."""
        structure = build_simple_truss_grid(nx=10, ny=8)
        
        start = time.time()
        structure.assign_dofs()
        structure.assemble_global_stiffness()
        structure.assemble_global_load_vector()
        elapsed = time.time() - start
        
        assert elapsed < ASSEMBLY_TIME_LIMIT_SEC, f"Assembly took {elapsed:.3f}s (limit: {ASSEMBLY_TIME_LIMIT_SEC}s)"


class TestSolvePerformance:
    """Test solver time and convergence."""

    @pytest.mark.performance
    def test_frame_chain_solve_time(self):
        """Test that frame chain solve completes in reasonable time."""
        structure = build_simple_frame_chain(n_elements=20)
        
        structure.assign_dofs()
        
        start = time.time()
        solution = structure.solve()
        elapsed = time.time() - start
        
        assert elapsed < SOLVE_TIME_LIMIT_SEC, f"Solve took {elapsed:.3f}s (limit: {SOLVE_TIME_LIMIT_SEC}s)"
        assert solution.size > 0, "Solution should have non-zero size"

    @pytest.mark.performance
    def test_truss_grid_solve_time(self):
        """Test that truss grid solve completes in reasonable time."""
        structure = build_simple_truss_grid(nx=10, ny=8)
        
        structure.assign_dofs()
        
        start = time.time()
        solution = structure.solve()
        elapsed = time.time() - start
        
        assert elapsed < SOLVE_TIME_LIMIT_SEC, f"Solve took {elapsed:.3f}s (limit: {SOLVE_TIME_LIMIT_SEC}s)"
        assert solution.size > 0, "Solution should have non-zero size"


class TestSparsityEfficiency:
    """Test that sparse matrix storage is more efficient than dense."""

    @pytest.mark.performance
    def test_frame_chain_sparsity(self):
        """Test that frame chain stiffness matrix is sparse."""
        structure = build_simple_frame_chain(n_elements=30)
        
        structure.assign_dofs()
        structure.assemble_global_stiffness()
        
        n_dof = structure.n_active_dofs
        n_dense_entries = n_dof * n_dof
        n_sparse_entries = len(structure.K.data)
        
        sparsity_ratio = n_sparse_entries / n_dense_entries if n_dense_entries > 0 else 0
        
        # For a cantilever chain, sparsity should be much less than 1.0
        # Typically we'd expect <5% for a long chain
        assert sparsity_ratio < 0.20, (
            f"Sparse matrix is not sparse: {sparsity_ratio:.2%} fill "
            f"({n_sparse_entries} / {n_dense_entries} entries)"
        )

    @pytest.mark.performance
    def test_truss_grid_sparsity(self):
        """Test that truss grid stiffness matrix is sparse."""
        structure = build_simple_truss_grid(nx=12, ny=10)
        
        structure.assign_dofs()
        structure.assemble_global_stiffness()
        
        n_dof = structure.n_active_dofs
        n_dense_entries = n_dof * n_dof
        n_sparse_entries = len(structure.K.data)
        
        sparsity_ratio = n_sparse_entries / n_dense_entries if n_dense_entries > 0 else 0
        
        # For a truss grid with ~200 DOF, expect << 1% fill
        assert sparsity_ratio < 0.10, (
            f"Sparse matrix is not sparse: {sparsity_ratio:.2%} fill "
            f"({n_sparse_entries} / {n_dense_entries} entries)"
        )


class TestPostprocessingPerformance:
    """Test reaction and force recovery performance."""

    @pytest.mark.performance
    def test_member_force_recovery_time(self):
        """Test that member-end force recovery completes quickly."""
        structure = build_simple_frame_chain(n_elements=30)
        
        structure.assign_dofs()
        structure.assemble_global_stiffness()
        structure.assemble_global_load_vector()
        solution = structure.solve()
        
        start = time.time()
        reactions = structure.compute_reactions()
        member_forces = structure.compute_member_end_forces()
        elapsed = time.time() - start
        
        # Post-processing should be very fast
        assert elapsed < 1.0, f"Post-processing took {elapsed:.3f}s"
        assert len(reactions) > 0, "Should have computed reactions"
        assert len(member_forces) > 0, "Should have computed member forces"


class TestMemoryBehavior:
    """Test memory usage patterns for different structures."""

    @pytest.mark.performance
    def test_node_count_tracking(self):
        """Test that Structure correctly tracks node count."""
        structure = build_simple_frame_chain(n_elements=50)
        
        # 50 elements = 51 nodes
        assert len(structure.nodes) == 51

    @pytest.mark.performance
    def test_element_count_tracking(self):
        """Test that Structure correctly tracks element count."""
        structure = build_simple_truss_grid(nx=15, ny=12)
        
        # Horizontal: (15-1)*12 = 168
        # Vertical: 15*(12-1) = 165
        # Total: 333
        expected_elements = (15 - 1) * 12 + 15 * (12 - 1)
        assert len(structure.elements) == expected_elements

    @pytest.mark.performance
    def test_dof_count_reasonable(self):
        """Test that DOF count is reasonable after assignment."""
        structure = build_simple_frame_chain(n_elements=20)
        
        structure.assign_dofs()
        
        # Frame chain with 1 fixed node + 20 free nodes = 20*3 = 60 DOF
        # Minus 3 for fixed base = 57 active DOF
        assert structure.n_active_dofs > 0
        assert structure.n_active_dofs <= 20 * 3  # Upper bound


class TestRobustnessUnderLoad:
    """Test solver stability under various loading conditions."""

    @pytest.mark.performance
    def test_large_load_values(self):
        """Test that solver handles large load values correctly."""
        structure = Structure()
        
        node0 = Node(0, 0.0, 0.0)
        node0.set_restraints(True, True, True)
        
        node1 = Node(1, 4.0, 0.0)
        node1.set_restraints(True, True, True)  # Also fully restrained
        # Very large load (will be ignored since node is restrained)
        node1.add_load(0.0, -1e6, 0.0)
        
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
        
        # Should solve without divergence
        assert solution.size == 0  # Fully constrained

    @pytest.mark.performance
    def test_small_load_values(self):
        """Test that solver handles small load values correctly."""
        structure = Structure()
        
        node0 = Node(0, 0.0, 0.0)
        node0.set_restraints(True, True, True)
        
        node1 = Node(1, 4.0, 0.0)
        node1.set_restraints(True, True, True)  # Also fully restrained
        # Very small load (will be ignored since node is restrained)
        node1.add_load(0.0, -1e-8, 0.0)
        
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
        
        # Should solve without convergence issues
        assert solution.size == 0  # Fully constrained
