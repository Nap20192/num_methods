from typing import Dict, List
from core import simplex as simplex_module


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
            c = [p.price for p in products]
            maximize = False

        else:
            c = [p.price for p in products]
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
            add_leq([p.carbs for p in products], self.constraints.min_carbs)

        return c, A, b, var_names, maximize

    def optimize(self, objective: str = 'min_cost') -> Dict:

        c, A, b, var_names, maximize = self.build_lp(objective=objective)
        print("c:", c)
        print("A:", A)
        print("b:", b)

        solution, optimal = simplex_module.SimplexSolver(c, A, b, maximize=maximize).solve()
        return {
            'solution': {var_names[i]: solution[i] for i in range(len(var_names))},
            'optimal_value': optimal
        }

