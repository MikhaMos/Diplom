import os 
import sys
import PySide6
from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt, Signal, QTimer)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QMainWindow, QMenuBar, QPushButton,
    QSizePolicy, QStatusBar, QTextEdit, QWidget)
from PySide6 import QtUiTools
import json
from websocket_client import WebsocketClient


class App(QMainWindow):
    def __init__(self):
        super().__init__()
        self.resize(600,300)
        
        current_dir = os.path.dirname(os.path.abspath(__file__))
        ui_file=os.path.join(current_dir,'un.ui') 

        loader = QtUiTools.QUiLoader()
        self.ui=loader.load(ui_file)

        if self.ui:
                print("UI loaded successfully!")
                print(f"UI object type: {type(self.ui)}")

        self.ui.Button.setText("Send")
        self.ui.Button.clicked.connect(self.send_command)
        
        self.ui.Input.setPlaceholderText("Enter command")
        
        self.ui.Output.setReadOnly(True)

        self.ui.status.setText("Status: Disconnected")
        self.setCentralWidget(self.ui)

        QTimer.singleShot(100, self.init_websocket)
        
    
    def init_websocket(self):
        self.ws_client=WebsocketClient()
        self.ws_client.connected.connect(self.on_websocket_connected)
        self.ws_client.disconnected.connect(self.on_websocket_disconnected)
        self.ws_client.message_received.connect(self.on_websocket_message)
        self.ws_client.status_message.connect(self.on_status_message)
        self.ws_client.error_occurred.connect(self.on_websocket_error)
        
        self.ws_client.start()

    def on_websocket_connected(self):
        self.update_status("Connected", "green")
        self.log_message("[system] connection established")
        self.ui.Button.setEnabled(True)
    
    def on_websocket_disconnected(self):
        self.update_status("disconnected", "red")
        self.log_message("[system] connection closed")
        self.ui.Button.setEnabled(False)
    
    def on_websocket_message(self,data):
        try:
            formatted=json.dumps(data, indent=2,ensure_ascii=False)
            self.log_message(f"[Server] {formatted}")
        except:
            self.log_message(f"[Server] {data}")
    
    def on_status_message(self,message):
        self.log_message(f"[Status] {message}")
    
    def on_websocket_error(self,error_msg):
        self.log_message(f"[Error] {error_msg}")
        self.update_status(f"Error: {error_msg[:30]}", "red")
    
    def send_command(self):
        command_text = self.ui.Input.text().strip()

        if not command_text == None:
            command_text = '{"action": "test", "message": "Hello from QtDesigner!"}'
    
        try:
            command_data = json.loads(command_text)
            self.log_message(f"[Sending]")
            self.ws_client.send_message(command_data)
            self.log_message(f"[Debug] Команда передана в WebSocket клиент")
            self.ui.Input.clear()

        except json.JSONDecodeError:
            self.log_message(f"[FAILED] Invalid JSON format")
            self.ws_client.send_message(command_text)
            self.ui.Input.clear()
        except Exception as e:
            self.log_message(f"[FAILED] {str(e)}")
            self.ui.Input.clear()
    
    def log_message(self,message):
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        log_widget=self.ui.Output

        log_widget.append(f"[{timestamp}] {message}")


    def update_status(self,status,color="black"):
        self.ui.status.setText(f"Status: {status}")
        self.ui.status.setStyleSheet(f"""QLabel {{background-color: {color}}}""")
        self.ui.status.update()
        
    def closeEvent(self, event):
        if self.ws_client:
            self.ws_client.stop()
        super().closeEvent(event)

def main():
    app = QApplication(sys.argv)
    window = App()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()

