import streamlit as st

# Настройка страницы
st.set_page_config(page_title="Калькулятор Бухгалтерских Услуг", layout="centered")

# Стилизация (сделаем интерфейс более профессиональным)
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stButton>button { width: 100%; background-color: #007bff; color: white; }
    .big-font { font-size:24px !important; font-weight: bold; color: #1e293b; }
    </style>
    """, unsafe_allow_html=True)

st.title("🧮 Калькулятор стоимости бухуслуг")
st.write("Внутренний инструмент для быстрого расчета стоимости обслуживания.")

st.markdown("---")

# 1. ВВОДНЫЕ ДАННЫЕ
st.header("1. Параметры бизнеса")

legal_form = st.radio(
    "Форма собственности", 
    ["ИП (Индивидуальный предприниматель)", "ТОО (Товарищество с огр. ответственностью)"]
)

tax_regime = st.selectbox(
    "Режим налогообложения", 
    ["Упрощенный режим", "Общеустановленный режим (ОУР)"]
)

# Динамическая логика для сотрудников
if "ТОО" in legal_form:
    st.info("ℹ️ Для ТОО минимум 1 сотрудник (директор) учтен автоматически по закону.")
    employees = st.number_input("Количество сотрудников (включая директора)", min_value=1, value=1, step=1)
else:
    employees = st.number_input("Количество сотрудников", min_value=0, value=0, step=1)

operations = st.number_input("Количество первичных операций в месяц", min_value=0, value=25, step=5)

st.header("2. Дополнительные услуги (в месяц)")
consultations = st.number_input("Часов консультаций", min_value=0, value=0, step=1)
stat_reports = st.number_input("Количество статистических отчетов", min_value=0, value=0, step=1)
gov_repr = st.checkbox("Представление в гос. органах и банках")
mgmt_report = st.checkbox("Управленческая отчетность")

st.markdown("---")

# 2. РАСЧЕТ СЕБЕСТОИМОСТИ (на основе вашего файла тарифов)
PRICE_PER_OP = 500
PRICE_PER_EMP = 2500
PRICE_PER_CONSULT = 6500
PRICE_STAT_REPORT = 5000
PRICE_GOV_REPR = 10000
PRICE_MGMT_REPORT = 40000

# Цены налоговых отчетов из файла
COST_SEMI_ANNUAL = 25000  # Полугодовой (910 форма)
COST_QUARTERLY = 15000    # Квартальный (200 форма)
COST_ANNUAL = 70000       # Годовой
COST_MONTHLY_DECLR = 6000 # Ежемесячный

tax_monthly_share = 0

if tax_regime == "Упрощенный режим":
    # Базово: 2 полугодовых отчета в год = (2 * 25000) / 12 месяцев
    tax_monthly_share += (2 * COST_SEMI_ANNUAL) / 12
    
    # Новая логика: Если у ИП есть сотрудники ИЛИ это ТОО -> добавляется 4 квартальных отчета
    if employees > 0 or "ТОО" in legal_form:
        tax_monthly_share += (4 * COST_QUARTERLY) / 12
else:
    # Общеустановленный режим (ОУР)
    tax_monthly_share += (1 * COST_ANNUAL) / 12      # 1 годовой
    tax_monthly_share += (4 * COST_QUARTERLY) / 12    # 4 квартальных
    tax_monthly_share += COST_MONTHLY_DECLR           # Ежемесячные расчеты

# Наценка за специфику ТОО (сложный вывод прибыли, дивиденды, фин. отчетность)
too_surcharge = 15000 if "ТОО" in legal_form else 0

# Калькуляция составляющих
cost_ops = operations * PRICE_PER_OP
cost_emp = employees * PRICE_PER_EMP
cost_consult = consultations * PRICE_PER_CONSULT
cost_stat = stat_reports * PRICE_STAT_REPORT
cost_gov = PRICE_GOV_REPR if gov_repr else 0
cost_mgmt = PRICE_MGMT_REPORT if mgmt_report else 0

# Итоговая базовая себестоимость
total_raw = (cost_ops + cost_emp + tax_monthly_share + cost_consult + cost_stat + cost_gov + cost_mgmt + too_surcharge)

# Красивое округление ("наводим красоту" для клиента)
def round_beauty(price):
    if price < 30000:
        return round(price / 1000) * 1000
    elif price < 100000:
        return round(price / 5000) * 5000
    else:
        return round(price / 10000) * 10000

total_final = round_beauty(total_raw)

# 3. ВЫВОД РЕЗУЛЬТАТОВ КЛИЕНТУ
st.header("3. Итоговый расчет")

# Выделенная плашка с финальной стоимостью
st.success(f"### 💰 Рекомендуемая стоимость тарифа: {total_final:,.0f} ₸ / месяц")

# Раскрывающийся список с детализацией для менеджера по продажам
with st.expander("🔎 Посмотреть детализацию расчета (себестоимость)"):
    col1, col2 = st.columns(2)
    with col1:
        st.write(f"Операции ({operations} шт.):")
        st.write(f"Кадровый учет ({employees} чел.):")
        st.write("Налоговые отчеты (доля в мес.):")
        if too_surcharge > 0:
            st.write("Наценка за риски/дивиденды ТОО:")
        st.write("Дополнительные услуги:")
    with col2:
        st.write(f"**{cost_ops:,.0f} ₸**")
        st.write(f"**{cost_emp:,.0f} ₸**")
        st.write(f"**{tax_monthly_share:,.0f} ₸**")
        if too_surcharge > 0:
            st.write(f"**{too_surcharge:,.0f} ₸**")
        st.write(f"**{(cost_consult + cost_stat + cost_gov + cost_mgmt):,.0f} ₸**")
