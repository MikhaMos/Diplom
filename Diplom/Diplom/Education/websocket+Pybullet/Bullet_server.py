import json
import asyncio
from websockets.asyncio.server import serve

import threading
import time 
from Pybullet import SimpleRobot

class RobotWebsocketServer:

    def __init__(self,host="localhost",port=8765):
        self.host = host
        self.port = port
        self.clients = set()
        self.robot = None
        
    async def hadler_client(self, websocket):
        self.clients.add(websocket)

        try:
            await websocket.send(json.dumps({
                "status": "OK",
                "serve_note": "Соединение установлено"
            }))

            async for message in websocket:
                try:
                    data = json.loads(message)
                    print(f"[Server] recived {data}")


                    response = await self.process_command(data)
                    await websocket.send(json.dumps(response))

                except json.JSONDecodeError:
                    await websocket.send(json.dumps({
                        "error": "Invalid JSON format"
                    }))
        except serve.exceptions.ConnectionClosed:
            print(f"Client disconnected")
        finally:
            self.clients.remove(websocket)
    
    async def process_command(self,command):
        cmd_type = command.get("command", "")

        if cmd_type == "move":
            positions = command.get("positions", [])

            if len(positions) != 6:
                return {
                    "error": "Invalid positions format"
                }
            
            success = self.robot.set_joint_position(positions)

            if success:
                return {
                    "status": "OK",
                    "positions": f" Positions: {positions}"
                }
            
        elif cmd_type == "reset":
            self.robot.reset()
            return {
                "status": "OK",
                "reset": "Robot reset"
            }
        
        elif cmd_type == "get_state":
            state = self.robot.get_state()
            return {
                "status": "OK",
                "state": state
            }
            
        else:
            return {
                "error": "Invalid command"
            }
    
    def run_simulation_loop(self):
        print("Simulation loop started")
        self.robot = SimpleRobot()
        self.robot.reset()

        while True:
            self.robot.step()
            time.sleep(1/240)


    async def run_server(self):
    
        sim_thread = threading.Thread(target = self.run_simulation_loop, daemon=True)
        sim_thread.start()

        await asyncio.sleep(2)
        
        print(f"Запуск WebSocket сервера на {self.host}:{self.port}")
        async with serve(self.hadler_client,"localhost",8765) as server:
            await server.serve_forever()


if __name__ == "__main__":
    server = RobotWebsocketServer()
    asyncio.run(server.run_server())