"""
Run only the original 8 tests from test_solver_suite.py

Usage:
    python run_original_tests.py
    
Or via pytest:
    pytest tests/test_solver_suite.py::test_unit_frame_stiffness -v
    pytest tests/test_solver_suite.py::test_unit_frame_transformation -v
    pytest tests/test_solver_suite.py::test_unit_frame_equiv_loads -v
    pytest tests/test_solver_suite.py::test_interface_frame_assembly -v
    pytest tests/test_solver_suite.py::test_interface_mixed_assembly -v
    pytest tests/test_solver_suite.py::test_regression_frame -v
    pytest tests/test_solver_suite.py::test_regression_truss -v
    pytest tests/test_solver_suite.py::test_regression_mixed -v

Or run all 8 at once:
    pytest tests/test_solver_suite.py -k "unit_frame_stiffness or unit_frame_transformation or unit_frame_equiv_loads or interface_frame_assembly or interface_mixed_assembly or regression_frame or regression_truss or regression_mixed" -v
"""

import subprocess
import sys

# Original 8 test functions
ORIGINAL_TESTS = [
    "tests/test_solver_suite.py::test_unit_frame_stiffness",
    "tests/test_solver_suite.py::test_unit_frame_transformation",
    "tests/test_solver_suite.py::test_unit_frame_equiv_loads",
    "tests/test_solver_suite.py::test_interface_frame_assembly",
    "tests/test_solver_suite.py::test_interface_mixed_assembly",
    "tests/test_solver_suite.py::test_regression_frame",
    "tests/test_solver_suite.py::test_regression_truss",
    "tests/test_solver_suite.py::test_regression_mixed",
]

if __name__ == "__main__":
    print("Running original 8 test cases from CE4011 Assignment 3...")
    print("=" * 70)
    
    cmd = ["python", "-m", "pytest"] + ORIGINAL_TESTS + ["-v"]
    result = subprocess.run(cmd)
    
    sys.exit(result.returncode)
