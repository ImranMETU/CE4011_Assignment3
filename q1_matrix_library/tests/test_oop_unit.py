import inspect

import pytest

from q1_matrix_library.conjugate_gradient_solver import ConjugateGradientSolver
from q1_matrix_library.linear_solver import LinearSolver
from q1_matrix_library.matrix import Matrix
from q1_matrix_library.symmetric_sparse_matrix import SymmetricSparseMatrix
from q1_matrix_library.vector import Vector


# -----------------------------------------------------------------------------
# Vector tests
# -----------------------------------------------------------------------------

def test_vector_creation_valid_size_initializes_zero_state():
	v = Vector(4)

	assert v.size == 4
	assert v.values == [0.0, 0.0, 0.0, 0.0]


@pytest.mark.parametrize("size", [0, -1, -10])
def test_vector_creation_invalid_size_raises_value_error(size):
	with pytest.raises(ValueError):
		Vector(size)


def test_vector_set_get_add_preserve_internal_state_and_boundaries():
	v = Vector(3)

	v.set(0, 1.5)
	v.set(2, -2.0)
	v.add(0, 0.5)
	v.add(2, 5.0)

	assert v.get(0) == 2.0
	assert v.get(1) == 0.0
	assert v.get(2) == 3.0


def test_vector_copy_creates_independent_object():
	original = Vector(3)
	original.set(0, 2.0)
	original.set(1, 4.0)

	cloned = original.copy()
	cloned.add(0, 10.0)

	assert cloned is not original
	assert cloned.values is not original.values
	assert original.get(0) == 2.0
	assert cloned.get(0) == 12.0


def test_vector_dot_norm_and_size_mismatch_behavior():
	v = Vector(3)
	w = Vector(3)
	v.values = [1.0, 2.0, 3.0]
	w.values = [4.0, 5.0, 6.0]

	assert v.dot(w) == 32.0
	assert v.norm() == pytest.approx((1.0**2 + 2.0**2 + 3.0**2) ** 0.5)

	other_size = Vector(2)
	with pytest.raises(ValueError):
		v.dot(other_size)


@pytest.mark.parametrize("op", ["get", "set", "add"])
@pytest.mark.parametrize("idx", [-1, 3])
def test_vector_out_of_bounds_operations_raise_index_error(op, idx):
	v = Vector(3)

	with pytest.raises(IndexError):
		if op == "get":
			v.get(idx)
		elif op == "set":
			v.set(idx, 1.0)
		else:
			v.add(idx, 1.0)


# -----------------------------------------------------------------------------
# Matrix tests (Matrix ABC behavior + SymmetricSparseMatrix implementation)
# -----------------------------------------------------------------------------

def test_matrix_interface_contract_or_instantiation_restriction():
	if inspect.isabstract(Matrix):
		with pytest.raises(TypeError):
			Matrix(2)
		return

	m = Matrix(2)
	assert m.size == 2
	with pytest.raises(NotImplementedError):
		m.get(0, 0)
	with pytest.raises(NotImplementedError):
		m.set(0, 0, 1.0)
	with pytest.raises(NotImplementedError):
		m.add(0, 0, 1.0)
	with pytest.raises(NotImplementedError):
		m.matvec(Vector(2))


def test_matrix_creation_invalid_size_raises_value_error():
	with pytest.raises(ValueError):
		Matrix(0)


def test_matrix_symmetric_sparse_initialization_and_interface_compliance():
	A = SymmetricSparseMatrix(5)

	assert isinstance(A, Matrix)
	assert A.size == 5
	assert isinstance(A.data, dict)
	assert len(A.data) == 0


@pytest.mark.parametrize("size", [0, -3])
def test_matrix_symmetric_sparse_invalid_size_raises_value_error(size):
	with pytest.raises(ValueError):
		SymmetricSparseMatrix(size)


def test_matrix_add_get_and_symmetric_storage_behavior():
	A = SymmetricSparseMatrix(4)

	A.add(0, 3, 2.5)
	A.add(3, 0, 1.5)
	A.add(2, 2, -7.0)

	assert A.get(0, 3) == 4.0
	assert A.get(3, 0) == 4.0
	assert A.get(2, 2) == -7.0
	assert A.get(1, 1) == 0.0

	# Symmetry normalization should keep only upper-triangle key for off-diagonal.
	assert (0, 3) in A.data
	assert (3, 0) not in A.data


def test_matrix_set_overwrites_value_consistently_with_symmetry():
	A = SymmetricSparseMatrix(3)

	A.set(2, 0, 9.0)
	assert A.get(0, 2) == 9.0

	A.set(0, 2, -1.25)
	assert A.get(2, 0) == -1.25
	assert len(A.data) == 1


@pytest.mark.parametrize("i,j", [(-1, 0), (0, -1), (3, 0), (0, 3)])
def test_matrix_index_out_of_bounds_raises_index_error(i, j):
	A = SymmetricSparseMatrix(3)

	with pytest.raises(IndexError):
		A.get(i, j)
	with pytest.raises(IndexError):
		A.set(i, j, 1.0)
	with pytest.raises(IndexError):
		A.add(i, j, 1.0)


def test_matrix_matvec_returns_vector_of_expected_size():
	A = SymmetricSparseMatrix(3)
	A.set(0, 0, 2.0)
	A.set(1, 1, 3.0)
	A.set(2, 2, 4.0)

	x = Vector(3)
	x.values = [1.0, 1.0, 1.0]

	y = A.matvec(x)
	assert isinstance(y, Vector)
	assert y.size == 3


def test_matrix_matvec_dimension_mismatch_raises_value_error():
	A = SymmetricSparseMatrix(3)
	x = Vector(2)

	with pytest.raises(ValueError):
		A.matvec(x)


# -----------------------------------------------------------------------------
# Solver tests (LinearSolver ABC behavior + ConjugateGradientSolver)
# -----------------------------------------------------------------------------

def test_solver_interface_contract_or_instantiation_restriction():
	if inspect.isabstract(LinearSolver):
		with pytest.raises(TypeError):
			LinearSolver()
		return

	solver = LinearSolver()
	with pytest.raises(NotImplementedError):
		solver.solve(SymmetricSparseMatrix(1), Vector(1))


def test_solver_conjugate_gradient_creation_valid_parameters():
	solver = ConjugateGradientSolver(tol=1e-8, max_iter=250)

	assert isinstance(solver, LinearSolver)
	assert solver.tol == 1e-8
	assert solver.max_iter == 250


@pytest.mark.parametrize("tol", [0, -1e-8, -1.0])
def test_solver_conjugate_gradient_invalid_tolerance_raises_value_error(tol):
	with pytest.raises(ValueError):
		ConjugateGradientSolver(tol=tol, max_iter=10)


@pytest.mark.parametrize("max_iter", [0, -1, -50])
def test_solver_conjugate_gradient_invalid_max_iter_raises_value_error(max_iter):
	with pytest.raises(ValueError):
		ConjugateGradientSolver(tol=1e-6, max_iter=max_iter)


def test_solver_solve_returns_vector_of_correct_size():
	A = SymmetricSparseMatrix(3)
	A.set(0, 0, 1.0)
	A.set(1, 1, 1.0)
	A.set(2, 2, 1.0)

	b = Vector(3)
	b.values = [1.0, 2.0, 3.0]

	solver = ConjugateGradientSolver(tol=1e-12, max_iter=5)
	x = solver.solve(A, b)

	assert isinstance(x, Vector)
	assert x.size == b.size


def test_solver_dimension_mismatch_raises_value_error():
	A = SymmetricSparseMatrix(2)
	b = Vector(3)
	solver = ConjugateGradientSolver()

	with pytest.raises(ValueError):
		solver.solve(A, b)


def test_solver_robustness_non_spd_behavior_raises_runtime_error():
	# Zero matrix makes p^T A p equal zero, which should trigger runtime protection.
	A = SymmetricSparseMatrix(2)
	b = Vector(2)
	b.values = [1.0, 0.0]
	solver = ConjugateGradientSolver(max_iter=5)

	with pytest.raises(RuntimeError):
		solver.solve(A, b)

