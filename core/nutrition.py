class Nutrition:
    def __init__(self, protein: float, fat: float, carbs: float, calories: float, price: float, max_qty: float = None, name: str = None):
        self.protein = float(protein)
        self.fat = float(fat)
        self.carbs = float(carbs)
        self.calories = float(calories)
        self.price = float(price)
        self.max_qty = None if max_qty is None or max_qty <= 0 else float(max_qty)
        self.name = name


class Constraints:

    def __init__(self,name: str,
                 range_protein=(0.0, float('inf')),
                 range_fat=(0.0, float('inf')),
                 range_carbs=(0.0, float('inf')),
                 calories=(0.0, float('inf')),
                 budget: float = None):

        self.name = name
        self.min_protein = float(range_protein[0])
        self.max_protein = float(range_protein[1])

        self.min_fat = float(range_fat[0])
        self.max_fat = float(range_fat[1])

        self.min_carbs = float(range_carbs[0])
        self.max_carbs = float(range_carbs[1])

        self.min_calories = float(calories[0])
        self.max_calories = float(calories[1])

        self.budget = None if budget is None or budget <= 0 else float(budget)
