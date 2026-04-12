graph TD
    subgraph Vector["Vector - Dense Vector Storage"]
        V1["<b>Attributes:</b><br/>- size: int<br/>- values: list[float]"]
        V2["<b>Methods:</b><br/>+ get/set/add<br/>+ dot product<br/>+ norm<br/>+ copy"]
    end
    
    subgraph MatrixHierarchy["Matrix Class Hierarchy"]
        M0["<b>Matrix</b><br/>(Abstract)<br/>═══════<br/>- size: int<br/>+ get/set/add<br/>+ matvec"]
        
        M1["<b>SymmetricSparseMatrix</b><br/>(Concrete)<br/>═══════<br/>- data: dict<br/>Storage: {i,j}: v<br/>where i ≤ j<br/>═══════<br/>▶ Symmetry: A[i,j]=A[j,i]<br/>▶ O(nnz) matvec<br/>▶ FEM stiffness matrices"]
        
        M0 --> M1
    end
    
    subgraph SolverHierarchy["Solver Class Hierarchy"]
        S0["<b>LinearSolver</b><br/>(Abstract)<br/>═══════<br/>+ solve(A,b): Vector"]
        
        S1["<b>ConjugateGradientSolver</b><br/>(Concrete)<br/>═══════<br/>- tol: float<br/>- max_iter: int<br/>═══════<br/>▶ CG algorithm for SPD<br/>▶ Relative residual criterion<br/>▶ Suitable for large sparse"]
        
        S0 --> S1
    end
    
    subgraph Workflow["Typical Solve Workflow"]
        W1["1. Create: A = SymmetricSparseMatrix(n)"]
        W2["2. Assemble: A.add(i,j,value)"]
        W3["3. RHS: b = Vector(n); b.set(i,val)"]
        W4["4. Solver: solver = ConjugateGradientSolver()"]
        W5["5. Solve: x = solver.solve(A, b)"]
        W1 --> W2 --> W3 --> W4 --> W5
    end
    
    M1 --> |uses| Vector
    S1 --> |solves| M1
    S1 --> |operates on| Vector
    S1 --> Workflow
    
    style Vector fill:#CCFFCC
    style M1 fill:#CCFFCC
    style M0 fill:#FFFFCC
    style S1 fill:#CCFFCC
    style S0 fill:#FFFFCC
    style Workflow fill:#E6F2FF
