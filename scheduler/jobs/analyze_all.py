import logging
from datetime import datetime, timedelta, timezone
from service.threshold_service import (
    calculate_static_threshold,
    handle_successful_analysis,
    handle_failed_analysis
)
from service.sensor_service import update_sensor_state, get_sensor_list_by_state
from storage.local_storage import get_sensor_meta

# 한국 시간대 정의 (Asia/Seoul == UTC+9)
KST = timezone(timedelta(hours=9))

def analyze_all_sensors():
    logging.info("전체 센서 분석 시작")
    now = datetime.now(KST)

    try:
        sensors = get_sensor_list_by_state(["completed", "abandoned"])
    except Exception as e:
        logging.error(f"센서 목록 조회 실패: {e}", exc_info=True)
        return

    for sensor in sensors:
        sid = sensor.get("sensor_id", "UNKNOWN")
        try:
            gid = sensor["gateway_id"]
            stype = sensor["type_en_name"]

            meta = get_sensor_meta(gid, sid, stype)
            last_count = meta.get("last_data_count", 0)
            last_at_str = meta.get("last_analysis_at")

            # abandoned → pending 복구
            if sensor["sensor_status"] == "ABANDONED" and last_count > 0:
                update_sensor_state(gid, sid, stype, "pending")
                logging.info(f"[STATE] {sid} → pending (데이터 유입 확인)")
                continue

            # completed → 하루 경과한 경우만 재분석
            if last_at_str:
                last_at = datetime.fromisoformat(last_at_str).astimezone(KST)
                if now - last_at < timedelta(days=1):
                    continue

            # 재분석
            result = calculate_static_threshold(gid, sid, stype, duration="-7d")
            new_count = result.get("count", 0)

            if result["ready"]:
                handle_successful_analysis(gid, sid, stype, result)
            else:
                logging.warning(result)
                handle_failed_analysis(gid, sid, stype, new_count, result.get("reason"))

        except Exception as e:
            logging.error(f"{sid} 재분석 실패: {e}", exc_info=True)
