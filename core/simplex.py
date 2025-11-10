"""
Simplex solver (business logic)
Contract:
- Inputs: c (list of profits coefficients), A (list of constraint rows), b (list of RHS limits)
- All constraints are assumed to be of type <= and all variables >= 0.
- Returns: (solution_list, optimal_value)

This is a small, self-contained tableau implementation suitable for teaching and small LPs.
"""

from typing import List, Tuple


def solve(c: List[float], A: List[List[float]], b: List[float]) -> Tuple[List[float], float]:
    """Solve the LP: maximize c^T x subject to A x <= b, x >= 0.

    Args:
        c: objective coefficients (length n)
        A: list of m rows, each row is length n
        b: right-hand side vector (length m)

    Returns:
        (solution, optimal_value)
    """
    # Input validation
    if not c:
        return [], 0.0
    m = len(A)
    n = len(c)
    if any(len(row) != n for row in A):
        raise ValueError("Each row in A must have the same length as c")
    if len(b) != m:
        raise ValueError("Length of b must equal number of rows in A")

    # Build initial tableau with slack variables
    # tableau rows: [x1..xn, s1..sm, rhs]
    tableau = []
    for i in range(m):
        row = [float(x) for x in A[i]] + [0.0] * m + [float(b[i])]
        row[n + i] = 1.0  # slack variable
        tableau.append(row)

    # z-row (objective): we store -c for maximization
    z_row = [-float(ci) for ci in c] + [0.0] * m + [0.0]
    tableau.append(z_row)

    # Simplex iterations
    while True:
        last_row = tableau[-1]
        # choose entering variable (most negative coefficient in z-row)
        entering_candidates = [(j, last_row[j]) for j in range(len(last_row) - 1) if last_row[j] < -1e-12]
        if not entering_candidates:
            break  # optimal
        entering = min(entering_candidates, key=lambda t: t[1])[0]

        # ratio test to choose leaving row
        ratios = []
        for i in range(m):
            aij = tableau[i][entering]
            if aij > 1e-12:
                ratios.append(tableau[i][-1] / aij)
            else:
                ratios.append(float('inf'))
        min_ratio = min(ratios)
        if min_ratio == float('inf'):
            raise ValueError("Linear program is unbounded")
        leaving = ratios.index(min_ratio)

        # pivot
        pivot = tableau[leaving][entering]
        tableau[leaving] = [v / pivot for v in tableau[leaving]]
        for i in range(len(tableau)):
            if i != leaving:
                factor = tableau[i][entering]
                tableau[i] = [tableau[i][j] - factor * tableau[leaving][j] for j in range(len(tableau[i]))]

    # extract solution for original n variables
    solution = [0.0] * n
    for j in range(n):
        # check if column j is a basic unit column
        col = [tableau[i][j] for i in range(m)]
        if sum(1 for v in col if abs(v - 1.0) < 1e-9) == 1 and sum(abs(v) for v in col) - 1.0 < 1e-9:
            one_row = next(i for i in range(m) if abs(tableau[i][j] - 1.0) < 1e-9)
            solution[j] = tableau[one_row][-1]
        else:
            solution[j] = 0.0

    optimal_value = tableau[-1][-1]
    return solution, optimal_value
