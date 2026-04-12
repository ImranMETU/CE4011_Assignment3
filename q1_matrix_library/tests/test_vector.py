from q1_matrix_library.vector import Vector


def test_vector_dot_product_smoke():
    v = Vector(3)
    v.values = [1, 2, 3]

    w = Vector(3)
    w.values = [4, 5, 6]

    assert v.dot(w) == 32


def test_vector_norm_smoke():
    v = Vector(3)
    v.values = [1, 2, 3]

    assert v.norm() == (14 ** 0.5)