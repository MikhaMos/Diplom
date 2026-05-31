import numpy as np
import pandas as pd
from scipy.integrate import solve_ivp
from datetime import datetime, timedelta

np.random.seed(100)
np.random.default_rng(seed=42)

# ------------------------------------------------------------
# Фиксированные индивидуальные параметры человека (из статьи)
a_tilda = [0.0015, 0.00162, 0.045]   # ã₁, ã₂, ã₃
b_tilda = [0.480, 0.233, 4.1]    # b̃₁, b̃₂, b̃₃
k_tilda = [0.65, 0.980, 0.2]      # k̃₁, k̃₂, k̃₃
gamma_tilda = [0.025, 0.050, 0.02] # γ̃₁, γ̃₂, γ̃₃
h_tilda = 0.89                     # h̃₁
d = [0.0002, 0.007, 0.05]         # d₁, d₂, d₃
c = [0.0015, 0.001, 0.010]        # c₁, c₂, c₃

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
    4: (0.10, 0.15, 0.12)    # пятница
}

# ------------------------------------------------------------
# Функция правой части системы (1)
def system(t, y, params):
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
def generate_survey_data(start_date, num_weeks):
    """
    Генерирует опросы для num_weeks недель (пн–пт) и сохраняет в CSV.
    """
    data_rows = []
    task_complexity_map = {}
    current_date = start_date
    # Ищем первый понедельник
    while current_date.weekday() != 0:
        current_date += timedelta(days=1)
    
    # Временная сетка: с 10:00 до 19:00 с шагом 20 минут
    t_start = 10.0
    t_end = 19.0
    step = 20/ 60.0   # 20 минут = 1/12 часа

    # Время обеда (начало перерыва) – 14:00
    lunch_time = 14.0
    lunch_end = lunch_time + 1

    # Создаём сетку через np.linspace, чтобы гарантировать попадание в границы
    n_steps = int(round((t_end - t_start) / step)) + 1
    t_eval = np.linspace(t_start, t_end, n_steps)

    # Точки до обеда (включительно) и после обеда (исключая точку обеда, чтобы не дублировать)
    t_before = t_eval[t_eval <= lunch_time]
    t_after = t_eval[t_eval > lunch_end]


    # Коэффициенты восстановления после обеда
    recovery_W = 1.4   # работоспособность увеличивается на 25%
    recovery_F = 0.6   # утомляемость снижается на 25%
    recovery_E = 0.6   # ошибаемость снижается на 25%

    
    for week in range(num_weeks):
        for day_offset in range(5):   # пн–пт
            day_idx = day_offset
            date = current_date + timedelta(days=day_offset)
            day_of_week = date.weekday()   # 0-4
            y0 = init_conditions[day_of_week]
            """
            sol = solve_ivp(system, t_span=(t_eval[0], t_eval[-1]), y0=y0, method='RK45',
                t_eval=t_eval, args=(None,), rtol=1e-6, atol=1e-8)
            W_vals, F_vals, E_vals = sol.y[0], sol.y[1], sol.y[2]
           """

            # Интегрируем систему
            # ---- ПЕРВЫЙ ЭТАП: до обеда ----
            sol = solve_ivp(system, t_span=(t_start, lunch_time), y0=y0, method='RK45',
                t_eval=t_before, args=(None,), rtol=1e-6, atol=1e-8)
            
            W1, F1, E1 = sol.y[0], sol.y[1], sol.y[2]
            
            # ---- КОРРЕКТИРОВКА после обеда ----
            W_last = W1[-1]
            F_last = F1[-1]
            E_last = E1[-1]
            W_new = min(1.0, W_last * recovery_W)      # не выше 1.0
            F_new = max(0.0, F_last * recovery_F)      # не ниже 0.0
            E_new = max(0.0, E_last * recovery_E)
            y0_after = (W_new, F_new, E_new)
            
            # ---- ВТОРОЙ ЭТАП: после обеда ----
            if len(t_after) > 0:
                sol2 = solve_ivp(system, t_span=(lunch_end, t_end), y0=y0_after,
                                 method='RK45', t_eval=t_after, args=(None,),
                                 rtol=1e-6, atol=1e-8)
                W2 = sol2.y[0]
                F2 = sol2.y[1]
                E2 = sol2.y[2]
                # Объединяем результаты
                W_vals = np.concatenate([W1, W2])
                F_vals = np.concatenate([F1, F2])
                E_vals = np.concatenate([E1, E2])
                times = np.concatenate([t_before, t_after])
            else:
                times = t_before
                W_vals, F_vals, E_vals = W1, F1, E1
      
                    
            # Для каждого момента времени сохраняем опрос
            hour_complexity = {}
            for hour in range(10, 19):
                # вероятность 0.4, 0.4,0.2
                task_complexity = np.random.choice([0, 1, 2], p=[0.2, 0.5, 0.3])
                hour_complexity[hour] = task_complexity
            
            # Для каждого момента времени сохраняем опрос
            for i, t in enumerate(times):

                # Если точка попадает в обед (ровно lunch_time) – пропускаем (оператор не работает)
                if lunch_time <= t < lunch_end:
                    continue

                # Преобразуем F и E в fatigue и concentration
                fatigue_raw = 1 + 9 * F_vals[i]
                concentration_raw = 10 - 9 * E_vals[i]


                if task_complexity == 0:
                    fatigue_raw = fatigue_raw * 0.7
                    concentration_raw = concentration_raw * 1.3

                if task_complexity == 2:
                    fatigue_raw = fatigue_raw * 1.2
                    concentration_raw = concentration_raw * 0.8

                # Добавляем шум (нормальный, σ=0.4)
                fatigue_noisy = fatigue_raw + np.random.normal(-0.5, 0.4)
                concentration_noisy = concentration_raw + np.random.normal(-0.5, 0.4)
                fatigue = int(np.clip(np.round(fatigue_noisy), 1, 10))
                concentration = int(np.clip(np.round(concentration_noisy), 1, 10))
                
                # Время в формате datetime
                hour = int(t)
                if hour not in hour_complexity:
                    continue
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
                    'minute_of_hour': timestamp.minute,
                    'day_of_week': day_of_week,
                    'task_complexity': hour_complexity[hour]
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
    # Ограничим время 10-19 часами
    df = df[(df['time_hours'] >= 10) & (df['time_hours'] <= 19)]

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
            ax.set_xlim(10, 19)
            ax.grid(True, linestyle='--', alpha=0.6)
            ax.legend(fontsize='small')
        else:
            ax.text(0.5, 0.5, 'Нет данных', ha='center', va='center', transform=ax.transAxes)
            ax.set_title(days[i])
            ax.set_xlim(10, 19)

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
    ax_avg.set_xlim(10, 19)
    ax_avg.grid(True, linestyle='--', alpha=0.6)
    ax_avg.legend(fontsize='small')

    plt.tight_layout()
    plt.show()

# ------------------------------------------------------------
if __name__ == "__main__":
    start = datetime(2026, 3, 2)   # 1 апреля 2026
    generate_survey_data(start, num_weeks=8)
    plot_survey_data('survey_response.csv')