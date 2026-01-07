import ffmpeg
import subprocess
import socket
from enum import Enum


ffmpegProcess = None


class Mode(Enum):
    SCREEN = 0
    VIDEO = 1


def ipcheck():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(('8.8.8.8', 1))
    ip = s.getsockname()[0]
    s.close()
    return ip


def start_streaming(mode: Mode, video_path: str):
    print(f"mode:{mode}, video:{video_path}")

    ip = ipcheck()  # Server IP address
    url = ""
    # TODO: MULTICAST_URL & PORT NUM Logic
    # = f"{MULTICAST_URL}?localaddr={ip}"

    if mode == Mode.SCREEN:
        # SCREEN MODE
        # TODO: 스크린 모드 추후 진행
        print("[SCREEN MODE]")

    elif mode == Mode.VIDEO:
        print("[VIDEO MODE]")
        inputStream = ffmpeg.input(video_path, re=None)

        # 출력 옵션 설정 (예시)
        stream = ffmpeg.output(
            inputStream,
            url,
            vcodec='libx264',               # H.264 인코딩
            preset='veryfast',              # 인코딩 속도 우선
            tune='zerolatency',             # 지연 시간 최소화
            video_bitrate='3000k',          # 화질 결정 (네트워크 상황에 따라 조절)
            g=30,                           # 키프레임 간격 (보통 1~2초 단위)
            bufsize='4000k',                # 버퍼 크기
            mpegts_flags='resend_headers',  # 스트림 헤더 정보 주기적 송신
            pat_peroid='0.1',               # PAT 정보 전송
            an=None,                        # 오디오 제거
            f='mpegts'                      # 멀티캐스트용 포맷
        )

        # 명령어 실행
        args = stream.get_args()   # Build command-line arguments to be passed to ffmpeg

        ffmpegProcess = subprocess.Popen(
            ['ffmpeg'] + args,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
            text=True,
            encoding='utf-8',  # 바이트를 문자열로 자동 변환
            errors='ignore'
        )

    print(f"[STREAM]   Start streaming!")
