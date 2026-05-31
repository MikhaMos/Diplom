import asyncio
import websockets
from websockets.asyncio.server import serve
import json
import signal
import logging
import numpy as np

from ml_model import FatiguePredictor
from database import Database
from time_controller import now

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MLServer:
    def __init__(self, host: str="localhost", port:int = 8766):
        self.host = host
        self.port = port  
        self.server = None
        self.running = False
        self.db = Database()
        self.model = FatiguePredictor()

    async def handle_client(self, websocket, path=None):
        """Обрабатывает соединение с клиентом"""
        client_address = websocket.remote_address
        logger.info(f"New ML client connected: {client_address}")

        try:
            async for message in websocket:
                try:
                    data = json.loads(message)
                    command = data.get('command')
                    logger.info(f"ML resived time:{now()} data: {data}")

                    if command == 'predict':
                        timestamp_str = data.get('timestamp')
                        task_complexity = data.get('task_complexity', 1) # по умолчанию 1 (средняя)
                        if timestamp_str:
                            try:
                                from datetime import datetime
                                timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                            except:
                                timestamp = now()
                        else:
                            timestamp = now()
                         
                        pred_class, confidence, proba  = self.model.predict(timestamp, task_complexity)
                        adaptation_level = self.model.get_adaptation_level(pred_class)
                        response = {
                            'type': 'prediction',
                            'prediction_class': int(pred_class),
                            'confidence': float(confidence),
                            'probabilities': [float(p) for p in proba],
                            #'threshold_used': float(self.model.confidence_threshold),
                            'adaptation_level': self.model.get_adaptation_level(pred_class),
                            'complexity': task_complexity,
                            'timestamp': timestamp.isoformat()
                        }

                        #Логируем предсказание
                        self.db.log_command(
                            source="server_ml",
                            command="predict_result",
                            parameters= f"timestamp_predict: {timestamp}, prediction_class: {pred_class}, confidence: {confidence:.2f}, probabilities: [{proba[0]:.2f}, {proba[1]:.2f}, {proba[2]:.2f}]",
                            success=True
                        )

                        await websocket.send(json.dumps(response))
                        logger.info(f"ML send: {response}")
                        """
                    elif command == 'retrain':
                        # Запрос на дообучение модели

                        X_data = data.get('X')
                        y_data = data.get('y')

                        if X_data and y_data:
                            X = np.array(X_data)
                            y = np.array(y_data)
                            accuracy = self.model.train(X, y)

                            response = {
                                'type': 'retrain_result',
                                'accuracy': float(accuracy),
                                'message': 'Model retrained successfully.'
                            }
                        

                        else:
                            response = {
                                'type': 'error',
                                'message': 'Invalid training data format.'
                            }

                        await websocket.send(json.dumps(response))
                        """

                    else:
                        response = {
                            'type': 'error',
                            'message': 'Invalid command.'
                        }
                        await websocket.send(json.dumps(response))

                except json.JSONDecodeError:
                    await websocket.send(json.dumps({
                        'type': 'error',
                        'message': 'Invalid JSON format'
                    }))
                except Exception as e:
                    await websocket.send(json.dumps({
                        'type': 'error',
                        'message': str(e)
                            }))
        except websockets.exceptions.ConnectionClosed:
            logger.info(f"ML client disconnected: {client_address}")

    async def periodic_model_update(self):
        """Переобучение каждые 20 минут"""
        while self.running:
            await self.wait_virtual(1200) # 20 минут
            try:
                rows = self.db.get_training_data(limit=10000)
                if len(rows)<10:
                    continue
                X,y = [],[]
                for row in rows:
                    timestamp_str = row['timestamp']
                    try:
                        from datetime import datetime
                        timestamp = datetime.fromisoformat(timestamp_str)
                    except:
                        continue
                    
                    fatigue_level = row['fatigue_level']
                    concentration_level = row['concentration_level']
                    task_complexity = row['task_complexity']

                    
                    X.append(self.model.extract_features(timestamp,task_complexity))
                    
                    # Трёхклассовая цель
                    if fatigue_level >= 7 and concentration_level <= 4:
                        target = 2
                    elif 5 <= fatigue_level <= 7 and 4 <= concentration_level <= 7:
                        target = 1
                    else:
                        target = 0
                    y.append(target)

                if len(X)>0:
                    X = np.array(X)
                    y = np.array(y)
                    accuracy = self.model.train(X, y)
                    logger.info('Predictor model updated complete')
                    self.db.log_command(
                        source="server_ml",
                        command="periodic_model_update",
                        parameters= accuracy,
                        success=True
                    )
            except Exception as e:
                logger.error(f"Failed to update model: {e}")
    
    async def start(self):
        # Запускаем сервер
        self.running = True
        async with serve(self.handle_client, self.host, self.port) as server:

        # Запускаем периодическую задачу обновления модели
            asyncio.create_task(self.periodic_model_update())
            self.server = server
        # Ждем завершения
            await server.serve_forever()
        
    
    async def wait_virtual(self, virtual_seconds: float):
        start = now()
        while (now() - start).total_seconds() < virtual_seconds:
            await asyncio.sleep(0.1)
    
    def stop(self):
        # Останавливаем сервер
        self.running = False
        if self.server:
            self.server.close()
        self.db.close()
        logger.info("ML Server stopped")

    
async def main():
    server = MLServer()

    # Обработка Ctrl+C
    try:
        await server.start()
    except asyncio.CancelledError:
        pass
    except Exception as e:
        logger.error(f"Server error: {e}")
    finally:
        server.stop()

if __name__ == "__main__":
    asyncio.run(main())