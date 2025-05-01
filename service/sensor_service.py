import datetime
import requests
from typing import List, Optional, Union

# 과거 임계치 조회
def get_recent_thresholds(gateway_id, sensor_id, sensor_type, limit=5):
    # TODO: storage-service 연동해서 과거 임계치 가져오기
    return []  # 초기에는 빈 리스트 반환

# 임계치 계산 결과 저장
def save_result(gateway_id, sensor_id, sensor_type, result):
    payload = {
        "gateway_id": gateway_id,
        "sensor_id": sensor_id,
        "sensor_type": sensor_type,
        "calculated_at": datetime.now(datetime.timezone.utc).isoformat(),
        **result
    }
    response = requests.post("http://storage-service/api/threshold", json=payload)
    print(f"[POST] 저장 결과: {response.status_code}")

# 모든 게이트웨이 id 조회
def get_all_gateway_id():
    response = requests.get(f"http://sensor-service/gateways")
    response.raise_for_status()
    return response.json()

# 상태에 따른 센서 정보 조회
VALID_STATES = {"pending", "completed", "abandoned"}

def get_sensor_list_by_state(state: Optional[Union[str, List[str]]] = None) -> list:
    if isinstance(state, list):
        invalid = [s for s in state if s not in VALID_STATES]
        if invalid:
            raise ValueError(f"Invalid state(s): {invalid}")
        params = [("state", s) for s in state]
    elif isinstance(state, str):
        if state not in VALID_STATES:
            raise ValueError(f"Invalid state: {state}")
        params = {"state": state}
    else:
        params = {}

    response = requests.get("http://sensor-service/sensors", params=params)
    response.raise_for_status()
    return response.json()

# gateway Id에 따른 센서 정보 조회
def get_sensor_list_by_gateway_id(gateway_id):
    response = requests.get(f"http://sensor-service/gateways/{gateway_id}/sensons")
    response.raise_for_status()
    return response.json()

# 센서 state update
def update_sensor_state(gateway_id, sensor_id, sensor_type, state):
    url = f"http://sensor-service/gateways/{gateway_id}/sensors/{sensor_id}/types/{sensor_type}"
    payload = {"state": state}

    try:
        response = requests.patch(url, json=payload)
        response.raise_for_status()
        print(f"[STATE] {sensor_id} 상태 → {state} 변경 성공 ({response.status_code})")
    except requests.exceptions.RequestException as e:
        print(f"[ERROR] {sensor_id} 상태 변경 실패: {e}")