import can
import time

class CANCommInterface:
    def __init__(self, channel='can0', bitrate=500000):
        try:
            # 라즈베리파이 SocketCAN 인터페이스 연결
            self.bus = can.interface.Bus(channel=channel, bustype='socketcan', bitrate=bitrate)
            print(f"[System] CAN Bus ({channel}) 초기화 완료.")
        except OSError:
            print(f"[Error] CAN 보드를 찾을 수 없습니다. {channel} 인터페이스를 확인하세요.")
            self.bus = None

    def send_command(self, command_type):
        if self.bus is None:
            return

        # CAN ID 및 데이터 페이로드 정의 (팀원 2와 협의된 규격 적용 필요)
        can_id = 0x000
        data = [0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]

        if command_type == "NORMAL":
            can_id = 0x100
            data[0] = 0x01 # 주행 유지 플래그
        elif command_type == "EMERGENCY_BRAKE":
            can_id = 0x101
            data[0] = 0x02 # 급제동 플래그
        elif command_type == "MRM_PULL_OVER":
            can_id = 0x102
            data[0] = 0x03 # 갓길 대피 플래그

        msg = can.Message(arbitration_id=can_id, data=data, is_extended_id=False)
        
        try:
            self.bus.send(msg)
            print(f"[CAN TX] ID: {hex(can_id)} | Command: {command_type}")
        except can.CanError:
            print("[CAN Error] 메시지 전송 실패")