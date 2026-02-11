
class AdaptationManager:
    def __init__(self):
        self.styles = {
            'normal': self.get_normal_style(),
            'simple': self.get_simple_style(),
            'contrast': self.get_contrast_style()
        }

    def get_normal_style(self):
        return """
            QMainWindow {
                background-color: #f0f0f0;
            }
            QPushButton {
                background-color: #0078d7;
                color: white;
                border: none;
                padding: 8px;
                border-radius: 4px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #005a9e;
            }
            QPushButton:pressed {
                background-color: #004578;
            }
            QGroupBox {
                border: 2px solid #cccccc;
                border-radius: 5px;
                margin-top: 10px;
                font-weight: bold;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
            
        """
    def get_simple_style(self):
        """Упрощенный стиль для адаптивного режима"""
        return """
            QMainWindow {
                background-color: #e6f3ff;
            }
            QPushButton {
                background-color: #28a745;
                color: white;
                border: none;
                padding: 12px;
                border-radius: 6px;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #218838;
            }
            QPushButton:pressed {
                background-color: #1e7e34;
            }
            QGroupBox {
                border: 3px solid #28a745;
                border-radius: 5px;
                margin-top: 10px;
                font-weight: bold;
                font-size: 14px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                color: #28a745;
            }
            QTextEdit {
                background-color: #ffffff;
                border: 2px solid #cccccc;
                font-size: 14px;
            }
        """
    
    def get_contrast_style(self):
        """Контрастный стиль для уставших операторов"""
        return """
            QMainWindow {
                background-color: #000000;
            }
            QPushButton {
                background-color: #ff6b6b;
                color: black;
                border: 2px solid #ff6b6b;
                padding: 10px;
                border-radius: 5px;
                font-size: 15px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #ff5252;
            }
            QGroupBox {
                border: 2px solid #ff6b6b;
                color: #ff6b6b;
                font-weight: bold;
            }
            QLabel {
                color: #ffffff;
                font-size: 14px;
            }
            QTextEdit {
                background-color: #333333;
                color: #ffffff;
                border: 1px solid #ff6b6b;
            }"""
    
    def apply_normal_style(self, ui):
        """Применение обычного стиля"""
        ui.setStyleSheet(self.styles['normal'])
        self.normalize_button_size(ui)

    def apply_simple_style(self, ui):
        """Применение упрощенного стиля"""
        ui.setStyleSheet(self.styles['simple'])
        self.hide_non_essential_elements(ui)

    def apply_contrast_style(self, ui):
        """Применение контрастного стиля"""
        ui.setStyleSheet(self.styles['contrast'])
        self.hide_non_essential_elements(ui)

    def hide_non_essential_elements(self,ui):
        """Скрытие ненужных элементов"""
        # Пример скрытия ненужных элементов
        if hasattr(ui,'pushButton_22'):
            ui.pushButton_22.hide()
        if hasattr(ui, 'pushButton_23'):
            ui.pushButton_23.hide()
        if hasattr(ui, 'pushButton_24'):
            ui.pushButton_24.hide()
        
        # Увеличиваем основные кнопки
        self.increase_button_size(ui)

    def increase_button_size(self, ui):
        """Увеличение размера основных кнопок"""
        buttons_names = ['XForwardButton','XBackwardButton', 
                         'YForwardButton', 'YBackwardButton', 
                         'ZForwardButton', 'ZBackwardButton', 
                         'AForwardButton', 'ABackwardButton', 
                         'BForwardButton', 'BBackwardButton', 
                         'CForwardButton', 'CBackwardButton']

        for name in buttons_names:
            if hasattr(ui, name):
                button = getattr(ui, name)
                button.setMinimumSize(80,40)

    def normalize_button_size(self, ui):
        """Востановление размера основных кнопок"""
        buttons_names = ['XForwardButton','XBackwardButton', 
                         'YForwardButton', 'YBackwardButton', 
                         'ZForwardButton', 'ZBackwardButton', 
                         'AForwardButton', 'ABackwardButton', 
                         'BForwardButton', 'BBackwardButton', 
                         'CForwardButton', 'CBackwardButton']

        for name in buttons_names:
            if hasattr(ui, name):
                button = getattr(ui, name)
                button.setMinimumSize(40,40)
                
    def adjust_for_fatigue_level(self, ui, fatigue_level):
        """Настройка интерфейса в зависимости от уровня усталости"""
        if fatigue_level >= 8:
            self.apply_normal_style(ui)
        elif fatigue_level >= 5:
            self.apply_simple_style(ui)
        else:
            self.apply_contrast_style(ui)