import pytest

from q1_matrix_library.symmetric_sparse_matrix import SymmetricSparseMatrix
from q1_matrix_library.vector import Vector
from q1_matrix_library.conjugate_gradient_solver import ConjugateGradientSolver


def test_conjugate_gradient_solver_smoke():
    K = SymmetricSparseMatrix(3)

    K.add(0, 0, 10)
    K.add(0, 1, 2)
    K.add(1, 1, 7)
    K.add(1, 2, 3)
    K.add(2, 2, 5)

    b = Vector(3)
    b.values = [12, 12, 8]

    solver = ConjugateGradientSolver()

    x = solver.solve(K, b)
    y = K.matvec(x)

    assert x.size == 3
    assert y.values[0] == pytest.approx(12.0, abs=1e-5)
    assert y.values[1] == pytest.approx(12.0, abs=1e-5)
    assert y.values[2] == pytest.approx(8.0, abs=1e-5)