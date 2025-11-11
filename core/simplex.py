class SimplexSolver:
    def __init__(self, c, A, b, maximize=True):
        self.c = [float(x) for x in c]
        self.A = [[float(x) for x in row] for row in A]
        self.b = [float(x) for x in b]
        self.maximize = maximize

    def solve(self):
        m = len(self.A)
        n = len(self.A[0]) if m > 0 else len(self.c)

        if m == 0:
            if self.maximize and any(x > 1e-12 for x in self.c):
                raise Exception("Linear program is unbounded (no constraints)")
            return [0.0] * n, 0.0

        # Build tableau
        tableau = [[0.0 for _ in range(n + m + 1)] for _ in range(m + 1)]

        for i in range(m):
            for j in range(n):
                tableau[i][j] = self.A[i][j]
            tableau[i][n + i] = 1.0
            tableau[i][-1] = self.b[i]

        for j in range(n):
            tableau[-1][j] = -self.c[j] if self.maximize else self.c[j]

        # Simplex iteration
        while True:
            for i in tableau:
                print(i)
            # Find pivot column (most negative coefficient in objective row)
            pivot_col = min(range(n + m), key=lambda j: tableau[-1][j])
            if tableau[-1][pivot_col] >= 0:
                break  # Optimal reached

            # Find pivot row (minimum ratio test)
            ratios = []
            for i in range(m):
                if tableau[i][pivot_col] > 0:
                    ratios.append(tableau[i][-1] / tableau[i][pivot_col])
                else:
                    ratios.append(float('inf'))

            pivot_row = ratios.index(min(ratios))
            if ratios[pivot_row] == float('inf'):
                raise Exception("Неограниченная задача")

            pivot = tableau[pivot_row][pivot_col]

            # Normalize pivot row
            tableau[pivot_row] = [x / pivot for x in tableau[pivot_row]]

            # Eliminate pivot column from other rows
            for i in range(m + 1):
                if i != pivot_row:
                    factor = tableau[i][pivot_col]
                    tableau[i] = [
                        tableau[i][j] - factor * tableau[pivot_row][j]
                        for j in range(len(tableau[i]))
                    ]

        solution = [0.0] * n
        for i in range(m):
            pivot_cols = [j for j in range(n) if abs(tableau[i][j] - 1.0) < 1e-9]

            if len(pivot_cols) == 1:
                solution[pivot_cols[0]] = tableau[i][-1]

        optimal_value = tableau[-1][-1]
        if self.maximize:
            optimal_value = -optimal_value

        print("solution:", solution)
        print("optimal_value:", optimal_value)
        return solution, optimal_value


if __name__ == "__main__":

    c = [3, 2]
    A = [
        [2, 1],
        [2, 3],
        [3, 1]
    ]
    b = [18, 42, 24]

    solver = SimplexSolver(c, A, b, maximize=True)
    solver.solve()
