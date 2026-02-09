import websockets
import asyncio
import json
from threading import Thread
import time
from PySide6.QtCore import Signal, QObject, Slot
import sys

class WebsocketClientApp(QObject):

    connected = Signal()
    disconnected = Signal()
    message_received = Signal(dict)
    error_occurred = Signal(str)
    
    def __init__(self,uri="ws://localhost:8765"):
        super().__init__()
        self.uri = uri
        self.websocket=None
        self.running=False
        self.loop=None

    async def connect_async(self):
        try: 
            self.websocket=await websockets.connect(self.uri)
            self.running =True
            self.connected.emit()

            self.message_received.emit({
                'type':'log',
                'data':f"connect to {self.uri}",
                'timestamp':time.time()
            })

            while self.running:
                try:
                    message = await self.websocket.recv()
                    data = json.loads(message)
                    self.message_received.emit(data)
                except websockets.exceptions.ConnectionClosed:
                    break

        except Exception as e:
            self.error_occurred.emit(str(e))
            self.running=False
        finally:
            self.disconnect_async()

    async def disconnect_async(self):
        self.running=False
        if self.websocket:
            await self.websocket.close()
            self.websocket=None
        self.disconnected.emit()
    
    def send_command(self,command, joint=None, direction =1):
        if self.websocket and self.running:
            message={
                'command':command,
                'joint':joint,
                'direction':direction   
            }
            asyncio.run_coroutine_threadsafe(
                self._send_async(json.dumps(message)),
                self.loop
            )
    
    async def _send_async(self,message):
        if self.websocket:
            await self.websocket.send(message)

    def start(self):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        self.loop.run_until_complete(self.connect_async())

    def run_in_thread(self):
        thread = Thread(target=self.start, daemon=True)
        thread.start()
        return thread
    
    def stop(self):
        self.running=False
        if self.loop and self.loop.is_running():
            self.loop.call_soon_threadsafe(self.loop.stop)
                            
        

