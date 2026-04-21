import numpy as np
import pandas as pd
from scipy.integrate import odeint
from datetime import datetime, timedelta

np.random.seed(100)
np.random.default_rng(seed=42)

# ------------------------------------------------------------
# Фиксированные индивидуальные параметры человека (из статьи)
a_tilda = [0.0015, 0.0010, 0.045]   # ã₁, ã₂, ã₃
b_tilda = [0.480, 0.023, 3]    # b̃₁, b̃₂, b̃₃
k_tilda = [0.65, 0.420, 0.25]      # k̃₁, k̃₂, k̃₃
gamma_tilda = [0.025, 0.050, 0.15] # γ̃₁, γ̃₂, γ̃₃
h_tilda = 0.89                     # h̃₁
d = [0.0002, 0.0007, 0.07]         # d₁, d₂, d₃
c = [0.0015, 0.0009, 0.010]        # c₁, c₂, c₃

# Коэффициенты чувствительности для S(t) (можно настраивать)
kW = 0.4   # чувствительность к снижению работоспособности
kF = 0.3   # чувствительность к утомляемости
kE = 0.4  # чувствительность к ошибаемости
S0 = 0.3   # базовая автономность (при W=1, F=0, E=0)

# Рабочая нагрузка (константа)
L = 0.7

# Начальные условия для разных дней (W0, F0, E0)
# W0 = 0.5 для всех, F0 и E0 варьируются
init_conditions = {
    0: (0.10, 0.05, 0.10),   # понедельник
    1: (0.20, 0.10, 0.08),   # вторник
    2: (0.15, 0.12, 0.07),   # среда
    3: (0.10, 0.17, 0.09),   # четверг
    4: (0.20, 0.15, 0.12)    # пятница
}

# ------------------------------------------------------------
# Функция правой части системы (1)
def system(y, t, params):
    W, F, E = y
    # Уровень автономности S(t) по формуле (3)
    S = S0 + kW * (1 - W) + kF * F + kE * E
    S = np.clip(S, 0.0, 1.0)   # ограничиваем [0,1]
    
    # Коэффициенты из внешних параметров
    a1, a2, a3 = a_tilda
    b1, b2, b3 = b_tilda
    k1, k2, k3 = k_tilda
    g1, g2, g3 = gamma_tilda
    h = h_tilda
    d1, d2, d3 = d
    c1, c2, c3 = c
    
    # Уравнения
    dWdt = a1 * (W / (d1*W + c1)) * (1 - W/k1) - b1 * W * F - h * W * E - g1 * L * (1 - S)
    dFdt = a2 * (F / (d2*F + c2)) * (1 - F/k2) + b2 * W * F + g2 * L * (1 - S)
    dEdt = a3 * (E / (d3*E + c3)) * (1 - E/k3) + b3 * F * E + g3 * L * (1 - S)
    return [dWdt, dFdt, dEdt]

# ------------------------------------------------------------
def generate_survey_data(start_date, num_weeks=4):
    """
    Генерирует опросы для num_weeks недель (пн–пт) и сохраняет в CSV.
    """
    data_rows = []
    current_date = start_date
    # Ищем первый понедельник
    while current_date.weekday() != 0:
        current_date += timedelta(days=1)
    
    # Временная сетка: с 9:00 до 19:00 с шагом 20 минут
    t_start = 9.0
    t_end = 19.0
    dt_hours = 20 / 60.0   # 20 минут = 1/12 часа
    t_eval = np.arange(t_start, t_end + dt_hours, dt_hours)
    
    
    for week in range(num_weeks):
        for day_offset in range(5):   # пн–пт
            day_idx = day_offset
            date = current_date + timedelta(days=day_offset)
            day_of_week = date.weekday()   # 0-4
            y0 = init_conditions[day_of_week]
            
            # Интегрируем систему
            sol = odeint(system, y0, t_eval, args=(None,))
            W_vals, F_vals, E_vals = sol[:,0], sol[:,1], sol[:,2]
            
            # Для каждого момента времени сохраняем опрос
            for i, t in enumerate(t_eval):
                # Преобразуем F и E в fatigue и concentration
                fatigue_raw = 1 + 9 * F_vals[i]
                concentration_raw = 10 - 9 * E_vals[i]
                # Добавляем шум (нормальный, σ=0.4)
                fatigue_noisy = fatigue_raw + np.random.normal(0, 0.4)
                concentration_noisy = concentration_raw + np.random.normal(0, 0.4)
                fatigue = int(np.clip(np.round(fatigue_noisy), 1, 10))
                concentration = int(np.clip(np.round(concentration_noisy), 1, 10))
                
                # Время в формате datetime
                hour = int(t)
                minute = int(round((t - hour) * 60))
                if minute == 60:
                    hour += 1
                    minute = 0
                # Пропускаем время после 19:00
                if hour >= 19 and minute > 0:
                    continue
                timestamp = datetime(date.year, date.month, date.day, hour, minute, 0)
                
                data_rows.append({
                    'timestamp': timestamp,
                    'fatigue_level': fatigue,
                    'concentration_level': concentration,
                    'hour_of_day': timestamp.hour,
                    'minute_of_day': timestamp.minute,
                    'day_of_week': day_of_week
                })
        # Переход к следующей неделе
        current_date += timedelta(days=7)
    
    df = pd.DataFrame(data_rows)
    df.insert(0, 'id', range(1, len(df)+1))   # <-- добавить столбец id в начало
    df.to_csv('survey_response.csv', index=False, encoding='utf-8')
    print(f"Сгенерировано {len(df)} записей. Файл: survey_response.csv")
    return df

def plot_survey_data(csv_path='survey_response.csv',week_offset = 0):
    """
    Строит 6 subplot'ов для fatigue_level и concentration_level по дням недели.
    Данные загружаются из CSV-файла, сгенерированного ранее.
    """
    import pandas as pd
    import matplotlib.pyplot as plt
    import numpy as np

    # Загрузка данных
    df = pd.read_csv(csv_path, parse_dates=['timestamp'])
    if df.empty:
        print("Нет данных в CSV.")
        return
    
    
    # Выбор одной недели
    min_date = df['timestamp'].min()
    print(min_date)
    start_week = min_date + pd.Timedelta(weeks=week_offset)
    print(start_week)
    end_week = start_week + pd.Timedelta(weeks=4)
    print(end_week)
    df = df[(df['timestamp'] >= start_week) & (df['timestamp'] < end_week)]

    # Подготовка данных
    df['time_hours'] = df['timestamp'].dt.hour + df['timestamp'].dt.minute / 60.0
    # Ограничим время 9-19 часами
    df = df[(df['time_hours'] >= 9) & (df['time_hours'] <= 19)]

    days = ['Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница']
    fig, axes = plt.subplots(2, 3, figsize=(15, 10))
    axes = axes.flatten()

    # 1. Графики по дням недели
    for i, day_idx in enumerate(range(5)):
        ax = axes[i]
        day_data = df[df['day_of_week'] == day_idx].copy()
        if not day_data.empty:
            day_data = day_data.sort_values('time_hours')
            # Исходные точки (можно закомментировать)
            ax.plot(day_data['time_hours'], day_data['fatigue_level'], 'o', alpha=0.3, markersize=3, color='blue')
            ax.plot(day_data['time_hours'], day_data['concentration_level'], 'o', alpha=0.3, markersize=3, color='red')
            # Сглаженные линии
            ax.plot(day_data['time_hours'], day_data['fatigue_level'], 'b-', linewidth=2, label='Усталость')
            ax.plot(day_data['time_hours'], day_data['concentration_level'], 'r-', linewidth=2, label='Концентрация')
            ax.axhline(y=5, color='gray', linestyle='--', linewidth=1, alpha=0.7)
            ax.set_title(days[i])
            ax.set_xlabel('Время суток (часы)')
            ax.set_ylabel('Уровень (1-10)')
            ax.set_ylim(1, 10)
            ax.set_xlim(9, 19)
            ax.grid(True, linestyle='--', alpha=0.6)
            ax.legend(fontsize='small')
        else:
            ax.text(0.5, 0.5, 'Нет данных', ha='center', va='center', transform=ax.transAxes)
            ax.set_title(days[i])
            ax.set_xlim(9, 19)

    # 2. Шестой subplot – средние кривые по всем дням
    ax_avg = axes[5]
    # Группировка по бинам времени (0.1 часа ≈ 6 минут)
    df['time_bin'] = np.round(df['time_hours'] * 10) / 10.0
    avg_fatigue = df.groupby('time_bin')['fatigue_level'].mean().reset_index()
    avg_concentration = df.groupby('time_bin')['concentration_level'].mean().reset_index()
    avg_data = pd.merge(avg_fatigue, avg_concentration, on='time_bin')
    avg_data = avg_data.sort_values('time_bin')
    # Сглаживание
    avg_data['fatigue_smooth'] = avg_data['fatigue_level'].rolling(window=3, center=True).mean()
    avg_data['concentration_smooth'] = avg_data['concentration_level'].rolling(window=3, center=True).mean()
    ax_avg.plot(avg_data['time_bin'], avg_data['fatigue_smooth'], 'b-', linewidth=2, label='Усталость (средняя)')
    ax_avg.plot(avg_data['time_bin'], avg_data['concentration_smooth'], 'r-', linewidth=2, label='Концентрация (средняя)')
    ax_avg.axhline(y=5, color='gray', linestyle='--', linewidth=1, alpha=0.7)
    ax_avg.set_title('Средние за смену (все дни)')
    ax_avg.set_xlabel('Время суток (часы)')
    ax_avg.set_ylabel('Уровень (1-10)')
    ax_avg.set_ylim(1, 10)
    ax_avg.set_xlim(9, 19)
    ax_avg.grid(True, linestyle='--', alpha=0.6)
    ax_avg.legend(fontsize='small')

    plt.tight_layout()
    plt.show()

# ------------------------------------------------------------
if __name__ == "__main__":
    start = datetime(2026, 3, 30)   # 1 апреля 2026
    generate_survey_data(start, num_weeks=4)
    plot_survey_data('survey_response.csv')