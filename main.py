from fastapi import FastAPI, WebSocket
from contextlib import asynccontextmanager
import multiprocessing
from udp_sock import run_udp_server
import session
from typing import Dict
import asyncio


clients: Dict[str, WebSocket] = {}
clients_lock = asyncio.Lock()
manager = session.SessionManager()


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
            message = await websocket.receive_json()
            messageType = message.get("type")

            data = message.get("data")

            print(f"[{client_uuid}] {message}")

            match messageType:
                case "HELLO":
                    await handle_hello(websocket, client_uuid)
                case "SESSION_LIST_REQ":
                    await handle_session_list_request(websocket, client_uuid)
                    print("SESSION_LIST_REQ")
                case "SESSION_CREATE":
                    await handle_session_create(websocket, client_uuid, data)
                    print("SESSION_CREATE")
                case "SESSION_JOIN":
                    await handle_session_join(websocket, client_uuid, data)
                    print("SESSION_JOIN")
                case "SESSION_LEAVE":
                    await handle_session_leave(client_uuid)
                    print("SESSION_LEAVE")
                case "START":
                    print("START")
                case _:
                    print("UNKNOWN")

    except Exception as e:
        print(f"Connection closed: {e}")
    finally:
        # TODO: Session Manager를 통해 해당 client id가 속해있는 session에서 제거

        async with clients_lock:
            del clients[client_uuid]

        print(f"Disconnection routine {client_uuid}")


async def handle_hello(websocket: WebSocket | None, client_uuid: str, data):
    async with clients_lock:
        clients[client_uuid] = websocket


async def handle_session_list_request(websocket: WebSocket | None, client_uuid: str):
    if not websocket:
        print(f"[ERROR]  {client_uuid} not found..")
        return

    try:
        # get session list
        session_data = manager.getSessionList()

        # send list data (JSON format)
        await websocket.send_json({
            "type": "SESSION_LIST_RES",
            "data": session_data
        })
        print(f"[SUCCESS]   Send session list to {client_uuid}")
    except Exception as e:
        print(f"[ERROR]  Failed to send session list to {client_uuid}: {e}")


async def handle_session_create(websocket: WebSocket | None, client_uuid: str, session_name: str):
    if not websocket:
        print(f"[ERROR]  {client_uuid} not found..")
        return

    try:
        # session 생성
        new_session = await manager.createSession(client_uuid, session_name)

        # send list data (JSON format)
        await websocket.send_json({
            "type": "SESSION_CREATED",
            "data": new_session.sessionId
        })
        print(f"[SUCCESS]   Session Created for {client_uuid}: {session_name}")
    except Exception as e:
        print(f"[ERROR]  Failed to create session for {client_uuid}: {e}")


async def handle_session_join(websocket: WebSocket | None, client_uuid: str, session_id: str):
    if not websocket:
        print(f"[ERROR]  {client_uuid} not found..")
        return

    try:
        session = await manager.getSessionBySessionId(session_id)

        if session:
            manager.joinSession(session_id, client_uuid)

            await websocket.send_json(
                {
                    "type": "SESSION_JOINED",
                    "data": {
                        "ClientMarkerID": session.currClientCount,
                        "SessionList": manager.getSessionList()
                    }
                }
            )
            session.currClientCount += 1

            print("[JOIN]    Success to join this section")
        else:
            print(f"[ERROR]  This session does not exist.. [{client_uuid}]")

    except Exception as e:
        print(f"[ERROR]  Failed to join the session  {client_uuid}: {e}")


async def handle_session_leave(client_uuid: str):
    # 해당 Client가 특정 Session 내에 존재하는 경우
    if await manager.leaveSession(client_uuid):
        print(
            f"[SUCCESS]   {client_uuid} has been removed from their session.")
    else:
        print(f"[NOTICE]   {client_uuid} was not in any session.")
