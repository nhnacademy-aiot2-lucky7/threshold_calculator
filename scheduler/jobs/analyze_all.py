from datetime import datetime, timedelta
from service.threshold_service import (
    calculate_threshold_with_prophet,
    handle_successful_analysis,
    handle_failed_analysis
)
from service.sensor_service import update_sensor_state, get_sensor_list_by_state
from storage.local_storage import get_sensor_meta

def analyze_all_sensors():
    print("[INFO] 전체 센서 분석 시작")
    now = datetime.now(datetime.timezone.utc)

    sensors = get_sensor_list_by_state(["completed", "abandoned"])

    for sensor in sensors:
        try:
            gid = sensor["gateway_id"]
            sid = sensor["sensor_id"]
            stype = sensor["sensor_type"]

            meta = get_sensor_meta(gid, sid, stype)
            last_count = meta.get("last_data_count", 0)
            last_at_str = meta.get("last_analysis_at")

            # ✅ abandoned → pending 복구 조건
            if sensor["state"] == "abandoned":
                if last_count > 0:
                    update_sensor_state(sid, "pending")
                    print(f"[STATE] {sid} → pending (데이터 유입 확인)")
                continue  # 복구된 센서는 pending 분석 대상에서 처리됨

            # ✅ completed → 하루 주기 재분석 여부
            if last_at_str:
                last_at = datetime.fromisoformat(last_at_str)
                if now - last_at < timedelta(days=1):
                    continue

            # ✅ 재분석 시도
            result = calculate_threshold_with_prophet(gid, sid, stype, duration="-1h")
            new_count = result.get("count", 0)

            if result["ready"]:
                handle_successful_analysis(gid, sid, stype, result)
            else:
                handle_failed_analysis(gid, sid, stype, new_count, result.get("reason"))

        except Exception as e:
            print(f"[ERROR] {sid} 재분석 실패: {str(e)}")