import cv2
import time

from serial_interface import SerialCommInterface
from situation_evaluator import SituationEvaluator
from vision_perception import VisionPerception

def get_bio_signal_from_team3():
    """
    [요청 사항] 팀원 3(STM32/ESP32)으로부터 생체 신호를 어떻게 받을지 구현해야 합니다.
    현재는 실차 테스트를 위해 10초 뒤 무조건 이상이 발생하도록 임시 처리했습니다.
    """
    return False 

def main():
    print("--- SafeCar Vision & Decision Node Start ---")
    
    can_net = CANCommInterface(channel='can0')
    evaluator = SituationEvaluator()
    vision = VisionPerception(hef_path="yolov8n_hailo8.hef")

    # C920 웹캠 연결 (포트 0 또는 1)
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    if not cap.isOpened():
        print("[Error] C920 카메라를 찾을 수 없습니다.")
        return

    last_command = ""
    start_time = time.time()

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # 1. 비전 처리 (차선 및 장애물)
        processed_frame, obstacle_detected = vision.process_frame(frame)

        # 2. 생체 신호 수신 (임시: 10초 후 이상 발생 시뮬레이션)
        bio_anomaly = (time.time() - start_time) > 10.0

        # 3. 상황 판단
        current_command = evaluator.evaluate(bio_anomaly, obstacle_detected)

        # 4. CAN 명령 송신 (상태가 변했을 때만 전송)
        if current_command != last_command:
            can_net.send_command(current_command)
            last_command = current_command

        # UI 출력
        cv2.putText(processed_frame, f"CMD: {current_command}", (10, 40), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 0, 0), 2)
        cv2.imshow("SafeCar - Team 1", processed_frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()