import websockets
import asyncio
import json
import logging
import threading 
from typing import Optional,Dict,Any
from database import Database
from PySide6.QtCore import Signal, QObject

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PyBulletClient(QObject):

    connected = Signal()
    disconnected = Signal()
    positions_received = Signal(dict)
    error_occurred = Signal(str)
    command_response = Signal(str)

    def __init__(self, uri: str ="ws://localhost:8765"):
        super().__init__()
        self.uri = uri
        self.websocket: Optional[websockets.WebSocketClientProtocol] = None
        self.running =False
        self.loop: Optional[asyncio.AbstractEventLoop] = None
        self.db = Database()

        self._reconnect_attempts = -1 # -1 - бесконечно
        self._reconnect_delay = 1 # начальная задержка
        self._max_reconnect_delay = 60 # максимальная задержка
        self._reconnect_task: Optional[asyncio.Task]  = None 
        self._monitor_task: Optional[asyncio.Task] = None

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
                        'FramePositions':data.get('FramePositions'),
                        'End_effector_Orientation':data.get('End_effector_Orientation'),
                        }
                    self.positions_received.emit(positions)
                else:
                    response=data.get('message')
                    self.command_response.emit(response)
        except Exception as e:
            logger.error(f"Error while monitoring positions: {e}")
            self.error_occurred.emit(str(e))
            raise
            
                
                
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
        self.running=True
        try:
            self._reconnect_task=self.loop.create_task(self._run_reconnecting())
            self.loop.run_until_complete(self._reconnect_task)
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

    async def _run_reconnecting(self):
        while self.running:
            try:
                await self._connect_with_retry()
                await self._run_connected()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Connection error in main loop: {e} ")
                self.error_occurred.emit(str(e))
                if self.running:
                    await asyncio.sleep(self._reconnect_delay)
            finally:
                await self._close_connection()

    async def _connect_with_retry(self):
        """Пытается подключиться с экспоненциальной задержкой"""
        attempt = 0
        while self.running:
            try:
                self.websocket = await websockets.connect(self.uri)
                logger.info(f"Connected to {self.uri}")
                self.db.log_command("pybullet", "connect", f"uri: {self.uri}", True)
                self.connected.emit()
                return
            except Exception as e:
                logger.warning(f"Connection attempt {attempt+1} failed: {e}")
                if self._reconnect_attempts != -1 and attempt >= self._reconnect_attempts:
                    raise # Превышено количество попыток
                delay =  min(self._reconnect_delay*(2**attempt), self._max_reconnect_delay)
                attempt += 1
                await asyncio.sleep(delay)

    async def _run_connected(self):
        """Запускаем мониторинг и ждет его завершения"""
        self._monitor_task = asyncio.create_task(self._monitor_positions())
        try:
            await self._monitor_task
        except asyncio.CancelledError:
            #Штатная остановка 
            pass
        except Exception as e:
            logger.error(f"Monitor task failed: {e}")
            raise

    async def _close_connection(self):
        if self.websocket:
            await self.websocket.close()
            self.websocket = None
            self.disconnected.emit()
            logger.info("Disconnected from server")


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
            asyncio.run_coroutine_threadsafe(self._shutdown(), self.loop)

    async def _shutdown(self):
        """Корутина для корректной остановки клиента"""
        # Отменяем задачу переподключения
        if self._reconnect_task and not self._reconnect_task.done():
            self._reconnect_task.cancel()
            try:
                await self._reconnect_task
            except asyncio.CancelledError:
                pass

        #Отменяем мониторинг
        if self._monitor_task and not self._monitor_task.done():
            self._monitor_task.cancel()
            try:
                await self._monitor_task
            except asyncio.CancelledError:
                pass

        # Закрываем соединение
        await self._close_connection()

        