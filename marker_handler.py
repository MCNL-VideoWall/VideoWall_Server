import cv2
from typing import Dict


def capture_marker(session: Dict[int, any]):
    targets = sorted(list(session.keys()))
    # 인식할 마커 개수
    print(f"[CAPTURE_MARKER] WebCam 실행 : Find {len(targets)} markers..")
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
        color = (0, 0, 255) # default Red : 준비 안됨

        # 검증 로직
        if marker_count == len(cur_ids):
            found_ids = set(ids.flatten())

            if found_ids == cur_ids:
                status_text = "All markers detected."
                color = (0, 255, 0) # Green : 성공

                cv2.putText(frame, status_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
                cv2.imshow('Auto Capture & Validation System', frame)
                cv2.waitKey(500) 

                captured_frame = frame.copy()
                final_corners = corners
                final_ids = ids
                break
            else:
                status_text = "Mismatch.. Adjusting.."
                color = (0, 255, 255) # Yellow  : 주의 / 확인 필요
        
        # 화면 표시
        cv2.putText(frame, status_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
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
        