import websockets
import asyncio
import json
import logging
import threading 
from typing import Optional,Dict,Any
from database import Database
from datetime import datetime
from PySide6.QtCore import Signal, QObject

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PyBulletClient(QObject):

    connected = Signal()
    disconnected = Signal()
    positions_received = Signal(dict)
    error_occurred = Signal(str)
    command_response = Signal(dict)

    def __init__(self, uri: str ="ws://localhost:8765"):
        super().__init__()
        self.uri = uri
        self.websocket: Optional[websockets.WebSocketClientProtocol] = None
        self.running =False
        self.loop: Optional[asyncio.AbstractEventLoop] = None
        self.db = Database()
        

    async def connect_async(self):
        try: 
            self.websocket=await websockets.connect(self.uri)
            self.running =True
            logger.info(f"connect to {self.uri}")
            
            self.connected.emit()
            
            self.db.log_command("pybullet", "connect", f"uri: {self.uri}", True)

            # Запускаем мониторинг позиций
            asyncio.create_task(self._monitor_positions())

        except Exception as e:
            logger.error(f"Error while connecting: {e}")
            self.db.log_command("pybullet", "connect", f"uri: {self.uri}", False)
            raise
    
    async def _monitor_positions(self):
        try:
            async for message in self.websocket:
                data =json.loads(message)
                if data.get('type') == 'positions':
                    positions = {
                        'JointPositions':data.get('JointPositions',), 
                        'FramePositions':data.get('FramePositions')
                        }
                    self.positions_received.emit(positions)
        except Exception as e:
            logger.error(f"Error while monitoring positions: {e}")
            self.error_occurred.emit(str(e))
            
                
                
    async def send_command_async(self, command: str, **kwargs) -> dict[str, Any]:
        # Отправляет команду на сервер симуляции
        if not self.websocket or not self.running:
            raise ConnectionError("Not connected to server")
        try:
            message = {"command": command, **kwargs}
            await self.websocket.send(json.dumps( message))
            logger.info(f"Sending command: {message}")

            params_str = json.dumps(kwargs) if kwargs else {}

            self.db.log_command("send_pybullet_client", command, params_str, True)

        except Exception as e:
            logger.error(f"Error while sending command: {e}")
            self.db.log_command("pybullet_client", command, json.dumps(kwargs), False)
            raise
        
    async def disconnect_async(self):
        if self.websocket:
            await self.websocket.close()
            self.running=False
            self.disconnected.emit()
            logger.info("Disconnected from server")

    def start(self):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        try:
            self.loop.run_until_complete(self.connect_async())
            
            self.loop.run_forever()
        except Exception as e:
            logger.error(f"Error while starting client: {e}")
        finally:
            # Очистка при завершении
            if self.loop and not self.loop.is_closed():
                if self.loop.is_running():
                    self.loop.stop()
                    
                # Завершаем все задачи
                tasks = asyncio.all_tasks(self.loop)
                if tasks:
                    for task in tasks:
                        if not task.done():
                            task.cancel()
                    
                    # Даем задачам время на завершение
                    self.loop.run_until_complete(
                        asyncio.gather(*tasks, return_exceptions=True)
                    )
                
                self.loop.close()
            self.loop = None
            logger.info("Client event loop stopped")

    def run_in_thread(self):
        thread = threading.Thread(target=self.start, daemon=True)
        thread.start()
        return thread
    
    def send_command(self, command: str, **kwargs):
        """Отправляет команду из главного потока"""
        if not self.running or not self.loop or self.loop.is_closed():
            logger.warning("Cannot send command: client not running")
            return
        
        # Используем thread-safe вызов
        asyncio.run_coroutine_threadsafe(
            self.send_command_async(command, **kwargs),
            self.loop
        )
    
    def stop(self):
        self.running=False
        if self.loop and self.loop.is_running():
            asyncio.run_coroutine_threadsafe(self.disconnect_async(), self.loop)
        