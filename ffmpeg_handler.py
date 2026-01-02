import ffmpeg  # ffmpeg-python 필요
from enum import Enum


class Mode(Enum):
    SCREEN = 0
    VIDEO = 1


def start_streaming(mode: Mode, video_path: str):
    print(f"mode:{mode}, video:{video_path}")
