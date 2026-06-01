from PySide6.QtCore import QTimer, QSize, Qt
from PySide6.QtGui import  QColor
from PySide6.QtWidgets import QPushButton, QLabel, QGraphicsOpacityEffect, QWidget, QMainWindow
from time_controller import now, time_controller
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

    # Цвета для анимации
    NORMAL_COLOR = QColor(31, 176, 255)        # #0077B6 (синий)
    ADAPTIVE_COLOR = QColor(255, 159, 28)     # #FF9F1C (оранжевый)
    NORMAL_BG_COLOR = QColor(245, 247, 250)   # #F5F7FA (светлый фон)
    ADAPTIVE_BG_COLOR = QColor(30, 30, 47)    # #1E1E2F (тёмный фон)

    NORMAL_GROUP_BG = QColor(245, 247, 250)    #f5f7fa
    ADAPTIVE_GROUP_BG = QColor(255, 200, 148)  ##ffc894
    """
    NORMAL_TEXT_COLOR = QColor(44, 62, 80)    # #2C3E50
    ADAPTIVE_TEXT_COLOR = QColor(233, 196, 106)  # #E9C46A (или белый)
    NORMAL_BUTTON_TEXT_COLOR = QColor(255, 255, 255)  # белый
    ADAPTIVE_BUTTON_TEXT_COLOR = QColor(30, 30, 47)   # #1E1E2F
    """


    def __init__(self):
        self.animation_active = False
        self.animation_timer = None
        self.target_state = None
        self.start_time = None
        self.start_values = {}
        self.target_values = {}

        # Имена второстепенных элементов, которые скрываются в адаптивном режиме
        self.non_essential_buttons = [
                'pushButton_22', 'pushButton_23', 
                'pushButton_24', 'pushButton_5', 
                'pushButton_6', 'pushButton_7'
            ]
        
        # Основные кнопки управления движением (должны быть крупнее в адаптивном режиме)
        self.main_control_buttons = [
            'XForward', 'XBackward',
            'YForward', 'YBackward',
            'ZForward', 'ZBackward',
            'AForward', 'ABackward',
            'BForward', 'BBackward',
            'CForward', 'CBackward'
        ]

         # Важные функциональные кнопки (Home, SavePoint, ClearProgram)
        self.functional_buttons = [
            'HomeButton', 'SavePointButton', 'ClearProgramButtons', 'pushButton_23', 
        ]

        self.controlPage_buttons = [
            'ControlPageButton','SurveyPageButton' 
            ]

        self.all_animated_buttons = self.main_control_buttons + self.functional_buttons

        self.normal_sizes = {
            btn: QSize(50, 30) if btn in self.main_control_buttons else QSize(70, 30)
            for btn in self.all_animated_buttons
        }

        self.adaptive_sizes = {
            btn: QSize(100, 50) if btn in self.main_control_buttons else QSize(80, 36)
            for btn in self.all_animated_buttons
        }

        self.opacity_effects={}
        self.current_colors={}



    def _ensure_opacity_effect(self, widget):
        if widget not in self.opacity_effects:
            effect = QGraphicsOpacityEffect()
            effect.setOpacity(1.0)
            widget.setGraphicsEffect(effect)
            self.opacity_effects[widget] = effect
        return self.opacity_effects[widget]
    
    def _get_current_size(self, btn):
        return btn.minimumSize()
    
    def _get_current_opacity(self, btn):
        effect = btn.graphicsEffect()
        if isinstance(effect, QGraphicsOpacityEffect):
            return effect.opacity()
        return 1.0
    
    def _get_current_color(self, widget):
        if not isinstance(widget, QWidget):
            return self.NORMAL_COLOR
        if widget in self.current_colors:
            return self.current_colors[widget]
        # Для центрального виджета и групп возвращаем цвет фона нормального режима
        if isinstance(widget, (QMainWindow, QWidget)) and widget.objectName() in ('centralwidget', 'MainWindow'):
            return self.NORMAL_GROUP_BG
        # Для кнопок – цвет кнопок нормального режима
        if isinstance(widget, QPushButton):
            return self.NORMAL_COLOR
        # По умолчанию – цвет фона окна
        return self.NORMAL_GROUP_BG

    def _set_widget_bg_color(self, widget, color):
        if not isinstance(widget, QWidget):
            return
        self.current_colors[widget] = color
        if isinstance(widget, QPushButton):
            widget.setStyleSheet(f"background-color: rgb({color.red()}, {color.green()}, {color.blue()}); color: white;")
        else:
            widget.setStyleSheet(f"background-color: rgb({color.red()}, {color.green()}, {color.blue()});")
               

    def _stop_animation(self):
        if self.animation_timer:
            self.animation_timer.stop()
            self.animation_timer = None
        self.animation_active = False
        self.target_state = None

    def _start_animation(self, ui, target_state):
        self._stop_animation()
        self.target_state = target_state
        self.start_time = now()
        self.start_values.clear()
        self.target_values.clear()
        # 1 Размеры кнопок
        for btn_name in self.all_animated_buttons:
            btn = getattr(ui, btn_name, None)
            if btn is None: continue
            if btn and isinstance(btn, QPushButton):
                start_size  = self._get_current_size(btn)
                target_size = self.normal_sizes[btn_name] if target_state == 'normal' else self.adaptive_sizes[btn_name]
                self.start_values[(btn, 'size')] = start_size
                self.target_values[(btn, 'size')] = target_size

        # 2 Прозрачность второстепенных кнопок
        for btn_name in self.non_essential_buttons:
            btn = getattr(ui, btn_name, None)
            if btn is None: continue
            if btn:
                target_opacity = 1.0 if target_state == 'normal' else 0.0
                start_opacity = self._get_current_opacity(btn)
                self._ensure_opacity_effect(btn)
                self.start_values[(btn, 'opacity')] = start_opacity
                self.target_values[(btn, 'opacity')] = target_opacity
        
        # 3 Цвет фона кнопок
        for btn_name in self.all_animated_buttons+self.controlPage_buttons:
            btn = getattr(ui, btn_name, None)
            if btn is None: continue
            if btn:
                start_color = self._get_current_color(btn)
                target_color = self.NORMAL_COLOR if target_state == 'normal' else self.ADAPTIVE_COLOR
                self.start_values[(btn, 'bg_color')] = start_color
                self.target_values[(btn, 'bg_color')] = target_color
        """
        # 4 Цвет фона панели статуса (Если есть)
        status_panel = getattr(ui, 'PagesButton', None)
        if status_panel:
            start_color = self._get_current_color(status_panel)
            target_color = self.NORMAL_BG_COLOR if target_state == 'normal' else self.ADAPTIVE_BG_COLOR
            self.start_values[(status_panel, 'bg_color')] = start_color
            self.target_values[(status_panel, 'bg_color')] = target_color
        """
        # 5 цвет фона центрального виджета(главное окно)
        main_window = ui.window() if ui else None
        
        if main_window:
            start_color = self._get_current_color(main_window)
            target_color = self.NORMAL_GROUP_BG if target_state == 'normal' else self.ADAPTIVE_GROUP_BG
            self.start_values[(main_window, 'bg_color')] = start_color
            self.target_values[(main_window, 'bg_color')] = target_color
        """
        # 6 Цвет фона для всех QGroupBox (найти по имени или типу)
        for group_name in ['MoveBox', 'OutputCode', 'ParametrsButtons', 'StatusSurvey', 
                   'Question_1', 'HistorySurvey', 'Question_2', 'StatusPanel_2',
                   'Positions', 'OutLog', 'PagesButton', 'StatusRobot']:
            group = getattr(ui, group_name, None)
            if btn is None: continue
            if group:
                start_color = self._get_current_color(group)
                target_color = self.NORMAL_GROUP_BG if target_state == 'normal' else self.ADAPTIVE_GROUP_BG
                self.start_values[(group, 'bg_color')] = start_color
                self.target_values[(group, 'bg_color')] = target_color
        
        # 7 Цвет текста для кнопок
        for btn_name in self.all_animated_buttons:
            btn = getattr(ui, btn_name, None)
            if btn:
                start_color = btn.palette().buttonText().color()  # или хранить в current_colors
                target_color = self.NORMAL_BUTTON_TEXT_COLOR if target_state == 'normal' else self.ADAPTIVE_BUTTON_TEXT_COLOR
                self.start_values[(btn, 'text_color')] = start_color
                self.target_values[(btn, 'text_color')] = target_color
        """

        # Запускаем таймер обновления
        self.animation_timer = QTimer()
        self.animation_timer.timeout.connect(lambda:self._update_animation(ui))
        self.animation_timer.start(50)
        self.animation_active = True
        logger.info(f"Animation started to {target_state}")

    def _update_animation(self, ui):
        if not self.animation_active:
            return
        
        if not time_controller.is_running:
            return
        current_virtual = now()
        elapsed = (current_virtual - self.start_time).total_seconds()
        progress = min(1, elapsed / self.ANIMATION_DURATION)

        for (widget, prop), start_val in self.start_values.items():
            target_val = self.target_values[(widget, prop)]
            if prop == 'size':
                w = start_val.width() + (target_val.width() - start_val.width()) * progress
                h = start_val.height() + (target_val.height() - start_val.height()) * progress
                widget.setMinimumSize(int(w), int(h))
            elif prop == 'opacity':
                opacity = (start_val + (target_val - start_val) * progress)
                effect = widget.graphicsEffect()
                if isinstance(effect, QGraphicsOpacityEffect):
                    effect.setOpacity(opacity)
                if progress >= 0.6 and target_val == 0.0:
                    widget.setVisible(False)
                elif progress >= 0.6 and target_val == 1.0:
                    widget.setVisible(True)
            elif prop == 'bg_color':
                r = int(start_val.red() + (target_val.red() - start_val.red()) * progress)
                g = int(start_val.green() + (target_val.green() - start_val.green()) * progress)
                b = int(start_val.blue() + (target_val.blue() - start_val.blue()) * progress)
                interp_color = QColor(int(r), int(g), int(b))
                self._set_widget_bg_color(widget, interp_color)
            """
            elif prop == 'text_color':
                r = int(start_val.red() + (target_val.red() - start_val.red()) * progress)
                g = int(start_val.green() + (target_val.green() - start_val.green()) * progress)
                b = int(start_val.blue() + (target_val.blue() - start_val.blue()) * progress)
                interp_color = QColor(r, g, b)
                widget.setStyleSheet(f"color: rgb({r}, {g}, {b});")
            """
        if progress >= 0.8:
            target_state = self.target_state
            self._stop_animation()
            self._apply_final_style(ui, target_state)
            logger.info(f"Animation finished to {target_state}")

    def _apply_final_style(self, ui, target_state):
        main_window = ui.window() if ui else None
        if main_window:
            if target_state == 'normal':
                main_window.setStyleSheet(self._get_normal_style())
            else:
                main_window.setStyleSheet(self._get_adaptive_style())

    def apply_normal_style(self,ui, instant=False):
        if instant:
            self._apply_instant_normal(ui)
        else:
            self._start_animation(ui, 'normal')

    def apply_adaptive_style(self,ui, instant=False):
        if instant:
            self._apply_instant_adaptive(ui)
        else:
            self._start_animation(ui, 'adaptive')

    def _apply_instant_normal(self, ui):
        """Мгновенно применить нормальный стиль (без анимации)."""
        self._stop_animation()
        main_window = ui.window() if ui else None
        if main_window:
            main_window.setStyleSheet(self._get_normal_style())
        for btn_name in self.all_animated_buttons:
            btn = getattr(ui, btn_name, None)
            if btn and isinstance(btn, QPushButton):
                btn.setMinimumSize(self.normal_sizes[btn_name])
        for btn_name in self.non_essential_buttons:
            btn = getattr(ui, btn_name, None)
            if btn:
                btn.setVisible(True)
                effect = btn.graphicsEffect()
                if isinstance(effect, QGraphicsOpacityEffect):
                    effect.setOpacity(1.0)
        self.target_state = 'normal'

    def _apply_instant_adaptive(self, ui):
        """Мгновенно применить адаптивный стиль (без анимации)."""
        self._stop_animation()
        self._stop_animation()
        main_window = ui.window() if ui else None
        if main_window:
            main_window.setStyleSheet(self._get_adaptive_style())
        for btn_name in self.all_animated_buttons:
            btn = getattr(ui, btn_name, None)
            if btn and isinstance(btn, QPushButton):
                btn.setMinimumSize(self.adaptive_sizes[btn_name])
        for btn_name in self.non_essential_buttons:
            btn = getattr(ui, btn_name, None)
            if btn:
                btn.setVisible(False)
                effect = btn.graphicsEffect()
                if isinstance(effect, QGraphicsOpacityEffect):
                    effect.setOpacity(0.0)
        self.target_state = 'adaptive'

    def _get_normal_style(self):
        return """
            /* ГЛАВНОЕ ОКНО */
            QMainWindow {
                background-color: #F5F7FA;
            }

            /* БАЗОВЫЕ КНОПКИ */
             QPushButton {
                background-color: #0077B6;
                color: white !important;
                border: none;
                border-radius: 4px;
                font-size: 12px;
                font-weight: 500;
                padding: 6px 12px;
            }
            /* ВТОРОСТЕПЕННЫЕ КНОПКИ */
            #HomeButton, #SavePointButton, #ClearProgramButtons {
                background-color: #0077B6;
                color: white !important;
                border-radius: 4px;
            }
            /* ПАНЕЛЬ УПРАВЛЕНИЯ ДВИЖЕНИЕМ */
            #XForward, #XBackward, #YForward, #YBackward,
            #ZForward, #ZBackward, #AForward, #ABackward,
            #BForward, #BBackward, #CForward, #CBackward {
                background-color: #0077B6;
                color: white !important;
                border-radius: 4px;

            }
            /* КНОПКИ ПЕРЕКЛЮЧЕНИЯ СТРАНИЦ */
            #ControlPageButton, #SurveyPageButton,
            #pushButton_5, #pushButton_6, #pushButton_7, #pushButton_8 {
                background-color: #d1d4d7;
                color: #2C3E50;
                border-radius: 4px;
            }
            #ControlPageButton:checked, #SurveyPageButton:checked {
                background-color: #0077B6;
                color: white !important;
            }

            QPushButton:pressed {
                background-color: #023E8A;
                border: 2px solid white;
            }

            /* ЧЕКБОКСЫ И РАДИО-КНОПКИ */
            #AutomaticModeButton, QRadioButton {
                color: #2C3E50;
                spacing: 6px;
                font-size: 12px;
            }
            #AutomaticModeButton::indicator, QRadioButton::indicator {
                width: 15px;
                height: 15px;
                border-radius: 4px;
                background-color: #F5F7FA;
                border: 1px solid #ADB5BD;
            }
            
            #AutomaticModeButton::indicator:checked {
                background-color: #0077B6;
                border: 1px solid #0077B6;
            }

            /* Стиль индикатора в ВЫБРАННОМ состоянии */
            QRadioButton::indicator:checked {
                background-color: #0077B6;
                border: 1px solid #0077B6;
            }

            /* Стиль индикатора при НАВЕДЕНИИ МЫШИ */
            QRadioButton::indicator:hover {
                border: 1px solid #5DADE2;
            }

            QRadioButton::indicator {
                border-radius: 8px;
            }

            /* ГРУППЫ И НАДПИСИ */
            QGroupBox {
                background-color: #F5F7FA;
                border: 0px solid #DEE2E6;
                border-radius: 8px;
                margin-top: 12px;
                color: #2C3E50;
            }
            QLabel {
                color: #2C3E50;
                font-size: 12px;
                background-color: #F5F7FA;
            }
            #TimeLabel, #StatusPanel,
            #Label_adaptive_mode, #Label_ML_status, #Label_robot_status {
                font-weight: bold;
                color: #0077B6;
                background-color: #F5F7FA;
            }

            /* ТЕКСТОВЫЕ ПОЛЯ */
            QTextEdit, QPlainTextEdit {
                background-color: #F5F7FA;
                border: 1px solid #CED4DA;
                border-radius: 6px;
                font-size: 12px;
            }
        """

    def _get_adaptive_style(self):
        return """
            /* ГЛАВНОЕ ОКНО */
            QMainWindow {
                background-color: #1E1E2F;
            }

            /* БАЗОВЫЕ КНОПКИ */
            QPushButton {
                background-color: #FF9F1C;
                color: #1E1E2F;
                border: none;
                border-radius: 20px;
                font-size: 14px;
                font-weight: bold;
                padding: 10px 16px;
            }
            QPushButton:hover {
                background-color: #FFBF69;
            }
            QPushButton:pressed {
                background-color: #023E8A;
                border: 2px solid white;
            }

            /* ВТОРОСТЕПЕННЫЕ КНОПКИ (будут скрыты анимацией) */
            #HomeButton, #SavePointButton, #ClearProgramButtons {
                background-color: #E76F51;
                color: white;
                border-radius: 20px;
            }

            /* ПАНЕЛЬ УПРАВЛЕНИЯ ДВИЖЕНИЕМ (увеличенные кнопки) */
            #XForward, #XBackward, #YForward, #YBackward,
            #ZForward, #ZBackward, #AForward, #ABackward,
            #BForward, #BBackward, #CForward, #CBackward {
                background-color: #FF9F1C;
                color: white;
                font-size: 14px;
                border-radius: 20px;
            }

            /* КНОПКИ ПЕРЕКЛЮЧЕНИЯ СТРАНИЦ */
            #ControlPageButton, #SurveyPageButton,
            #pushButton_5, #pushButton_6, #pushButton_7, #pushButton_8 {
                background-color: #2A9D8F;
                color: white;
                border-radius: 20px;
            }
            #ControlPageButton:checked, #SurveyPageButton:checked {
                background-color: #E9C46A;
                color: #1E1E2F;
            }

            /* ЧЕКБОКСЫ И РАДИО-КНОПКИ */
            #AutomaticModeButton, QRadioButton {
                color: #E9C46A;
                spacing: 2px;
                font-size: 12px;
            }
            #AutomaticModeButton::indicator, QRadioButton::indicator {
                width: 18px;
                height: 18px;
                border-radius: 4px;
                background-color: #2A9D8F;
                border: 1px solid #E9C46A;
            }

            /* Стиль индикатора в ВЫБРАННОМ состоянии */
            QRadioButton::indicator:checked {
                background-color: #FF9F1C;
                border: 1px solid #FF9F1C;
            }

            /* Стиль индикатора при НАВЕДЕНИИ МЫШИ */
            QRadioButton::indicator:hover {
                border: 3px solid #FF9F1C;
            }
            QPushButton:pressed {
                background-color: #E85D04;
                border: 5px solid #FFFFFF;
            }



            /* ГРУППЫ И НАДПИСИ */
            QGroupBox {
                background-color: #1E1E2F;
                border: 0px solid #E9C46A;
                border-radius: 12px;
                margin-top: 12px;
                color: #FFFFFF;
            }
            QLabel {
                color: #E9C46A;
                font-size: 13px;
            }
            #TimeLabel, #StatusPanel,
            #Label_adaptive_mode, #Label_ML_status, #Label_robot_status {
                font-weight: bold;
                color: #FF9F1C;
                background-color: #1E1E2F
            }

            /* ТЕКСТОВЫЕ ПОЛЯ */
            QTextEdit, QPlainTextEdit {
            
                background-color: #1E1E2F;
                color: #E9C46A;
                border: 1px solid #E9C46A;
                border-radius: 8px;
                font-size: 13px;
            }
        """
    
