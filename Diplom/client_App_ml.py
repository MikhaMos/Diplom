import websockets
import asyncio
import json
from database import Database
import logging

from typing import Optional,Dict,Any, List
import threading
from threading import Thread
from PySide6.QtCore import Signal, QObject

from time_controller import now 

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MLClient(QObject):
    connected = Signal()
    disconnected = Signal()
    predictions_received = Signal(dict)
    error_occurred = Signal(str)

    def __init__(self, uri: str = "ws://localhost:8766", prediction_interval: float = 60.0):
        super().__init__()
        self.uri = uri
        self.websocket: Optional[websockets.WebSocketClientProtocol] = None
        self.running = False
        self.db = Database()
        self.loop: Optional[asyncio.AbstractEventLoop] = None
        self.prediction_interval = prediction_interval
        self.last_prediction: Optional[Dict[str, Any]] = None

        self._reconnect_attempts = -1 # -1 - бесконечно
        self._reconnect_delay = 1 # начальная задержка
        self._max_reconnect_delay = 60 # максимальная задержка
        self._reconnect_task: Optional[asyncio.Task]  = None 
        self._monitor_task: Optional[asyncio.Task] = None

    
    async def _monitor_predictions(self):
        while self.websocket and self.running:
            try:
                await self.get_prediction_async()
                await asyncio.sleep(self.prediction_interval)
            except Exception as e:
                logger.error(f"Error while monitoring predictions: {e}")
                self.error_occurred.emit(str(e))
                raise
    
    async def get_prediction_async(self, timestamp = None) -> Dict[str, Any]:
        if not self.websocket or not self.running:
            raise ConnectionError("Not connected to server")
        try:
            if timestamp is None:
                timestamp = now()
            message = {
                "command": "predict",
                "timestamp": timestamp.isoformat()
                }
            await self.websocket.send(json.dumps(message))
            response = await self.websocket.recv()
            result  = json.loads(response)

            if result.get('type') == 'prediction':
                self.last_prediction = result

                features = {
                    'hour': timestamp.hour,
                    'day_of_week': timestamp.weekday
                }

                self.db.log_ml_prediction(
                                    features=features,
                                    prediction=result.get('prediction'),
                                    coffidence=result.get('confidence'),
                                    threshold_used=result.get('threshold',0.8),
                                    adaptation_triggered=result.get('requires_adaptation',False)
                                    )

                self.predictions_received.emit(result)
            return result
        
        except Exception as e:
            logger.error(f"Error while getting prediction: {e}")
            raise

    async def should_adapt_interface(self):
        """Определяет, нужно ли адаптировать интерфейс"""
        if not self.last_prediction:
            await self.get_prediction_async()

        return self.last_prediction.get('requires_adaptation', False)
    
    async def get_adaptation_level(self):
        """Возвращает уровень адаптации (0.0-1.0)"""
        if not self.last_prediction:
            await self.get_prediction_async()

        confidence = self.last_prediction.get('confidence', 0.0)
        threshold = self.last_prediction.get('threshold', 0.8)

        if confidence <= threshold:
            return 0.0
        else:
            return min(1.0, (confidence-threshold)/(1.0-threshold))

    async def send_training_data_async(self, X:List, y:List):
         """Отправляет данные для дообучения модели"""
         if not self.websocket or not self.running:
            raise ConnectionError("Not connected to server")
         try:
            message = {
                "command": "retrain",
                "X": X,
                "y": y
                }
            await self.websocket.send(json.dumps(message))
            response = await self.websocket.recv()
            result  = json.loads(response)
            return result
        
         except Exception as e:
            logger.error(f"Error while sending training data: {e}")
            raise
    
    def start(self):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        self.running = True
        try:
            self._reconnect_task=self.loop.create_task(self._run_reconnecting())
            self.loop.run_until_complete(self._reconnect_task)
        except Exception as e:
            logger.error(f"Error while starting client: {e}")
        finally:
            if self.loop and not self.loop.is_closed():
                tasks= asyncio.all_tasks(self.loop)
                for task in tasks:
                    task.cancel()
                self.loop.run_until_complete(asyncio.gather(*tasks,return_exceptions=True))
                self.loop.close()
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
        attempt = 0
        while self.running:
            try:
                self.websocket = await websockets.connect(self.uri)
                logger.info(f"Connected to {self.uri}")
                self.db.log_command("ml", "connect", f"uri: {self.uri}", True)
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
        self._monitor_task = self.loop.create_task(self._monitor_predictions())
        try:
            await self._monitor_task
        except asyncio.CancelledError:
            pass
        except Exception as e:
            logger.error(f"Monitor task failed: {e}")
            raise
    
    async def _close_connection(self):
        if self.websocket:
            await self.websocket.close()
            self.websocket = None
            logger.info("Disconnected from server")
            self.disconnected.emit()

    def run_in_thread(self):
        thread = threading.Thread(target=self.start, daemon=True)
        thread.start()
        return thread

    def get_prediction(self):
        """Запрашивает предсказание из главного потока"""
        if not self.running or not self.loop or self.loop.is_closed():
            logger.warning("Cannot get prediction: client not running")
            return
        
        asyncio.run_coroutine_threadsafe(
            self.get_prediction_async(),
            self.loop
        )

    def send_training_data(self, X: list, y: list):
        """Отправляет данные для обучения из главного потока"""
        if not self.running or not self.loop or self.loop.is_closed():
            logger.warning("Cannot send training data: client not running")
            return
        
        asyncio.run_coroutine_threadsafe(
            self.send_training_data_async(X, y),
            self.loop
        )

    def stop(self):
        self.running=False
        if self.loop and self.loop.is_running():
            asyncio.run_coroutine_threadsafe(self._shutdown(), self.loop)
        
    async def _shutdown(self):
        if self._reconnect_task and not self._reconnect_task.done():
            self._reconnect_task.cancel()
            try:
                await self._reconnect_task
            except asyncio.CancelledError:
                pass
        if self._monitor_task and not self._monitor_task.done():
            self._monitor_task.cancel()
            try:
                await self._monitor_task
            except asyncio.CancelledError:
                pass
        await self._close_connection()
    