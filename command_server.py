import serial
import asyncio
import sys
import websockets

class CommandServer:

    def __init__(self):
        self.connected = set()
        #self.serial = serial.Serial('/dev/camera0')
        self.allowed_commands = set(['W', 'A', 'S', 'D', 'L', 'K', 'I', 'O'])

    async def on_connect(self, websocket):
        print('Client connected ' + websocket.remote_address[0])
        
        self.connected.add(websocket)
        
        try:
            async for message in websocket:
                message = message.strip()
                if message not in self.allowed_commands:
                    print('Discarding command ' + message)
                    continue
                serial.write((message + '\n').encode('utf-8'))
        finally:
            print('Client disconnected')
            self.connected.remove(websocket)
        

    async def run(self):
        print('Starting server')
        async with websockets.serve(self.on_connect, '0.0.0.0', 5678):
            await asyncio.Future()
        print('Closing server')

if __name__ == '__main__':
    server = CommandServer()
    asyncio.run(server.run())
