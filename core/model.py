from typing import Dict, List

class ModelNutrition:
    def __init__(self, nutrition: List, constraints):
        self.products = nutrition
        self.constraints = constraints

    def build_lp(self, objective: str = 'min_cost'):
        products = self.products
        n = len(products)

        var_names = [getattr(p, 'name', f'prod_{i}') for i, p in enumerate(products)]
        if objective == 'max_calories':
            c = [p.calories for p in products]
            maximize = True

        elif objective == 'min_cost':
            c = [-p.price for p in products]
            maximize = True

        else:
            c = [-p.price for p in products]
            maximize = True

        A = []
        b = []

        def add_leq(coeffs, rhs):
            A.append([float(x) for x in coeffs])
            b.append(float(rhs))

        if self.constraints.budget is not None:
            add_leq([p.price for p in products], self.constraints.budget)

        if self.constraints.max_calories != float('inf'):
            add_leq([p.calories for p in products], self.constraints.max_calories)

        if self.constraints.min_calories > 0:
            add_leq([-p.calories for p in products], -self.constraints.min_calories)

        if self.constraints.max_protein != float('inf'):
            add_leq([p.protein for p in products], self.constraints.max_protein)

        if self.constraints.min_protein > 0:
            add_leq([-p.protein for p in products], -self.constraints.min_protein)

        if self.constraints.max_fat != float('inf'):
            add_leq([p.fat for p in products], self.constraints.max_fat)

        if self.constraints.min_fat > 0:
            add_leq([-p.fat for p in products], -self.constraints.min_fat)

        if self.constraints.max_carbs != float('inf'):
            add_leq([p.carbs for p in products], self.constraints.max_carbs)

        if self.constraints.min_carbs > 0:
            add_leq([-p.carbs for p in products], -self.constraints.min_carbs)

        return c, A, b, var_names, maximize

    def optimize(self, objective: str = 'min_cost') -> Dict:

        c, A, b, var_names, maximize = self.build_lp(objective=objective)

        solution, optimal = simplex.SimplexSolver(c, A, b, maximize=maximize).solve()

        return {
            'solution': {var_names[i]: solution[i] for i in range(len(var_names))},
            'optimal_value': optimal
        }

if __name__ == '__main__':
    import simplex
    import nutrition

    products = [
        nutrition.Nutrition(name='Product1', protein=10, fat=5, carbs=20, calories=150, price=2.0),
        nutrition.Nutrition(name='Product2', protein=20, fat=10, carbs=30, calories=250, price=3.0),
    ]

    constraints = nutrition.Constraints(
        name='TestConstraints',
        range_protein=(333, float('inf')),
        range_fat=(200, float('inf')),
        range_carbs=(1000, float('inf')),
        calories=(800, float('inf')),
        budget=10.0
    )

    model = ModelNutrition(products, constraints)
    result = model.optimize(objective='min_cost')
    print(result)
