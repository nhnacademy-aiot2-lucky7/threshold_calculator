import time
import schedule
import logging
from threading import Thread
from scheduler.jobs.analyze_pending import analyze_pending_sensors
from scheduler.jobs.analyze_all import analyze_all_sensors
from config import config

initAnalysisDuration = config.INIT_ANALYSIS_DURATION

def run_async(job_func):
    t = Thread(target=job_func)
    t.daemon = True  # 종료 시 강제 kill 가능
    t.start()

def run_scheduler():
    logging.info("[SCHEDULER] pending 분석: 1시간마다 실행 예약됨")
    schedule.every(initAnalysisDuration).minutes.do(lambda: run_async(analyze_pending_sensors))

    logging.info("[SCHEDULER] 전체 분석: 매일 02:00 실행 예약됨")
    schedule.every().day.at("02:00").do(lambda: run_async(analyze_all_sensors))

    logging.info("[SCHEDULER] 스케줄러 시작됨")

    while True:
        schedule.run_pending()
        time.sleep(1)
