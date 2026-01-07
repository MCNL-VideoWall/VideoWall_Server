from fastapi import FastAPI, WebSocket
from contextlib import asynccontextmanager
import multiprocessing
from udp_sock import run_udp_server
from typing import Dict
import asyncio


clients: Dict[str, WebSocket] = {}
clients_lock = asyncio.Lock()


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


@app.websocket("/ws/{client_uuid}")
async def websocket_endpoint(websocket: WebSocket, client_uuid: str):
    await websocket.accept()
    async with clients_lock:
        clients[client_uuid] = websocket

    try:
        websocket.send_json({
            "type": "WELCOME",
            # TODO: Marker ID 생성 및 비트맵 생성하여 json에 포함
            # TODO: Multicast IP 담아서 보내기
        })
    except Exception as e:
        print(f"Connection closed: {e}")
    finally:

        async with clients_lock:
            clients.pop(client_uuid, None)

        print(f"Disconnection routine {client_uuid}")
