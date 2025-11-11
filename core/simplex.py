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
        constraint_types = ['<=' for _ in range(m)]

        # Normalize: flip rows with b < 0 to make b >= 0 and mark as '>='
        for i in range(m):
            if self.b[i] < 0:
                self.A[i] = [-a for a in self.A[i]]
                self.b[i] = -self.b[i]
                constraint_types[i] = '>='

        num_leq = constraint_types.count('<=')
        num_geq = constraint_types.count('>=')
        num_arts = num_geq  # Artificials only for >= constraints

        total_slacks = num_leq
        total_surplus = num_geq
        total_vars = n + total_slacks + total_surplus + num_arts

        tableau = [[0.0 for _ in range(total_vars + 1)] for _ in range(m + 1)]

        # Build constraint rows
        row_idx = 0
        slack_idx = n
        surplus_idx = n + total_slacks
        art_idx = n + total_slacks + total_surplus
        geq_row_indices = []
        for i in range(m):
            # Original variables
            for j in range(n):
                tableau[row_idx][j] = self.A[i][j]
            if constraint_types[i] == '<=':
                tableau[row_idx][slack_idx] = 1.0
                slack_idx += 1
            elif constraint_types[i] == '>=':
                tableau[row_idx][surplus_idx] = -1.0
                surplus_idx += 1
                tableau[row_idx][art_idx] = 1.0
                art_idx += 1
                geq_row_indices.append(row_idx)
            tableau[row_idx][-1] = self.b[i]
            row_idx += 1

        # Original objective (for Phase 2)
        original_obj = [0.0 for _ in range(total_vars + 1)]
        for j in range(n):
            original_obj[j] = -self.c[j]

        if num_arts > 0:
            # Build Phase 1 objective: max -sum artificials -> obj coeffs +1 for arts (after -c_phase1)
            phase1_obj = [0.0 for _ in range(total_vars + 1)]
            art_start = n + total_slacks + total_surplus
            for k in range(num_arts):
                phase1_obj[art_start + k] = 1.0

            # Adjust Phase 1 obj by subtracting geq rows (to canonicalize initial basis)
            for r in geq_row_indices:
                for j in range(total_vars + 1):
                    phase1_obj[j] -= tableau[r][j]

            tableau[m] = phase1_obj

            # Run Phase 1 simplex
            while True:
                pivot_col = min(range(total_vars), key=lambda j: tableau[m][j])
                if tableau[m][pivot_col] >= 0:
                    break
                ratios = [tableau[i][-1] / tableau[i][pivot_col] if tableau[i][pivot_col] > 1e-12 else float('inf') for i in range(m)]
                min_ratio = min(ratios)
                if min_ratio == float('inf'):
                    raise Exception("Unbounded problem")
                pivot_row = ratios.index(min_ratio)
                pivot = tableau[pivot_row][pivot_col]
                for j in range(total_vars + 1):
                    tableau[pivot_row][j] /= pivot
                for i in range(m + 1):
                    if i != pivot_row:
                        factor = tableau[i][pivot_col]
                        for j in range(total_vars + 1):
                            tableau[i][j] -= factor * tableau[pivot_row][j]

            # Check feasibility (max -sum art >= 0 means sum art <= 0; since >=0 vars, ==0)
            if tableau[m][-1] < -1e-12:
                raise Exception("Infeasible problem")

            # Remove artificial columns
            art_start = n + total_slacks + total_surplus
            for i in range(m + 1):
                tableau[i] = tableau[i][:art_start] + [tableau[i][-1]]
            total_vars -= num_arts

            # Update original_obj to match new total_vars (arts removed)
            original_obj = original_obj[:total_vars + 1]

        # Set Phase 2 objective
        tableau[m] = original_obj

        # Canonicalize Phase 2 obj if after Phase 1 (eliminate basis coeffs)
        if num_arts > 0:
            basis = [-1] * m
            for j in range(total_vars):
                col = [tableau[k][j] for k in range(m)]
                ones = [k for k in range(m) if abs(tableau[k][j] - 1) < 1e-9]
                if len(ones) == 1 and all(abs(tableau[k][j]) < 1e-9 for k in range(m) if k != ones[0]):
                    basis[ones[0]] = j
            for r in range(m):
                j = basis[r]
                if j != -1:
                    coeff = tableau[m][j]
                    if abs(coeff) > 1e-12:
                        for k in range(total_vars + 1):
                            tableau[m][k] -= coeff * tableau[r][k]

        # Run Phase 2 simplex
        while True:
            pivot_col = min(range(total_vars), key=lambda j: tableau[m][j])
            if tableau[m][pivot_col] >= 0:
                break
            ratios = [tableau[i][-1] / tableau[i][pivot_col] if tableau[i][pivot_col] > 1e-12 else float('inf') for i in range(m)]
            min_ratio = min(ratios)
            if min_ratio == float('inf'):
                raise Exception("Unbounded problem")
            pivot_row = ratios.index(min_ratio)
            pivot = tableau[pivot_row][pivot_col]
            for j in range(total_vars + 1):
                tableau[pivot_row][j] /= pivot
            for i in range(m + 1):
                if i != pivot_row:
                    factor = tableau[i][pivot_col]
                    for j in range(total_vars + 1):
                        tableau[i][j] -= factor * tableau[pivot_row][j]

        optimal_value = tableau[m][-1]
        if any(x < 0 for x in self.c):
            optimal_value = -optimal_value

        # Extract solution (only original variables)
        solution = [0.0] * n
        for j in range(n):
            col = [tableau[i][j] for i in range(m)]
            ones = [k for k in range(m) if abs(col[k] - 1) < 1e-9]
            if len(ones) == 1 and all(abs(col[k]) < 1e-9 for k in range(m) if k != ones[0]):
                solution[j] = tableau[ones[0]][-1]

        return solution, optimal_value