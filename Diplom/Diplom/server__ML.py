import asyncio
import websockets
from websockets.asyncio.server import serve
import json
import signal
from datetime import datetime 
from ml_model import FatiguePredictor
from database import Database
import logging
import numpy as np

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
                    logger.info(f"ML resived: {data}")

                    if command == 'predict':
                        timestamp_str = data.get('timestamp')
                        timestamp = datetime.fromtimestamp(timestamp) if timestamp_str else datetime.now()

                        hour = timestamp.hour
                        day_of_week = timestamp.weekday()

                        prediction, confidence  = self.model.predict([[hour, day_of_week]])
                        
                        response = {
                            'type': 'prediction',
                            'prediction': bool(prediction),
                            'confidence': float(confidence),
                            'threshold_used': float(self.model.confidence_threshold),
                            'requires_adaptation': confidence > self.model.confidence_threshold,
                            'timestamp': timestamp.isoformat()
                        }

                        #Логируем предсказание
                        self.db.log_command(
                            source="ml_client",
                            command="predict",
                            parameters= f"timestamp: {timestamp}, prediction: {prediction}, confidence: {confidence:.2f}",
                            success=True
                        )

                        await websocket.send(json.dumps(response))
                        logger.info(f"ML send: {response}")
                    
                    elif command == 'retrain':
                        # Запрос на дообучение модели

                        X_data = data.get('X', [])
                        y_data = data.get('y', [])

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
    
    async def start(self):
        # Запускаем сервер
        self.running = True

        async with serve(self.handle_client, self.host, self.port) as server:

        # Запускаем периодическую задачу обновления модели
            asyncio.create_task(self.periodic_model_update())
            self.server = server
        # Ждем завершения
            await server.serve_forever()

    async def periodic_model_update(self):
        while self.running:
            try: 
                # Каждые 5 минут пытаемся дообучить модель
                await asyncio.sleep(300)
                
                training_data = self.db.get_training_data()
                if len(training_data)> 20:  # Минимум 10 записей
                    X=[]
                    y=[]

                    for row in training_data:
                        X.append([row['hour_of_day'], row['day_of_week']])
                        y.append(1 if row['fatigue_level']>=7 else 0) # Уставший если оценка >= 7

                    if len(y)>0:
                        self.model.train(np.array(X), np.array(y))
                        logger.info('Predictor model updated complete')
            except Exception as e:
                logger.error(f"Failed to update model: {e}")
    
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