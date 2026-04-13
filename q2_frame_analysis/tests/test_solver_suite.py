from q2_frame_analysis.main import example_input_data # type: ignore
from model import FrameElement, Material, Node, Section, Structure, TrussElement # type: ignore

from helpers import assert_close, assert_matrix_close, assert_symmetric, assert_vector_close, identity, matmul, transpose

# Tolerances used throughout:
#   Stiffness matrix entries : abs tolerance 1e-8
#   Displacements and forces  : abs tolerance 1e-6


def test_unit_frame_stiffness():
    # Verifies the unreleased 2D frame local stiffness matrix.
    material = Material("m1", 10.0)
    section = Section("s1", 2.0, 3.0)
    node_i = Node(0, 0.0, 0.0)
    node_j = Node(1, 4.0, 0.0)
    element = FrameElement(1, node_i, node_j, material, section)

    local_stiffness = element.local_stiffness()

    assert len(local_stiffness) == 6, "Frame local stiffness matrix must have 6 rows"
    assert all(len(row) == 6 for row in local_stiffness), "Frame local stiffness matrix must be 6x6"
    assert_symmetric(local_stiffness, "frame local stiffness matrix")

    expected = [
        [5.0, 0.0, 0.0, -5.0, 0.0, 0.0],
        [0.0, 5.625, 11.25, 0.0, -5.625, 11.25],
        [0.0, 11.25, 30.0, 0.0, -11.25, 15.0],
        [-5.0, 0.0, 0.0, 5.0, 0.0, 0.0],
        [0.0, -5.625, -11.25, 0.0, 5.625, -11.25],
        [0.0, 11.25, 15.0, 0.0, -11.25, 30.0],
    ]

    assert_matrix_close(local_stiffness, expected, "frame local stiffness matrix")


def test_unit_frame_transformation():
    # Verifies the transformation matrix and global stiffness for horizontal and vertical frame elements.
    material = Material("m1", 10.0)
    section = Section("s1", 2.0, 3.0)

    horizontal = FrameElement(1, Node(0, 0.0, 0.0), Node(1, 4.0, 0.0), material, section)
    rotation_h = horizontal.transformation_matrix()
    assert_matrix_close(matmul(rotation_h, transpose(rotation_h)), identity(6), "horizontal transformation orthogonality")
    assert_matrix_close(horizontal.global_stiffness(), horizontal.local_stiffness(), "horizontal frame global stiffness")

    vertical = FrameElement(2, Node(0, 0.0, 0.0), Node(1, 0.0, 4.0), material, section)
    rotation_v = vertical.transformation_matrix()
    assert_matrix_close(matmul(rotation_v, transpose(rotation_v)), identity(6), "vertical transformation orthogonality")

    global_stiffness = vertical.global_stiffness()
    assert_symmetric(global_stiffness, "vertical frame global stiffness matrix")

    expected_checks = {
        (0, 0): 5.625,
        (1, 1): 5.0,
        (2, 2): 30.0,
        (0, 2): -11.25,
        (3, 3): 5.625,
        (4, 4): 5.0,
        (5, 5): 30.0,
        (1, 4): -5.0,
    }

    for (row, col), expected_value in expected_checks.items():
        assert_close(global_stiffness[row][col], expected_value, f"vertical global stiffness entry ({row}, {col})")


def test_unit_frame_equiv_loads():
    # Verifies the UDL and point-load sign convention for fixed-end reactions.
    material = Material("m1", 10.0)
    section = Section("s1", 2.0, 3.0)

    udl_element = FrameElement(1, Node(0, 0.0, 0.0), Node(1, 4.0, 0.0), material, section)
    udl_element.member_loads.append({"type": "udl", "direction": "local_y", "w": -5.0})
    assert_vector_close(
        udl_element.equivalent_nodal_load_local(),
        [0.0, 10.0, 6.666666666666667, 0.0, 10.0, -6.666666666666667],
        "UDL equivalent nodal load",
    )

    point_element = FrameElement(2, Node(0, 0.0, 0.0), Node(1, 4.0, 0.0), material, section)
    point_element.member_loads.append({"type": "point", "direction": "local_y", "p": -10.0, "a": 2.0})
    assert_vector_close(
        point_element.equivalent_nodal_load_local(),
        [0.0, 5.0, 5.0, 0.0, 5.0, -5.0],
        "point-load equivalent nodal load",
    )


def test_interface_frame_assembly():
    # Verifies global stiffness assembly for a small frame chain.
    structure = Structure()

    node0 = Node(0, 0.0, 0.0)
    node0.set_restraints(True, True, True)
    node1 = Node(1, 4.0, 0.0)
    node2 = Node(2, 8.0, 0.0)

    for node in (node0, node1, node2):
        structure.add_node(node)

    material = Material("m1", 10.0)
    section = Section("s1", 2.0, 3.0)
    structure.add_material(material)
    structure.add_section(section)

    structure.add_element(FrameElement(1, node0, node1, material, section))
    structure.add_element(FrameElement(2, node1, node2, material, section))

    structure.assign_dofs()
    stiffness = structure.assemble_global_stiffness()

    assert structure.n_active_dofs == 6, "Expected 6 active DOFs for the two free frame nodes"
    assert stiffness.size == 6, "Global stiffness matrix size must match active DOFs"
    assert_symmetric(stiffness, "assembled frame stiffness matrix")

    node1_dofs = node1.get_global_dof_numbers()
    node2_dofs = node2.get_global_dof_numbers()

    assert_close(stiffness.get(node1_dofs[0] - 1, node1_dofs[0] - 1), 10.0, "node1 ux diagonal")
    assert_close(stiffness.get(node1_dofs[1] - 1, node1_dofs[1] - 1), 11.25, "node1 uy diagonal")
    assert_close(stiffness.get(node1_dofs[2] - 1, node1_dofs[2] - 1), 60.0, "node1 rz diagonal")
    assert_close(stiffness.get(node1_dofs[0] - 1, node2_dofs[0] - 1), -5.0, "node1-node2 ux coupling")
    assert_close(stiffness.get(node1_dofs[1] - 1, node2_dofs[1] - 1), -5.625, "node1-node2 uy coupling")
    assert_close(stiffness.get(node1_dofs[2] - 1, node2_dofs[2] - 1), 15.0, "node1-node2 rz coupling")


def test_interface_mixed_assembly():
    # Verifies mixed assembly with frame and truss elements in one global matrix.
    structure = Structure()

    node0 = Node(0, 0.0, 0.0)
    node0.set_restraints(True, True, True)
    node1 = Node(1, 4.0, 0.0)
    node2 = Node(2, 8.0, 0.0)
    node2.set_restraints(False, True, True)

    for node in (node0, node1, node2):
        structure.add_node(node)

    material = Material("m1", 10.0)
    frame_section = Section("frame", 2.0, 3.0)
    truss_section = Section("truss", 2.0, 0.0)
    structure.add_material(material)
    structure.add_section(frame_section)
    structure.add_section(truss_section)

    structure.add_element(FrameElement(1, node0, node1, material, frame_section))
    structure.add_element(TrussElement(2, node1, node2, material, truss_section))

    structure.assign_dofs()
    stiffness = structure.assemble_global_stiffness()

    assert structure.n_active_dofs == 4, "Expected 4 active DOFs in the mixed model"
    assert stiffness.size == 4, "Mixed global stiffness matrix size must match active DOFs"
    assert_symmetric(stiffness, "assembled mixed stiffness matrix")

    node1_dofs = node1.get_global_dof_numbers()
    node2_dofs = node2.get_global_dof_numbers()

    assert_close(stiffness.get(node1_dofs[2] - 1, node1_dofs[2] - 1), 30.0, "frame bending term at node1 rz")
    assert_close(stiffness.get(node2_dofs[0] - 1, node2_dofs[0] - 1), 5.0, "truss axial stiffness at node2 ux")
    assert_close(stiffness.get(node1_dofs[0] - 1, node2_dofs[0] - 1), -5.0, "truss ux coupling across nodes")
    assert_close(stiffness.get(node1_dofs[2] - 1, node2_dofs[0] - 1), 0.0, "no spurious truss rotational coupling")


def test_regression_frame():
    # Verifies a fully restrained single-frame model under a central point load.
    structure = Structure()

    node0 = Node(0, 0.0, 0.0)
    node0.set_restraints(True, True, True)
    node1 = Node(1, 4.0, 0.0)
    node1.set_restraints(True, True, True)

    structure.add_node(node0)
    structure.add_node(node1)

    material = Material("m1", 10.0)
    section = Section("s1", 2.0, 3.0)
    structure.add_material(material)
    structure.add_section(section)

    element = FrameElement(1, node0, node1, material, section)
    element.member_loads.append({"type": "point", "direction": "local_y", "p": -10.0, "a": 2.0})
    structure.add_element(element)

    structure.assign_dofs()
    solution = structure.solve()

    assert solution.size == 0, "Fully restrained model should have no active displacement unknowns"
    assert_vector_close(structure.full_displacement_vector(), [0.0, 0.0, 0.0, 0.0, 0.0, 0.0], "full displacement vector")

    reactions = structure.compute_reactions()
    assert_close(reactions[0]["rx"], 0.0, "left support horizontal reaction")
    assert_close(reactions[0]["ry"], 5.0, "left support vertical reaction")
    assert_close(reactions[0]["mz"], -5.0, "left support moment reaction")
    assert_close(reactions[1]["rx"], 0.0, "right support horizontal reaction")
    assert_close(reactions[1]["ry"], 5.0, "right support vertical reaction")
    assert_close(reactions[1]["mz"], 5.0, "right support moment reaction")

    member_forces = structure.compute_member_end_forces()
    q = member_forces[1]
    assert_close(q["node_i"]["nx"], 0.0, "frame i-end axial force")
    assert_close(q["node_i"]["vy"], -5.0, "frame i-end shear force")
    assert_close(q["node_i"]["mz"], -5.0, "frame i-end moment")
    assert_close(q["node_j"]["nx"], 0.0, "frame j-end axial force")
    assert_close(q["node_j"]["vy"], -5.0, "frame j-end shear force")
    assert_close(q["node_j"]["mz"], 5.0, "frame j-end moment")


def test_regression_truss():
    # Verifies a simple two-bar axial chain under a tip load.
    structure = Structure()

    node0 = Node(0, 0.0, 0.0)
    node0.set_restraints(True, True, True)
    node1 = Node(1, 2.0, 0.0)
    node1.set_restraints(False, True, True)
    node2 = Node(2, 4.0, 0.0)
    node2.set_restraints(False, True, True)

    for node in (node0, node1, node2):
        structure.add_node(node)

    material = Material("m1", 100.0)
    section = Section("s1", 1.0, 0.0)
    structure.add_material(material)
    structure.add_section(section)

    structure.add_element(TrussElement(1, node0, node1, material, section))
    structure.add_element(TrussElement(2, node1, node2, material, section))
    node2.add_load(100.0, 0.0, 0.0)

    structure.assign_dofs()
    solution = structure.solve()

    assert solution.size == 2, "Two free axial DOFs are expected in the truss chain"
    assert_vector_close([solution.get(i) for i in range(solution.size)], [2.0, 4.0], "truss active displacements")

    reactions = structure.compute_reactions()
    assert_close(reactions[0]["rx"], -100.0, "truss support horizontal reaction")
    assert_close(reactions[0]["ry"], 0.0, "truss support vertical reaction")
    assert_close(reactions[0]["mz"], 0.0, "truss support moment reaction")

    member_forces = structure.compute_member_end_forces()
    for element_id in (1, 2):
        q = member_forces[element_id]
        assert_close(q["node_i"]["nx"], -100.0, f"truss element {element_id} i-end axial force")
        assert_close(q["node_j"]["nx"], 100.0, f"truss element {element_id} j-end axial force")
        assert_close(q["node_i"]["vy"], 0.0, f"truss element {element_id} i-end shear force")
        assert_close(q["node_j"]["vy"], 0.0, f"truss element {element_id} j-end shear force")
        assert_close(q["node_i"]["mz"], 0.0, f"truss element {element_id} i-end moment")
        assert_close(q["node_j"]["mz"], 0.0, f"truss element {element_id} j-end moment")


def test_regression_mixed():
    # Verifies the built-in mixed example used by the project entrypoint.
    structure = Structure.from_dict(example_input_data())
    solution = structure.solve()

    expected_displacements = [
        4.2442685307605155e-06,
        3.1568917073137324e-10,
        -1.829086593088014e-06,
        1.2415476645457006e-05,
        -7.029011124653938e-06,
        -3.3860390851249154e-06,
        2.257359390083293e-06,
        -3.386039085124942e-06,
    ]
    assert solution.size == len(expected_displacements), "Mixed example active DOF count changed"
    assert_vector_close([solution.get(i) for i in range(solution.size)], expected_displacements, "mixed example displacements")

    reactions = structure.compute_reactions()
    assert_close(reactions[0]["rx"], -4.99999999999495, "mixed node 0 horizontal reaction")
    assert_close(reactions[0]["ry"], -1.3720148328718869, "mixed node 0 vertical reaction")
    assert_close(reactions[0]["mz"], 22.01194066850668, "mixed node 0 moment reaction")
    assert_close(reactions[3]["ry"], 9.372014832871917, "mixed node 3 vertical reaction")

    member_forces = structure.compute_member_end_forces()
    frame_1 = member_forces[1]
    truss_4 = member_forces[4]

    assert_close(frame_1["node_i"]["mz"], 22.01194066850668, "mixed frame element end moment")
    assert_close(truss_4["node_i"]["nx"], -2.285989856629297, "mixed truss axial force at i-end")
    assert_close(truss_4["node_j"]["nx"], 2.285989856629297, "mixed truss axial force at j-end")
    assert_close(truss_4["node_i"]["vy"], 0.0, "mixed truss i-end shear force")
    assert_close(truss_4["node_i"]["mz"], 0.0, "mixed truss i-end moment")


def test_unit_frame_released_with_member_load():
    # Verifies the complex interaction of element moment release with member loads.
    # This tests end-release condensation combined with equivalent nodal load transformation.
    material = Material("m1", 10.0)
    section = Section("s1", 2.0, 3.0)
    node_i = Node(0, 0.0, 0.0)
    node_j = Node(1, 4.0, 0.0)
    
    element = FrameElement(1, node_i, node_j, material, section, release_end=True)
    element.member_loads.append({"type": "point", "direction": "local_y", "p": -10.0, "a": 2.0})
    
    # Local stiffness with release
    k_local = element.local_stiffness()
    assert_symmetric(k_local, "released frame local stiffness matrix")
    
    # Verify that condensed stiffness removes moment DOF at free end
    # (position [5][5] should have modified stiffness reflecting release)
    assert_close(k_local[5][5], 15.0, "moment stiffness at free end (partially condensed)")
    
    # Equivalent nodal load must reflect the release
    f_eq = element.equivalent_nodal_load_local()
    assert_vector_close(
        f_eq,
        [0.0, 5.0, 5.0, 0.0, 5.0, 0.0],  # Last element is zero due to moment release
        "released frame equivalent nodal load with member load",
    )