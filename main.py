import cv2
import time
from serial_interface import SerialCommInterface
from situation_evaluator import SituationEvaluator
from vision_perception import VisionPerception

def main():
    print("--- SafeCar Vision & Decision Node Start ---")
    
    # 1. 시리얼 통신 초기화
    serial_net = SerialCommInterface(port='/dev/ttyUSB0', baudrate=115200)
    evaluator = SituationEvaluator()
    vision = VisionPerception(hef_path="yolov8n.hef")

    # 2. 라즈베리파이 카메라 하드웨어 최적화 연결
    # GStreamer 파이프라인을 통해 하드웨어 가속을 직접 사용합니다.
    pipeline = "libcamerasrc ! video/x-raw, width=640, height=480, framerate=30/1 ! videoconvert ! appsink"
    cap = cv2.VideoCapture(pipeline, cv2.CAP_GSTREAMER)

    # 3. 만약 GStreamer 연결 실패 시 V4L2 표준 모드로 안전하게 재시도
    if not cap.isOpened():
        print("[System] GStreamer 연결 실패, V4L2 모드로 전환합니다.")
        cap = cv2.VideoCapture(0, cv2.CAP_V4L2)
        cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))

    if not cap.isOpened():
        print("[Error] 최종적으로 카메라를 열 수 없습니다. 하드웨어 연결을 다시 확인하세요.")
        return

    print("[System] 카메라 연결 성공! 주행 로직을 시작합니다.")
    
    last_command = ""
    start_time = time.time()

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                print("[Error] 프레임을 읽어올 수 없습니다.")
                break

            # 비전 처리
            processed_frame, obstacle_detected = vision.process_frame(frame)
            
            # 생체 신호 시뮬레이션
            bio_anomaly = (time.time() - start_time) > 10.0

            # 상황 판단 및 제어
            current_command = evaluator.evaluate(bio_anomaly, obstacle_detected)

            # 시리얼 통신 전송
            if current_command != last_command:
                serial_net.send_command(current_command)
                last_command = current_command
                print(f"[Run] 명령 송신: {current_command}")

            # 'q' 키 입력 시 종료
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    except KeyboardInterrupt:
        print("[System] 사용자에 의해 강제 종료됩니다.")
    finally:
        cap.release()
        cv2.destroyAllWindows()
        print("[System] 리소스를 정리하고 종료합니다.")

if __name__ == "__main__":
    main()