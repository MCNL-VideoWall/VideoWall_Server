from fastapi import FastAPI, WebSocket
from contextlib import asynccontextmanager
import multiprocessing
from udp_sock import run_udp_server
import session
from typing import Dict


clients: Dict[str, WebSocket] = {}


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

    try:
        while True:
            data = await websocket.receive_json()
            messageType = data.get("type")

            print(f"[{client_uuid}] {data}")

            match messageType:
                case "HELLO":
                    await handle_hello(websocket, client_uuid)
                case "SESSION_LIST_REQ":
                    print("SESSION_LIST_REQ")
                case "SESSION_CREATE":
                    print("SESSION_CREATE")
                case "SESSION_JOIN":
                    print("SESSION_JOIN")
                case "SESSION_LEAVE":
                    print("SESSION_LEAVE")
                case "START":
                    print("START")
                case _:
                    print("UNKNOWN")

    except Exception as e:
        print(f"Connection closed: {e}")
    finally:
        # TODO: Session Manager를 통해 해당 client id가 속해있는 session에서 제거
        # TODO: Client Dict에서 해당 client id 제거
        print(f"Disconnection routine {client_uuid}")


async def handle_hello(websocket: WebSocket, client_uuid: str, data):
    clients[client_uuid] = websocket
