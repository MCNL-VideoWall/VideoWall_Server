import socket
import logging


def run_udp_server(host: str = "0.0.0.0", port: int = 65535):

    # FastAPI 프로세스에서 UDP 서버의 로그 출력을 위한 로거 획득
    logging.basicConfig(level=logging.INFO,
                        format="%(asctime)s [%(levelname)s] %(message)s")
    logger = logging.getLogger("UDP_Server")

    udp_server_sock = socket.socket(
        family=socket.AF_INET,
        type=socket.SOCK_DGRAM
    )

    udp_server_sock.bind((host, port))

    while True:
        data, addr = udp_server_sock.recvfrom(100)

        if data.decode().strip() == "VIDEO_WALL_CONNECT_REQUEST":
            udp_server_sock.sendto(
                "VIDEO_WALL_CONNECT_RESPONSE".encode(), addr)
