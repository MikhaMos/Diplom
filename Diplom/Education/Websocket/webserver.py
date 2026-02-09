import asyncio 
import json
from websockets.asyncio.server import serve

async def handler_client(websocket):
    try:
        print("Клиент подключился")
        async for message in websocket:
            print(f"Получено сообщение: {message}")
            data = json.loads(message)

            response_data  = {
                "original_command": data,
                "status": "OK",
                "serve_note": "Принято в" + asyncio.get_event_loop().time().__str__()
            }
            response_json = json.dumps(response_data)
            
            await websocket.send(response_json)
    except Exception:
        print("Ршибка")
        
async def main():
    async with serve(handler_client,"localhost",8765) as server:
        await server.serve_forever()

asyncio.run(main())