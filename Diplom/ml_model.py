import numpy as np
import pickle
import os
from typing import Tuple, Optional
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
import logging

from time_controller import now

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FatiguePredictor:
    def __init__(self, model_path: str = "fatigue_model.pkl"):
        self.model_path = model_path
        self.model: Optional[LogisticRegression] = None
        self.scaler = StandardScaler()
        self.confidence_threshold = 0.7 # Порог уверенности для адаптации

        if os.path.exists(model_path):
            self.load_model()
        else:
            self.initialize_model()
            # Если модель не найдена, создаем новую

    def _raw_features(self, hour: int, minute: int, day_of_week: int):
        #Час дня (преобразуем в циклические признаки
        hour_sin = np.sin(2 * np.pi * hour / 24)
        hour_cos = np.cos(2 * np.pi * hour / 24)
        minute_sin = np.sin(2 * np.pi * minute / 60)
        minute_cos = np.cos(2 * np.pi * minute / 60)
        # Количество часов с начала рабочего дня (предполагаем 9:00 начало)
        hours_since_start = max(0, hour-9) + minute/60
        # Послеобеденное время (после 13:00)
        is_afternoon = 1 if hour >= 14 else 0.0

        return np.array([hour_sin, hour_cos, minute_sin, minute_cos, day_of_week, hours_since_start, is_afternoon])


    def extract_features(self, timestamp: None) -> np.ndarray:
        #"""Извлекает признаки из времени"""
        if timestamp is None:
            timestamp = now()
        day_of_week = timestamp.weekday() # 0=понедельник, 6=воскресенье
        hour = timestamp.hour
        minute = timestamp.minute
        return self._raw_features(hour, minute, day_of_week)

    
    def initialize_model(self):
        """Инициализирует новую модель с начальными данными"""
        # Начальные фиктивные данные для инициализации
        X_synth, y_synth = [], []

        # Генерируем примеры для будних дней с 8 до 19
        for hour in range(8, 20):
            for day in range(5): # Пятница
                X_synth.append(self._raw_features(hour, 0, day))
                y_synth.append(1 if hour >= 17 else 0)
        X_synth = np.array(X_synth)
        y_synth = np.array(y_synth)

        # Обучаем scaler и модель
        self.scaler.fit(X_synth)
        X_scaled = self.scaler.fit_transform(X_synth)
        self.model = LogisticRegression()
        self.model.fit(X_scaled, y_synth)
        self.save_model()
        logger.info("Initial model created with synthetic data")


    def predict(self, timestamp: None) -> Tuple[bool,float]:
        """Предсказывает усталость и возвращает предсказание и уверенность"""
        if self.model is None:
            return False, 0.0
        if timestamp is None:
            timestamp = now()

        features = self.extract_features(timestamp).reshape(1,-1)
        features_scaled = self.scaler.transform(features)

        prob_class1 = self.model.predict_proba(features_scaled)[0,1]
        prob_class0 = 1 - prob_class1
        prediction =  prob_class1 > self.confidence_threshold
        # Уверенность в принятом решении
        if prediction:
            confidence = prob_class1  # уверен, что устал
        else:
            confidence = prob_class0  # уверен, что не устал
        return prediction,  confidence, prob_class1
    
    def train(self, X: np.ndarray, y: np.ndarray):
        """Дообучает модель на новых данных"""
        if self.model is None:
            self.initialize_model()
        
        self.scaler.fit(X)
        X_scaled = self.scaler.transform(X)
        self.model.fit(X_scaled, y)
        self.save_model()

        accuracy = self.model.score(X_scaled, y)
        logger.info(f"Model accuracy: {accuracy}")
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
