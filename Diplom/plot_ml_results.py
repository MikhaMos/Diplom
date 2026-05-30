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
"""
# 2. Загрузка данных из БД и формирование X, y, timestamps
def load_data_from_db(db, limit=10000):
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
"""
# ----------------------------------------------------------------------
# 3. График динамики вероятности по времени (хронология)
def plot_prediction_over_time(db, threshold=0.68):
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
            ax.axhline(y=0.68, color='blue', linestyle='--', linewidth=1.5, label='Порог 0.68')
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
    ax_avg.axhline(y=0.68, color='red', linestyle='--', linewidth=1.5, label='Порог 0.68')
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
    plt.axhline(y=0.68, color='r', linestyle='--', label='Порог адаптации (0.68)')
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

def plot_fatigue_concentration_decision(db):
    """
    Строит границу решения логистической регрессии,
    обученной на двух признаках: fatigue_level и concentration_level.
    """
    import sqlite3
    import numpy as np
    import matplotlib.pyplot as plt
    from sklearn.linear_model import LogisticRegression
    from sklearn.preprocessing import StandardScaler

    # Загружаем данные из БД
    conn = sqlite3.connect(db.db)
    query = """
        SELECT fatigue_level, concentration_level
        FROM survey_response
        WHERE fatigue_level IS NOT NULL AND concentration_level IS NOT NULL
    """
    data = pd.read_sql_query(query, conn)
    conn.close()
    if data.empty:
        print("Нет данных для графика усталость vs концентрация.")
        return

    # Формируем признаки X (fatigue, concentration) и целевую переменную y
    X_fc = data[['fatigue_level', 'concentration_level']].values
    # Цель: устал если fatigue >= 5 и concentration <= 4 (как в вашей модели)
    y_fc = ((data['fatigue_level'] >= 5) & (data['concentration_level'] <= 4)).astype(int)

    # Масштабируем признаки
    scaler_fc = StandardScaler()
    X_scaled_fc = scaler_fc.fit_transform(X_fc)

    # Обучаем логистическую регрессию
    model_fc = LogisticRegression(C=1)
    model_fc.fit(X_scaled_fc, y_fc)

    # Строим границу решения
    plt.figure(4,figsize=(8, 6))
    # Используем уже имеющуюся функцию plot_decision_regions
    plot_decision_regions(X_scaled_fc, y_fc, model_fc, resolution=0.05)
    plt.xlabel('Усталость (fatigue_level, масштабированная)')
    plt.ylabel('Концентрация (concentration_level, масштабированная)')
    plt.title('Граница решения: усталость vs концентрация')
    plt.legend()
    plt.tight_layout()
    plt.show()

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

# 7. Подготовка данных из БД для многоклассовой классификации
def prepare_multiclass_data(db, limit=10000):
    """
    Загружает данные из БД, формирует признаки (время + task_complexity)
    и целевые метки: 0 - не устал, 1 - устал, 2 - очень устал.
    Возвращает X, y, timestamps.
    """
    rows = db.get_training_data(limit=limit)  # (timestamp, fatigue, concentration, complexity)
    if not rows:
        return None, None, None
    predictor = FatiguePredictor()  # нужен только для extract_features
    X_list, y_list, timestamps = [], [], []
    for row in rows:
        # row: (timestamp_str, fatigue, concentration, task_complexity)
        ts_str = row[0]
        fatigue = row[1]
        concentration = row[2]
        complexity = row[3] if len(row) > 3 else 1  # по умолчанию средняя
        if complexity is None:
            complexity = 1
        dt = datetime.fromisoformat(ts_str)
        features = predictor.extract_features(dt, complexity)  # теперь с параметром сложности
        # Целевая метка (по правилам, использованным при обучении)
        if fatigue >= 7 and concentration <= 3:
            target = 2
        elif 4 <= fatigue <= 6 and 4 <= concentration <= 5:
            target = 1
        else:
            target = 0
        X_list.append(features)
        y_list.append(target)
        timestamps.append(dt)
    return np.array(X_list), np.array(y_list), timestamps

# ----------------------------------------------------------------------
# 8. Оценка многоклассовой модели: отчёт, матрица ошибок, ROC-кривые
def evaluate_multiclass_model(X, y, model=None, test_size=0.3, random_state=42):
    """
    Обучает (или использует переданную) модель на признаках X и метках y.
    Выводит classification report, строит матрицу ошибок и ROC-кривые (один против всех).
    """

    from sklearn.model_selection import train_test_split
    from sklearn.metrics import classification_report, confusion_matrix, roc_curve, auc, ConfusionMatrixDisplay
    from sklearn.preprocessing import StandardScaler
    from sklearn.linear_model import LogisticRegression

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=random_state, stratify=y
    )
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    if model is None:
        model = LogisticRegression(solver='lbfgs', max_iter=1000, C=1.0)
    model.fit(X_train_scaled, y_train)
    y_pred = model.predict(X_test_scaled)
    y_proba = model.predict_proba(X_test_scaled)

    # Отчёт
    target_names = ['Не устал (0)', 'Устал (1)', 'Очень устал (2)']
    print("\n=== CLASSIFICATION REPORT ===")
    print(classification_report(y_test, y_pred, target_names=target_names))

    # Матрица ошибок
    
    cm = confusion_matrix(y_test, y_pred)
    disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=target_names)
    disp.plot(cmap=plt.cm.Blues)
    plt.title('Confusion Matrix')
    

    # ROC-кривые (One-vs-Rest)
    plt.figure(11)
    fpr, tpr, roc_auc = {}, {}, {}
    for i in range(3):
        fpr[i], tpr[i], _ = roc_curve(y_test == i, y_proba[:, i])
        roc_auc[i] = auc(fpr[i], tpr[i])

    colors = ['blue', 'green', 'red']
    for i in range(3):
        plt.plot(fpr[i], tpr[i], color=colors[i], lw=2,
                 label=f'{target_names[i]} (AUC = {roc_auc[i]:.2f})')
    plt.plot([0, 1], [0, 1], 'k--', lw=1)
    plt.xlim([0.0, 1.0])
    plt.ylim([0.0, 1.05])
    plt.xlabel('False Positive Rate')
    plt.ylabel('True Positive Rate')
    plt.title('ROC curves (One-vs-Rest)')
    plt.legend(loc='lower right')
    plt.grid(True)
    plt.show()

    return model, scaler

# ----------------------------------------------------------------------
# 9. Динамика применения адаптации
def plot_adaptation_levels_over_time(db):
    """
    Строит 5 subplot'ов (пн–пт) с количеством, когда модель предсказала:
    - уровень 1 (только интерфейс)
    - уровень 2 (интерфейс+робот)
    По оси X – время суток (20-минутные интервалы), по Y – количество предсказаний.
    Шестой subplot – среднее количество по всем дням (или сумма – по желанию).
    """
    import sqlite3
    import pandas as pd
    import matplotlib.pyplot as plt
    import numpy as np

    conn = sqlite3.connect(db.db)
    query = """
        SELECT timestamp, prediction
        FROM ml_predictions
        ORDER BY timestamp
    """
    df = pd.read_sql_query(query, conn)
    conn.close()
    if df.empty:
        print("Нет данных в ml_predictions.")
        return

    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df['day_of_week'] = df['timestamp'].dt.weekday
    df['time_hours'] = df['timestamp'].dt.hour + df['timestamp'].dt.minute / 60.0
    df = df[(df['day_of_week'].isin([0,1,2,3,4])) & (df['time_hours'] >= 9) & (df['time_hours'] <= 19)]

    days = ['Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница']
    fig, axes = plt.subplots(2, 3, figsize=(15, 10))
    axes = axes.flatten()

    bin_width = 20 / 60.0  # 20 минут
    bins = np.arange(9, 19 + bin_width, bin_width)

    # --- 1. По дням ---
    for i, day_idx in enumerate(range(5)):
        ax = axes[i]
        day_data = df[df['day_of_week'] == day_idx].copy()
        if not day_data.empty:
            day_data['time_bin'] = pd.cut(day_data['time_hours'], bins=bins, right=False)
            # Считаем количество (а не долю) для каждого класса
            level1_counts = day_data.groupby('time_bin').apply(lambda g: (g['prediction'] == 1).sum())
            level2_counts = day_data.groupby('time_bin').apply(lambda g: (g['prediction'] == 2).sum())
            bin_centers = [(interval.left + interval.right)/2 for interval in level1_counts.index]
            ax.bar(bin_centers, level1_counts.values, width=bin_width*0.8, alpha=0.7, label='Только интерфейс (ур.1)')
            ax.bar(bin_centers, level2_counts.values, width=bin_width*0.8, alpha=0.7, bottom=level1_counts.values, label='Интерфейс+робот (ур.2)')
            ax.set_title(days[i])
            ax.set_xlabel('Время суток (часы)')
            ax.set_ylabel('Количество адаптаций')
            # Убираем лимит 0..1, теперь автоматический
            ax.set_xlim(9, 19)
            ax.grid(True, linestyle='--', alpha=0.6)
            ax.legend(fontsize='small')
        else:
            ax.text(0.5, 0.5, 'Нет данных', ha='center', va='center', transform=ax.transAxes)
            ax.set_title(days[i])
            ax.set_xlim(9, 19)

    # --- 2. Шестой subplot – среднее количество по всем дням (сумма/количество дней) ---
    ax_avg = axes[5]
    df['time_bin'] = pd.cut(df['time_hours'], bins=bins, right=False)
    # Суммируем по всем дням
    total_level1 = df.groupby('time_bin').apply(lambda g: (g['prediction'] == 1).sum())
    total_level2 = df.groupby('time_bin').apply(lambda g: (g['prediction'] == 2).sum())
    bin_centers = [(interval.left + interval.right)/2 for interval in total_level1.index]
    # Сглаживание (скользящее окно 3) для уровней
    smooth1 = total_level1.rolling(window=3, center=True).mean()
    smooth2 = total_level2.rolling(window=3, center=True).mean()
    # Рисуем stacked bar – суммарное количество по всем дням
    ax_avg.bar(bin_centers, total_level1.values, width=bin_width*0.8, alpha=0.5, label='Ур.1 (только интерфейс)')
    ax_avg.bar(bin_centers, total_level2.values, width=bin_width*0.8, alpha=0.5, bottom=total_level1.values, label='Ур.2 (интерфейс+робот)')
    ax_avg.plot(bin_centers, smooth1, 'b-', linewidth=2, label='Тренд ур.1 (сумма)')
    ax_avg.plot(bin_centers, smooth2, 'r-', linewidth=2, label='Тренд ур.2 (сумма)')
    ax_avg.set_title('Общее количество адаптаций (все дни)')
    ax_avg.set_xlabel('Время суток (часы)')
    ax_avg.set_ylabel('Суммарное количество')
    ax_avg.set_xlim(9, 19)
    ax_avg.grid(True, linestyle='--', alpha=0.6)
    ax_avg.legend(fontsize='small')

    plt.tight_layout()
    plt.show()

# ----------------------------------------------------------------------
# 12. График границы решения: время суток vs сложность задачи (по дням недели)
def plot_decision_time_complexity_contour(db, model=None, scaler=None):
    """
    Строит 2x3 subplot с контурными картами решений модели
    на плоскости "время суток (часы) - сложность задачи (0,1,2)".
    Используется уже обученная модель (10 признаков).
    """
    import pickle
    import numpy as np
    import matplotlib.pyplot as plt
    from matplotlib.colors import ListedColormap
    from datetime import datetime
    from sklearn.preprocessing import StandardScaler
    from sklearn.linear_model import LogisticRegression

    # Загружаем или обучаем модель
    if model is None or scaler is None:
        try:
            with open("fatigue_model.pkl", "rb") as f:
                data = pickle.load(f)
                model = data["model"]
                scaler = data["scaler"]
            print("Загружена модель из fatigue_model.pkl")
        except:
            print("Модель не найдена. Обучаем новую на данных БД...")
            X, y, _ = prepare_multiclass_data(db, limit=10000)
            if X is None or len(X) == 0:
                print("Нет данных для обучения.")
                return
            from sklearn.model_selection import train_test_split
            X_train, _, y_train, _ = train_test_split(X, y, test_size=0.3, random_state=42)
            scaler = StandardScaler()
            X_train_scaled = scaler.fit_transform(X_train)
            model = LogisticRegression(solver='lbfgs', max_iter=1000, C=1.0)
            model.fit(X_train_scaled, y_train)
            print("Модель обучена.")

    # Параметры сетки
    hours = np.arange(9, 19.1, 0.05)          # шаг 0.05 часа (~3 мин) для гладкости
    complexities = [0, 1, 2]                 # три уровня сложности
    days = list(range(5))
    day_names = ['Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница']
    base_dates = [datetime(2026, 3, 2 + i) for i in range(5)]  # пн..пт

    predictor = FatiguePredictor()  # только для extract_features

    # Создаём сетку для контурного графика (время, сложность)
    # Но pcolormesh требует равномерную сетку, а у нас сложность дискретна,
    # поэтому мы построим 3 горизонтальные полосы, каждая с непрерывным временем.
    # Будем использовать pcolormesh: X – часы, Y – целые значения сложности.
    # Создаём массивы для mesh: границы ячеек по времени и по сложности.
    x_edges = np.append(hours, hours[-1] + 0.05) - 0.025  # центрирование
    y_edges = np.array([-0.5, 0.5, 1.5, 2.5])             # для сложности 0,1,2

    # Массив предсказаний: (день, сложность, час) -> Z
    Z_all = np.zeros((len(days), len(complexities), len(hours)))

    for d, base in enumerate(base_dates):
        for c_idx, comp in enumerate(complexities):
            for t_idx, h in enumerate(hours):
                minute = int((h - int(h)) * 60)
                hour = int(h)
                ts = base.replace(hour=hour, minute=minute, second=0)
                feats = predictor.extract_features(ts, comp).reshape(1, -1)
                feats_scaled = scaler.transform(feats)
                pred = model.predict(feats_scaled)[0]
                Z_all[d, c_idx, t_idx] = pred

    # Цветовая карта для трёх классов
    cmap = ListedColormap(['#2ca02c', '#ff7f0e', '#d62728'])  # зелёный, оранж, красный

    fig, axes = plt.subplots(2, 3, figsize=(15, 10))
    axes = axes.flatten()

    # 5 графиков по дням
    for i, d in enumerate(days):
        ax = axes[i]
        Z_day = Z_all[d, :, :]   # форма (3, len(hours))
        # pcolormesh ожидает Z размером (len(y_edges)-1, len(x_edges)-1) = (3, len(hours))
        mesh = ax.pcolormesh(x_edges, y_edges, Z_day, cmap=cmap, shading='flat', edgecolors='black', linewidth=0.3)
        ax.set_title(day_names[d])
        ax.set_xlabel('Время суток (часы)')
        ax.set_ylabel('Сложность задачи')
        ax.set_yticks([0, 1, 2])
        ax.set_yticklabels(['Лёгкая (0)', 'Средняя (1)', 'Сложная (2)'])
        ax.set_xlim(9, 19)
        ax.set_ylim(-0.5, 2.5)
        ax.grid(True, linestyle='--', alpha=0.4)

    # 6-й график: мода по дням
    ax_mode = axes[5]
    Z_mode = np.zeros((len(complexities), len(hours)))
    for c_idx in range(len(complexities)):
        for t_idx in range(len(hours)):
            preds_over_days = Z_all[:, c_idx, t_idx].astype(int)
            # если несколько мод, берём наименьшую (или можно выбрать любую)
            counts = np.bincount(preds_over_days)
            mode_class = np.argmax(counts)
            Z_mode[c_idx, t_idx] = mode_class
    ax_mode.pcolormesh(x_edges, y_edges, Z_mode, cmap=cmap, shading='flat', edgecolors='black', linewidth=0.3)
    ax_mode.set_title('Наиболее частый класс (мода по 5 дням)')
    ax_mode.set_xlabel('Время суток (часы)')
    ax_mode.set_ylabel('Сложность задачи')
    ax_mode.set_yticks([0, 1, 2])
    ax_mode.set_yticklabels(['Лёгкая (0)', 'Средняя (1)', 'Сложная (2)'])
    ax_mode.set_xlim(9, 19)
    ax_mode.set_ylim(-0.5, 2.5)
    ax_mode.grid(True, linestyle='--', alpha=0.4)

    # Общая легенда
    from matplotlib.patches import Patch
    legend_elements = [Patch(facecolor='#2ca02c', label='Не устал (0)'),
                       Patch(facecolor='#ff7f0e', label='Устал (1)'),
                       Patch(facecolor='#d62728', label='Очень устал (2)')]
    fig.legend(handles=legend_elements, loc='lower center', ncol=3, fontsize='large')
    plt.tight_layout(rect=[0, 0.05, 1, 1])
    plt.show()

def main():
    db = Database()
    """
    X, y, timestamps = load_data_from_db(db, limit=10000)
    if X is None:
        print("Нет данных в БД. Сначала соберите опросы.")
        return
    

    model, scaler = load_model()
    X_scaled = scaler.transform(X)
    y_prob = model.predict_proba(X_scaled)[:, 1]
    """

    # График 1: динамика вероятности по времени
    #plot_prediction_over_time(db)

    # График 2: средняя вероятность по часам
    #plot_hourly_avg_probability(timestamps, y_prob)

    # График 3: работоспособность (fatigue trend)
    #plot_fatigue_trend(db)
    # График 4: динамика частоты адаптаций
    #plot_adaptation_levels_over_time(db)

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
    """
    # 5. График 3: граница решения для двух признаков (hour_sin, hours_since_start)
    #plot_fatigue_concentration_decision(db)

    
    # ---- НОВОЕ: проверка модели на исторических данных ----
    X, y, timestamps = prepare_multiclass_data(db, limit=10000)
    if X is not None:
        print(f"Загружено {len(X)} образцов. Распределение классов: {np.bincount(y)}")
        evaluate_multiclass_model(X, y)
    else:
        print("Нет данных в БД. Сначала соберите опросы или сгенерируйте данные.")

    plt.show()

if __name__ == "__main__":
    main()