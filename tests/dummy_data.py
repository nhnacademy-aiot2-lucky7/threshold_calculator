
from datetime import datetime, timedelta
import pandas as pd

def get_dummy_sensor_list(state="pending"):
    return [
        {
            "gateway_id": "G1",
            "sensor_id": "TEMP-01",
            "sensor_type": "temperature",
            "state": state
        },
        {
            "gateway_id": "G1",
            "sensor_id": "HUM-01",
            "sensor_type": "humidity",
            "state": state
        },
        {
            "gateway_id": "G2",
            "sensor_id": "CO2-01",
            "sensor_type": "co2",
            "state": state
        }
    ]

def get_dummy_gateway_list():
    return ["G1", "G2"]

def get_dummy_influx_data(num_points=60):
    now = datetime.now(datetime.timezone.utc)
    return pd.DataFrame([
        {"time": now - timedelta(minutes=i), "value": 20 + i * 0.1}
        for i in range(num_points)
    ])

def get_dummy_analysis_result():
    return {
        "ready": True,
        "count": 60,
        "threshold_min": 18.5,
        "threshold_max": 25.7,
        "threshold_avg": 22.1,
        "min_range_min": 17.0,
        "min_range_max": 19.0,
        "max_range_min": 24.0,
        "max_range_max": 26.0,
        "avg_range_min": 21.5,
        "avg_range_max": 22.7,
        "min_diff": 0.3,
        "max_diff": 0.1,
        "avg_diff": 0.0
    }

def get_dummy_analysis_fail_reason_data_count():
    return {
        "ready": False,
        "reason": "데이터 부족: 20개 (최소 30개 필요)"
    }

def get_dummy_analysis_fail_reason_invalid_data():
    return {
        "ready": False,
        "reason": "데이터는 있으나 값 추출 실패"
    }