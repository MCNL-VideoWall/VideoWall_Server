import cv2
import numpy as np
from typing import Dict, Tuple
from enum import Enum
import logging
from fastapi import WebSocket


class Color(Enum):
    RED = (0, 0, 255)
    GREEN = (0, 255, 0)
    YELLOW = (0.255, 255)


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

            marker_count = len(ids) if ids is not None else 0  # len(ids) | 0
            detected_ids = set(ids.flatten()) if ids is not None else set()

            status_text = f"Found {marker_count} / {len(marker_ids)} markers"

            color = Color.RED.value  # 폰트 색상

            # Marker 개수 검증
            if marker_count == len(marker_ids):
                # ID가 일치하는 지 set 검증
                if detected_ids == marker_ids:
                    status_text = "SUCCESS: All marker detected"
                    color = Color.GREEN.value
                else:
                    status_text = "FAIL: Wrong markers detected"
                    color = Color.YELLOW.value

    except ConnectionError as e:
        logger.error(f"{e}")
    except RuntimeError as e:
        logger.error(f"{e}")


def capture_marker(session: Dict[int, any]):
    targets = sorted(list(session.keys()))
    # 인식할 마커 개수
    print(f"[CAPTURE_MARKER]  WebCam 실행 : Find {len(targets)} markers..")
    print(f"          Marker ID: {targets}")

    cap = cv2.VideoCapture(0)   # PC 연결 WebCam 열기
    if not cap.isOpened():
        print("[ERROR]  Failed to open camera..")
        return None, None, None

    # ArUco 검출기 설정
    aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_6X6_250)
    aruco_params = cv2.aruco.DetectorParameters()
    detector = cv2.aruco.ArucoDetector(aruco_dict, aruco_params)

    captured_frame, final_corners, final_ids = None, None, None

    while True:
        cur_ids = set(session.keys())
        if not cur_ids:
            print("[ERROR]  Stop Capturing..")
            break

        retrieve, frame = cap.read()    # retrieve: 상태 값, frame: data
        if not retrieve:
            break

        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        corners, ids, _ = detector.detectMarkers(gray_frame)

        marker_count = len(ids) if ids is not None else 0
        status_text = f"Found {marker_count} / {len(cur_ids)} markers"
        color = (0, 0, 255)  # default Red : 준비 안됨

        # 검증 로직
        if marker_count == len(cur_ids):
            found_ids = set(ids.flatten())

            if found_ids == cur_ids:
                status_text = "All markers detected."
                color = (0, 255, 0)  # Green : 성공

                cv2.putText(frame, status_text, (10, 30),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
                cv2.imshow('Auto Capture & Validation System', frame)
                cv2.waitKey(500)

                captured_frame = frame.copy()
                final_corners = corners
                final_ids = ids
                break
            else:
                status_text = "Mismatch.. Adjusting.."
                color = (0, 255, 255)  # Yellow  : 주의 / 확인 필요

        # 화면 표시
        cv2.putText(frame, status_text, (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
        cv2.imshow('Auto Capture & Validation System', frame)

        # key handle
        key = cv2.waitKey(1) & 0xFF
        if key == 27:           # ESC
            break
        elif key == ord(' '):   # SPACE : 강제 캡처
            captured_frame = frame.copy()
            final_corners = corners
            final_ids = ids
            break

    cap.release()
    cv2.destroyAllWindows()
    return captured_frame, final_corners, final_ids


def analyze_marker(frames, corners, ids):
    print("[ANALYZE_MARKER]  START.")

    if ids is None or len(ids) == 0:
        print("[ERROR]  No markers..")
        return None

    # save marker and corner information
    markers_info = []
    corners_list = []
    for i, marker_id in enumerate(ids):
        marker_corners = corners[i][0]
        markers_info.append({
            'id': int(marker_id[0]),
            'corners': marker_corners
        })
        corners_list.append(marker_corners)

    # STEP 1 : 2D 전체 경계 상자 계산
    try:
        all_points = np.vstack(corners_list)
        total_min_x = np.min(all_points[:, 0])
        total_min_y = np.min(all_points[:, 1])
        total_max_x = np.max(all_points[:, 0])
        total_max_y = np.max(all_points[:, 1])
    except ValueError:
        print("[ERROR]  No marker information..")
        return None

    total_wall_width = total_max_x - total_min_x
    total_wall_height = total_max_y - total_min_y

    if total_wall_width == 0 or total_wall_height == 0:
        print("[ERROR]  The area is zero..")
        return None

    wall_aspect_ratio = float(total_wall_width / total_wall_height)
    print(f"{total_wall_width}x{total_wall_height} (Ratio: {wall_aspect_ratio:.2f})")

    # STEP 2 : 모서리 좌표 게산
    layout = []

    for info in markers_info:

        normalized_corners = []
        for point in markers_info['corners']:

            # X, Y 정규화
            norm_x = (point[0] - total_min_x) / total_wall_width
            norm_y = (point[1] - total_min_y) / total_wall_height

            # Y축 불일치 해결
            flipped_norm_y = 1.0 - norm_y

            normalized_corners.append(
                {'x': float(norm_x), 'y': float(flipped_norm_y)})

        layout.append({
            "id": info['id'],
            "relative_corners": normalized_corners
        })

    json_file = {"layout": layout, "wall_aspect_ratio": wall_aspect_ratio}
    print("Analyze complete")

    return json_file


def getArucoList(marker_id: int, size: int = 8):
    dictionary = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_6X6_250)

    marker_img = cv2.aruco.generateImageMarker(dictionary, marker_id, size)

    # list 변환
    raw_list = marker_img.tolist()
    bitmap_list = [[1 if pixel > 128 else 0 for pixel in row]
                   for row in raw_list]

    return bitmap_list
