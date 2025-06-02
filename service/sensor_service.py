from datetime import datetime, timezone, timedelta
import logging
import requests
from typing import List, Optional, Union
from config import config

VALID_STATES = {"pending", "completed", "abandoned"}

sensor_url = config.SENSOR_SERVICE_URL
gateway_url = config.GATEWAY_SERVICE_URL

# 과거 임계치 조회
def get_recent_thresholds(gateway_id, sensor_id, sensor_type, limit=5):
    url = f"{sensor_url}/threshold-histories/gateway-id/{gateway_id}/sensor-id/{sensor_id}/type-en-name/{sensor_type}/limit/{limit}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logging.error(f"[ERROR] get_recent_thresholds 실패: {e}", exc_info=True)
        return []

# 임계치 계산 결과 저장
def save_result(gateway_id, sensor_id, sensor_type, result):
    filtered_result = {k: v for k, v in result.items() if k != "ready"}

    payload = {
            "sensor_info":{
            "gateway_id": gateway_id,
            "sensor_id": sensor_id,
            "type_en_name": sensor_type,
        },
        **filtered_result,
        "calculated_at": int(datetime.now(timezone(timedelta(hours=9))).timestamp() * 1000),
    }
    try:
        response = requests.post(f"{sensor_url}/threshold-histories", json=payload)
        response.raise_for_status()
        logging.info(f"[POST] 저장 성공: {response.status_code}")
    except requests.exceptions.RequestException as e:
        logging.error(f"[ERROR] save_result 실패: {e}", exc_info=True)

# 모든 게이트웨이 id 조회
def get_all_gateway_id():
    try:
        response = requests.get(f"{gateway_url}/gateways/ids")
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logging.error(f"[ERROR] get_all_gateway_id 실패: {e}", exc_info=True)
        return []

# 상태에 따른 센서 정보 조회
def get_sensor_list_by_state(state: Optional[Union[str, List[str]]] = None) -> list:
    if isinstance(state, list):
        invalid = [s for s in state if s not in VALID_STATES]
        if invalid:
            raise ValueError(f"Invalid state(s): {invalid}")
        params = [("status", s) for s in state]
    elif isinstance(state, str):
        if state not in VALID_STATES:
            raise ValueError(f"Invalid state: {state}")
        params = {"status": state}
    else:
        params = {}

    try:
        response = requests.get(f"{sensor_url}/sensor-data-mappings/search-status", params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logging.error(f"[ERROR] get_sensor_list_by_state 실패: {e}", exc_info=True)
        return []

# gateway Id에 따른 센서 정보 조회
def get_sensor_list_by_gateway_id(gateway_id):
    try:
        response = requests.get(f"{sensor_url}/sensor-data-mappings/{gateway_id}/sensors")
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logging.error(f"[ERROR] get_sensor_list_by_gateway_id 실패: {e}", exc_info=True)
        return []

# 센서 state update
def update_sensor_state(gateway_id, sensor_id, sensor_type, state):
    url = f"{sensor_url}/sensor-data-mappings"
    payload = {
        "gateway_id": gateway_id,
        "sensor_id": sensor_id,
        "type_en_name": sensor_type,
        "status": state
        }
    try:
        response = requests.put(url, json=payload)
        response.raise_for_status()
        logging.info(f"[STATE] {sensor_id} 상태 → {state} 변경 성공 ({response.status_code})")
    except requests.exceptions.RequestException as e:
        logging.error(f"[ERROR] update_sensor_state 실패: {e}", exc_info=True)
