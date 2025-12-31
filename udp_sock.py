import socket


def run_udp_server(host: str = "0.0.0.0", port: int = 65535):
    udp_server_sock = socket.socket(
        family=socket.AF_INET,
        type=socket.SOCK_DGRAM
    )

    udp_server_sock.bind((BRDCAST_ADDR, PORT))

    while True:
        data, addr = udp_server_sock.recvfrom(100)

        if data.decode().strip() == "VIDEO_WALL_CONNECT_REQUEST":
            udp_server_sock.sendto(
                "VIDEO_WALL_CONNECT_RESPONSE".encode(), addr)
