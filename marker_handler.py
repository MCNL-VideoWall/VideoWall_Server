import cv2
import numpy as np
from typing import Tuple, Set
from enum import Enum
import logging
from fastapi import WebSocket


class Color(Enum):
    RED = (0, 0, 255)
    GREEN = (0, 255, 0)
    YELLOW = (0.255, 255)


class ArucoDetector:
    def __init__(self, dictionary=cv2.aruco.DICT_6X6_250):
        self.detector = cv2.aruco.ArucoDetector(
            cv2.aruco.getPredefinedDictionary(dictionary),
            cv2.aruco.DetectorParameters()
        )

    def detectFrame(self, frame_gray) -> Tuple[list, np.ndarray, Set[int]]:
        corners, ids, _ = self.detector.detectMarkers(frame_gray)
        detected_ids = set(ids.flatten()) if ids is not None else set()
        return corners, ids, detected_ids


def draw_status(frame, text, color=Color.GREEN.value):
    cv2.putText(frame, text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)


def captureMarker(expected_ids: set):
    # FastAPI 프로세스에서 ArUco마커 캡쳐 흐름의 로그 출력을 위한 로거 획득
    logging.basicConfig(level=logging.INFO,
                        format="%(asctime)s [%(levelname)s] %(message)s")
    logger = logging.getLogger("Capture_ArUco")

    logger.info(f"WebCam 실행")

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        logger.error("Camera not found")

    try:
        detector = cv2.aruco.ArucoDetector(
            cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_6X6_250),
            cv2.aruco.DetectorParameters())

        layout_data = None

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            corners, ids, _ = detector.detectMarkers(gray_frame)

            detected_ids = set(ids.flatten()) if ids is not None else set()

            # 모든 마커가 일치
            if detected_ids == expected_ids:
                layout_data = run_analysis(corners, ids)

                draw_status(frame, "ALL DETECTED", Color.GREEN.value)
                cv2.imshow("Calibration", frame)
                cv2.waitKey(1000)
                break
            else:
                draw_status(
                    frame,
                    f"Searching {len(detected_ids)} / {len(expected_ids)} markers",
                    Color.RED.value
                )
                cv2.imshow("Calibration", frame)

            if (cv2.waitKey(1) & 0xFF) == 27:           # ESC
                break

        cap.release()
        cv2.destroyAllWindows()
        return layout_data

    except ConnectionError as e:
        logger.error(f"{e}")
    except RuntimeError as e:
        logger.error(f"{e}")


def run_analysis(corners, ids):
    corners_list = [c[0] for c in corners]
    all_points = np.vstack(corners_list)

    min_x, min_y = np.min(all_points[:, 0]), np.min(all_points[:, 1])
    max_x, max_y = np.max(all_points[:, 0]), np.max(all_points[:, 1])
    width, height = max_x - min_x, max_y - min_y

    layout = []
    for i, m_id in enumerate(ids):
        # 개별 마커의 4개 모서리 정규화 (Y축 반전 포함)
        norm_corners = []
        for p in corners[i][0]:
            norm_corners.append({
                'x': float((p[0] - min_x) / width),
                'y': float(1.0 - (p[1] - min_y) / height)
            })

        layout.append({
            "id": int(m_id[0]),
            "relative_corners": norm_corners
        })

    return {
        "layout": layout,
        "wall_aspect_ratio": float(width / height)
    }


def getArucoList(marker_id: int, size: int = 8):
    dictionary = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_6X6_250)

    marker_img = cv2.aruco.generateImageMarker(dictionary, marker_id, size)

    # list 변환
    raw_list = marker_img.tolist()
    bitmap_list = [[1 if pixel > 128 else 0 for pixel in row]
                   for row in raw_list]

    return bitmap_list
