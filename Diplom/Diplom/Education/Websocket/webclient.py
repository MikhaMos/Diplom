import asyncio
import websockets
import json

async def main():
    async with websockets.connect("ws://localhost:8765") as websocket:
        print("Подключены к серверу")

        command = {
            "command": "ВПЕРЕД",
            "speed": 50,
            "value": True,
        }

        await websocket.send(json.dumps(command))
        print(f"Отправили команду {command}")

        response = await websocket.recv()

        response_data = json.loads(response)
        print(f"Получили ответ {response_data}")
      

asyncio.get_event_loop().run_until_complete(main())