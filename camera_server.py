import cv2
import asyncio
import sys
import websockets

CAMERA_WIDTH = 720
CAMERA_HEIGHT = 480

class CommandServer:

    def __init__(self):
        self.connected = set()
        self.camera = cv2.VideoCapture(0)
        self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, CAMERA_WIDTH)
        self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, CAMERA_HEIGHT)

    async def on_connect(self, websocket):
        print('Client connected ' + websocket.remote_address[0])
        
        self.connected.add(websocket)
        
        try:
            await websocket.wait_closed()
        finally:
            print('Client disconnected')
            self.connected.remove(websocket)
        
    async def broadcast_frames(self):
        try:
            while True:
                read, frame = self.camera.read()
                if not read:
                    print('Couldn\'t read frame')
                    continue
                websockets.broadcast(self.connected, bytes(frame))
        except KeyboardInterrupt:
            print('Keyboard interrupted camera')
        finally:
            self.camera.release()

    async def run(self):
        print('Starting server')
        async with websockets.serve(self.on_connect, host='0.0.0.0', port=5678, compression=None):
            t1 = asyncio.create_task(self.broadcast_frames())
            t2 = asyncio.create_task(asyncio.Future())
            done, pending = await asyncio.wait([t1, t2], return_when=asyncio.FIRST_COMPLETED)
            for task in pending:
                task.cancel()
        print('Closing server')

if __name__ == '__main__':
    server = CommandServer()
    asyncio.run(server.run())
