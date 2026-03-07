import asyncio
import websockets
import json
import time
from threading import Thread
import logging

from main_simulation import KukaRobot
from database import Database
from time_controller import now

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PybulletServer:
    def __init__(self, host="localhost", port=8765):
        self.host = host
        self.port = port
        self.robot = KukaRobot(gui=True)
        self.robot.connect()
        self.db = Database()
        self.adaptive_mode = False
        self.clients = set()

    async def register(self,websocket):
        self.clients.add(websocket)
        print(f"New client: {websocket.remote_address}")
    
    async def unregister(self,websocket):
        self.clients.remove(websocket)
        print(f"Client disconnected: {websocket.remote_address}")

    
    async def broadcast_positions(self):
        """Передает текущие позиции суставов"""
        while True:
            try:
                positions = self.robot.get_joint_positions()
                message = {
                    'type': 'positions',
                    'JointPositions': positions.get('JointPositions'),
                    'FramePositions': positions.get('FramePositions'),
                    'End_effector_Orientation': positions.get('End_effector_Orientation'),
                    'timestamp': time.time(),
                    'virtual_time': now().isoformat(),
                    'adaptive_mode': self.adaptive_mode,
                    'speed_factor': positions.get('velosity')
                }
                

                self.db.save_telemetry(
                    positions=f'joint_positions:{positions.get('JointPositions')}, frame_positions:{positions.get("FramePositions")}, end_effector_orientation:{positions.get("End_effector_Orientation")}',
                    velocity=positions.get('velosity'),
                    adaptive_mode=self.adaptive_mode
                )
                try:
                    await asyncio.gather(
                        *[asyncio.create_task(client.send(json.dumps(message))) for client in self.clients]
                    )
                    
                except Exception as e:
                    logger.error(f"Error while broadcasting positions: {e}")
                    
                await asyncio.sleep(0.1)
            except Exception as e:
                logger.error(f"Error while broadcasting positions: {e}")
                break

    async def handle_client(self,websocket):
        await self.register(websocket)
        client_address = websocket.remote_address
        logger.info(f"Client connected: {client_address}")
        try:
            async for message in websocket:
                await self.process_message(websocket,message)
        except Exception as e:
            logger.error(f"Error while handling client: {e}")
        except websockets.exceptions.ConnectionClosed:
            logger.info(f"Client disconnected: {client_address}")

    async def process_message(self,websocket,message):
        try:
            data = json.loads(message)
            command = data.get('command')
            
            self.db.log_command(
                "response_pybullet_server", 
                command, 
                json.dumps(data), 
                True
            )
            response=None
            
            if command == 'move_joint':
                joint = data.get('joint')
                direction = data.get('direction')
                step = data.get('step', 0.1)
                success,log_msg = self.robot.move_joint(joint,direction,step)

                response={
                    'type': 'command_response',
                    'command':'move_joint',
                    'success': success,
                    'message': log_msg,
                    'timestamp': now()
                }

            elif command == 'reset_positions':
                self.robot.reset_positions()
                response={
                    'type': 'command_response',
                    'command':'reset_positions',
                    'success': True,
                    'message': 'Positions have been reset',
                    'timestamp': now()
                }
            
            elif command == 'start_automatic_mode':
                points = data.get('points')
                orientations = data.get('orientations', None)
                loop = data.get('loop_programming', False)
                success,log_msg = self.robot.start_automatic_mode(points, orientations, loop)
                response={
                    'type': 'command_response',
                    'command':'start_automatic',
                    'success': success,
                    'message': log_msg,
                    'point_count': len(points),
                    'timestamp': now()
                }
            
            elif command == 'stop_automatic_mode':
                self.robot.automatic_mode = False
                success,log_msg = self.robot.stop_automatic_mode()
                response={
                    'type': 'command_response',
                    'command':'stop_automatic',
                    'success': success,
                    'message': log_msg,
                    'timestamp': now()
                }
                
            elif command == 'set_adaptive_mode':
                self.adaptive_mode = data.get('enabled', False)
                self.robot.set_adaptive_mode(self.adaptive_mode, 'reduced' if self.adaptive_mode else 'full')
                response={
                    'type': 'command_response',
                    'command':'set_adaptive_mode',
                    'success': True,
                    'message': 'Adaptive mode has been set',
                    'adaptive_mode': self.adaptive_mode,
                    'timestamp': now()
                }
                
                logger.info(f"Adaptive mode: {self.adaptive_mode}, Speed mode: {self.speed_mode}")
                
                
            else:
                response={
                    'type': 'error',
                    'message': 'Unknown command',
                    'timestamp': now()
                }
            
            await websocket.send(json.dumps(response))
                
            
            logger.info(f"Sedding response: {response}")
            self.db.log_command(
                "send_pybullet_server",
                response.get('command'), 
                json.dumps(response), 
                True
            )
            
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

    
    async def start_server(self):
        async with websockets.serve(self.handle_client, self.host, self.port):
            logger.info(f"Server started on {self.host}:{self.port}")
            
            self.broadcast_task = asyncio.create_task(self.broadcast_positions())
            await asyncio.Future()

    def run(self):
        asyncio.run(self.start_server())

    def run_in_thread(self):
        thread = Thread(target=self.run , daemon=True)
        thread.start()
        return thread

    def stop(self):
        """Остановка сервера"""
        logger.info("Остановка сервера PyBullet...")
        self.running = False
        self.db.close()
        if self.broadcast_task and not self.broadcast_task.done():
            self.broadcast_task.cancel()
        
        if hasattr(self, 'robot') and self.robot:
            self.robot.disconnect()
    
if __name__ == "__main__":
    server = PybulletServer()
    
    try:
    # Запускаем сервер в отдельном потоке
        server_thread = server.run_in_thread()
    
        # Основной поток ждет завершения
        while True:
            time.sleep(1)
        
    except KeyboardInterrupt:
        logger.info("Получен сигнал KeyboardInterrupt")
        server.stop()