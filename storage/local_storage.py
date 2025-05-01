from datetime import datetime

# 센서별 메타 정보 저장용 전역 딕셔너리
sensor_meta = {}

# 게이트웨이 통보 이력 캐시
notified_gateways = set()

# 센서 key 생성
def _build_key(gateway_id: str, sensor_id: str, sensor_type: str) -> str:
    return f"{gateway_id}:{sensor_id}:{sensor_type}"

# 센서 메타 정보 조회
def get_sensor_meta(gateway_id: str, sensor_id: str, sensor_type: str) -> dict:
    key = _build_key(gateway_id, sensor_id, sensor_type)
    return sensor_meta.get(key, {})

# 센서 메타 정보 저장/업데이트
def set_sensor_meta(gateway_id: str, sensor_id: str, sensor_type: str, data_count: int, fail_count: int):
    key = _build_key(gateway_id, sensor_id, sensor_type)
    sensor_meta[key] = {
        "last_data_count": data_count,
        "fail_count": fail_count,
        "last_analysis_at": datetime.now(datetime.timezone.utc).isoformat()
    }

# 게이트웨이 활성화 이력 조회
def is_gateway_notified(gateway_id: str) -> bool:
    return gateway_id in notified_gateways

# 게이트웨이 활성화 이력 저장
def mark_gateway_as_notified(gateway_id: str):
    notified_gateways.add(gateway_id)