
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

        # преобразуем минимизацию в максимизацию для SimplexSolver
        if not maximize:
            c = [-x for x in c]
            maximize = True

        A = []
        b = []

        def add_leq(coeffs, rhs):
            A.append([float(x) for x in coeffs])
            b.append(float(rhs))

        # бюджет
        if self.constraints.budget is not None:
            add_leq([p.price for p in products], self.constraints.budget)

        # калории
        if self.constraints.max_calories != float('inf'):
            add_leq([p.calories for p in products], self.constraints.max_calories)
        if self.constraints.min_calories > 0:
            add_leq([-p.calories for p in products], -self.constraints.min_calories)

        # белки
        if self.constraints.max_protein != float('inf'):
            add_leq([p.protein for p in products], self.constraints.max_protein)
        if self.constraints.min_protein > 0:
            add_leq([-p.protein for p in products], -self.constraints.min_protein)

        # жиры
        if self.constraints.max_fat != float('inf'):
            add_leq([p.fat for p in products], self.constraints.max_fat)
        if self.constraints.min_fat > 0:
            add_leq([-p.fat for p in products], -self.constraints.min_fat)

        # углеводы
        if self.constraints.max_carbs != float('inf'):
            add_leq([p.carbs for p in products], self.constraints.max_carbs)
        if self.constraints.min_carbs > 0:
            add_leq([-p.carbs for p in products], -self.constraints.min_carbs)

        return c, A, b, var_names, maximize

    def optimize(self, objective='min_cost'):
        c, A, b, var_names, maximize = self.build_lp(objective)
        from core import simplex  
        solution, optimal = simplex.SimplexSolver(c, A, b, maximize=maximize).solve()
        # если минимизация, нужно вернуть знак обратно
        if objective == 'min_cost':
            optimal = optimal
        return {
            'solution': {var_names[i]: solution[i] for i in range(len(var_names))},
            'optimal_value': optimal
        }


