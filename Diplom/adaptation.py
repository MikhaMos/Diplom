from PySide6.QtCore import QTimer, QSize, Qt
from PySide6.QtGui import QGraphicsOpacityEffect, QColor
from PySide6.QtWidgets import QPushButton, QLabel
from time_controller import now
import logging

logger = logging.getLogger(__name__)



class AdaptationManager:
    """
    Управляет плавной анимацией интерфейса с синхронизацией по виртуальному времени.
    Длительность анимации: 20 минут виртуального времени (1200 секунд).
    Анимирует: 
      - размер кнопок (minimumSize)
      - прозрачность второстепенных элементов
      - цвет фона кнопок и панели статуса (интерполяция RGB)
    """

    ANIMATION_DURATION = 20*60 # # 20 минут в секундах виртуального времени

    #Цвета для интерполяции
    NORMAL_COLOR = QColor(44, 62, 80)   # #2c3e50
    ADAPTIVE_COLOR = QColor(243, 156, 18) # #f39c12
    NORMAL_BG_COLOR = QColor(240, 240, 240)  # фон главного окна #f0f0f0
    ADAPTIVE_BG_COLOR = QColor(38, 50, 56)   # фон #263238


    def __init__(self):
        self.styles = {
            'normal': self._get_normal_style(),
            'adaptive': self._get_adaptive_style()
        }

        # Имена второстепенных элементов, которые скрываются в адаптивном режиме
        self.non_essential_buttons = [
                'pushButton_22', 'pushButton_23', 'pushButton_24'
            ]
        
        # Основные кнопки управления движением (должны быть крупнее в адаптивном режиме)
        self.main_control_buttons = [
            'XForwardButton', 'XBackwardButton',
            'YForwardButton', 'YBackwardButton',
            'ZForwardButton', 'ZBackwardButton',
            'AForwardButton', 'ABackwardButton',
            'BForwardButton', 'BBackwardButton',
            'CForwardButton', 'CBackwardButton'
        ]

         # Важные функциональные кнопки (Home, SavePoint, ClearProgram)
        self.functional_buttons = [
            'HomeButton', 'SavePointButton', 'ClearProgramButtons'
        ]

    def _get_normal_style(self):
        """
        Нормальный режим (стандартная работа оператора).
        Цветовая гамма: нейтральные серые тона, синий акцент.
        Элементы среднего размера, хорошая читаемость, минимальная нагрузка на зрение.
        Соответствует рекомендациям по эргономике: равномерное распределение контраста,
        отсутствие резких переходов, единообразие форм.
        """
        return """
            /* ========== ГЛАВНОЕ ОКНО ========== */
            QMainWindow {
                background-color: #f0f0f0;
            }

            /* ========== КНОПКИ ========== */
            /* Базовый стиль для всех QPushButton */
            QPushButton {
                background-color: #2c3e50;
                color: white;
                border: none;
                padding: 6px 10px;
                border-radius: 0px;
                font-size: 11px;
                font-weight: normal;
            }
            QPushButton:hover {
                background-color: #34495e;
            }
            QPushButton:pressed {
                background-color: #1e2b38;
            }

            /* Кнопки управления движением (основные) */
            #XForward, #XBackward, #YForward, #YBackward,
            #ZForward, #ZBackward, #AForward, #ABackward,
            #BForward, #BBackward, #CForward, #CBackward {
                min-width: 50px;
                min-height: 30px;
            }

            /* Функциональные кнопки (Home, SavePoint, ClearProgram) */
            #HomeButton, #SavePointButton, #ClearProgramButtons {
                min-width: 70px;
                min-height: 30px;
            }

            /* Кнопки переключения страниц (верхняя панель) */
            #ControlPageButton, #SurveyPageButton,
            #pushButton_5, #pushButton_6, #pushButton_7, #pushButton_8 {
                background-color: #3f51b5;  /* выделены другим цветом */
            }
            #ControlPageButton:hover, #SurveyPageButton:hover,
            #pushButton_5:hover, #pushButton_6:hover,
            #pushButton_7:hover, #pushButton_8:hover {
                background-color: #5c6bc0;
            }

            /* ========== ЧЕКБОКС ========== */
            #AutomaticModeButton {
                color: #37474f;
                spacing: 4px;
            }
            #AutomaticModeButton::indicator {
                width: 14px;
                height: 14px;
            }

            /* ========== ГРУППЫ ========== */
            QGroupBox {
                border: 0px solid #b0bec5;
                border-radius: 4px;
                margin-top: 6px;
                font-weight: normal;
                color: #37474f;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 8px;
                padding: 0 4px;
                background-color: #f0f0f0;
            }

            /* ========== ТЕКСТОВЫЕ ПОЛЯ ========== */
            QTextEdit, QPlainTextEdit {
                background-color: white;
                border: 1px solid #b0bec5;
                border-radius: 2px;
                font-size: 11px;
            }

            /* ========== НАДПИСИ (LABEL) ========== */
            QLabel {
                color: #000000;
                font-size: 12px;
            }
            #TimeLabel, #StatusPanel,
            #Label_adaptive_mode, #Label_ML_status, #Label_robot_status {
                font-weight: bold;
            }
            #label_moving, #label_6, #label_7 {
                font-size: 12px;
            }

            /* ========== РАДИО-КНОПКИ ========== */
            QRadioButton {
                color: #000000;
                font-size: 13px;
            }
        """

    def _get_adaptive_style(self):
        """
        Адаптивный режим (для уставшего оператора).
        Повышенная контрастность, крупные элементы управления, тёплая цветовая гамма
        для поддержания внимания и снижения когнитивной нагрузки.
        Второстепенные элементы скрыты, основные кнопки увеличены.
        """
        return """
            /* ========== ГЛАВНОЕ ОКНО ========== */
            QMainWindow {
                background-color: #263238;
            }

            /* ========== КНОПКИ ========== */
            QPushButton {
                background-color: #f39c12;
                color: black;
                border: 1px solid #e67e22;
                padding: 8px 12px;
                border-radius: 4px;
                font-size: 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #e67e22;
            }
            QPushButton:pressed {
                background-color: #d35400;
            }

            /* Кнопки управления движением (чуть крупнее) */
            #XForward, #XBackward, #YForward, #YBackward,
            #ZForward, #ZBackward, #AForward, #ABackward,
            #BForward, #BBackward, #CForward, #CBackward {
                min-width: 60px;
                min-height: 36px;
            }

            /* Функциональные кнопки */
            #HomeButton, #SavePointButton, #ClearProgramButtons {
                min-width: 80px;
                min-height: 36px;
            }

            /* Кнопки переключения страниц */
            #ControlPageButton, #SurveyPageButton,
            #pushButton_5, #pushButton_6, #pushButton_7, #pushButton_8 {
                background-color: #e67e22;
                border-color: #d35400;
            }
            #ControlPageButton:hover, #SurveyPageButton:hover,
            #pushButton_5:hover, #pushButton_6:hover,
            #pushButton_7:hover, #pushButton_8:hover {
                background-color: #d35400;
            }

            /* ========== ЧЕКБОКС ========== */
            #AutomaticModeButton {
                color: #ecf0f1;
                spacing: 5px;
                font-size: 12px;
            }
            #AutomaticModeButton::indicator {
                width: 16px;
                height: 16px;
            }

            /* ========== ГРУППЫ ========== */
            QGroupBox {
                border: 0px solid #f39c12;
                border-radius: 4px;
                margin-top: 6px;
                font-weight: normal;
                color: #f39c12;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 8px;
                padding: 0 4px;
                background-color: #263238;
            }

            /* ========== ТЕКСТОВЫЕ ПОЛЯ ========== */
            QTextEdit, QPlainTextEdit {
                background-color: #2c3e50;
                color: #ecf0f1;
                border: 1px solid #f39c12;
                border-radius: 3px;
                font-size: 12px;
            }

            /* ========== НАДПИСИ ========== */
            QLabel {
                color: #ecf0f1;
                font-size: 12px;
            }
            #TimeLabel, #StatusPanel,
            #Label_adaptive_mode, #Label_ML_status, #Label_robot_status {
                font-weight: bold;
            }
            #label_moving, #label_6, #label_7 {
                font-size: 13px;
            }

            /* ========== РАДИО-КНОПКИ ========== */
            QRadioButton {
                color: #ecf0f1;
                font-size: 13px;
            }
        """

    
    def apply_normal_style(self, ui):
        """Применение обычного стиля"""
        ui.setStyleSheet(self.styles['normal'])
        self._show_all_elements(ui)
        self._set_button_size(ui, self.main_control_buttons, width=60, height=30)
        self._set_button_size(ui, self.functional_buttons, width=70, height=30)

    def apply_adaptive_style(self, ui):
        """Применение упрощенного стиля"""
        ui.setStyleSheet(self.styles['adaptive'])
        self._hide_non_essential_elements(ui)
        self._set_button_size(ui, self.main_control_buttons, width=100, height=50)
        self._set_button_size(ui, self.functional_buttons, width=80, height=36)


    def _hide_non_essential_elements(self,ui):
        """Скрытие ненужных элементов"""
        # Пример скрытия ненужных элементов
        for btn_name in self.non_essential_buttons:
            if hasattr(ui, btn_name):
                getattr(ui, btn_name).hide()
        
    def _show_all_elements(self, ui):
        """Показывает все элементы (возврат к нормальному режиму)."""
        for btn_name in self.non_essential_buttons:
            if hasattr(ui, btn_name):
                getattr(ui, btn_name).show()


    def _set_button_size(self, ui, button_names, width, height):
        """Устанавливает минимальный размер для указанных кнопок."""
        for name in button_names:
            if hasattr(ui, name):
                btn = getattr(ui, name)
                btn.setMinimumSize(width, height)
