import json
import asyncio
import websockets
from threading import Thread
from PySide6.QtCore import Signal, QObject

class WebsocketClient(QObject):
        
    connected = Signal()
    disconnected = Signal()
    message_received = Signal(dict)
    status_message = Signal(str)
    error_occurred = Signal(str)

    def __init__(self, url="ws://localhost:8765"):
        super().__init__()
        self.url = url
        self._is_running=True
        self._websocket = None
        self._loop = None
        self._thread = None

    def start(self):
        """Запускает WebSocket клиент в отдельном потоке"""
        self._thread = Thread(target=self._run_async, daemon=True)
        self._thread.start()

    def _run_async(self):
        """Запускает asyncio event loop в отдельном потоке"""
        self._loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self._loop)
        self._loop.run_until_complete(self._connect_loop())
    
    async def _connect_loop(self):
        while self._is_running:
            try:
                self.status_message.emit(f"Connecting... to {self.url}")

                async with websockets.connect(self.url) as websocket:
                    self._websocket = websocket
                    self.status_message.emit("Connected")
                    self.connected.emit()
                
                    await self._receive_messages(websocket)
            
            except websockets.exceptions.ConnectionClosed:
                self.status_message.emit("Соединение закрыто")
                self.disconnected.emit()
            except ConnectionRefusedError:
                self.status_message.emit("Сервер недоступен")
                self.disconnected.emit()
                await asyncio.sleep(2)  # Ждем перед повторной попыткой
            except Exception as e:
                self.error_occurred.emit(str(e))
                await asyncio.sleep(1)

    async def _receive_messages(self,websocket):
        while self._is_running:
            try:
                message = await asyncio.wait_for(
                    websocket.recv(),
                    timeout=0.5
                )
                try:
                    data=json.loads(message)
                    self.message_received.emit(data)
                except json.JSONDecodeError:
                    self.message_received.emit({"message":message})
            except asyncio.TimeoutError:
                continue
            except websockets.exceptions.ConnectionClosed:
                raise
    
    def send_message(self,command_data):
        self.status_message.emit(f"command received: {command_data}")
        try:
            if isinstance(command_data, dict):
                command = json.dumps(command_data, ensure_ascii=False)
            else:
                command = str(command_data)
            

            asyncio.run_coroutine_threadsafe(
                self._send_command(command),
                self._loop
            )
        except Exception as e:
            self.error_occurred.emit(str(e))

    async def _send_command(self,command):
        if self._websocket:
            #await self._websocket.send(command)
            self.status_message.emit(f"DEBUG _send_command: Sending to websocket...")
            try:
                await self._websocket.send(command)
                self.status_message.emit(f"DEBUG _send_command: Successfully sent")
            except Exception as e:
                self.error_occurred.emit(f"DEBUG _send_command: Error while sending: {e}")
                raise
        else:
            self.error_occurred.emit(f"DEBUG _send_command: No websocket connection")
    
    def stop(self):
        self._is_running = False
        if self._websocket:
            asyncio.run_coroutine_threadsafe(
                self._websocket.close(),
                self._loop
            )
        if self._thread:
            self._thread.join(timeout=2)

        
