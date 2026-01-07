from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from contextlib import asynccontextmanager
import multiprocessing
from udp_sock import run_udp_server
from typing import Dict, Tuple
import asyncio
from marker_handler import getArucoList

marker_count = 0
clients: Dict[str, Tuple[int, WebSocket]] = {}
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
    global marker_count
    await websocket.accept()
    async with clients_lock:
        clients[client_uuid] = (marker_count, websocket)
        client_marker_id = marker_count
        marker_count += 1

    print(f"Connected: {client_uuid} (MARKER ID: {client_marker_id})")

    try:
        message = {
            "type": "WELCOME",
            "data": {
                "marker_id": client_marker_id,
                "aruco_bitmap": getArucoList(client_marker_id)
            }
            # TODO: Multicast IP 담아서 보내기
        }
        await websocket.send_json(message)

    except WebSocketDisconnect:
        print(f"WebSocketDisconnect: {client_uuid}")
    except Exception as e:
        print(f"Connection closed: {e}")
    finally:

        async with clients_lock:
            clients.pop(client_uuid, None)

        print(f"Disconnection routine {client_uuid}")


async def show_marker():
    async with clients_lock:
        sockets = [ws for _, ws in clients.values()]  # Tuple에서 websocket만 추출

    for ws in sockets:
        try:
            await ws.send_json({
                "type": "SHOW_MARKER"
            })
        except:
            pass
