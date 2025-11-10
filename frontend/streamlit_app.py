import sys
import os

# Ensure project root is on sys.path so package imports work when Streamlit runs
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

import streamlit as st
import pandas as pd

from handlers import product_handler


st.set_page_config(page_title="Diet / Product optimizer", layout="wide")

st.title("Оптимизация набора продуктов (симплекс)")

st.markdown(
    """
    Введите список продуктов (цена, калории, белки/жиры/углеводы) и ограничения.
    Выберите цель: минимизировать стоимость при соблюдении нормы калорий/БЖУ
    или максимизировать калории/прибыль при ограниченном бюджете.
    """
)

with st.form('products_form'):
    n = st.number_input('Число продуктов', min_value=1, max_value=20, value=3)
    products = []
    st.write('---')
    for i in range(int(n)):
        st.subheader(f'Продукт #{i+1}')
        cols = st.columns(6)
        name = cols[0].text_input('Название', value=f'Product {i+1}', key=f'name_{i}')
        price = cols[1].number_input('Цена', min_value=0.0, value=1.0, key=f'price_{i}')
        calories = cols[2].number_input('Ккал', min_value=0.0, value=100.0, key=f'cal_{i}')
        protein = cols[3].number_input('Белки (г)', min_value=0.0, value=10.0, key=f'prot_{i}')
        fat = cols[4].number_input('Жиры (г)', min_value=0.0, value=5.0, key=f'fat_{i}')
        carbs = cols[5].number_input('Углеводы (г)', min_value=0.0, value=10.0, key=f'carb_{i}')
        profit = st.number_input('Процент/выгода (для max_profit)', value=0.0, key=f'profit_{i}')
        max_qty = st.number_input('max_qty (опционально, 0=нет)', min_value=0.0, value=0.0, key=f'max_{i}')

        prod = {
            'name': name,
            'price': float(price),
            'calories': float(calories),
            'protein': float(protein),
            'fat': float(fat),
            'carbs': float(carbs),
            'profit': float(profit),
        }
        if max_qty > 0:
            prod['max_qty'] = float(max_qty)
        products.append(prod)

    st.write('---')
    st.subheader('Ограничения и цель')
    objective = st.selectbox('Цель оптимизации', options=['min_cost', 'max_calories', 'max_profit'], index=0,
                             format_func=lambda x: {'min_cost': 'Минимизировать стоимость',
                                                    'max_calories': 'Максимизировать калории',
                                                    'max_profit': 'Максимизировать прибыль'}[x])
    budget = st.number_input('Бюджет (<=)', min_value=0.0, value=0.0, help='0 — без ограничения')
    if budget == 0.0:
        budget = None

    calories_min = st.number_input('Калорий минимум (>=)', min_value=0.0, value=0.0)
    if calories_min == 0.0:
        calories_min = None
    calories_max = st.number_input('Калорий максимум (<=)', min_value=0.0, value=0.0)
    if calories_max == 0.0:
        calories_max = None

    st.write('БЖУ — минимумы (опционально)')
    prot_min = st.number_input('Белки минимум (г)', min_value=0.0, value=0.0)
    fat_min = st.number_input('Жиры минимум (г)', min_value=0.0, value=0.0)
    carb_min = st.number_input('Углеводы минимум (г)', min_value=0.0, value=0.0)
    if prot_min == 0.0:
        prot_min = None
    if fat_min == 0.0:
        fat_min = None
    if carb_min == 0.0:
        carb_min = None

    use_ratios = st.checkbox('Задать пропорции БЖУ (в сумме = 1.0)', value=False)
    ratios = None
    if use_ratios:
        st.write('Введите желаемые доли белков/жиров/углеводов (сумма ≈ 1.0)')
        r1 = st.number_input('Белки доля', min_value=0.0, max_value=1.0, value=0.3)
        r2 = st.number_input('Жиры доля', min_value=0.0, max_value=1.0, value=0.3)
        r3 = st.number_input('Углеводы доля', min_value=0.0, max_value=1.0, value=0.4)
        ratios = {'protein': r1, 'fat': r2, 'carbs': r3}

    submitted = st.form_submit_button('Запустить оптимизацию')

if submitted:
    constraints = {
        'objective': objective,
        'budget': budget,
        'calories_min': calories_min,
        'calories_max': calories_max,
        'protein_min': prot_min,
        'fat_min': fat_min,
        'carbs_min': carb_min,
        'macro_ratios': ratios,
    }

    with st.spinner('Вычисление...'):
        out = product_handler.optimize_products(products, constraints)

    if out.get('status') != 'ok':
        st.error(f"Ошибка: {out.get('status')}")
    else:
        st.success('Оптимизация выполнена')
        sol = out['solution']
        df = pd.DataFrame([{
            'product': name,
            'quantity': qty,
            'price': next((p['price'] for p in products if p['name'] == name), 0.0),
            'calories_per_unit': next((p['calories'] for p in products if p['name'] == name), 0.0),
        } for name, qty in sol.items()])

        df['cost'] = df['quantity'] * df['price']
        df['total_calories'] = df['quantity'] * df['calories_per_unit']

        st.subheader('План потребления')
        st.dataframe(df.style.format({'quantity': '{:.4f}', 'cost': '{:.2f}', 'total_calories': '{:.2f}'}))

        st.write('Итоговая цель:', objective)
        st.write('Значение цели:', float(out.get('objective_value', 0.0)))

        # Simple charts
        st.subheader('Графики')
        st.bar_chart(df.set_index('product')[['quantity', 'cost', 'total_calories']])

        st.write('Сырые данные решения (raw):', out.get('raw_value'))
