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

    except Exception as e:
        logger.critical(f"UDP Server error: {e}")

        # udp_server_sock.bind((host, port))

        # while True:
        #     data, addr = udp_server_sock.recvfrom(100)

        #     if data.decode().strip() == "VIDEO_WALL_CONNECT_REQUEST":
        #         udp_server_sock.sendto(
        #             "VIDEO_WALL_CONNECT_RESPONSE".encode(), addr)
