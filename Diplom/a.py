# Main_App.py
import sys
import os
from datetime import datetime
from PySide6.QtCore import Qt, QTimer, Signal, QObject
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, 
    QHBoxLayout, QPushButton, QLabel, QTextEdit, 
    QGroupBox, QRadioButton, QStackedWidget, QListWidget,
    QMessageBox, QStyleFactory
)
from PySide6.QtGui import QFont, QPalette, QColor
import logging

# Импортируем наши компоненты
from database import Database
from client_App_pybullet import PyBulletClient
from client_App_ml import MLClient

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MainApp(QMainWindow):
    """Главное приложение с двумя вкладками"""
    
    def __init__(self):
        super().__init__()
        
        # Инициализация компонентов
        self.db = Database()
        self.pybullet_client = None
        self.ml_client = None
        self.pybullet_thread = None
        self.ml_thread = None
        
        # Состояние адаптации
        self.adaptive_mode = False
        self.last_fatigue_level = None
        
        # Настройка окна
        self.setWindowTitle("Адаптивная система управления коботом")
        self.setGeometry(100, 100, 900, 700)
        
        # Создаем интерфейс
        self.init_ui()
        
        # Запускаем компоненты
        self.start_components()
        
        # Таймер для обновления интерфейса
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_ui)
        self.update_timer.start(100)  # 10 Гц
        
        # Таймер для проверки адаптации
        self.adaptation_timer = QTimer()
        self.adaptation_timer.timeout.connect(self.check_adaptation)
        self.adaptation_timer.start(5000)  # Каждые 5 секунд
    
    def init_ui(self):
        """Инициализация пользовательского интерфейса"""
        # Главный виджет
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Основной layout
        main_layout = QVBoxLayout(central_widget)
        
        # Статус бар сверху
        self.status_label = QLabel("Статус: Инициализация...")
        self.status_label.setStyleSheet("font-weight: bold; padding: 5px;")
        main_layout.addWidget(self.status_label)
        
        # Виджет с вкладками (StackedWidget + ListWidget для навигации)
        content_widget = QWidget()
        content_layout = QHBoxLayout(content_widget)
        
        # Левая панель навигации
        self.nav_list = QListWidget()
        self.nav_list.setMaximumWidth(150)
        self.nav_list.addItems(["Управление роботом", "Опрос усталости"])
        self.nav_list.currentRowChanged.connect(self.change_tab)
        content_layout.addWidget(self.nav_list)
        
        # Правая панель с содержимым
        self.stacked_widget = QStackedWidget()
        content_layout.addWidget(self.stacked_widget)
        
        main_layout.addWidget(content_widget)
        
        # Создаем вкладки
        self.create_control_tab()
        self.create_survey_tab()
        
        # Статус бар снизу
        self.status_bar = self.statusBar()
        self.status_bar.showMessage("Готово")
    
    def create_control_tab(self):
        """Создает вкладку управления роботом"""
        control_widget = QWidget()
        layout = QVBoxLayout(control_widget)
        
        # Панель статуса
        status_group = QGroupBox("Статус системы")
        status_layout = QVBoxLayout()
        
        self.connection_status = QLabel("PyBullet: ❌ Не подключено | ML: ❌ Не подключено")
        self.robot_status = QLabel("Робот: Неактивен")
        self.ml_status = QLabel("ML модель: Неактивна | Усталость: ❓")
        
        status_layout.addWidget(self.connection_status)
        status_layout.addWidget(self.robot_status)
        status_layout.addWidget(self.ml_status)
        status_group.setLayout(status_layout)
        layout.addWidget(status_group)
        
        # Панель управления суставами
        control_group = QGroupBox("Управление суставами робота")
        control_layout = QVBoxLayout()
        
        # Создаем кнопки для каждого сустава
        self.joint_buttons = {}
        joints = [
            ("X (Базовый)", "X"),
            ("Y (Плечо)", "Y"), 
            ("Z (Локоть)", "Z"),
            ("A (Запястье 1)", "A"),
            ("B (Запястье 2)", "B"),
            ("C (Запястье 3)", "C")
        ]
        
        for joint_name, joint_code in joints:
            joint_widget = QWidget()
            joint_layout = QHBoxLayout(joint_widget)
            
            label = QLabel(joint_name)
            label.setMinimumWidth(100)
            
            btn_minus = QPushButton("←")
            btn_minus.setObjectName(f"btn_{joint_code}_minus")
            btn_minus.clicked.connect(lambda checked, jc=joint_code: self.move_joint(jc, -1))
            
            btn_plus = QPushButton("→")
            btn_plus.setObjectName(f"btn_{joint_code}_plus")
            btn_plus.clicked.connect(lambda checked, jc=joint_code: self.move_joint(jc, 1))
            
            joint_layout.addWidget(label)
            joint_layout.addWidget(btn_minus)
            joint_layout.addWidget(btn_plus)
            
            self.joint_buttons[joint_code] = {'minus': btn_minus, 'plus': btn_plus}
            control_layout.addWidget(joint_widget)
        
        control_group.setLayout(control_layout)
        layout.addWidget(control_group)
        
        # Панель позиций
        pos_group = QGroupBox("Текущие позиции суставов")
        pos_layout = QVBoxLayout()
        
        self.position_display = QTextEdit()
        self.position_display.setReadOnly(True)
        self.position_display.setMaximumHeight(150)
        self.position_display.setPlainText("X: 0.00°\nY: 0.00°\nZ: 0.00°\nA: 0.00°\nB: 0.00°\nC: 0.00°")
        
        pos_layout.addWidget(self.position_display)
        pos_group.setLayout(pos_layout)
        layout.addWidget(pos_group)
        
        # Кнопки управления
        button_layout = QHBoxLayout()
        
        self.reset_btn = QPushButton("Сбросить позиции")
        self.reset_btn.clicked.connect(self.reset_robot)
        
        self.adaptation_btn = QPushButton("Адаптация: Выключено")
        self.adaptation_btn.setStyleSheet("background-color: lightgray")
        self.adaptation_btn.clicked.connect(self.toggle_adaptation)
        
        button_layout.addWidget(self.reset_btn)
        button_layout.addWidget(self.adaptation_btn)
        layout.addLayout(button_layout)
        
        self.stacked_widget.addWidget(control_widget)
    
    def create_survey_tab(self):
        """Создает вкладку опроса усталости"""
        survey_widget = QWidget()
        layout = QVBoxLayout(survey_widget)
        
        # Информация о следующем опросе
        info_group = QGroupBox("Информация об опросах")
        info_layout = QVBoxLayout()
        
        self.next_survey_label = QLabel("Следующий опрос: загрузка...")
        self.survey_count_label = QLabel("Всего опросов: 0")
        self.survey_interval_label = QLabel("Интервал: 30 минут")
        
        info_layout.addWidget(self.next_survey_label)
        info_layout.addWidget(self.survey_count_label)
        info_layout.addWidget(self.survey_interval_label)
        info_group.setLayout(info_layout)
        layout.addWidget(info_group)
        
        # Текущий опрос
        survey_group = QGroupBox("Оценка усталости")
        survey_layout = QVBoxLayout()
        
        instructions = QLabel("Оцените вашу текущую усталость по шкале от 1 до 10:")
        instructions.setStyleSheet("font-weight: bold;")
        survey_layout.addWidget(instructions)
        
        # Радио-кнопки для оценки
        self.radio_buttons = []
        for i in range(1, 11):
            radio = QRadioButton(f"{i} - {'Минимальная' if i == 1 else 'Максимальная' if i == 10 else ''}")
            radio.number = i
            self.radio_buttons.append(radio)
            survey_layout.addWidget(radio)
        
        # Кнопка отправки
        self.submit_btn = QPushButton("Отправить оценку")
        self.submit_btn.clicked.connect(self.submit_survey)
        survey_layout.addWidget(self.submit_btn)
        
        survey_group.setLayout(survey_layout)
        layout.addWidget(survey_group)
        
        # История опросов
        history_group = QGroupBox("История опросов")
        history_layout = QVBoxLayout()
        
        self.history_display = QTextEdit()
        self.history_display.setReadOnly(True)
        self.history_display.setMaximumHeight(200)
        
        history_layout.addWidget(self.history_display)
        history_group.setLayout(history_layout)
        layout.addWidget(history_group)
        
        self.stacked_widget.addWidget(survey_widget)
    
    def start_components(self):
        """Запускает все компоненты системы"""
        try:
            # Запускаем PyBullet клиент
            self.pybullet_client = PyBulletClient()
            self.pybullet_client.set_callbacks(
                connected=self.on_pybullet_connected,
                disconnected=self.on_pybullet_disconnected,
                positions_received=self.on_positions_received,
                error_occurred=self.on_pybullet_error
            )
            self.pybullet_thread = self.pybullet_client.run_in_thread()
            
            # Запускаем ML клиент
            self.ml_client = MLClient(prediction_interval=60.0)  # Каждую минуту
            self.ml_client.set_callbacks(
                connected=self.on_ml_connected,
                disconnected=self.on_ml_disconnected,
                prediction_received=self.on_prediction_received,
                error_occurred=self.on_ml_error
            )
            self.ml_thread = self.ml_client.run_in_thread()
            
            # Запускаем таймер опросов
            self.db.start_survey_scheduler(self.show_survey_dialog)
            
            self.update_status("Компоненты запущены")
            
        except Exception as e:
            logger.error(f"Ошибка запуска компонентов: {e}")
            self.update_status(f"Ошибка: {str(e)}")
    
    def update_status(self, message: str):
        """Обновляет статусную строку"""
        self.status_label.setText(f"Статус: {message}")
        self.status_bar.showMessage(message)
        logger.info(message)
    
    def on_pybullet_connected(self):
        """Callback при подключении к PyBullet"""
        self.update_status("Подключено к симуляции PyBullet")
        QTimer.singleShot(0, self.update_connection_status)
    
    def on_pybullet_disconnected(self):
        """Callback при отключении от PyBullet"""
        self.update_status("Отключено от PyBullet")
        QTimer.singleShot(0, self.update_connection_status)
    
    def on_ml_connected(self):
        """Callback при подключении к ML серверу"""
        self.update_status("Подключено к ML серверу")
        QTimer.singleShot(0, self.update_connection_status)
    
    def on_ml_disconnected(self):
        """Callback при отключении от ML сервера"""
        self.update_status("Отключено от ML сервера")
        QTimer.singleShot(0, self.update_connection_status)
    
    def on_positions_received(self, positions: list):
        """Callback при получении позиций робота"""
        if len(positions) >= 6:
            self.current_positions = positions
            QTimer.singleShot(0, lambda: self.update_position_display(positions))
    
    def on_prediction_received(self, prediction: dict):
        """Callback при получении предсказания ML"""
        self.last_prediction = prediction
        QTimer.singleShot(0, self.update_ml_status)
        
        # Если требуется адаптация, включаем ее
        if prediction.get('requires_adaptation', False):
            self.enable_adaptation()
    
    def on_pybullet_error(self, error: str):
        """Callback при ошибке PyBullet"""
        self.update_status(f"Ошибка PyBullet: {error}")
    
    def on_ml_error(self, error: str):
        """Callback при ошибке ML"""
        self.update_status(f"Ошибка ML: {error}")
    
    def update_connection_status(self):
        """Обновляет статус подключений"""
        pb_status = "✅" if self.pybullet_client and self.pybullet_client.running else "❌"
        ml_status = "✅" if self.ml_client and self.ml_client.running else "❌"
        self.connection_status.setText(f"PyBullet: {pb_status} | ML: {ml_status}")
    
    def update_position_display(self, positions: list):
        """Обновляет отображение позиций"""
        if len(positions) >= 6:
            text = f"X: {positions[0]:.2f}°\n"
            text += f"Y: {positions[1]:.2f}°\n"
            text += f"Z: {positions[2]:.2f}°\n"
            text += f"A: {positions[3]:.2f}°\n"
            text += f"B: {positions[4]:.2f}°\n"
            text += f"C: {positions[5]:.2f}°"
            self.position_display.setPlainText(text)
    
    def update_ml_status(self):
        """Обновляет статус ML модели"""
        if not self.last_prediction:
            self.ml_status.setText("ML модель: Активна | Усталость: ❓")
            return
        
        prediction = self.last_prediction.get('prediction', False)
        confidence = self.last_prediction.get('confidence', 0.0) * 100
        
        status = "Уставший" if prediction else "Не уставший"
        color = "🔴" if prediction else "🟢"
        
        self.ml_status.setText(
            f"ML модель: Активна | Усталость: {color} {status} ({confidence:.1f}%)"
        )
    
    def move_joint(self, joint_code: str, direction: int):
        """Двигает указанный сустав"""
        if not self.pybullet_client or not self.pybullet_client.running:
            QMessageBox.warning(self, "Ошибка", "Не подключено к симуляции")
            return
        
        # Маппинг кодов суставов к индексам
        joint_map = {'X': 0, 'Y': 1, 'Z': 2, 'A': 3, 'B': 4, 'C': 5}
        
        if joint_code in joint_map:
            joint_index = joint_map[joint_code]
            self.pybullet_client.move_joint(joint_index, direction)
            
            # Логируем действие
            self.db.log_command(
                "main_app",
                f"move_joint_{joint_code}",
                f"direction={direction}, index={joint_index}",
                True
            )
    
    def reset_robot(self):
        """Сбрасывает робота в начальное положение"""
        if self.pybullet_client and self.pybullet_client.running:
            self.pybullet_client.send_command("reset")
            self.update_status("Робот сброшен в начальное положение")
    
    def toggle_adaptation(self):
        """Включает/выключает адаптивный режим"""
        self.adaptive_mode = not self.adaptive_mode
        
        if self.adaptive_mode:
            self.enable_adaptation()
        else:
            self.disable_adaptation()
    
    def enable_adaptation(self):
        """Включает адаптацию"""
        self.adaptive_mode = True
        self.adaptation_btn.setText("Адаптация: Включено")
        self.adaptation_btn.setStyleSheet("background-color: #add8e6")  # Синий цвет
        
        # Включаем адаптивный режим в симуляции
        if self.pybullet_client and self.pybullet_client.running:
            self.pybullet_client.set_adaptive_mode(True, 0.5)  # Замедляем в 2 раза
        
        self.update_status("Адаптивный режим включен")
    
    def disable_adaptation(self):
        """Выключает адаптацию"""
        self.adaptive_mode = False
        self.adaptation_btn.setText("Адаптация: Выключено")
        self.adaptation_btn.setStyleSheet("background-color: lightgray")
        
        # Выключаем адаптивный режим в симуляции
        if self.pybullet_client and self.pybullet_client.running:
            self.pybullet_client.set_adaptive_mode(False, 1.0)
        
        self.update_status("Адаптивный режим выключен")
    
    def check_adaptation(self):
        """Проверяет нужно ли включать адаптацию"""
        if self.ml_client and self.ml_client.should_adapt_interface():
            if not self.adaptive_mode:
                self.enable_adaptation()
    
    def show_survey_dialog(self):
        """Показывает диалог опроса"""
        # Переключаемся на вкладку опроса
        self.nav_list.setCurrentRow(1)
        
        # Показываем сообщение
        QMessageBox.information(
            self,
            "Время опроса",
            "Пожалуйста, оцените вашу текущую усталость по шкале от 1 до 10."
        )
    
    def submit_survey(self):
        """Отправляет оценку усталости"""
        # Находим выбранную радио-кнопку
        selected_value = None
        for radio in self.radio_buttons:
            if radio.isChecked():
                selected_value = radio.number
                break
        
        if not selected_value:
            QMessageBox.warning(self, "Ошибка", "Пожалуйста, выберите оценку")
            return
        
        try:
            # Сохраняем в базу
            survey_id = self.db.save_survey(selected_value, "scheduled")
            
            # Сбрасываем выбор
            for radio in self.radio_buttons:
                radio.setAutoExclusive(False)
                radio.setChecked(False)
                radio.setAutoExclusive(True)
            
            # Обновляем историю
            self.update_survey_history()
            
            # Обновляем статистику
            self.update_survey_stats()
            
            QMessageBox.information(self, "Успех", f"Оценка {selected_value} сохранена")
            
            # Логируем
            self.db.log_command("main_app", "submit_survey", f"value={selected_value}", True)
            
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось сохранить оценку: {str(e)}")
    
    def update_survey_history(self):
        """Обновляет историю опросов"""
        try:
            cursor = self.db.connection.cursor()
            cursor.execute("""
                SELECT timestamp, fatigue_level 
                FROM fatigue_survey 
                ORDER BY timestamp DESC 
                LIMIT 10
            """)
            
            history_text = "Последние 10 опросов:\n"
            for row in cursor.fetchall():
                timestamp = datetime.strptime(row['timestamp'], '%Y-%m-%d %H:%M:%S.%f')
                time_str = timestamp.strftime("%H:%M")
                history_text += f"{time_str} - Оценка: {row['fatigue_level']}/10\n"
            
            self.history_display.setPlainText(history_text)
            
        except Exception as e:
            logger.error(f"Ошибка обновления истории: {e}")
    
    def update_survey_stats(self):
        """Обновляет статистику опросов"""
        try:
            cursor = self.db.connection.cursor()
            
            # Общее количество
            cursor.execute("SELECT COUNT(*) as count FROM fatigue_survey")
            total = cursor.fetchone()['count']
            
            # Средняя оценка
            cursor.execute("SELECT AVG(fatigue_level) as avg FROM fatigue_survey")
            avg = cursor.fetchone()['avg'] or 0
            
            self.survey_count_label.setText(f"Всего опросов: {total}")
            self.next_survey_label.setText(f"Средняя оценка: {avg:.1f}/10")
            self.survey_interval_label.setText(f"Интервал: {self.db.survey_interval // 60} минут")
            
        except Exception as e:
            logger.error(f"Ошибка обновления статистики: {e}")
    
    def update_ui(self):
        """Обновляет пользовательский интерфейс"""
        self.update_connection_status()
        
        # Если есть позиции, обновляем отображение
        if hasattr(self, 'current_positions'):
            self.update_position_display(self.current_positions)
        
        # Обновляем статус ML
        self.update_ml_status()
        
        # Обновляем статус робота
        robot_status = "Активен" if self.pybullet_client and self.pybullet_client.running else "Неактивен"
        if self.adaptive_mode:
            robot_status += " (Адаптивный режим)"
        self.robot_status.setText(f"Робот: {robot_status}")
    
    def change_tab(self, index: int):
        """Переключает вкладки"""
        self.stacked_widget.setCurrentIndex(index)
        
        # Если переключились на вкладку опросов, обновляем статистику
        if index == 1:
            self.update_survey_history()
            self.update_survey_stats()
    
    def closeEvent(self, event):
        """Обработчик закрытия окна"""
        reply = QMessageBox.question(
            self, 'Подтверждение',
            'Вы уверены, что хотите выйти?',
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # Останавливаем клиенты
            if self.pybullet_client:
                self.pybullet_client.stop()
            if self.ml_client:
                self.ml_client.stop()
            
            # Закрываем базу данных
            self.db.close()
            
            event.accept()
        else:
            event.ignore()

def main():
    app = QApplication(sys.argv)
    
    # Устанавливаем стиль приложения
    app.setStyle(QStyleFactory.create("Fusion"))
    
    # Создаем и показываем главное окно
    window = MainApp()
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()