import sys
import os
from PySide6 import QtUiTools
from PySide6.QtWidgets import (QApplication, QCheckBox, QGroupBox, QHBoxLayout,
    QLabel, QMainWindow, QMenuBar, QPushButton,
    QRadioButton, QSizePolicy, QStackedWidget, QStatusBar,
    QTextEdit, QVBoxLayout, QWidget, QMessageBox, QButtonGroup)
from PySide6.QtCore import Qt, QTimer, Signal, QObject, Slot, QThread
import json
import asyncio
import threading
from datetime import datetime


from database import Database
from client_App_pybullet import PyBulletClient
from client_App_ml import MLClient
import adaptation

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Control panel")
        self.resize(1200,800)
        
        current_dir = os.path.dirname(os.path.abspath(__file__))
        ui_file=os.path.join(current_dir,'Gui.ui')

        loader = QtUiTools.QUiLoader()
        self.ui =loader.load(ui_file)
        self.setCentralWidget(self.ui)

        # инициализация компонентов
        self.robot_client = PyBulletClient()
        self.adaptation = adaptation.AdaptationManager()
        self.ml_client = MLClient()
        self.db = Database()

        self.robot_client.connected.connect(self.on_robot_connect)
        self.robot_client.disconnected.connect(self.on_robot_disconnect)
        self.robot_client.positions_received.connect(self.on_robot_positions)
        self.robot_client.error_occurred.connect(self.on_robot_error)
        self.robot_client.command_response.connect(self.log_message)

        self.ml_client.connected.connect(self.on_ml_connect)
        self.ml_client.disconnected.connect(self.on_ml_disconnect)
        self.ml_client.predictions_received.connect(self.on_ml_prediction)
        self.ml_client.error_occurred.connect(self.on_ml_error)

        #self.adaptation.apply_simple_style(self.ui) #Стиль по умолчанию
        # Состояния
        self.adaptive_mode = False
        self.survey_answered = False
        self.current_fatigue_level = 0
        self.current_frame_pos_robot = []
        self.current_orientation_robot = []

        # переменные для автоматики
        self.automatic_mode_active = False
        self.automatic_thread = None
        self.points_robot=[]
        self.orientation_robot=[]

        # настройка интерфейса
        self.setup_ui()

        #Подключение к серверам
        self.connect_to_servers()

        # Таймеры 
        self.setup_timers()

        # Логирование
        self.log_message("Application started")

        
    def setup_ui(self):
        """Настройка элементов интерфейса"""
        # Настройка переключения страниц
        self.ui.ControlPageButton.setCheckable(True)
        self.ui.SurveyPageButton.setCheckable(True)

        self.page_button_group = QButtonGroup(self)
        self.page_button_group.addButton(self.ui.ControlPageButton)
        self.page_button_group.addButton(self.ui.SurveyPageButton)
        self.page_button_group.setExclusive(True)
        
        # Подключаем переключение страниц
        self.ui.ControlPageButton.clicked.connect(self.show_control_page)
        self.ui.SurveyPageButton.clicked.connect(self.show_survey_page)

         # Устанавливаем начальную страницу
        self.ui.ControlPageButton.setChecked(True)
        self.ui.stackedWidget.setCurrentWidget(self.ui.ControlPage)

        # Настройка управления роботом
        self.setup_robot_controls()

        # Настройка опроса
        self.setup_survey()

        #Настройка кнопки автоматического режима (CheckBox)
        self.ui.AutomaticModeButton.stateChanged.connect(self.on_automatic_mode_toggled)

         # Настройка других кнопок (пока без функционала)
        self.ui.HomeButton.clicked.connect(self.go_home)
        self.ui.SavePointButton.clicked.connect(self.save_positions)
        self.ui.pushButton_23.clicked.connect(lambda: self.log_message("Кнопка 2 нажата"))
        self.ui.ClearProgramButtons.clicked.connect(self.clear_points)

        # Настройка вывода
        self.ui.Output.setReadOnly(True)
        self.ui.OutputPos.setReadOnly(True)

    def setup_robot_controls(self):
        # Настройка управления роботом
        # Маппинг кнопок на суставы (индекс сустава, направление)
        self.joint_buttons = [
            (self.ui.XForward, 'X', 1), (self.ui.XBackward, 'X', -1),
            (self.ui.YForward, 'Y', 1), (self.ui.YBackward, 'Y', -1),
            (self.ui.ZForward, 'Z', 1), (self.ui.ZBackward, 'Z', -1),
            (self.ui.AForward, 'A', 1), (self.ui.ABackward, 'A', -1),
            (self.ui.BForward, 'B', 1), (self.ui.BBackward, 'B', -1),
            (self.ui.CForward, 'C', 1), (self.ui.CBackward, 'C', -1),
        ]

        self.joint_map = ['Y', 'X', 'A', 'Z', 'B', 'C']

        for button, joint_name, direction in self.joint_buttons:
            # Настраиваем автоповтор для непрерывного движения при удержании
            button.setAutoRepeat(True)
            button.setAutoRepeatDelay(500)
            button.setAutoRepeatInterval(100)
            joint_index = self.joint_map.index(joint_name)
            button.clicked.connect(
                lambda checked, j=joint_index, d=direction: self.move_joint(j, d)
            )
    
    def setup_survey(self):
        # Настройка опроса
        # группа кнопок
        self.radio_button = [
            self.ui.radioButton, self.ui.radioButton_2, self.ui.radioButton_3,
            self.ui.radioButton_4, self.ui.radioButton_5, self.ui.radioButton_6,
            self.ui.radioButton_7, self.ui.radioButton_8, self.ui.radioButton_9,
            self.ui.radioButton_10
        ]

        # Создаем группу для радио-кнопок
        self.survey_group = QButtonGroup(self)
        for i, btn in enumerate(self.radio_button, 1):
            self.survey_group.addButton(btn, i)

        # Кнопка отправки опроса
        self.ui.SentAnswer.clicked.connect(self.submit_survey)

    def setup_timers(self):
        # Таймеры
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_time)
        self.timer.start(1000)

        # Таймеры для автоматисческого опроса(каждые 30 минут)
        self.survey_timer = QTimer()
        self.survey_timer.timeout.connect(self.show_survey_notification)
        self.survey_timer.start(1800000)  # 30 минут

        # Таймеры для проверки адаптации ML
        self.ml_check_timer = QTimer()
        self.ml_check_timer.timeout.connect(self.check_ml_adaptation)
        self.ml_check_timer.start(60000)  # Каждую минуту

    def connect_to_servers(self):
        # Подключаемся к серверам
        # ЗАпускаем в отдельных потоках
        self.robot_thread = self.robot_client.run_in_thread()
        self.ml_thread = self.ml_client.run_in_thread() 

        

    @Slot()
    def show_control_page(self):
        self.ui.stackedWidget.setCurrentWidget(self.ui.ControlPage)

    @Slot()
    def show_survey_page(self):
        self.ui.stackedWidget.setCurrentWidget(self.ui.SurvayPage)

    @Slot()
    def move_joint(self,joint_index, direction):
        if hasattr(self, 'robot_client') and self.robot_client.running:
            self.robot_client.send_command('move_joint', joint=joint_index, direction=direction, step=0.1)

        # Логируем действие
        self.db.log_command(
            source='main_app',
            command=f'move_joint_{joint_index}',
            parameters=f'direction={direction}',
            success=True
        )
        
    @Slot()
    def go_home(self):
        if hasattr(self, 'robot_client') and self.robot_client.running:
            self.robot_client.send_command('reset_positions')

        # Логируем действие
        self.db.log_command(
            source='main_app',
            command='reset_positions',
            parameters="",
            success=True
        )

        self.ui.Code.append(f"Reset positions")

    @Slot()
    def save_positions(self):
        if hasattr(self, 'robot_client') and self.robot_client.running:
           self.ui.Code.append(f"Save position {["%.2f" % framepos for framepos in self.current_frame_pos_robot]}")
           self.points_robot.append(self.current_frame_pos_robot)
           self.orientation_robot.append(self.current_orientation_robot)
        
        self.db.log_command(
            source='main_app',
            command='Save_positions',
            parameters=f"positions={self.current_frame_pos_robot, self.current_orientation_robot}",
            success=True
        )
    
    @Slot(int)
    def on_automatic_mode_toggled(self, state):
        if self.ui.AutomaticModeButton.isChecked():
            self.start_automatic_mode()
            self.db.log_command(
                source='main_app',
                command='start_automatic_mode',
                parameters="",
                success=True
            )
        else:
            self.stop_automatic_mode()
            self.db.log_command(
                source='main_app',
                command='stop_automatic_mode',
                parameters="",
                success=True
            )

    @Slot()
    def submit_survey(self):
        select_id = self.survey_group.checkedId()

        if select_id == -1:
            QMessageBox.warning(
                self,
                "Error",
                "Please answer all questions"
            ) 
        
        # Сохраняем опрос в базу данных
        fatigue_level = select_id 
        self.db.save_survey(fatigue_level)

        # Обновляем состояние
        self.current_fatigue_level = fatigue_level
        self.survey_answered = True

        self.log_message(f"Answered survey: {fatigue_level}")


        # Сбрасываем выбор
        self.survey_group.setExclusive(False)
        checked_button = self.survey_group.checkedButton()
        if checked_button:
            checked_button.setChecked(False)
        self.survey_group.setExclusive(True)

        # Обновляем интервал опроса
        self.update_survey_interval()

        # переключаемся на страницу управления
        self.ui.ControlPageButton.click()

    def update_survey_interval(self):
        """Обновление интервала опроса на основе количества данных"""
        training_data=self.db.get_training_data()
        count=len(training_data)

        if count<1440:
            interval= 30*60*1000 # 30 минут
        elif count<=2880:
            interval= 60*60*1000 # 1 час
        else:
            interval= 120*60*1000 # 2 часа

        self.survey_timer.setInterval(interval)
        self.log_message(f"Updated survey interval to {interval}")
    

    @Slot()
    def show_survey_notification(self):
        #Показать уведомление об опросе
        QMessageBox().information(self, "Опрос", "Пожалуйста, ответьте на опрос!")
        self.ui.SurveyPageButton.click()
        self.log_message("Show survey notification")

    @Slot()
    def check_ml_adaptation(self):
        # Проверяем адаптацию ML
        if hasattr(self, 'ml_client') and self.ml_client.running:
            self.ml_client.get_prediction()
    
    @Slot(dict)
    def on_robot_positions(self,positions):
        # Обновляем позиции робота
        self.current_frame_pos_robot=positions.get('FramePositions')
        self.current_orientation_robot=positions.get('End_effector_Orientation')
        text=""
        for i, pos in enumerate(positions.get('JointPositions')):
            text += f"Joint {i}: {pos:.2f}\n"
        text += f"Frame Position: {["%.2f" % framepos for framepos in self.current_frame_pos_robot]}"
        self.ui.OutputPos.setPlainText(text)

    @Slot()
    def start_automatic_mode(self):
        if not self.points_robot:
            QMessageBox.warning(
                self,
                "Error",
                "Please save positions first"
            )
            self.ui.AutomaticModeButton.setChecked(False)
            return

        if hasattr(self, 'robot_client') and self.robot_client.running:
            self.robot_client.send_command(
                command = 'start_automatic_mode',
                points = self.points_robot,
                orientations = self.orientation_robot,
                loop_programming = True
                )
            self.ui.Code.clear()
            for i,points in enumerate(self.points_robot): 
                self.ui.Code.append(f"Point {i}: {points}\n")
            self.automatic_mode_active = True
            self.log_message("Automatic mode started")
            self.set_manual_controls_enabled(False)
    
    @Slot()
    def stop_automatic_mode(self):
        if hasattr(self, 'robot_client') and self.robot_client.running:
            self.robot_client.send_command(command='stop_automatic_mode')
            self.automatic_mode_active = False
            self.log_message("Automatic mode stopped")
            self.set_manual_controls_enabled(True)
    
    def set_manual_controls_enabled(self, enabled):
        for buttons, _, _ in self.joint_buttons:
            buttons.setEnabled(enabled)
        self.ui.HomeButton.setEnabled(enabled)
        self.ui.SavePointButton.setEnabled(enabled)

    @Slot()
    def clear_points(self):
        self.points_robot = []
        self.db.log_command(
            source='main_app',
            command='clear_points',
            parameters="",
            success=True
        )
        self.log_message("Points cleared")
        self.ui.Code.clear()
        self.ui.Code.append("Points cleared")

    def on_robot_error(self, error):
        self.log_message(f"Robot error: {error}")

    def on_robot_connect(self):
        self.log_message("Robot connected")

    def on_robot_disconnect(self):
        self.log_message("Robot disconnected")
    
    def on_ml_prediction(self, prediction):
        requires_adaptation = prediction.get('requires_adaptation', False)
        confidencce= prediction.get('confidence', 0.0)

        self.log_message(f"ML prediction: requires_adaptation={requires_adaptation}, confidence={confidencce}")

        if requires_adaptation and not self.adaptive_mode:
            self.enable_adaptive_mode()
        elif not requires_adaptation and self.adaptive_mode:
            self.disable_adaptive_mode()
    
    def on_ml_error(self, error):
        self.log_message(f"ML error: {error}")
    
    def on_ml_connect(self):
        self.log_message("ML connected")
    
    def on_ml_disconnect(self):
        self.log_message("ML disconnected")

    def enable_adaptive_mode(self):
        self.adaptive_mode = True
        self.log_message("Adaptive mode enabled")

        self.adaptation.apply_simple_style(self.ui)

        #Отправляем команду адаптацию робота
        if hasattr(self, 'robot_client') and self.robot_client.running:
            self.robot_client.send_command('set_adaptive_mode',enabled=True)
    
    def disable_adaptive_mode(self):
        self.adaptive_mode = False
        self.log_message("Adaptive mode disabled")
        self.adaptation.apply_normal_style(self.ui)
        #Отправляем команду на возврат к обычному режиму робота
        if hasattr(self, 'robot_client') and self.robot_client.running:
            self.robot_client.send_command('set_adaptive_mode', enabled=False)

    
    @Slot()
    def update_time(self):
        current_time = datetime.now().strftime( "%H:%M:%S")
        self.ui.TimeLabel.setText(current_time)

    def log_message(self, message):
        #Логирование сообщений в интерфейс
        timestamp =datetime.now().strftime("%H:%M:%S")
        self.ui.Output.append(f"[{timestamp }] {message}")

    def closeEvent(self,event):
        self.log_message("Application closed")

        if hasattr(self, 'robot_client'):
            self.robot_client.stop()
        if hasattr(self, 'ml_client'):
            self.ml_client.stop()
        
        if hasattr(self, 'db'):
            self.db.close()

        event.accept()

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()