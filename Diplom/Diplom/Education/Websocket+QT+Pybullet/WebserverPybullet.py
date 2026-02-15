import asyncio
import websockets
from websockets.asyncio.server import serve
import json
import time
from Pybuk import KukaRobot
from threading import Thread


class WebServerRobot():
    def __init__(self, host="localhost",port=8765):
        self.host=host
        self.port=port
        self.clients=set()
        self.robot=KukaRobot(gui=True)
        self.robot.connect()

    async def register(self,websocket):
        self.clients.add(websocket)
        print(f"New client: {websocket.remote_address}")
    
    async def unregister(self,websocket):
        self.clients.remove(websocket)
        print(f"Client disconnected: {websocket.remote_address}")
    
    async def send_to_all(self,message):
        if self.clients:
            await asyncio.gather(
                *[client.send(message) for client in self.clients]
            )

    async def send_positions(self):
        while True:
            positions=self.robot.get_joint_positions()
            message= {
                'type': 'positions',
                'positions': positions,
                'timestamp': time.time()
            }
            await self.send_to_all(json.dumps(message))
            await asyncio.sleep(0.1)

    async def handle_message(self,websocket,message):
        try:
            data = json.loads(message)
            command = data.get('command')
            joint = data.get('joint')
            direction = data.get('direction')

            if command=='move_joint':
                success,log_msg = self.robot.move_joint(joint,direction)

                log_message={
                    'type': 'log',
                    'data': log_msg,
                    'timestamp': time.time()
                }

                await websocket.send(json.dumps(log_message))

                positions=self.robot.get_joint_positions()
                pos_message={
                    'type': 'positions',
                    'positions': positions,
                    'timestamp': time.time()
                }
                await websocket.send(json.dumps(pos_message))

            elif command == 'reset':
                self.robot.reset_positions()
                await websocket.send(json.dumps(
                    {
                        'type': 'log',
                        'data': 'Robot reset',
                        'timestamp': time.time()
                    }
                ))

        except json.JSONDecodeError:
            await websocket.send(json.dumps({
                'type': 'error',
                'data': 'Invalid JSON format',
                'timestamp': time.time()
            }))

        except Exception as e:
            await websocket.send(json.dumps({
                'type': 'error',
                'data': str(e),
                'timestamp': time.time()
            }))
    
    async def handler(self,websocket,path=None):
        await self.register(websocket)
        try:
            async for message in websocket:
                await self.handle_message(websocket,message)
        except websockets.exceptions.ConnectionClosed:
            pass
        finally:
            await self.unregister(websocket)

    async def start_server(self):
        async with serve(self.handler, self.host, self.port) as server:
            print(f"Server started on {self.host}:{self.port}")

            positions_task = asyncio.create_task(self.send_positions())
            await server.serve_forever()
    
    def run(self):
        asyncio.run(self.start_server())

    def run_in_thread(self):
        thread = Thread(target=self.run , daemon=True)
        thread.start()
        return thread

if __name__ == "__main__":
    server = WebServerRobot()
    server.run_in_thread()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Server stopped")