import sys
import os
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout
from PySide6.QtCore import Qt
from PySide6 import QtUiTools  # Альтернатива: можно использовать loadUiType


class MyApp(QWidget):
    def __init__(self):
        super().__init__()
        
        # Загрузка UI файла
        current_dir = os.path.dirname(os.path.abspath(__file__))
        ui_file = os.path.join(current_dir, 'Gui.ui')
        main_ui_file = os.path.join(current_dir, 'Main.ui')
        
        # Способ 1: Использование QtUiTools (предпочтительный для PySide6)
        loader = QtUiTools.QUiLoader()
        self.ui = loader.load(ui_file)
        self.main_ui = loader.load(main_ui_file)
        
        # Устанавливаем загруженный виджет как центральный
        layout = QVBoxLayout()
        layout.addWidget(self.ui)
        self.setLayout(layout)
        
        # Подключаем сигналы - обратите внимание на префикс ui.
        self.ui.button.clicked.connect(self.sayhello)
    
    def sayhello(self):
        inputtext = self.ui.input.text()
        self.ui.output.setText(f"hello {inputtext}")


app = QApplication(sys.argv)
myapp = MyApp()
myapp.show()
app.exec()