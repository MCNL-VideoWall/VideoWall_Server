from typing import Dict, List

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

    def createSession(self, hostId: int, name: str) -> Session:
        newSession = Session(sessionId=hostId, sessionName=name)
        self.sessionList.append(newSession)
        return newSession

    def getSessionList(self):
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
