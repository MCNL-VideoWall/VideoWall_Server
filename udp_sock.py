import socket

BRDCAST_ADDR = "0.0.0.0"
PORT = 65535

udp_server_sock = socket.socket(
    family=socket.AF_INET,
    type=socket.SOCK_DGRAM
)
