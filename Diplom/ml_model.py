import numpy as np
import pickle
import os
import sklearn
from typing import Tuple, Optional
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
import logging

from time_controller import now

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FatiguePredictor:
    def __init__(self, model_path: str = "fatigue_model.pkl"):
        self.model_path = model_path
        self.model: Optional[LogisticRegression] = None
        self.classes_ = [0,1,2]  # 0 - не устал, 1 - устал, 2 - очень устал
        self.scaler = StandardScaler()
        self.confidence_threshold = 0.68 # Порог уверенности для адаптации

        if os.path.exists(model_path):
            self.load_model()
        else:
            self.initialize_model()
            # Если модель не найдена, создаем новую

    def _raw_features(self, hour: int, minute: int, day_of_week: int, task_complexity: int):
        #Час дня (преобразуем в циклические признаки
        hour_sin = np.sin(2 * np.pi * hour / 24)
        hour_cos = np.cos(2 * np.pi * hour / 24)
        minute_sin = np.sin(2 * np.pi * minute / 60)
        minute_cos = np.cos(2 * np.pi * minute / 60)
        # Количество часов с начала рабочего дня (предполагаем 9:00 начало)
        hours_since_start = max(0, hour-10) + minute/60
        # Послеобеденное время (после 14:00)
        is_afternoon = 1 if hour >= 14 else 0.0
        # one-hot кодирование сложности (3 категории)
        comp_onehot = [0,0,0]
        if task_complexity is None:
            task_complexity = 1
        weights = {0: 0.8, 1: 1, 2: 2.0}
        comp_onehot[task_complexity] = weights[task_complexity]


        return np.array([hour_sin, hour_cos, minute_sin, minute_cos, day_of_week, hours_since_start, is_afternoon]+ comp_onehot)


    def extract_features(self, timestamp: None, task_complexity: int) -> np.ndarray:
        #"""Извлекает признаки из времени"""
        if timestamp is None:
            timestamp = now()
        day_of_week = timestamp.weekday() # 0=понедельник, 6=воскресенье
        hour = timestamp.hour
        minute = timestamp.minute
        return self._raw_features(hour, minute, day_of_week, task_complexity)

    
    def initialize_model(self):
        """Инициализирует новую модель с начальными данными"""
        
        # Начальные фиктивные данные для инициализации
        X_synth, y_synth = [], []
        # Генерируем примеры для будних дней с 10 до 19
        for hour in range(10, 20):
            for day in range(5): # Пятница
                for comp in [0,1,2]:
                    X_synth.append(self._raw_features(hour, 0, day, comp))
                    if hour >= 16:
                        y_synth.append(2) # очень устал
                    elif hour >= 13:
                        y_synth.append(1) # устал
                    else:
                        y_synth.append(0) # не устал
        X_synth = np.array(X_synth)
        y_synth = np.array(y_synth)
        self.scaler.fit(X_synth)
        X_synth = self.scaler.transform(X_synth)

        # Обучаем scaler и модель
        self.model = LogisticRegression(solver='lbfgs', max_iter=1000, C=1.0)
        self.model.fit(X_synth, y_synth)
        logger.info(f"Model classes: {self.model.classes_}")   # должно быть [0 1 2])    
        self.save_model()
        logger.info("Initial model created with synthetic data")


    def predict(self, timestamp: None, task_complexity: int) -> Tuple[bool,float]:
        """Предсказывает усталость и возвращает предсказание и уверенность"""
        """
        Возвращает:
          predicted_class : int (0,1,2)
          confidence       : float (вероятность предсказанного класса)
          proba            : list[float] вероятности для классов [0,1,2]
        """

        if timestamp is None:
            timestamp = now()

        features = self.extract_features(timestamp, task_complexity).reshape(1,-1)
        features_scaled = self.scaler.transform(features)

        proba = self.model.predict_proba(features_scaled)[0]
        pred_class = np.argmax(proba)
        confidence = proba[pred_class]
        
        return pred_class,  confidence, proba
    
    def get_adaptation_level(self, pred_class):
        """0 - нет адаптации, 1 - только интерфейс, 2 - интерфейс+робот"""
        if pred_class == 2:
            return 2
        elif pred_class == 1:
            return 1
        else:
            return 0
    
    def train(self, X, y):
        """Дообучает модель на новых данных"""
        """
        X: список массивов признаков (каждый получен через extract_features)
        y: список меток классов (0,1,2)
        """
        if self.model is None:
            self.initialize_model()
        X = np.array(X)
        y = np.array(y)
        self.scaler.fit(X)
        X_scaled = self.scaler.transform(X)
        self.model.fit(X_scaled, y)
        logger.info(f"Model classes: {self.model.classes_}")   # должно быть [0 1 2])    
        self.save_model()
    
        from sklearn.metrics import accuracy_score#
        y_pred = self.model.predict(X_scaled)
        accuracy = accuracy_score(y, y_pred)
        return accuracy

    
    def save_model(self):
        """Сохраняет модель и скейлер"""
        with open(self.model_path, "wb") as f:
            pickle.dump({
                "model": self.model,
                "scaler": self.scaler,
                "threshold": self.confidence_threshold
            }, f)
    

    def load_model(self):
        """Загружает модель и скейлер"""
        try:
            with open(self.model_path, "rb") as f:
                data = pickle.load(f)
                self.model = data["model"]
                self.scaler = data["scaler"]
                self.confidence_threshold = data.get('threshold', self.confidence_threshold)
            logger.info(f"Model loaded from {self.model_path}")
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            self.initialize_model()
