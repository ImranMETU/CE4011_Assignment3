"""Pytest integration/regression tests for the matrix library.

These tests keep practical end-to-end checks while avoiding duplicated,
fine-grained OOP contract testing covered in test_oop_unit.py.
"""

import pytest

from q1_matrix_library.conjugate_gradient_solver import ConjugateGradientSolver
from q1_matrix_library.symmetric_sparse_matrix import SymmetricSparseMatrix
from q1_matrix_library.vector import Vector


def test_vector_matrix_workflow_smoke():
    A = SymmetricSparseMatrix(3)
    A.add(0, 0, 10)
    A.add(0, 1, 2)
    A.add(1, 1, 7)
    A.add(1, 2, 3)
    A.add(2, 2, 5)

    x = Vector(3)
    x.values = [1.0, 1.0, 1.0]

    y = A.matvec(x)
    assert y.values == [12.0, 12.0, 8.0]


def test_solver_converges_small_spd_system():
    A = SymmetricSparseMatrix(3)
    A.add(0, 0, 10)
    A.add(0, 1, 2)
    A.add(1, 1, 7)
    A.add(1, 2, 3)
    A.add(2, 2, 5)

    b = Vector(3)
    b.values = [12.0, 12.0, 8.0]

    solver = ConjugateGradientSolver(tol=1e-8, max_iter=100)
    x = solver.solve(A, b)

    y = A.matvec(x)
    residual = [abs(b.values[i] - y.values[i]) for i in range(3)]

    assert x.size == 3
    assert max(residual) < 1e-5


@pytest.mark.parametrize("tol", [0, -1e-6])
def test_solver_rejects_invalid_tolerance(tol):
    with pytest.raises(ValueError):
        ConjugateGradientSolver(tol=tol, max_iter=10)


@pytest.mark.parametrize("max_iter", [0, -3])
def test_solver_rejects_invalid_max_iter(max_iter):
    with pytest.raises(ValueError):
        ConjugateGradientSolver(tol=1e-6, max_iter=max_iter)


def test_dimension_mismatch_raises_value_error():
    A = SymmetricSparseMatrix(3)
    b = Vector(5)

    solver = ConjugateGradientSolver()
    with pytest.raises(ValueError):
        solver.solve(A, b)


def test_structural_analysis_small_truss_regression():
    # Reduced 1-DOF problem from a 2-node truss with k = 100 and F = 10.
    K_reduced = SymmetricSparseMatrix(1)
    K_reduced.set(0, 0, 100.0)

    f = Vector(1)
    f.values = [10.0]

    solver = ConjugateGradientSolver(tol=1e-10, max_iter=20)
    u = solver.solve(K_reduced, f)

    assert u.values[0] == pytest.approx(0.1, abs=1e-8)
