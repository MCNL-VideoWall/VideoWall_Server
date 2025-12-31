from fastapi import FastAPI, WebSocket
from typing import Dict
from contextlib import asynccontextmanager
import multiprocessing
from udp_sock import run_udp_server

app = FastAPI()

# ----------------------------------------------------
# 1. Session class


class Session:
    def __init__(self, sessionId: int, sessionName: str):
        self.sessionId = sessionId
        self.name = sessionName
        self.slot: int = 1024
        self.Clients: Dict[int, WebSocket] = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Server Startup Routine
    print("UDP Server Starting Up...")
    udp_process = multiprocessing.Process(
        target=run_udp_server,
        args=("0.0.0.0", 65535),
        daemon=True
    )
    udp_process.start()
    print("UDP Server On")

    # Server Cleanup Routine
    yield


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        data = await websocket.receive_text()
        await websocket.send_text(f"Message text was: {data}")
