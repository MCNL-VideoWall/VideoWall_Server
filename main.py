from fastapi import FastAPI, WebSocket
from typing import Dict

app = FastAPI()

# ----------------------------------------------------
# 1. Session class
class Session:
    def __init__(self, sessionId: int, sessionName: str):
        self.sessionId = sessionId
        self.name = sessionName
        self.slot: int = 1024
        self.Clients: Dict[int, WebSocket] = {}


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        data = await websocket.receive_text()
        await websocket.send_text(f"Message text was: {data}")