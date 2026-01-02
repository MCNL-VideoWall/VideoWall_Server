from fastapi import WebSocket
from typing import Dict

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
