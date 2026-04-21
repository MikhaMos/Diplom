import sqlite3
import pickle
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from sklearn.metrics import confusion_matrix, ConfusionMatrixDisplay
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from datetime import datetime
from database import Database
from ml_model import FatiguePredictor

# ----------------------------------------------------------------------
# 1. Загрузка модели
def load_model(model_path="fatigue_model.pkl"):
    with open(model_path, "rb") as f:
        data = pickle.load(f)
    return data['model'], data['scaler']

# ----------------------------------------------------------------------
# 2. Загрузка данных из БД и формирование X, y, timestamps
def load_data_from_db(db, limit=1000):
    rows = db.get_training_data(limit=limit)
    if not rows:
        return None, None, None
    predictor = FatiguePredictor()
    X_list = []
    y_list = []
    timestamps = []
    for row in rows:
        # row: (timestamp, fatigue, concentration) или больше полей
        if len(row) == 3:
            ts_str, fatigue, concentration = row
            dt = datetime.fromisoformat(ts_str)
        else:
            # если get_training_data возвращает больше полей (например, с минутами)
            ts_str = row[0]
            fatigue = row[4] if len(row) > 4 else row[1]
            concentration = row[5] if len(row) > 5 else row[2]
            dt = datetime.fromisoformat(ts_str)
        features = predictor.extract_features(dt)
        target = 1 if (fatigue >= 6 and concentration <= 4) else 0
        X_list.append(features)
        y_list.append(target)
        timestamps.append(dt)
    return np.array(X_list), np.array(y_list), timestamps

# ----------------------------------------------------------------------
# 3. График динамики вероятности по времени (хронология)
def plot_prediction_over_time(db, threshold=0.55):
    import sqlite3
    import pandas as pd
    import numpy as np
    import matplotlib.pyplot as plt

    conn = sqlite3.connect(db.db)
    query = "SELECT timestamp, prob_class1 FROM ml_predictions ORDER BY timestamp"
    df = pd.read_sql_query(query, conn)
    conn.close()
    if df.empty:
        print("Нет данных в ml_predictions")
        return

    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df['day_of_week'] = df['timestamp'].dt.weekday
    df['time_hours'] = df['timestamp'].dt.hour + df['timestamp'].dt.minute / 60.0
    df = df[(df['day_of_week'].isin([0,1,2,3,4])) & (df['time_hours'] >= 9) & (df['time_hours'] <= 19)]

    days = ['Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница']
    fig, axes = plt.subplots(2, 3, figsize=(15, 10))
    axes = axes.flatten()

    for i, day_idx in enumerate(range(5)):
        ax = axes[i]
        day_data = df[df['day_of_week'] == day_idx].copy()
        if not day_data.empty:
            day_data = day_data.sort_values('time_hours')
            
            ax.plot(day_data['time_hours'], day_data['prob_class1'], 'o', alpha=0.4, markersize=4, label='Вероятность усталости')
            ax.plot(day_data['time_hours'], day_data['prob_class1'], 'r-', linewidth=1, label='Кривая prob_class1')
            ax.set_title(days[i])
            ax.set_xlabel('Время суток (часы)')
            ax.set_ylabel('Вероятность усталости')
            ax.set_ylim(0, 1)
            ax.set_xlim(9, 19)
            ax.axhline(y=0.55, color='blue', linestyle='--', linewidth=1.5, label='Порог 0.55')
            ax.grid(True, linestyle='--', alpha=0.6)
            ax.legend(fontsize='small')
        else:
            ax.text(0.5, 0.5, 'Нет данных', ha='center', va='center', transform=ax.transAxes)
            ax.set_title(days[i])
            ax.set_xlim(9, 19)

    # Шестой subplot – средняя кривая
    ax_avg = axes[5]
    df['time_bin'] = np.round(df['time_hours'] * 10) / 10.0
    avg_data = df.groupby('time_bin')['prob_class1'].mean().reset_index()
    avg_data = avg_data.sort_values('time_bin')
    avg_data['prob_smooth'] = avg_data['prob_class1'].rolling(window=3, center=True).mean()
    ax_avg.plot(avg_data['time_bin'], avg_data['prob_class1'], 'o', alpha=0.4, markersize=3, label='Средняя по интервалам')
    ax_avg.plot(avg_data['time_bin'], avg_data['prob_smooth'], 'g-', linewidth=2, label='Сглаженная средняя')
    ax_avg.axhline(y=0.55, color='red', linestyle='--', linewidth=1.5, label='Порог 0.55')
    ax_avg.set_title('Средняя за смену (все дни)')
    ax_avg.set_xlabel('Время суток (часы)')
    ax_avg.set_ylabel('Вероятность усталости')
    ax_avg.set_ylim(0, 1)
    ax_avg.set_xlim(9, 19)
    ax_avg.grid(True, linestyle='--', alpha=0.6)
    ax_avg.legend(fontsize='small')

    plt.tight_layout()
    
    
# ----------------------------------------------------------------------
# 4. График средней вероятности по часам рабочего дня
def plot_hourly_avg_probability(timestamps, y_prob):
    df = pd.DataFrame({
        'timestamp': timestamps,
        'probability': y_prob
    })
    df['hour'] = df['timestamp'].dt.hour
    hourly_avg = df.groupby('hour')['probability'].mean().reset_index()
    hourly_avg = hourly_avg[(hourly_avg['hour'] >= 9) & (hourly_avg['hour'] <= 19)]
    plt.figure(2, figsize=(10, 6))
    plt.plot(hourly_avg['hour'], hourly_avg['probability'],
             marker='o', linestyle='-', linewidth=2, markersize=6,
             label='Средняя вероятность усталости')
    plt.axhline(y=0.7, color='r', linestyle='--', label='Порог адаптации (0.7)')
    plt.xlabel('Часы рабочей смены (9:00 - 19:00)')
    plt.ylabel('Вероятность усталости')
    plt.title('Динамика средней вероятности усталости оператора в течение дня')
    plt.legend()
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.xticks(range(9, 19, 1))
    plt.ylim(0, 1)
    plt.tight_layout()

# ----------------------------------------------------------------------
# 5. График работоспособности (на основе fatigue_level)
def plot_fatigue_trend(db):
    """
    Строит 5 subplot'ов (пн–пт) с динамикой работоспособности.
    По оси X – время суток (часы + минуты/60), по Y – alertness.
    Используется скользящее среднее (окно 3) для сглаживания.
    """
    import sqlite3
    import pandas as pd
    import matplotlib.pyplot as plt

    # Загружаем данные
    conn = sqlite3.connect(db.db)
    query = """
        SELECT timestamp, fatigue_level, day_of_week
        FROM survey_response
        ORDER BY timestamp
    """
    df = pd.read_sql_query(query, conn)
    conn.close()
    if df.empty:
        print("Нет данных для графика по дням недели.")
        return

    # Подготовка данных
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df['alertness'] = (10 - df['fatigue_level']) / 9.0
    df['time_hours'] = df['timestamp'].dt.hour + df['timestamp'].dt.minute / 60.0
    # Фильтрация опросов по времени суток (оставить только с 9:00 до 19:00)
    df = df[(df['time_hours'] >= 9) & (df['time_hours'] <= 19)]
    # Названия дней (индексы: 0=пн,1=вт,2=ср,3=чт,4=пт)
    days = ['Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница']
    fig, axes = plt.subplots(2, 3, figsize=(15, 10))
    axes = axes.flatten()

    # --- 1. Строим графики для каждого рабочего дня (пн–пт) ---
    for i, day_idx in enumerate(range(5)):
        ax = axes[i]
        day_data = df[df['day_of_week'] == day_idx].copy()
        if not day_data.empty:
            day_data = day_data.sort_values('time_hours')
            # Скользящее среднее с окном 3 (центрированное)
            day_data['alertness_smooth'] = day_data['alertness'].rolling(window=3, center=True).mean()
            # Отдельные точки
            ax.plot(day_data['time_hours'], day_data['alertness'], 'o', alpha=0.4, markersize=4, label='Опросы')
            # Сглаженная линия (только не-NaN значения)
            ax.plot(day_data['time_hours'], day_data['alertness_smooth'], 'r-', linewidth=2, label='Сглаженный тренд')
            # Добавляем затенённую область обеда
            ax.axvspan(14.5, 15.0, alpha=0.2, color='orange', label='Обеденный перерыв')
            ax.axhline(y=5/9, color='orange', linestyle=':', linewidth=1.5, label='Усталость = 5')
            ax.set_title(days[i])
            ax.set_xlabel('Время суток (часы)')
            ax.set_ylabel('Работоспособность')
            ax.set_ylim(0, 1)
            ax.set_xlim(9, 19)
            ax.grid(True, linestyle='--', alpha=0.6)
            ax.legend(fontsize='small')
        else:
            ax.text(0.5, 0.5, 'Нет данных', ha='center', va='center', transform=ax.transAxes)
            ax.set_title(days[i])

    # --- 2. Шестой subplot – средняя кривая за смену по всем данным --
    ax_avg = axes[5]
    # Группируем по времени суток с шагом 0.1 часа (6 минут) и вычисляем среднюю alertness
    # Округляем time_hours до 0.1 для группировки
    df['time_bin'] = np.round(df['time_hours'] * 10) / 10.0
    avg_data = df.groupby('time_bin')['alertness'].mean().reset_index()
    avg_data = avg_data.sort_values('time_bin')
    # Сглаживание скользящим окном (окно 3, центрированное)
    avg_data['alertness_smooth'] = avg_data['alertness'].rolling(window=3, center=True).mean()
    # Строим точки и линию
    ax_avg.plot(avg_data['time_bin'], avg_data['alertness'], 'o', alpha=0.4, markersize=3, label='Средние по интервалам')
    ax_avg.plot(avg_data['time_bin'], avg_data['alertness_smooth'], 'g-', linewidth=2, label='Сглаженная средняя')
    ax_avg.axvspan(14.5, 15.0, alpha=0.2, color='orange', label='Обеденный перерыв')
    ax_avg.axhline(y=5/9, color='orange', linestyle=':', linewidth=1.5, label='Усталость = 5')
    ax_avg.set_title('Средняя за смену (все дни)')
    ax_avg.set_xlabel('Время суток (часы)')
    ax_avg.set_ylabel('Работоспособность')
    ax_avg.set_ylim(0, 1)
    ax_avg.set_xlim(9, 19)
    ax_avg.grid(True, linestyle='--', alpha=0.6)
    ax_avg.legend(fontsize='small')


    plt.tight_layout()

# ----------------------------------------------------------------------
# 6. Вспомогательная функция для границы решения (оставлена как в оригинале)
def plot_decision_regions(X, y, classifier, resolution=0.02):
    from matplotlib.colors import ListedColormap
    markers = ('s', 'x', 'o', '^', 'v')
    colors = ('red', 'blue', 'lightgreen', 'gray', 'cyan')
    cmap = ListedColormap(colors[:len(np.unique(y))])
    x1_min, x1_max = X[:, 0].min() - 1, X[:, 0].max() + 1
    x2_min, x2_max = X[:, 1].min() - 1, X[:, 1].max() + 1
    xx1, xx2 = np.meshgrid(np.arange(x1_min, x1_max, resolution),
                           np.arange(x2_min, x2_max, resolution))
    Z = classifier.predict(np.array([xx1.ravel(), xx2.ravel()]).T)
    Z = Z.reshape(xx1.shape)
    plt.contourf(xx1, xx2, Z, alpha=0.4, cmap=cmap)
    plt.xlim(xx1.min(), xx1.max())
    plt.ylim(xx2.min(), xx2.max())
    for idx, cl in enumerate(np.unique(y)):
        plt.scatter(x=X[y == cl, 0], y=X[y == cl, 1],
                    alpha=0.8, c=colors[idx], edgecolor='black',
                    marker=markers[idx], label=cl)

# ----------------------------------------------------------------------
def main():
    db = Database()
    X, y, timestamps = load_data_from_db(db, limit=1000)
    if X is None:
        print("Нет данных в БД. Сначала соберите опросы.")
        return

    model, scaler = load_model()
    X_scaled = scaler.transform(X)
    y_prob = model.predict_proba(X_scaled)[:, 1]

    # График 1: динамика вероятности по времени
    plot_prediction_over_time(db)

    # График 2: средняя вероятность по часам
    plot_hourly_avg_probability(timestamps, y_prob)

    # График 3: работоспособность (fatigue trend)
    plot_fatigue_trend(db)

    # ------------------------------------------------------------------
    # Закомментированные графики (матрица ошибок, граница решения)
    # оставлены как в исходном коде
    """
    # 4. График 2: матрица ошибок
    y_pred = model.predict(X_scaled)
    cm = confusion_matrix(y, y_pred)
    disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=['Не устал', 'Устал'])
    plt.figure(3)
    disp.plot(ax=plt.gca())
    plt.title('Матрица ошибок')

    # 5. График 3: граница решения для двух признаков (hour_sin, hours_since_start)
    X_two = X[:, [0, 5]]
    scaler_two = StandardScaler()
    X_two_scaled = scaler_two.fit_transform(X_two)
    model_two = LogisticRegression()
    model_two.fit(X_two_scaled, y)
    plt.figure(4)
    plot_decision_regions(X_two_scaled, y, model_two)
    plt.xlabel('hour_sin (масштабированный)')
    plt.ylabel('hours_since_start (масштабированный)')
    plt.title('Граница решения (hour_sin vs hours_since_start)')
    plt.legend()
    """
    plt.show()

if __name__ == "__main__":
    main()