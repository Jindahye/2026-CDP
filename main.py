import cv2
import time
from serial_interface import SerialCommInterface
from situation_evaluator import SituationEvaluator
from vision_perception import VisionPerception

def main():
    print("--- SafeCar Vision & Decision Node Start ---")
    
    # 시리얼 통신 연결
    serial_net = SerialCommInterface(port='/dev/ttyUSB0', baudrate=115200)
    evaluator = SituationEvaluator()
    vision = VisionPerception(hef_path="yolov8n.hef")

    # 카메라 연결 (가장 확실한 방법)
    # 0번이 안 되면 1번, 그것도 안 되면 V4L2 옵션을 붙이는 방식입니다.
    cap = cv2.VideoCapture(0, cv2.CAP_V4L2)

    if not cap.isOpened():
        print("[Error] 카메라를 열 수 없습니다. 0번 대신 1번으로 시도해보세요.")
        return

    print("[System] 카메라 연결 성공! 주행 로직을 시작합니다.")
    
    last_command = ""
    start_time = time.time()

    while True:
        ret, frame = cap.read()
        if not ret:
            print("[Error] 프레임을 읽을 수 없습니다.")
            break

        processed_frame, obstacle_detected = vision.process_frame(frame)
        bio_anomaly = (time.time() - start_time) > 10.0
        current_command = evaluator.evaluate(bio_anomaly, obstacle_detected)

        if current_command != last_command:
            serial_net.send_command(current_command)
            last_command = current_command
            print(f"[Run] 명령 송신: {current_command}")

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()