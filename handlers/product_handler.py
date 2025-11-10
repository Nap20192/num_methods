"""
Handler module: converts product/nutrition descriptions into LP matrices and calls the core simplex solver.

This module provides a small adapter that turns a list of products (price, calories,
protein, fat, carbs, optional profit) together with a set of constraints into the
matrices expected by `core.simplex.solve` (which solves a maximization problem with
constraints of type Ax <= b, x >= 0).

The handler supports several objective modes:
 - 'min_cost' : minimize total cost while meeting nutrition minima
 - 'max_calories' : maximize total calories subject to budget/limits
 - 'max_profit' : maximize provided 'profit' field on products

All constraints and products are provided from the frontend.
"""

from typing import List, Dict, Tuple, Optional
from core import simplex


def build_lp(products: List[Dict], constraints: Dict) -> Tuple[List[float], List[List[float]], List[float], List[str], bool]:
    """Build LP (c, A, b) and variable names from products + constraints.

    Returns:
        c: objective coefficients (length n) for maximization
        A: list of rows (each row is length n) for constraints of type <=
        b: rhs vector for those constraints
        var_names: list of product names
        is_maximize: always True for core.simplex (we adapt signs for minimization)
    """
    var_names = [p.get('name', f'prod_{i}') for i, p in enumerate(products)]
    n = len(products)

    # Objective setup
    mode = constraints.get('objective', 'min_cost')
    if mode == 'max_calories':
        c = [float(p.get('calories', 0.0)) for p in products]
    elif mode == 'max_profit':
        c = [float(p.get('profit', 0.0)) for p in products]
    else:  # 'min_cost' (default)
        # core.simplex maximizes c^T x. To minimize cost, maximize negative cost.
        c = [-float(p.get('price', 0.0)) for p in products]

    A: List[List[float]] = []
    b: List[float] = []

    # Helper to append a <= constraint
    def add_leq(coeffs: List[float], rhs: float):
        A.append([float(v) for v in coeffs])
        b.append(float(rhs))

    # Budget limit: sum(price_i * x_i) <= budget
    budget = constraints.get('budget')
    if budget is not None:
        add_leq([p.get('price', 0.0) for p in products], budget)

    # Calorie min/max
    cal_min = constraints.get('calories_min')
    cal_max = constraints.get('calories_max')
    if cal_max is not None:
        add_leq([p.get('calories', 0.0) for p in products], cal_max)
    if cal_min is not None:
        # -sum(cal_i * x_i) <= -cal_min
        add_leq([-p.get('calories', 0.0) for p in products], -cal_min)

    # Macro minima (protein/fat/carbs)
    for macro in ('protein', 'fat', 'carbs'):
        key = f'{macro}_min'
        if constraints.get(key) is not None:
            add_leq([-p.get(macro, 0.0) for p in products], -constraints[key])

    # Macro proportional constraints: if user supplies ratios, enforce
    ratios: Optional[Dict] = constraints.get('macro_ratios')
    if ratios:
        # Enforce for each macro: macro >= ratio * (protein+fat+carbs)
        # which is: -macro + ratio*(protein+fat+carbs) <= 0
        for macro in ('protein', 'fat', 'carbs'):
            r = float(ratios.get(macro, 0.0))
            if r <= 0:
                continue
            coeffs = []
            for p in products:
                coeff = r * (p.get('protein', 0.0) + p.get('fat', 0.0) + p.get('carbs', 0.0))
                # subtract the macro itself
                coeff -= p.get(macro, 0.0)
                coeffs.append(coeff)
            add_leq(coeffs, 0.0)

    # Optionally: upper bounds on each product (e.g., availability)
    # Represented as individual constraints x_i <= ub
    for i, p in enumerate(products):
        ub = p.get('max_qty')
        if ub is not None:
            coeffs = [0.0] * n
            coeffs[i] = 1.0
            add_leq(coeffs, ub)

    return c, A, b, var_names, True


def optimize_products(products: List[Dict], constraints: Dict) -> Dict:
    """Build LP and run simplex solver. Return mapping product->quantity and optimal value.

    Args:
        products: list of dicts with keys: name, price, calories, protein, fat, carbs, profit (optional)
        constraints: dict with keys described in build_lp

    Returns:
        dict with keys: 'solution' (name->qty), 'objective_value' (interpreted per objective),
                      'raw_value' (value returned by solver), 'status' (ok/error/message)
    """
    if not products:
        return {'solution': {}, 'objective_value': 0.0, 'raw_value': 0.0, 'status': 'no products provided'}

    try:
        c, A, b, var_names, is_max = build_lp(products, constraints)
        sol, raw_val = simplex.solve(c, A, b)

        mode = constraints.get('objective', 'min_cost')
        if mode == 'min_cost':
            objective_value = -raw_val  # because we maximized negative cost
        else:
            objective_value = raw_val

        result = {name: qty for name, qty in zip(var_names, sol)}
        return {
            'solution': result,
            'objective_value': float(objective_value),
            'raw_value': float(raw_val),
            'status': 'ok',
        }
    except Exception as exc:
        return {'solution': {}, 'objective_value': 0.0, 'raw_value': 0.0, 'status': f'error: {exc}'}
