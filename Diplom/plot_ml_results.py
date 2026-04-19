import sqlite3
import pickle
import numpy as np
import matplotlib.pyplot as plt
from sklearn.metrics import confusion_matrix, ConfusionMatrixDisplay
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from datetime import datetime
from database import Database
from ml_model import FatiguePredictor
import pandas as pd

def load_model(model_path="fatigue_model.pkl"):
    with open(model_path, "rb") as f:
        data = pickle.load(f)
    return data['model'], data['scaler']

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

def main():
    # 1. Загрузка данных из БД
    db = Database()
    rows = db.get_training_data(limit=1000)  # если метод возвращает минуты
    if not rows:
        print("Нет данных в БД. Сначала соберите опросы.")
        return

    # Создаём временный объект для извлечения признаков
    predictor = FatiguePredictor()
    X_list = []
    y_list = []
    timestamps = []
    for row in rows:
        # предполагаем, что row содержит: (timestamp, fatigue, concentration)
        # если get_training_data не возвращает минуты, парсим timestamp
        if len(row) == 3:
            ts_str, fatigue, concentration = row
            dt = datetime.fromisoformat(ts_str)
        features = predictor.extract_features(dt)
        target = 1 if (fatigue >= 6 and concentration <= 4) else 0
        X_list.append(features)
        y_list.append(target)
        timestamps.append(dt)

    X = np.array(X_list)
    y = np.array(y_list)

    # 2. Загружаем обученную модель
    model, scaler = load_model()
    X_scaled = scaler.transform(X)
    y_pred = model.predict(X_scaled)
    y_prob = model.predict_proba(X_scaled)[:, 1]

    # 3. Группировка данных по часам и расчёт средней вероятности
    df = pd.DataFrame({
        'timestamp': timestamps,
        'probability': y_prob
    })

    # Извлекаем час из временной метки
    df['hour'] = df['timestamp'].dt.hour

    # Группируем по часу и вычисляем среднюю вероятность
    hourly_avg = df.groupby('hour')['probability'].mean().reset_index()

    # Оставляем только рабочие часы (с 9 до 18)
    hourly_avg = hourly_avg[(hourly_avg['hour'] >= 9) & (hourly_avg['hour'] <= 18)]

    
    # 4. Построение графика средней вероятности по часам
    plt.figure(1, figsize=(10, 6))
    plt.plot(hourly_avg['hour'], hourly_avg['probability'], 
            marker='o', linestyle='-', linewidth=2, markersize=6, 
            label='Средняя вероятность усталости')
    plt.axhline(y=0.7, color='r', linestyle='--', label='Порог адаптации (0.7)')
    plt.xlabel('Часы рабочей смены (9:00 - 18:00)')
    plt.ylabel('Вероятность усталости')
    plt.title('Динамика средней вероятности усталости оператора в течение дня')
    plt.legend()
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.xticks(range(9, 19, 1))
    plt.ylim(0, 1)
    plt.tight_layout()

    """
    # 4. График 2: матрица ошибок
    cm = confusion_matrix(y, y_pred)
    disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=['Не устал', 'Устал'])
    plt.figure(2)
    disp.plot(ax=plt.gca())
    plt.title('Матрица ошибок')


    # 5. График 3: граница решения для двух признаков (hour_sin, hours_since_start)
    # Извлекаем два признака: hour_sin (индекс 0) и hours_since_start (индекс 5)
    X_two = X[:, [0, 5]]
    # Обучаем простую модель на этих двух признаках для визуализации
    scaler_two = StandardScaler()
    X_two_scaled = scaler_two.fit_transform(X_two)
    model_two = LogisticRegression()
    model_two.fit(X_two_scaled, y)

    plt.figure(3)
    plot_decision_regions(X_two_scaled, y, model_two)
    plt.xlabel('hour_sin (масштабированный)')
    plt.ylabel('hours_since_start (масштабированный)')
    plt.title('Граница решения (hour_sin vs hours_since_start)')
    plt.legend()
    """
    plt.show()

if __name__ == "__main__":
    main()