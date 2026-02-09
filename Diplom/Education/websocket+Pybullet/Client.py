import json
import asyncio
import websockets

async def send_command():
    uri = "ws://localhost:8765"

    try:
        print("Connecting to WebSocket server...")
        async with websockets.connect(uri) as websocket:
            response = await websocket.recv()
            print(f"Received response {response}")
             
            while True:
                print("\n" + "="*50)
                print("Control Panel")
                print("="*50)
                print("1. Move")
                print("2. Reset")
                print("3. Get state")
                print("4. Exit")
                print("="*50)
                
                print("Enter your choice (1-4): ")
                choice = input().strip()

                if choice == "1":
                    positions = []
                    for i in range(6):
                        positions.append(float(input(f"Input position {i+1}: ")))

                    command = {
                        "command": "move",
                        "positions": positions   
                    }
                    
                    print(f"Sending command {command}")
                    await websocket.send(json.dumps(command))

                    response = await websocket.recv()
                    print(f"Received response {response}")

                elif choice == "2":
                    command = {"command": "reset"}
                    print(f"Sending command {command}")
                    await websocket.send(json.dumps(command))

                    response = await websocket.recv()
                    print(f"Received response {response}")

                elif choice == "3":
                    command = {"command": "get_state"}
                    print(f"Sending command {command}")
                    await websocket.send(json.dumps(command))

                    response = await websocket.recv()
                    print(f"Received response {response}")
                    data = json.loads(response)
                    if "state" in data:
                        positions = data['state']['joint_positions']
                        print(f"Positions: {positions}")
                        for i, pos in enumerate(positions):
                            print(f"joint {i+1}: {pos:.3f}")

                elif choice == "4":
                    print("Exiting...")
                    break

                else:
                    print("Invalid choice.")
    except ConnectionRefusedError:
        print("Connection refused. Make sure the server is running.")
    except Exception as e:
        print(f"An error occurred: {e}")


asyncio.run(send_command())