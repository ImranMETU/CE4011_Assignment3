from math import isclose


REL_TOL = 1e-6
ABS_TOL = 1e-8


def as_dense_vector(vector):
    if isinstance(vector, list):
        return vector
    return [vector.get(i) for i in range(vector.size)]


def as_dense_matrix(matrix):
    if isinstance(matrix, list):
        return matrix
    return [[matrix.get(i, j) for j in range(matrix.size)] for i in range(matrix.size)]


def assert_close(actual, expected, message):
    assert isclose(actual, expected, rel_tol=REL_TOL, abs_tol=ABS_TOL), (
        f"{message}: expected {expected!r}, got {actual!r} "
        f"(rel_tol={REL_TOL}, abs_tol={ABS_TOL})"
    )


def assert_vector_close(actual, expected, message):
    actual_list = as_dense_vector(actual)
    expected_list = as_dense_vector(expected)
    assert len(actual_list) == len(expected_list), (
        f"{message}: expected vector length {len(expected_list)}, got {len(actual_list)}"
    )
    for index, (actual_value, expected_value) in enumerate(zip(actual_list, expected_list)):
        assert isclose(actual_value, expected_value, rel_tol=REL_TOL, abs_tol=ABS_TOL), (
            f"{message}: entry {index} expected {expected_value!r}, got {actual_value!r} "
            f"(rel_tol={REL_TOL}, abs_tol={ABS_TOL})"
        )


def assert_matrix_close(actual, expected, message):
    actual_matrix = as_dense_matrix(actual)
    expected_matrix = as_dense_matrix(expected)
    assert len(actual_matrix) == len(expected_matrix), (
        f"{message}: expected matrix size {len(expected_matrix)}x{len(expected_matrix)}, "
        f"got {len(actual_matrix)}x{len(actual_matrix)}"
    )
    for row_index, (actual_row, expected_row) in enumerate(zip(actual_matrix, expected_matrix)):
        assert len(actual_row) == len(expected_row), (
            f"{message}: row {row_index} expected length {len(expected_row)}, got {len(actual_row)}"
        )
        for col_index, (actual_value, expected_value) in enumerate(zip(actual_row, expected_row)):
            assert isclose(actual_value, expected_value, rel_tol=REL_TOL, abs_tol=ABS_TOL), (
                f"{message}: entry ({row_index}, {col_index}) expected {expected_value!r}, "
                f"got {actual_value!r} (rel_tol={REL_TOL}, abs_tol={ABS_TOL})"
            )


def assert_symmetric(matrix, message):
    dense = as_dense_matrix(matrix)
    size = len(dense)
    for row_index in range(size):
        assert len(dense[row_index]) == size, f"{message}: matrix row {row_index} has wrong length"
        for col_index in range(row_index + 1, size):
            assert isclose(dense[row_index][col_index], dense[col_index][row_index], rel_tol=REL_TOL, abs_tol=ABS_TOL), (
                f"{message}: entries ({row_index}, {col_index}) and ({col_index}, {row_index}) differ "
                f"({dense[row_index][col_index]!r} vs {dense[col_index][row_index]!r})"
            )


def transpose(matrix):
    return [list(row) for row in zip(*matrix)]


def matmul(a, b):
    return [
        [sum(a[i][k] * b[k][j] for k in range(len(b))) for j in range(len(b[0]))]
        for i in range(len(a))
    ]


def identity(size):
    return [[1.0 if i == j else 0.0 for j in range(size)] for i in range(size)]