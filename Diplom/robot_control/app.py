# 04_robot_controller.py
# Простой пульт управления роботом

import sys
from PyQt6.QtWidgets import (
    QApplication, QWidget, QPushButton, 
    QVBoxLayout, QLabel, QHBoxLayout,
    QGroupBox, QGridLayout
)
from PyQt6.QtCore import Qt

class RobotController(QWidget):
    def __init__(self):
        super().__init__()
        self.robot_status = "СТОП"  # текущий статус робота
        self.speed = 0               # текущая скорость
        self.direction = "●"         # направление
        self.setup_ui()
    
    def setup_ui(self):
        """Настраиваем интерфейс пульта управления"""
        self.setWindowTitle("Пульт управления роботом")
        self.resize(500, 400)
        
        # Главный вертикальный макет
        main_layout = QVBoxLayout()
        self.setLayout(main_layout)
        
        # === 1. ЗАГОЛОВОК ===
        title = QLabel(" ПУЛЬТ УПРАВЛЕНИЯ РОБОТОМ")
        title.setStyleSheet("""
            font-size: 20px; 
            font-weight: bold; 
            color: #1565C0;
            margin: 15px;
        """)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title)
        
        # === 2. ПАНЕЛЬ СТАТУСА ===
        status_group = QGroupBox("СТАТУС РОБОТА")
        status_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 14px;
                border: 2px solid #64B5F6;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
            }
        """)
        status_layout = QVBoxLayout()
        status_group.setLayout(status_layout)
        
        self.status_label = QLabel(self.robot_status)
        self.status_label.setStyleSheet("""
            font-size: 28px;
            font-weight: bold;
            color: #D32F2F;
            margin: 10px;
            padding: 10px;
            background-color: #FFEBEE;
            border-radius: 5px;
            border: 2px solid #D32F2F;
        """)
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        status_layout.addWidget(self.status_label)
        
        # Скорость
        speed_layout = QHBoxLayout()
        speed_label = QLabel("Скорость:")
        speed_label.setStyleSheet("font-size: 16px;")
        self.speed_value = QLabel(f"{self.speed}%")
        self.speed_value.setStyleSheet("""
            font-size: 24px;
            font-weight: bold;
            color: #388E3C;
        """)
        speed_layout.addWidget(speed_label)
        speed_layout.addWidget(self.speed_value)
        speed_layout.addStretch()
        status_layout.addLayout(speed_layout)
        
        main_layout.addWidget(status_group)
        
        # === 3. ПАНЕЛЬ УПРАВЛЕНИЯ ===
        control_group = QGroupBox("УПРАВЛЕНИЕ ДВИЖЕНИЕМ")
        control_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 14px;
                border: 2px solid #4CAF50;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
            }
        """)
        control_layout = QGridLayout()
        control_group.setLayout(control_layout)
        
        # Создаем кнопки управления
        buttons_data = [
            ("ВПЕРЕД", 0, 1, "#4CAF50"),
            ("ЛЕВО", 1, 0, "#FF9800"),
            ("СТОП", 1, 1, "#F44336"),
            ("ПРАВО", 1, 2, "#FF9800"),
            ("НАЗАД", 2, 1, "#2196F3"),
        ]
        
        for text, row, col, color in buttons_data:
            btn = QPushButton(text)
            btn.setStyleSheet(f"""
                QPushButton {{
                    font-size: 14px;
                    font-weight: bold;
                    padding: 15px;
                    background-color: {color};
                    color: white;
                    border-radius: 8px;
                    min-width: 80px;
                    min-height: 60px;
                }}
                QPushButton:hover {{
                    background-color: {self.darken_color(color)};
                }}
            """)
            btn.clicked.connect(lambda checked, t=text: self.handle_movement(t))
            control_layout.addWidget(btn, row, col)
        
        main_layout.addWidget(control_group)
        
        # === 4. ПАНЕЛЬ СКОРОСТИ ===
        speed_group = QGroupBox("УПРАВЛЕНИЕ СКОРОСТЬЮ")
        speed_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 14px;
                border: 2px solid #FF9800;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
            }
        """)
        speed_control_layout = QHBoxLayout()
        speed_group.setLayout(speed_control_layout)
        
        # Кнопки скорости
        for percent in [0, 25, 50, 75, 100]:
            btn = QPushButton(f"{percent}%")
            btn.setStyleSheet("""
                QPushButton {
                    font-size: 14px;
                    padding: 10px;
                    background-color: #9C27B0;
                    color: white;
                    border-radius: 5px;
                    min-width: 60px;
                }
                QPushButton:hover {
                    background-color: #7B1FA2;
                }
            """)
            btn.clicked.connect(lambda checked, p=percent: self.set_speed(p))
            speed_control_layout.addWidget(btn)
        
        main_layout.addWidget(speed_group)
        
        # === 5. ИНФОРМАЦИОННАЯ ПАНЕЛЬ ===
        info_label = QLabel("Нажми кнопки для управления движением робота")
        info_label.setStyleSheet("""
            color: #666;
            font-size: 12px;
            margin: 10px;
            padding: 10px;
            background-color: #F5F5F5;
            border-radius: 5px;
        """)
        info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(info_label)
        
        # Растяжка снизу
        main_layout.addStretch()
    
    def darken_color(self, hex_color):
        """Немного затемняем цвет для эффекта hover"""
        # Простая функция для затемнения цвета
        colors = {
            "#4CAF50": "#388E3C",  # зеленый
            "#FF9800": "#F57C00",  # оранжевый
            "#F44336": "#D32F2F",  # красный
            "#2196F3": "#1976D2",  # синий
            "#9C27B0": "#7B1FA2",  # фиолетовый
        }
        return colors.get(hex_color, hex_color)
    
    def handle_movement(self, command):
        """Обработка команд движения"""
        # Меняем статус робота
        self.robot_status = command
        self.status_label.setText(self.robot_status)
        
        # Меняем цвет статуса в зависимости от команды
        colors = {
            "ВПЕРЕД": ("#4CAF50", "#E8F5E9"),
            "НАЗАД": ("#2196F3", "#E3F2FD"),
            "ЛЕВО": ("#FF9800", "#FFF3E0"),
            "ПРАВО": ("#FF9800", "#FFF3E0"),
            "СТОП": ("#D32F2F", "#FFEBEE"),
        }
        
        color, bg_color = colors.get(command, ("#666", "#F5F5F5"))
        self.status_label.setStyleSheet(f"""
            font-size: 28px;
            font-weight: bold;
            color: {color};
            margin: 10px;
            padding: 10px;
            background-color: {bg_color};
            border-radius: 5px;
            border: 2px solid {color};
        """)
        
        print(f"Команда роботу: {command}")
    
    def set_speed(self, percent):
        """Установка скорости робота"""
        self.speed = percent
        self.speed_value.setText(f"{self.speed}%")
        print(f"Установлена скорость: {self.speed}%")

# Создаем и запускаем приложение
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = RobotController()
    window.show()
    sys.exit(app.exec())