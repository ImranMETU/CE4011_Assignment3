# CE4011 Assignment 3 — Structural Analysis Software

## Overview
This project implements an object-oriented 2D structural analysis solver using the Direct Stiffness Method (DSM). The program supports both frame and truss elements, including moment releases, point loads, and uniformly distributed loads.

The solver computes:
- Nodal displacements
- Support reactions
- Member-end forces

---

## Repository Structure

- `model/`  
  Core OOP implementation: Structure, Node, Element, FrameElement, TrussElement. Handles assembly, solving, and post-processing.

- `matrixlib/`  
  Custom numerical library (Assignment 2): symmetric sparse matrix and vector operations.

- `fem/`  
  Finite element utilities: transformations, element formulations, load handling.

- `tests/`  
  Unit, interface, and regression tests.

---

## How to Run

Run the built-in example:

```bash
python main.py
