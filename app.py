"""
Streamlit frontend for nutrition optimization using simplex method.
Run: streamlit run app.py
"""
import streamlit as st
import sys
import os

# Ensure project root is on sys.path
ROOT = os.path.abspath(os.path.dirname(__file__))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from core.model import ModelNutrition
from core.nutrition import Nutrition, Constraints

# Page config
st.set_page_config(
    page_title="Product Optimization — Simplex",
    page_icon="🥗",
    layout="wide"
)

st.title("🥗 Product Optimization")
st.markdown("""
This program finds the optimal quantity of products based on calories, protein, fat, carbs, and budget.  
Uses the **simplex method** to solve a linear programming problem.
""")

# Sidebar for objective selection
with st.sidebar:
    st.header("⚙️ Optimization Settings")
    objective = st.radio(
        "Optimization Goal:",
        options=["min_cost", "max_calories"],
        format_func=lambda x: "Minimize Cost" if x == "min_cost" else "Maximize Calories",
        index=0
    )
    st.info("**min_cost**: find the cheapest set that meets requirements\n\n**max_calories**: maximize calories within budget")

# Products section
st.header("📦 Products")
st.markdown("Enter product data (price, calories, macros):")

num_products = st.number_input("Number of Products", min_value=1, max_value=20, value=3, step=1)

products = []
cols_per_row = 3
for i in range(num_products):
    with st.expander(f"Product #{i+1}", expanded=(i < 2)):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            name = st.text_input("Name", value=f"Product {i+1}", key=f"name_{i}")
            price = st.number_input("Price ($)", min_value=0.0, value=10.0 + i*5, step=0.1, key=f"price_{i}")
        
        with col2:
            calories = st.number_input("Calories (kcal)", min_value=0.0, value=100.0 + i*50, step=1.0, key=f"cal_{i}")
            protein = st.number_input("Protein (g)", min_value=0.0, value=10.0 + i*5, step=0.1, key=f"prot_{i}")
        
        with col3:
            fat = st.number_input("Fat (g)", min_value=0.0, value=5.0 + i*2, step=0.1, key=f"fat_{i}")
            carbs = st.number_input("Carbs (g)", min_value=0.0, value=15.0 + i*10, step=0.1, key=f"carb_{i}")
        
        max_qty = st.number_input("Max Qty (0 = unlimited)", min_value=0.0, value=0.0, step=1.0, key=f"maxqty_{i}")
        
        products.append(Nutrition(
            name=name,
            protein=protein,
            fat=fat,
            carbs=carbs,
            calories=calories,
            price=price,
            max_qty=(max_qty if max_qty > 0 else None)
        ))

# Constraints section
st.header("⚖️ Constraints")
st.markdown("Set minimum and maximum values (0 = no limit):")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Calories (kcal)")
    min_calories = st.number_input("Minimum Calories", min_value=0.0, value=2000.0, step=50.0, key="min_cal")
    max_calories_input = st.number_input("Maximum Calories", min_value=0.0, value=0.0, step=50.0, key="max_cal")
    max_calories = float('inf') if max_calories_input == 0 else max_calories_input

with col2:
    st.subheader("Budget ($)")
    budget_input = st.number_input("Maximum Budget", min_value=0.0, value=500.0, step=10.0, key="budget")
    budget = budget_input if budget_input > 0 else None

st.subheader("Protein / Fat / Carbs (g)")
col_p, col_f, col_c = st.columns(3)

with col_p:
    st.markdown("**Protein**")
    min_protein = st.number_input("Min", min_value=0.0, value=50.0, step=1.0, key="min_prot")
    max_protein_input = st.number_input("Max", min_value=0.0, value=0.0, step=1.0, key="max_prot")
    max_protein = float('inf') if max_protein_input == 0 else max_protein_input

with col_f:
    st.markdown("**Fat**")
    min_fat = st.number_input("Min", min_value=0.0, value=30.0, step=1.0, key="min_fat")
    max_fat_input = st.number_input("Max", min_value=0.0, value=0.0, step=1.0, key="max_fat")
    max_fat = float('inf') if max_fat_input == 0 else max_fat_input

with col_c:
    st.markdown("**Carbs**")
    min_carbs = st.number_input("Min", min_value=0.0, value=200.0, step=1.0, key="min_carb")
    max_carbs_input = st.number_input("Max", min_value=0.0, value=0.0, step=1.0, key="max_carb")
    max_carbs = float('inf') if max_carbs_input == 0 else max_carbs_input

st.markdown("---")

# Optimize button
if st.button("🚀 Run Optimization", type="primary", use_container_width=True):
    with st.spinner("Solving with simplex method..."):
        try:
            # Build constraints
            constraints = Constraints(
                name="User constraints",
                range_protein=(min_protein, max_protein),
                range_fat=(min_fat, max_fat),
                range_carbs=(min_carbs, max_carbs),
                calories=(min_calories, max_calories),
                budget=budget
            )
            
            # Build and solve model
            model = ModelNutrition(products, constraints)
            result = model.optimize(objective=objective)
            print(result)
            st.success("✅ Optimization completed successfully!")
            
            # Display results
            st.subheader("📊 Results")
            
            solution = result['solution']
            optimal_value = result['optimal_value']
            
            # Filter products with non-zero quantity
            selected = [(name, qty) for name, qty in solution.items() if qty > 1e-6]
            
            if not selected:
                st.warning("⚠️ No solution found or all quantities are zero. Check constraints.")
            else:
                # Build result table
                result_data = []
                total_cost = 0
                total_calories = 0
                total_protein = 0
                total_fat = 0
                total_carbs = 0
                
                for prod_name, qty in selected:
                    prod = next(p for p in products if p.name == prod_name)
                    cost = qty * prod.price
                    cals = qty * prod.calories
                    prot = qty * prod.protein
                    fats = qty * prod.fat
                    carb = qty * prod.carbs
                    
                    total_cost += cost
                    total_calories += cals
                    total_protein += prot
                    total_fat += fats
                    total_carbs += carb
                    
                    result_data.append({
                        "Product": prod_name,
                        "Quantity": f"{qty:.2f}",
                        "Price ($)": f"{cost:.2f}",
                        "Calories": f"{cals:.1f}",
                        "Protein (g)": f"{prot:.1f}",
                        "Fat (g)": f"{fats:.1f}",
                        "Carbs (g)": f"{carb:.1f}"
                    })
                
                st.table(result_data)
                
                # Summary metrics
                st.subheader("📈 Summary Metrics")
                metric_cols = st.columns(5)
                
                with metric_cols[0]:
                    st.metric("Cost", f"${total_cost:.2f}")
                with metric_cols[1]:
                    st.metric("Calories", f"{total_calories:.0f} kcal")
                with metric_cols[2]:
                    st.metric("Protein", f"{total_protein:.1f} g")
                with metric_cols[3]:
                    st.metric("Fat", f"{total_fat:.1f} g")
                with metric_cols[4]:
                    st.metric("Carbs", f"{total_carbs:.1f} g")
                
                # Optimal value explanation
                st.info(f"""
                **Objective Value:** {abs(optimal_value):.2f}  
                {'(minimum cost)' if objective == 'min_cost' else '(maximum calories)'}
                """)
        
        except Exception as e:
            st.error(f"❌ Optimization error: {str(e)}")
            st.info("""
            **Possible causes:**
            - Constraints are contradictory (impossible to satisfy all simultaneously)
            - Budget is too low to meet minimum requirements
            - Minimum macros/calories values are too high
            
            Try relaxing constraints or increasing budget.
            """)

# Footer
st.markdown("---")
st.caption("💡 Tip: Set maximums to 0 if you don't want upper limits. The app uses the simplex method from the `core.simplex` module.")
