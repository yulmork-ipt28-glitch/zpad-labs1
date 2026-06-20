import streamlit as st
import pandas as pd
import numpy as np

# Налаштовуємо сторінку програми на широкий формат
st.set_page_config(layout="wide", page_title="Лабораторна робота №5")

# --- Автоматична генерація демонстраційних даних ---
@st.cache_data
def load_data():
    years = list(range(2000, 2025))
    weeks = list(range(1, 53))
    regions = ["Вінницька", "Волинська", "Дніпропетровська", "Донецька", "Київська", "Львівська", "Одеська"]
    data = []
    for r in regions:
        for y in years:
            for w in weeks:
                data.append({
                    "Year": y, "Week": w, "Region": r,
                    "VCI": np.random.uniform(10, 90),
                    "TCI": np.random.uniform(10, 90),
                    "VHI": np.random.uniform(10, 90)
                })
    return pd.DataFrame(data)

df_original = load_data()

# Початкові дефолтні значення
DEFAULT_INDEX = "VHI"
DEFAULT_REGION = "Київська"
DEFAULT_WEEKS = (1, 52)
DEFAULT_YEARS = (2010, 2020)

# Ініціалізація ключів у session_state, якщо їх ще немає
if "index_key" not in st.session_state: st.session_state.index_key = DEFAULT_INDEX
if "region_key" not in st.session_state: st.session_state.region_key = DEFAULT_REGION
if "weeks_key" not in st.session_state: st.session_state.weeks_key = DEFAULT_WEEKS
if "years_key" not in st.session_state: st.session_state.years_key = DEFAULT_YEARS
if "sort_asc_key" not in st.session_state: st.session_state.sort_asc_key = False
if "sort_desc_key" not in st.session_state: st.session_state.sort_desc_key = False

# Функція для кнопки скидання фільтрів
def reset_all_filters():
    st.session_state.index_key = DEFAULT_INDEX
    st.session_state.region_key = DEFAULT_REGION
    st.session_state.weeks_key = DEFAULT_WEEKS
    st.session_state.years_key = DEFAULT_YEARS
    st.session_state.sort_asc_key = False
    st.session_state.sort_desc_key = False

# Функції для контролю чекбоксів сортування
def handle_asc_change():
    if st.session_state.sort_asc_key:
        st.session_state.sort_desc_key = False

def handle_desc_change():
    if st.session_state.sort_desc_key:
        st.session_state.sort_asc_key = False

# Створюємо дві колонки (ліва для фільтрів, права для результатів)
col_sidebar, col_main = st.columns([1, 3])

with col_sidebar:
    st.header("⚙️ Панель керування")
    
    # Вибір індексу
    selected_index = st.selectbox("1. Оберіть часовий ряд:", options=["VCI", "TCI", "VHI"], key="index_key")
    
    # Вибір області
    selected_region = st.selectbox("2. Оберіть область:", options=sorted(df_original["Region"].unique()), key="region_key")
    
    # Слайдери тижнів та років
    selected_weeks = st.slider("3. Інтервал тижнів:", min_value=1, max_value=52, key="weeks_key")
    selected_years = st.slider("4. Інтервал років:", min_value=int(df_original["Year"].min()), max_value=int(df_original["Year"].max()), key="years_key")
    
    st.write("---")
    st.subheader("Сортування")
    
    # Чекбокси сортування з безпечною логікою перемикання
    sort_asc = st.checkbox("За зростанням", key="sort_asc_key", on_change=handle_asc_change)
    sort_desc = st.checkbox("За спаданням", key="sort_desc_key", on_change=handle_desc_change)
    
    st.write("---")
    st.button("🔄 Скинути всі фільтри", on_click=reset_all_filters, use_container_width=True)

# --- Логіка обробки та фільтрації даних ---
df_time_filtered = df_original[
    (df_original["Year"] >= selected_years[0]) & (df_original["Year"] <= selected_years[1]) &
    (df_original["Week"] >= selected_weeks[0]) & (df_original["Week"] <= selected_weeks[1])
]
df_region_filtered = df_time_filtered[df_time_filtered["Region"] == selected_region].copy()
df_region_filtered["Period"] = df_region_filtered["Year"].astype(str) + "-W" + df_region_filtered["Week"].astype(str)

df_table_display = df_region_filtered.copy()

if sort_asc: 
    df_table_display = df_table_display.sort_values(by=selected_index, ascending=True)
elif sort_desc: 
    df_table_display = df_table_display.sort_values(by=selected_index, ascending=False)

# --- Відображення результатів (Права колонка) ---
with col_main:
    st.title("📊 Результати аналізу індексів")
    tab_table, tab_chart1, tab_chart2 = st.tabs(["📋 Таблиця даних", "📈 Графік часового ряду", "⚔️ Порівняння областей"])
    
    with tab_table:
        st.subheader("Відфільтрована таблиця")
        st.dataframe(df_table_display[["Year", "Week", "Region", "VCI", "TCI", "VHI"]], use_container_width=True, hide_index=True)
    
    with tab_chart1:
        st.subheader(f"Динаміка індексу {selected_index} для області: {selected_region}")
        if not df_region_filtered.empty:
            chart_chronological = df_region_filtered.sort_values(by=["Year", "Week"])
            st.line_chart(data=chart_chronological, x="Period", y=selected_index, use_container_width=True)
        else:
            st.warning("Немає даних.")
            
    with tab_chart2:
        st.subheader(f"Порівняння середнього значення {selected_index} між областями")
        if not df_time_filtered.empty:
            df_compare = df_time_filtered.groupby("Region")[selected_index].mean().reset_index()
            df_compare["Статус області"] = df_compare["Region"].apply(lambda x: "Обрана область" if x == selected_region else "Інші області")
            st.bar_chart(data=df_compare, x="Region", y=selected_index, color="Статус області", use_container_width=True)
        else:
            st.warning("Немає даних.")