from q1_matrix_library.symmetric_sparse_matrix import SymmetricSparseMatrix
from q1_matrix_library.vector import Vector


def test_sparse_matrix_matvec_smoke():
    K = SymmetricSparseMatrix(3)

    K.add(0, 0, 10)
    K.add(0, 1, 2)
    K.add(1, 1, 7)
    K.add(1, 2, 3)
    K.add(2, 2, 5)

    x = Vector(3)
    x.values = [1, 1, 1]

    y = K.matvec(x)

    assert y.values == [12.0, 12.0, 8.0]