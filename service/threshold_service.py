import pandas as pd
import numpy as np
import logging
from prophet import Prophet
from service.influx_service import get_sensor_data_count, get_sensor_values_with_time
from config.config import MIN_REQUIRED_COUNT
from storage.local_storage import set_sensor_meta, get_sensor_meta
from service.sensor_service import update_sensor_state, save_result, get_recent_thresholds

def calculate_threshold_with_prophet(gateway_id, sensor_id, sensor_type, duration="-1d"):
    count = get_sensor_data_count(gateway_id, sensor_id, sensor_type)

    if count < MIN_REQUIRED_COUNT:
        return {"ready": False, "reason": f"데이터 부족: {count}개 (최소 {MIN_REQUIRED_COUNT}개 필요)", "count": count}

    records = get_sensor_values_with_time(gateway_id, sensor_id, sensor_type, duration)
    if not records:
        return {"ready": False, "reason": "데이터는 있으나 값 추출 실패", "count" : count}

    df = pd.DataFrame(records)
    df.rename(columns={"time": "ds", "value": "y"}, inplace=True)


    df['ds'] = pd.to_datetime(df['ds']).dt.tz_localize(None)

    model = Prophet()
    model.fit(df)
    future = model.make_future_dataframe(periods=0)
    forecast = model.predict(future)
    last = forecast.iloc[-1]

    threshold_min = round(last["yhat_lower"], 2)
    threshold_max = round(last["yhat_upper"], 2)
    threshold_avg = round(last["yhat"], 2)

    previous = get_recent_thresholds(gateway_id, sensor_id, sensor_type, limit=5)
    if previous:
        delta_min = round(threshold_min - np.mean([p["threshold_min"] for p in previous]), 2)
        delta_max = round(threshold_max - np.mean([p["threshold_max"] for p in previous]), 2)
        delta_avg = round(threshold_avg - np.mean([p["threshold_avg"] for p in previous]), 2)

        min_range_min = round(np.min([p["threshold_min"] for p in previous]), 2)
        min_range_max = round(threshold_min + np.std([p["threshold_min"] for p in previous]), 2)

        max_range_min = round(threshold_max - np.std([p["threshold_max"] for p in previous]), 2)
        max_range_max = round(np.max([p["threshold_max"] for p in previous]), 2)

        avg_std = np.std([p["threshold_avg"] for p in previous])
        avg_range_min = round(threshold_avg - avg_std, 2)
        avg_range_max = round(threshold_avg + avg_std, 2)
    else:
        delta_min = delta_max = delta_avg = 0.0
        min_range_min = threshold_min
        min_range_max = threshold_min + 1.0
        max_range_min = threshold_max - 1.0
        max_range_max = threshold_max
        avg_range_min = threshold_avg - 0.5
        avg_range_max = threshold_avg + 0.5

    return {
        "ready": True,
        "threshold":{
            "min": threshold_min,
            "max": threshold_max,
            "avg": threshold_avg
        },
        "min_range":{
            "min": min_range_min,
            "max": min_range_max
        },
        "max_range":{
            "min": max_range_min,
            "max": max_range_max
        },
        "avg_range":{
            "min": avg_range_min,
            "max": avg_range_max
        },
        "diff":{
            "min":delta_min,
            "max":delta_max,
            "avg":delta_avg
        },
        "data_count": count
    }

# 분석 성공 처리
def handle_successful_analysis(gateway_id: str, sensor_id: str, sensor_type: str, result: dict):
    save_result(gateway_id, sensor_id, sensor_type, result)
    update_sensor_state(gateway_id, sensor_id, sensor_type, "completed")
    set_sensor_meta(gateway_id, sensor_id, sensor_type, result.get("count", 0), 0)
    logging.info(f"[OK] {sensor_id} 분석 완료")

# 분석 실패 처리
def handle_failed_analysis(gateway_id: str, sensor_id: str, sensor_type: str, new_count: int, reason: str):
    meta = get_sensor_meta(gateway_id, sensor_id, sensor_type)
    last_count = meta.get("last_data_count")
    fail_count = meta.get("fail_count", 0)

    if last_count is not None and new_count == last_count:
        fail_count += 1
    else:
        fail_count = 0

    set_sensor_meta(gateway_id, sensor_id, sensor_type, new_count, fail_count)
    logging.warning(f"[handle_failed_analysis (new count) = {new_count}]")

    if fail_count >= 5 or new_count == 0:
        update_sensor_state(gateway_id, sensor_id, sensor_type, "abandoned")
        logging.warning(f"[ABANDON] {sensor_id} → abandoned (fail_count={fail_count})")
    else:
        logging.warning(f"[SKIP] {sensor_id} 분석 실패: {reason} (fail_count={fail_count})")
