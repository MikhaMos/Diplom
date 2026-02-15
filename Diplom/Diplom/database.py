import sqlite3
from datetime import datetime, timedelta
import os
from typing import List, Optional, Dict, Any
import threading 
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Database:
    def __init__(self, db_name="adaptive_robot.db"):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        db_path = os.path.join(current_dir, db_name)
        self.db = db_path
        self.connection = sqlite3.connect(db_path, check_same_thread=False)
        self.connection.row_factory = sqlite3.Row  # возвращает словари вместо кортежей 
        self.create_tables()

        # Таймер для управления частотой опросов
        self.survey_timer = None
        self.survey_interval = 30*60
        self.survey_callback = None
        self.survey_thread = None


    def create_tables(self):
        cursor = self.connection.cursor()

        # Таблица для опросов
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS survey_response (
            id integer PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME,
            fatigue_level integer CHECK(FATIGUE_LEVEL >= 0 AND FATIGUE_LEVEL <= 10),
            hour_of_day integer,
            day_of_week integer
            )
        """)

        # Таблица для телеметрии
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS robot_telemetry(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME not null,
                positions TEXT,
                velocity REAL,
                adaptive_mode TEXT
                )
        """)

        # Таблица для логов команд
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS command_log(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME not null,
                source TEXT,
                command TEXT,
                parameters TEXT,
                success BOOLEAN
                )
        """)

        # Таблица для ML
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ml_predictions(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME not null,
                hour_of_day INTEGER,
                day_of_week INTEGER,
                features TEXT, 
                prediction boolean, 
                confidence REAL,
                threshold_used REAL, 
                adaptation_triggered boolean
                )
        """)

        # JSON с признаками
            # Предсказание (уставший/не уставший)
            # Уверенность модели (0.0-1.0)
            # Порог, который использовался
            # Была ли запущена адаптация
        self.connection.commit()

    def start_survey_scheduler(self,callback):
        """Запускает планировщик опросов в отдельном потоке"""
        self.survey_callback = callback
        def survey_worker():
            while True:
                try:
                    # Ждем интервал
                    threading.Event().wait(self.survey_interval)
                    # Вызываем callback в главном потоке
                    if self.survey_callback:
                        # Нужно будет вызвать через QTimer или QMetaObject.invokeMethod
                        # Пока просто логируем
                        
                        logger.info("Survey time! (Need to trigger in main thread)")
                        
                        # Обновляем интервал на основе количества опросов
                        self._update_survey_interval()
                
                except Exception as e:
                    logger.error(f"Error while monitoring survey: {e}")
                    raise
        
        self.survey_thread = threading.Thread(target=survey_worker, daemon=True)
        self.survey_thread.start()
        logger.info(f"Survey scheduler started with interval {self.survey_interval}s")


    def save_survey(self, fatigue_level: int):
        cursor = self.connection.cursor()

        cursor.execute("""
            INSERT INTO Survey_response (timestamp, fatigue_level, hour_of_day, day_of_week)
            values(?,?,?,?)
        """,
            (datetime.now(), fatigue_level, datetime.now().hour, datetime.now().weekday()))
        self.connection.commit()
       
        self._update_survey_interval()

        return cursor.lastrowid
    
    def _update_survey_interval(self):
        """Обновляет интервал опросов на основе количества данных"""
        cursor = self.connection.cursor()
        cursor.execute("SELECT COUNT(*) FROM survey_response")
        count = cursor.fetchone()[0]
        if count < 1440: # первый месяц
            self.survey_interval_minutes = 30 # 30 мин
        elif count <= 2880: # второй месяц
            self.survey_interval_minutes = 60 # 1 час
        else: # после второго месяца
            self.survey_interval_minutes = 120 # 2 часа


    def save_telemetry(self, positions: str, velocity:float, adaptive_mode: bool=False):
        #Сохраняет телеметрию, поддерживая максимум 50 записей
        cursor = self.connection.cursor()

        # Удаляем старые записи, если больше 50
        cursor.execute("SELECT COUNT(*) FROM robot_telemetry")
        count = cursor.fetchone()[0]
        if count > 50:
            cursor.execute("""DELETE FROM robot_telemetry 
            WHERE id IN( 
                SELECT id FROM robot_telemetry
                ORDER BY timestamp ASC
                LIMIT ?
            ) 
            """, (count - 49,))
        positions_json=json.dumps(positions)
        # Вставляем новую запись
        cursor.execute("""
            INSERT INTO robot_telemetry 
            (timestamp, positions, velocity, adaptive_mode)
            values(?,?,?,?)
        """,
            (datetime.now(), positions_json, velocity, adaptive_mode))
        self.connection.commit()
    
    def log_command(self, source: str, command: str, parameters: str, success: bool = True):
        # Логирует команды межды компонентами
        cursor = self.connection.cursor()

        cursor.execute("SELECT COUNT(*) FROM command_log")
        count_log = cursor.fetchone()[0]
        if count_log > 300:
            cursor.execute("""DELETE FROM command_log 
            WHERE id IN( 
                SELECT id FROM command_log
                ORDER BY timestamp ASC
                LIMIT ?
            ) 
            """, (count_log - 299,))

        # Если parameters - это dict, преобразуем в строку
        if isinstance(parameters, dict):
            parameters = json.dumps(parameters)
        cursor.execute("""
            INSERT INTO command_log (timestamp, source, command, parameters, success)
            values(?,?,?,?,?)
        """,
            (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), source, command, parameters, success))
        self.connection.commit()

    def get_training_data(self, limit: int= 1000):
        cursor = self.connection.cursor()
        cursor.execute("""
            SELECT hour_of_day, day_of_week, fatigue_level
            FROM Survey_response
            ORDER BY timestamp DESC
            LIMIT ?
            """, (limit,))  
        return cursor.fetchall()
    
    def log_ml_prediction(self, features:dict, prediction:bool,
                        coffidence:float, threshold_used:float,
                        adaptation_triggered:bool):
        """Логирует предсказание ML модели"""
        cursor = self.connection.cursor()
        features_json = json.dumps(features)
        cursor.execute("""
            INSERT INTO ml_predictions (timestamp, hour_of_day, day_of_week, features, prediction, confidence, threshold_used, adaptation_triggered)
            values(?,?,?,?,?,?,?,?)
        """,
            (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), datetime.now().hour, datetime.now().weekday(), features_json, prediction, coffidence, threshold_used, adaptation_triggered))
        self.connection.commit()

    def stop_survey_scheduler(self):
        """Останавливает планировщик опросов"""
        if self.survey_thread and self.survey_thread.is_alive():
            # Нет простого способа остановить, но поток daemon=True
            # сам завершится при завершении программы
            pass
    
    def close(self):
        self.stop_survey_scheduler()
        if self.connection:
            self.connection.close()