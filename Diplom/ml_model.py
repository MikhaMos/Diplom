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
        self.confidence_threshold = 0.8 # Порог уверенности для адаптации

        if os.path.exists(model_path):
            self.load_model()
        else:
            self.initialize_model()
            # Если модель не найдена, создаем новую

    
    def initialize_model(self):
        """Инициализирует новую модель с начальными данными"""
        # Начальные фиктивные данные для инициализации
        # В реальности здесь можно добавить базовые паттерны
        initial_X = np.array([
            [8, 0], [9, 0], [10, 0],  # Утро, понедельник - не уставший
            [14, 0], [15, 0], [16, 0],  # День, понедельник
            [17, 0], [18, 0], [19, 0],  # Вечер, понедельник - уставший
            [8, 4], [9, 4], [10, 4],    # Утро, пятница
            [14, 4], [15, 4], [16, 4],  # День, пятница
        ])

        initial_y = np.array([0, 0, 0, 0, 0, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0])

        self.model = LogisticRegression()
        X_scaled = self.scaler.fit_transform(initial_X)
        self.model.fit(X_scaled, initial_y)

        self.save_model()

    def extract_features(self, timestamp: None) -> np.ndarray:
        #"""Извлекает признаки из времени"""
        if timestamp is None:
            timestamp = now()

        #Час дня (преобразуем в циклические признаки
        hour = timestamp.hour
        hour_sin = np.sin(2 * np.pi * hour / 24)
        hour_cos = np.cos(2 * np.pi * hour / 24)

        # День недели
        day_of_week = timestamp.weekday() # 0=понедельник, 6=воскресенье
        
        # Количество часов с начала рабочего дня (предполагаем 9:00 начало)
        hours_since_start = max(0, hour-9)

        # Послеобеденное время (после 13:00)
        is_afternoon = 1 if hour >= 14 else 0

        return np.array([hour_sin, hour_cos, day_of_week, hours_since_start, is_afternoon])

    def predict(self, timestamp: None) -> Tuple[bool,float]:
        """Предсказывает усталость и возвращает уверенность"""
        if self.model is None:
            return False, 0.0

        features = self.extract_features(timestamp)
        features_scaled = self.scaler.transform(features)

        probability = self.model.predict_proba(features_scaled)[0,1]
        prediction = probability > self.confidence_threshold
        return prediction, probability
    
    def train(self, X: np.ndarray, y: np.ndarray):
        """Дообучает модель на новых данных"""
        if self.model is None:
            self.initialize_model()

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
                self.confidence_threshold = data.get('threshold', 0.8)
            logger.info(f"Model loaded from {self.model_path}")
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            self.initialize_model()
