class SituationEvaluator:
    def __init__(self):
        print("[System] Situation Evaluator 초기화 완료.")

    def evaluate(self, bio_anomaly, obstacle_detected):
        # 1. 운전자 상태 정상
        if not bio_anomaly:
            return "NORMAL"
        
        # 2. 운전자 이상 발생 시: 전방 상황에 따른 페일세이프(MRM) 이중 개입
        if obstacle_detected:
            return "EMERGENCY_BRAKE"  # 현 차선 급제동 (장애물 있음)
        else:
            return "MRM_PULL_OVER"    # 우측 갓길 대피 (공간 확보됨)