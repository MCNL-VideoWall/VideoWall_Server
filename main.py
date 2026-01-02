from fastapi import FastAPI, WebSocket
from typing import Dict, List
from contextlib import asynccontextmanager
import multiprocessing
from udp_sock import run_udp_server


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
    print("UDP Server process started")

    # Server Cleanup Routine
    yield
    print("UDP Server Shutting Down...")
    if udp_process.is_alive():
        udp_process.terminate()
        udp_process.join()
        print("UDP Server process terminated")

app = FastAPI(lifespan=lifespan)

# ----------------------------------------------------
# 1. Session class


class Session:

    def __init__(self, sessionId: int, sessionName: str):
        self.sessionId = sessionId
        self.name = sessionName
        self.slot: int = 1024
        self.clients: Dict[int, WebSocket] = {}


# 2. Session Manager class
class SessionManager:

    def __init__(self):
        self.sessionList: Dict[int, Session] = {}   # HostId, Session

    def createSession(self, hostId: int, name: str) -> Session:
        newSession = Session(sessionId=hostId, sessionName=name)
        self.sessionList[hostId] = newSession
        return newSession

    def getSessionList(self):
        result = []
        for session in self.sessionList.values():
            result.append({
                "sessionId": session.sessionId,
                "sessionName": session.name,
                "currentClients": len(session.Clients),
                "maxSlots": session.slot
            })
        return result


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        data = await websocket.receive_text()
        await websocket.send_text(f"Message text was: {data}")
