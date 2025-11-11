import numpy as np

class SimplexSolver:
    def __init__(self, c, A, b, maximize=True):

        self.c = np.array(c, dtype=float)
        self.A = np.array(A, dtype=float)
        self.b = np.array(b, dtype=float)

        self.maximize = maximize

    def solve(self):
        m, n = self.A.shape

        tableau = np.zeros((m + 1, n + m + 1))

        tableau[:m, :n] = self.A
        tableau[:m, n:n + m] = np.eye(m)
        tableau[:m, -1] = self.b

        tableau[-1, :n] = -self.c if self.maximize else self.c

        while True:
            pivot_col = np.argmin(tableau[-1, :-1])
            if tableau[-1, pivot_col] >= 0:
                break
            ratios = []

            for i in range(m):
                if tableau[i, pivot_col] > 0:
                    ratios.append(tableau[i, -1] / tableau[i, pivot_col])
                else:
                    ratios.append(np.inf)
            pivot_row = np.argmin(ratios)
            if ratios[pivot_row] == np.inf:
                raise Exception("Неограниченная задача")

            pivot = tableau[pivot_row, pivot_col]
            tableau[pivot_row, :] /= pivot

            for i in range(m + 1):
                if i != pivot_row:
                    tableau[i, :] -= tableau[i, pivot_col] * tableau[pivot_row, :]

        solution = np.zeros(n)

        for i in range(m):
            pivot_cols = np.where(np.isclose(tableau[i, :n], 1))[0]
            if len(pivot_cols) == 1:
                solution[pivot_cols[0]] = tableau[i, -1]

        optimal_value = tableau[-1, -1]
        return solution, optimal_value
