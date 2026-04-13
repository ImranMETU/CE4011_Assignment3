# CE4011 Assignment 3

2D structural analysis solver report and codebase for CE4011, based on the Direct Stiffness Method with object-oriented design.

## What is included

- Report source (LaTeX): Chapters 1-5 and main.tex
- Structural solver: frame/truss analysis under static loading
- Verification assets: benchmark cases, FTool comparisons, diagnostics

## Project layout

- Chapter1_Object_Oriented_Structural_Analysis_Program.tex
- Chapter2_Testing_and_Verification.tex
- Chapter3_Warning_and_Error_Handling.tex
- Chapter4_Conclusion.tex
- Chapter5_References.tex
- main.tex
- q1_matrix_library/
- q2_frame_analysis/

## Quick start

### 1) Build the report

From the repository root:

```powershell
python compile_report.py
```

or:

```powershell
pdflatex -interaction=nonstopmode main.tex
```

### 2) Run the structural solver

From q2_frame_analysis:

```powershell
python main.py <input_case.json>
```

Example:

```powershell
python main.py q2_frame_regression_test.json
```

### 3) Run tests

From q2_frame_analysis:

```powershell
pytest
```

## Notes

- Python environment used during development: conda environment ce4011
- Generated build/cache files (aux, log, toc, pdf, pytest cache) are not part of core source
