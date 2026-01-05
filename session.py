from typing import Dict, List
import asyncio

# 1. Session class


class Session:

    def __init__(self, sessionId: str, sessionName: str):
        self.sessionId = sessionId
        self.name = sessionName
        self.clients: Dict[str, int] = {}  # uuid : marker id


# 2. Session Manager class
class SessionManager:

    def __init__(self):
        self.sessionList: List[Session] = []
        self.managerLock = asyncio.Lock()   # session manager lock

    async def createSession(self, hostId: int, name: str) -> Session:
        async with self.managerLock:
            newSession = Session(sessionId=hostId, sessionName=name)
            self.sessionList.append(newSession)
            return newSession

    async def getSessionList(self):
        async with self.managerLock:
            result = []
            for session in self.sessionList:

                clients_info = []
                for uuid, m_id in session.clients.items():
                    clients_info.append({
                        "uuid": uuid,
                        "markerId": m_id
                    })

                result.append({
                    "sessionId": session.sessionId,
                    "sessionName": session.name,
                    "currentClientCount": len(session.clients),
                    "clients": clients_info
                })
            return result

    async def isSessionExist(self, session_id: str) -> bool:
        async with self.managerLock:
            for session in self.sessionList:
                if session.sessionId == session_id:
                    return True
            return False

    async def joinSession(self, session_id: str, client_id: str) -> bool:
        async with self.managerLock:
            for session in self.sessionList:
                if session.sessionId == session_id:
                    session.clients[client_id] = len(session.clients)
                    return True

            return False
