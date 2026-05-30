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
from datetime import timedelta
import logging
import numpy as np

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from time_controller import now, time_controller

from database import Database
from client_App_pybullet import PyBulletClient
from client_App_ml import MLClient
import adaptation

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Control panel")
        self.resize(880,670)
        self.setMinimumSize(880,670)
        self.setMaximumSize(880,670)
        
        current_dir = os.path.dirname(os.path.abspath(__file__))
        ui_file=os.path.join(current_dir,'Gui.ui')

        loader = QtUiTools.QUiLoader()
        self.ui =loader.load(ui_file)
        self.setCentralWidget(self.ui)

        # инициализация компонентов
        self.robot_client = PyBulletClient()
        self.adaptation = adaptation.AdaptationManager()
        self.ml_check_interval = 5 # 5 минут
        self.ml_client = MLClient(prediction_interval=self.ml_check_interval*60)
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

        self.adaptation.apply_normal_style(self.ui, instant=True) #Стиль по умолчанию

        # Состояния
        #self.full_adaptive_mode = False
        #self.adaptive_mode = False
        self.adaptation_level = 0
        self.survey_answered = False
        self.current_fatigue_level = 0
        self.current_confidence_level = 0
        self.current_frame_pos_robot = []
        self.current_orientation_robot = []
        self.current_joint_positions = []
        self.last_positions = []

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

        # Cложность задачи
        self.current_task_complexity = 1
        self._last_task_complexity = None
        self.update_task_complexity() # установить согласно текущему часу
       

        self.log_message(f"Startup time: {now().strftime('%H:%M:%S')}")

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

        # Выводы
        self.ui.Output.document().setMaximumBlockCount(100)
        self.ui.history_answer.document().setMaximumBlockCount(100)
        self.ui.ML_prediction.document().setMaximumBlockCount(100)

        #Текста
        self.ui.StatusPanel.setText(f"Status: Инициализациия...")
        self.ui.Label_ML_status.setText(f" ML: не подключена")
        self.ui.Label_robot_status.setText(f" Robot: не подлючен")
        self.ui.Label_adaptive_mode.setText(f" Упрощенный режим: выкл")
        self.ui.label_moving.setText(f"❌")
        self.ui.label_speed.setText(f"-")
        
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
            (self.ui.XForward, '1', 1), (self.ui.XBackward, '1', -1),
            (self.ui.YForward, '2', 1), (self.ui.YBackward, '2', -1),
            (self.ui.ZForward, '3', 1), (self.ui.ZBackward, '3', -1),
            (self.ui.AForward, '4', 1), (self.ui.ABackward, '4', -1),
            (self.ui.BForward, '5', 1), (self.ui.BBackward, '5', -1),
            (self.ui.CForward, '6', 1), (self.ui.CBackward, '6', -1),
        ]

        self.joint_map = ['1', '2', '3', '4', '5', '6']

        for button, joint_name, direction in self.joint_buttons:
            # Настраиваем автоповтор для непрерывного движения при удержании
            button.setAutoRepeat(True)
            button.setAutoRepeatDelay(500)
            button.setAutoRepeatInterval(100)
            joint_index = self.joint_map.index(joint_name)
            button.clicked.connect(
                lambda checked, j=joint_index, d=direction: self.move_joint(j, d), 
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

        # Второй вопрос (radioButton 11-20)
        self.radio_button2 = [
            self.ui.radioButton_11, self.ui.radioButton_12, self.ui.radioButton_13,
            self.ui.radioButton_14, self.ui.radioButton_15, self.ui.radioButton_16,
            self.ui.radioButton_17, self.ui.radioButton_18, self.ui.radioButton_19,
            self.ui.radioButton_20
        ]
        self.survey_group2 = QButtonGroup(self)
        for i, btn in enumerate(self.radio_button2, 1):
            self.survey_group2.addButton(btn, i)

        # Кнопка отправки опроса
        self.ui.SentAnswer.clicked.connect(self.submit_survey)

    def setup_timers(self):

        """
        #Для реального времени
        # Таймеры
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_time)
        self.timer.start(100)

        # Таймеры для автоматисческого опроса(каждые 30 минут)
        self.survey_timer = QTimer()
        self.survey_timer.timeout.connect(self.show_survey_notification)
        self.survey_timer.start(1800000)  # 30 минут

        # Таймеры для проверки адаптации ML
        self.ml_check_timer = QTimer()
        self.ml_check_timer.timeout.connect(self.check_ml_adaptation)
        self.ml_check_timer.start(300000)  # Каждые 5 минут
    """

        #Для виртуального
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_time_and_check_events)
        self.timer.start(100)

        self.schedule_next_survey()
        self.schedule_next_ml_check()

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
        fatigue_level = self.survey_group.checkedId()
        concentration_level = self.survey_group2.checkedId()

        if fatigue_level == -1 or concentration_level == -1:
            QMessageBox.warning(
                self,
                "Error",
                "Please answer all questions"
            ) 
            return
        
        # Сохраняем опрос в базу данных
        self.db.save_survey(fatigue_level, concentration_level, None)

        # Сохраняем опрос в лог
        self.db.log_command(
            source='main_app',
            command='submit_survey',
            parameters=f"fatigue_level={fatigue_level}, concentration_level={concentration_level}",
            success=True
        )

        # Обновляем состояние
        self.current_fatigue_level = fatigue_level
        self.current_concentration_level = concentration_level
        self.survey_answered = True

        self.ui.history_answer.append(f"Ответы опроса в time={now().strftime('%m-%d %H:%M')}: fatigue_level={fatigue_level}, concentration_level={concentration_level}")

        # Сбрасываем выбор
        self.survey_group.setExclusive(False)
        checked_button = self.survey_group.checkedButton()
        if checked_button:
            checked_button.setChecked(False)
        self.survey_group.setExclusive(True)

        self.survey_group2.setExclusive(False)
        checked_button = self.survey_group2.checkedButton()
        if checked_button:
            checked_button.setChecked(False)
        self.survey_group2.setExclusive(True)

        # Обновляем интервал опроса
        self.get_current_survey_interval_minutes()
        # переключаемся на страницу управления
        self.ui.ControlPageButton.click()


    def schedule_next_survey(self):
        """Устанавливает следующее время опроса на основе текущего виртуального времени и интервала."""
        current = now()
        interval_minutes = self.get_current_survey_interval_minutes()
        self.next_survey_time = current + timedelta(minutes=interval_minutes)

    def get_current_survey_interval_minutes(self):
        """Обновление интервала опроса на основе количества данных"""
        count = self.db.get_survey_count()
        if count<1440:
            self.ui.interval_survey.setText(f"Интервал опроса: 30 минут")
            return 30 # 30 минут
        elif count<=2880:
            self.ui.interval_survey.setText(f"Интервал опроса: 60 минут")
            return 60 # 1 час
        else:
            self.ui.interval_survey.setText(f"Интервал опроса: 120 минут")
            return 120 # 2 часа
        
    
    def schedule_next_ml_check(self):
        """Следующая проверка адаптации через 5 виртуальных минут."""
        self.next_ml_check_time = now() + timedelta(minutes=self.ml_check_interval)
        
    def update_task_complexity(self):
        """Устанавливает сложность задачи для текущего часа (случайно)."""
        # Генерируем с теми же весами, что и в generate_data: 0.4, 0.4, 0.2
        complexity = np.random.choice([0, 1, 2], p=[0.4, 0.4, 0.2])
        self.current_task_complexity = complexity
        # Выводим в лог или интерфейс (опционально)
        complexity_name = {0: "Легкая", 1: "Средняя", 2: "Сложная"}
        self.log_message(f"Текущая сложность задачи: {complexity_name[complexity]}")

    @Slot()
    def show_survey_notification(self):
        """
        time_controller.pause()
        time_controller.configure(
                            time_controller.now(),
                            acceleration=1
                        )
        time_controller.resume()
        #Показать уведомление об опросе
        QMessageBox().information(self, "Опрос", "Пожалуйста, ответьте на опрос!")
        self.ui.SurveyPageButton.click()
        """
        self.log_message("Show survey notification")


    @Slot()
    def check_ml_adaptation(self):
        # Проверяем адаптацию ML
        current_hour = now().hour
        if not hasattr(self, '_last_complexity_hour') or current_hour != self._last_complexity_hour:
            self.update_task_complexity()
            self._last_complexity_hour = current_hour

        if hasattr(self, 'ml_client') and self.ml_client.running:
            self.ml_client.get_prediction(future_minutes=20, task_complexity=int(self.current_task_complexity))
        
        self.db.log_command(
            source='main_app',
            command='check_ml_adaptation',
            parameters=f"{now() + timedelta(minutes=20)}",
            success=True
        )
    
    @Slot(dict)
    def on_robot_positions(self,positions):
        # Обновляем позиции робота
        self.current_frame_pos_robot=positions.get('FramePositions')
        self.current_orientation_robot=positions.get('End_effector_Orientation')
        current_speed_robot=positions.get('speed_factor')
        text=""
        self.current_joint_positions=positions.get('JointPositions')
        for i, pos in enumerate(self.current_joint_positions):
            text += f"Joint {i}: {pos:.2f}\n"
        text += f"Frame Position: {["%.2f" % framepos for framepos in self.current_frame_pos_robot]}"
        self.ui.OutputPos.setPlainText(text)
        if self.last_positions and any(abs(c-l) > 0.01 for c,l in zip(self.current_joint_positions,self.last_positions)):
            self.ui.label_moving.setText(f"✅")
        else:
            self.ui.label_moving.setText(f"❌")
        self.last_positions= self.current_joint_positions
        self.ui.label_speed.setText(f" Speed:{current_speed_robot} рад/c")
        

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
        self.ui.Label_robot_status.setText(f" Robot подключен")
        self.log_message("Robot connected")

    def on_robot_disconnect(self):
        self.ui.Label_robot_status.setText(f" Robot отключен")
        self.log_message("Robot disconnected")
    
    def on_ml_prediction(self, prediction):
        new_level = prediction.get('adaptation_level', 0)
        confidencce= prediction.get('confidence', 0.0)
        timestamp = prediction.get('timestamp')
        complexity = prediction.get('complexity')
        self.ui.ML_prediction.append(f"ML prediction: timestamp={timestamp[11:16]}, level={new_level}, confidence={confidencce:.2f}, task_complexity={complexity}")
        logger.info(f"ML prediction: requires_adaptation_level={new_level}, confidence={confidencce:.2f}")

        if new_level == self.adaptation_level:
            return
        
        if new_level == 2:
            self.enable_full_adaptive_mode() # интерфейс+робот
        elif new_level == 1:
            self.enable_interface_adaptive_mode() # интерфейс
        elif new_level == 0:
            self.disable_adaptive_mode()
    
    def on_ml_error(self, error):
        self.log_message(f"ML error: {error}")
    
    def on_ml_connect(self):
        self.ui.Label_ML_status.setText(F" ML подключена")
        self.log_message("ML connected")
    
    def on_ml_disconnect(self):
        self.ui.Label_ML_status.setText(F" ML отключена")
        self.log_message("ML disconnected")

    def enable_full_adaptive_mode(self):
        if self.adaptation_level == 2:
            return
        self.adaptation_level = 2
        self.log_message("full adaptive mode enabled")
        self.ui.Label_adaptive_mode.setText(f" Адаптивный режим ВКЛ")

        self.adaptation.apply_adaptive_style(self.ui)
        #Отправляем команду адаптацию робота
        if hasattr(self, 'robot_client') and self.robot_client.running:
            self.robot_client.send_command('set_adaptive_mode',enabled=True)
    
    def enable_interface_adaptive_mode(self):
        if self.adaptation_level == 1:
            return
        self.adaptation_level = 1
        self.log_message("interface adaptive mode enabled")
        self.ui.Label_adaptive_mode.setText(f" Адаптивный режим ВКЛ")

        self.adaptation.apply_adaptive_style(self.ui)
        #Отправляем команду роботу
        if hasattr(self, 'robot_client') and self.robot_client.running:
            self.robot_client.send_command('set_adaptive_mode', enabled=False)

    def disable_adaptive_mode(self):
        if self.adaptation_level == 0:
            return
        self.adaptation_level = 0
        self.log_message("Adaptive mode disabled")
        self.ui.Label_adaptive_mode.setText(f" Адаптивный режим ВЫКЛ")
        self.adaptation.apply_normal_style(self.ui)
        #Отправляем команду на возврат к обычному режиму робота
        if hasattr(self, 'robot_client') and self.robot_client.running:
            self.robot_client.send_command('set_adaptive_mode', enabled=False)

    
    @Slot()
    def update_time_and_check_events(self):
        current_time = now().strftime( "%H:%M:%S")
        self.ui.TimeLabel.setText(f"{current_time}")
        day_names = ['Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница', 'Суббота', 'Воскресенье']
        self.ui.DayLabel.setText(f"{day_names[now().weekday()]}")
        self.ui.DateLabel.setText(f"{now().strftime('%d.%m.%Y')}")
        self.ui.last_survey.setText(f"До следующего опроса: {str(self.next_survey_time - now())[:-6]}")

        if now() >= self.next_survey_time:
            self.show_survey_notification()
            self.schedule_next_survey()

        if now() >= self.next_ml_check_time:
            self.check_ml_adaptation()
            self.schedule_next_ml_check()

    def log_message(self, message):
        #Логирование сообщений в интерфейс
        timestamp = now().strftime("%H:%M:%S")
        self.ui.Output.append(f"[{timestamp }] {message}")

    def closeEvent(self,event):
        self.log_message("Application closed")

        if hasattr(self, 'robot_client'):
            self.robot_client.stop()
        if hasattr(self, 'ml_client'):
            self.ml_client.stop()
        
        if hasattr(self, 'db'):
            self.db.close()
        QApplication.processEvents()
        event.accept()

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()