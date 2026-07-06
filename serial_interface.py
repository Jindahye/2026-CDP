import serial
import time

class SerialCommInterface:
    def __init__(self, port='/dev/ttyUSB0', baudrate=115200):
        try:
            # 라즈베리파이 USB 시리얼 포트 연결 (MoonWalker 제어기)
            self.serial = serial.Serial(port, baudrate, timeout=1)
            print(f"[System] 모터 제어기 시리얼 통신 ({port}) 초기화 완료.")
        except serial.SerialException:
            print(f"[Error] 모터 제어기를 찾을 수 없습니다. {port} 연결을 확인하세요.")
            self.serial = None

    def send_command(self, command_type):
        if self.serial is None:
            return

        # 문워커 제어기로 보낼 데이터 (팀원과 프로토콜 협의 후 수정 필요)
        data_to_send = b''

        if command_type == "NORMAL":
            data_to_send = b'NORMAL\n' 
        elif command_type == "EMERGENCY_BRAKE":
            data_to_send = b'BRAKE\n'
        elif command_type == "MRM_PULL_OVER":
            data_to_send = b'MRM\n'

        try:
            self.serial.write(data_to_send)
            print(f"[TX] Command: {command_type} | Sent: {data_to_send}")
        except Exception as e:
            print(f"[Error] 메시지 전송 실패: {e}")