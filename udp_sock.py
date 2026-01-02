import socket
import logging


def run_udp_server(host: str = "0.0.0.0", port: int = 65535):

    # FastAPI 프로세스에서 UDP 서버의 로그 출력을 위한 로거 획득
    logging.basicConfig(level=logging.INFO,
                        format="%(asctime)s [%(levelname)s] %(message)s")
    logger = logging.getLogger("UDP_Server")

    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as udp_server_sock:
            # set socket option REUSEADDR
            udp_server_sock.setsockopt(
                socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

            try:
                udp_server_sock.bind((host, port))
            except PermissionError:
                logger.error(f"Permission denied: Cannot use port {port}.")
                return
            except OSError as e:
                logger.error(f"bind() error: {e}")
                return

            recvPacket(udp_server_sock, logger)

    except Exception as e:
        logger.critical(f"UDP Server error: {e}")


def recvPacket(sock: socket.socket, logger: logging.Logger):
    while True:
        try:
            data, addr = sock.recvfrom(100)
            handlePacket(sock, data, addr, logger)
        except Exception as e:
            logger.error(f"Packet error: {e}")


def handlePacket(sock: socket.socket, data: bytes, addr, logger: logging.Logger):
    try:
        message = data.decode("utf-8").strip()
    except UnicodeDecodeError:
        logger.warning(f"data format is not utf-8. addr:{addr}")
        return

    if message == "VIDEO_WALL_CONNECT_REQUEST":
        sock.sendto("VIDEO_WALL_CONNECT_RESPONSE", addr)
        logger.info(f"Responded to {addr}")
