class SimplexSolver:
    def __init__(self, c, A, b, maximize=True):
        self.c = [float(x) for x in c]
        self.A = [[float(x) for x in row] for row in A]
        self.b = [float(x) for x in b]
        self.maximize = maximize

        if not self.maximize:
            self.c = [-x for x in self.c]
            self.maximize = True


    def solve(self):
        m = len(self.A)
        n = len(self.c)

        tableau = [[0.0 for _ in range(n + m + 1)] for _ in range(m + 1)]
        for i in range(m):
            for j in range(n):
                tableau[i][j] = self.A[i][j]
            tableau[i][n + i] = 1.0  # slack variable
            tableau[i][-1] = self.b[i]

        for j in range(n):
            tableau[-1][j] = -self.c[j]  # max

        # Симплекс-итерации
        while True:
            pivot_col = min(range(n), key=lambda j: tableau[-1][j])
            if tableau[-1][pivot_col] >= 0:
                break  # Optimal reached

            ratios = []
            for i in range(m):
                if tableau[i][pivot_col] > 1e-12:
                    ratios.append(tableau[i][-1] / tableau[i][pivot_col])
                else:
                    ratios.append(float('inf'))

            pivot_row = ratios.index(min(ratios))
            if ratios[pivot_row] == float('inf'):
                raise Exception("Неограниченная задача")

            pivot = tableau[pivot_row][pivot_col]
            tableau[pivot_row] = [x / pivot for x in tableau[pivot_row]]

            for i in range(m + 1):
                if i != pivot_row:
                    factor = tableau[i][pivot_col]
                    tableau[i] = [tableau[i][j] - factor * tableau[pivot_row][j] for j in range(len(tableau[i]))]

        solution = [0.0] * n
        for j in range(n):
            col = [tableau[i][j] for i in range(m)]
            if col.count(1.0) == 1 and all(abs(x) < 1e-9 for k, x in enumerate(col) if col[k] != 1.0):
                row_index = col.index(1.0)
                solution[j] = tableau[row_index][-1]

        optimal_value = tableau[-1][-1]
        if any(x < 0 for x in self.c):
            optimal_value = -optimal_value

        return solution, optimal_value
