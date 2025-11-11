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
    page_title="Оптимизация продуктов — Симплекс",
    page_icon="🥗",
    layout="wide"
)

st.title("🥗 Оптимизация набора продуктов")
st.markdown("""
Эта программа находит оптимальное количество продуктов с учётом калорий, белков, жиров, углеводов и бюджета.  
Используется **симплекс-метод** для решения задачи линейного программирования.
""")

# Sidebar for objective selection
with st.sidebar:
    st.header("⚙️ Настройки оптимизации")
    objective = st.radio(
        "Цель оптимизации:",
        options=["min_cost", "max_calories"],
        format_func=lambda x: "Минимизировать стоимость" if x == "min_cost" else "Максимизировать калории",
        index=0
    )
    st.info("**min_cost**: найти самый дешёвый набор при выполнении требований\n\n**max_calories**: максимум калорий в рамках бюджета")

# Products section
st.header("📦 Продукты")
st.markdown("Введите данные о продуктах (цена, калории, БЖУ):")

num_products = st.number_input("Количество продуктов", min_value=1, max_value=20, value=3, step=1)

products = []
cols_per_row = 3
for i in range(num_products):
    with st.expander(f"Продукт #{i+1}", expanded=(i < 2)):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            name = st.text_input("Название", value=f"Продукт {i+1}", key=f"name_{i}")
            price = st.number_input("Цена (руб)", min_value=0.0, value=10.0 + i*5, step=0.1, key=f"price_{i}")
        
        with col2:
            calories = st.number_input("Калории (ккал)", min_value=0.0, value=100.0 + i*50, step=1.0, key=f"cal_{i}")
            protein = st.number_input("Белки (г)", min_value=0.0, value=10.0 + i*5, step=0.1, key=f"prot_{i}")
        
        with col3:
            fat = st.number_input("Жиры (г)", min_value=0.0, value=5.0 + i*2, step=0.1, key=f"fat_{i}")
            carbs = st.number_input("Углеводы (г)", min_value=0.0, value=15.0 + i*10, step=0.1, key=f"carb_{i}")
        
        max_qty = st.number_input("Макс. кол-во (0 = без ограничений)", min_value=0.0, value=0.0, step=1.0, key=f"maxqty_{i}")
        
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
st.header("⚖️ Ограничения")
st.markdown("Задайте минимальные и максимальные значения (0 = нет ограничения):")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Калории (ккал)")
    min_calories = st.number_input("Минимум калорий", min_value=0.0, value=2000.0, step=50.0, key="min_cal")
    max_calories_input = st.number_input("Максимум калорий", min_value=0.0, value=0.0, step=50.0, key="max_cal")
    max_calories = float('inf') if max_calories_input == 0 else max_calories_input

with col2:
    st.subheader("Бюджет (руб)")
    budget_input = st.number_input("Максимальный бюджет", min_value=0.0, value=500.0, step=10.0, key="budget")
    budget = budget_input if budget_input > 0 else None

st.subheader("Белки / Жиры / Углеводы (г)")
col_p, col_f, col_c = st.columns(3)

with col_p:
    st.markdown("**Белки**")
    min_protein = st.number_input("Мин", min_value=0.0, value=50.0, step=1.0, key="min_prot")
    max_protein_input = st.number_input("Макс", min_value=0.0, value=0.0, step=1.0, key="max_prot")
    max_protein = float('inf') if max_protein_input == 0 else max_protein_input

with col_f:
    st.markdown("**Жиры**")
    min_fat = st.number_input("Мин", min_value=0.0, value=30.0, step=1.0, key="min_fat")
    max_fat_input = st.number_input("Макс", min_value=0.0, value=0.0, step=1.0, key="max_fat")
    max_fat = float('inf') if max_fat_input == 0 else max_fat_input

with col_c:
    st.markdown("**Углеводы**")
    min_carbs = st.number_input("Мин", min_value=0.0, value=200.0, step=1.0, key="min_carb")
    max_carbs_input = st.number_input("Макс", min_value=0.0, value=0.0, step=1.0, key="max_carb")
    max_carbs = float('inf') if max_carbs_input == 0 else max_carbs_input

st.markdown("---")

# Optimize button
if st.button("🚀 Запустить оптимизацию", type="primary", use_container_width=True):
    with st.spinner("Решаем задачу симплекс-методом..."):
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
            st.success("✅ Оптимизация успешно завершена!")
            
            # Display results
            st.subheader("📊 Результаты")
            
            solution = result['solution']
            optimal_value = result['optimal_value']
            
            # Filter products with non-zero quantity
            selected = [(name, qty) for name, qty in solution.items() if qty > 1e-6]
            
            if not selected:
                st.warning("⚠️ Решение не найдено или все количества равны нулю. Проверьте ограничения.")
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
                        "Продукт": prod_name,
                        "Количество": f"{qty:.2f}",
                        "Цена (руб)": f"{cost:.2f}",
                        "Калории": f"{cals:.1f}",
                        "Белки (г)": f"{prot:.1f}",
                        "Жиры (г)": f"{fats:.1f}",
                        "Углеводы (г)": f"{carb:.1f}"
                    })
                
                st.table(result_data)
                
                # Summary metrics
                st.subheader("📈 Итоговые показатели")
                metric_cols = st.columns(5)
                
                with metric_cols[0]:
                    st.metric("Стоимость", f"{total_cost:.2f} руб")
                with metric_cols[1]:
                    st.metric("Калории", f"{total_calories:.0f} ккал")
                with metric_cols[2]:
                    st.metric("Белки", f"{total_protein:.1f} г")
                with metric_cols[3]:
                    st.metric("Жиры", f"{total_fat:.1f} г")
                with metric_cols[4]:
                    st.metric("Углеводы", f"{total_carbs:.1f} г")
                
                # Optimal value explanation
                st.info(f"""
                **Целевое значение:** {abs(optimal_value):.2f}  
                {'(минимальная стоимость)' if objective == 'min_cost' else '(максимальные калории)'}
                """)
        
        except Exception as e:
            st.error(f"❌ Ошибка при оптимизации: {str(e)}")
            st.info("""
            **Возможные причины:**
            - Ограничения противоречивы (невозможно выполнить все одновременно)
            - Бюджет слишком мал для достижения минимальных требований
            - Минимальные значения БЖУ/калорий слишком высокие
            
            Попробуйте ослабить ограничения или увеличить бюджет.
            """)

# Footer
st.markdown("---")
st.caption("💡 Совет: установите максимумы в 0, если не хотите ограничивать сверху. Приложение использует симплекс-метод из модуля `core.simplex`.")
