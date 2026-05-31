from ml_model import FatiguePredictor
from datetime import datetime

model = FatiguePredictor("fatigue_model.pkl")  # загружает обученную модель

# Пример: строка №22 (2026-03-02 17:00, сложность 2)
timestamp = datetime(2026, 3, 2, 13, 30, 0)
task_complexity = 0  # 0,1,2

pred_class, confidence, probs = model.predict(timestamp, task_complexity)

print(f"Предсказанный класс: {pred_class}")
print(f"Вероятности: не устал={probs[0]:.3f}, устал={probs[1]:.3f}, очень устал={probs[2]:.3f}")
print(f"Уровень адаптации: {model.get_adaptation_level(pred_class)}")