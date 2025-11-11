
class ModelNutrition:
    def __init__(self, products, constraints):
        self.products = products
        self.constraints = constraints

    def build_lp(self, objective='min_cost'):
        products = self.products
        n = len(products)
        var_names = [p.name or f'prod_{i}' for i, p in enumerate(products)]

        if objective == 'min_cost':
            c = [p.price for p in products]
            maximize = False

        else:
            c = [p.calories for p in products]
            maximize = True

        # Convert minimization to maximization for SimplexSolver
        if not maximize:
            c = [-x for x in c]
            maximize = True

        A = []
        b = []

        def add_leq(coeffs, rhs):
            A.append([float(x) for x in coeffs])
            b.append(float(rhs))

        # Budget constraint
        if self.constraints.budget is not None:
            add_leq([p.price for p in products], self.constraints.budget)

        # Calorie constraints
        if self.constraints.max_calories != float('inf'):
            add_leq([p.calories for p in products], self.constraints.max_calories)
        if self.constraints.min_calories > 0:
            add_leq([-p.calories for p in products], -self.constraints.min_calories)

        # Protein constraints
        if self.constraints.max_protein != float('inf'):
            add_leq([p.protein for p in products], self.constraints.max_protein)
        if self.constraints.min_protein > 0:
            add_leq([-p.protein for p in products], -self.constraints.min_protein)

        # Fat constraints
        if self.constraints.max_fat != float('inf'):
            add_leq([p.fat for p in products], self.constraints.max_fat)
        if self.constraints.min_fat > 0:
            add_leq([-p.fat for p in products], -self.constraints.min_fat)

        # Carbs constraints
        if self.constraints.max_carbs != float('inf'):
            add_leq([p.carbs for p in products], self.constraints.max_carbs)
        if self.constraints.min_carbs > 0:
            add_leq([-p.carbs for p in products], -self.constraints.min_carbs)
        for i in range(n):
            coeffs = [0]*n
            coeffs[i] = -1 
            add_leq(coeffs, 0.1)
        

        return c, A, b, var_names, maximize

    def optimize(self, objective='min_cost'):
        c, A, b, var_names, maximize = self.build_lp(objective)
        from core import simplex  
        solution, optimal = simplex.SimplexSolver(c, A, b, maximize=maximize).solve()
        # For minimization, return the sign as-is (already handled in SimplexSolver)
        if objective == 'min_cost':
            optimal = optimal
        return {
            'solution': {var_names[i]: solution[i] for i in range(len(var_names))},
            'optimal_value': optimal
        }


