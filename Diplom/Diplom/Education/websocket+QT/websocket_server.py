import asyncio
from websockets.asyncio.server import serve
import json

from datetime import datetime

async def handle_client(websocket):
    client_ip = websocket.remote_address[0]
    print(f"New client connected from {client_ip}")
    
    try:
        async for message in websocket:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] Получено: {message}")
            try:
                data = json.loads(message)

                print(f"[Server] recived {data}")

                response = json.dumps({"status": "OK", "serve_note": "Принято в" + datetime.now().__str__()})
                await websocket.send(response)
                
            except json.JSONDecodeError:
                print(f"[Server] recived {message}")
            
    except serve.exceptions.ConnectionClosed:
        print(f"Client {client_ip} disconnected")

async def main():
    async with serve(handle_client, "localhost", 8765) as server:
        await server.serve_forever()

if __name__ == "__main__":
    asyncio.run(main())