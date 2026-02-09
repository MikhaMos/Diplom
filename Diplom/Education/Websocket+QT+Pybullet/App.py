import sys
import os
from PySide6 import QtUiTools
from PySide6.QtWidgets import QApplication, QMainWindow
from PySide6.QtCore import Qt, Slot
import json
import io
from WebsocketClientApp import WebsocketClientApp
from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QFrame, QHBoxLayout, QLabel,
    QLayout, QLineEdit, QMainWindow, QMenuBar,
    QPushButton, QSizePolicy, QStatusBar, QTextEdit,
    QVBoxLayout, QWidget)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Control panel")
        self.resize(800,600)

        current_dir = os.path.dirname(os.path.abspath(__file__))
        ui_file=os.path.join(current_dir,'Gui.ui')

        loader = QtUiTools.QUiLoader()
        self.ui =loader.load(ui_file)
        self.setCentralWidget(self.ui)
        self.client = WebsocketClientApp()

        self.connect_to_server()

        self.joint_buttons = {
            'X':{'plus': self.ui.XForwardButton, 'minus': self.ui.XBackwardButton},
            'Y':{'plus': self.ui.YForwardButton, 'minus': self.ui.YBackwardButton},
            'Z':{'plus': self.ui.ZForwardButton, 'minus': self.ui.ZBackwardButton},
            'A':{'plus': self.ui.AForwardButton, 'minus': self.ui.ABackwardButton},
            'B':{'plus': self.ui.BForwardButton, 'minus': self.ui.BBackwardButton},
            'C':{'plus': self.ui.CForwardButton, 'minus': self.ui.CBackwardButton},
        }
        self.joint_map=['Y', 'X', 'A', 'Z', 'B', 'C']

        self.setup_connections()

    def setup_connections(self):
        for i, joint in enumerate(self.joint_map):

            self.joint_buttons[joint]['plus'].setAutoRepeat(True)
            self.joint_buttons[joint]['minus'].setAutoRepeat(True)
            self.joint_buttons[joint]['minus'].setAutoRepeatDelay(500)
            self.joint_buttons[joint]['plus'].setAutoRepeatDelay(500)
            self.joint_buttons[joint]['plus'].setAutoRepeatInterval(100)
            self.joint_buttons[joint]['minus'].setAutoRepeatInterval(100)

            self.joint_buttons[joint]['plus'].clicked.connect(
                lambda checked, idx = i, dir=1: self.move_joint(idx,dir)
                )
            self.joint_buttons[joint]['minus'].clicked.connect(
                lambda checked, idx = i, dir=-1: self.move_joint(idx,dir)
                )
        self.ui.lnput.returnPressed.connect(self.send_custom_command)

        self.client.connected.connect(self.on_connected)
        self.client.disconnected.connect(self.on_disconnected)
        self.client.message_received.connect(self.on_message_received)
        self.client.error_occurred.connect(self.on_error_occurred)
    
    def move_joint(self, joint_index, direction):
        if hasattr(self, 'client'):
            self.client.send_command('move_joint', joint_index, direction)
    
    def connect_to_server(self):
        self.client.run_in_thread()

    def send_custom_command(self):
        if hasattr(self, 'client'):
            command=self.ui.lnput.text()
            if command:
                self.log_message(command)
                self.client.send_command(command)
                self.ui.lnput.clear()
    @Slot()
    def on_connected(self):
        self.log_message("Connected to server")
    
    @Slot()
    def on_disconnected(self):
        self.log_message("Disconnected from server")
    
    @Slot(dict)
    def on_message_received(self, data):
        msg_type=data.get('type')

        if msg_type=='log':
            self.log_message(data.get('data', ''))

        elif msg_type=='positions':
            positions=data.get('positions', [])
            self.update_positions_display(positions)

        elif msg_type=='error':
            error_msg=data.get('data', 'Unknown error')
            self.log_message(f"Error: {error_msg}")

    @Slot(str)
    def on_error_occurred(self,error_message):
        self.log_message(f"Error: {error_message}")

    def update_positions_display(self, positions):
        if positions:
            text=""
            for i,pos in enumerate(positions):
                joint_name= self.joint_map[i] if i <len(self.joint_map) else f"Joint {i}"
                text +=f"{joint_name}: {pos:.2f}\n"
            self.ui.positions.setPlainText(text)
    
    def log_message(self, message):
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.ui.Output.append(f"[{timestamp}] {message}")
        
    
    def closeEvent(self,event):
        if hasattr(self, 'client'):
            self.client.stop()
        event.accept()


def main():
    app=QApplication(sys.argv)
    window=MainWindow()
    window.show()
    app.exec()


if __name__ == "__main__":
    main()