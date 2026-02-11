import websockets
import asyncio
import json
from database import Database
import logging
from datetime import datetime
from typing import Optional,Dict,Any, List
import threading
from threading import Thread
from PySide6.QtCore import Signal, QObject

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


    async def connect(self):
        try:
            self.websocket = await websockets.connect(self.uri)
            self.running = True
            self.connected.emit()

            logger.info(f"Connected to {self.uri}")
            self.db.log_command("ml", "connect", f"uri: {self.uri}", True)

            asyncio.create_task(self._monitor_predictions())

        except Exception as e:
            logger.error(f"Error while connecting: {e}")
            self.error_occurred.emit(str(e))
            self.db.log_command("ml", "connect", f"uri: {self.uri}", False)
            raise
    
    async def _monitor_predictions(self):
        while self.websocket and self.running:
            try:
                await self.get_prediction_async()
                await asyncio.sleep(self.prediction_interval)
            except Exception as e:
                logger.error(f"Error while monitoring predictions: {e}")
                raise
    
    async def get_prediction_async(self, timestamp:datetime= None) -> Dict[str, Any]:
        if not self.websocket or not self.running:
            raise ConnectionError("Not connected to server")
        try:
            if timestamp is None:
                timestamp = datetime.now()
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
                    'day_of_week': timestamp.weekday()
                }

                self.db.log_ml_prediction(
                                    features=features,
                                    prediction=result['prediction'],
                                    coffidence=result['confidence'],
                                    threshold_used=result['threshold',0.8],
                                    adaptation_triggered=result['requires_adaptation',False]
                                    )

                self.predictions_received.emit(result)
            return result
        
        except Exception as e:
            logger.error(f"Error while getting prediction: {e}")
            raise

    

    async def should_adapt_interface(self):
        """Определяет, нужно ли адаптировать интерфейс"""
        if not self.last_prediction:
            await self.get_fatigue_prediction()

        return self.last_prediction.get('requires_adaptation', False)
    
    async def get_adaptation_level(self):
        """Возвращает уровень адаптации (0.0-1.0)"""
        if not self.last_prediction:
            await self.get_fatigue_prediction()

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
         
    async def disconnect_async(self):
        if self.websocket:
            await self.websocket.close()
            self.running = False
            logger.info("Disconnected from server")
            self.disconnected.emit()
    
    def start(self):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        try:
            self.loop.run_until_complete(self.connect())
            self.loop.run_forever()
        except Exception as e:
            logger.error(f"Error while starting client: {e}")
        finally:
            tasks= asyncio.all_tasks(self.loop)
            for task in tasks:
                task.cancel()
            self.loop.run_until_complete(asyncio.gather(*tasks),return_exceptions=True)
            self.loop.close()
    
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
            self.loop.call_soon_threadsafe(self.loop.stop) 
        