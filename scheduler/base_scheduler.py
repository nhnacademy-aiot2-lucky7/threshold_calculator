import time
import schedule
from threading import Thread
from jobs.analyze_pending import analyze_pending_sensors
from jobs.analyze_all import analyze_all_sensors

def run_async(job_func):
    t = Thread(target=job_func)
    t.daemon = True  # 종료 시 강제 kill 가능
    t.start()

def run_scheduler():
    # 최초 분석 대상: 1시간마다 실행
    schedule.every(1).hours.do(lambda: run_async(analyze_pending_sensors))

    # 전체 분석 대상: 매일 새벽 2시에 실행
    schedule.every().day.at("02:00").do(lambda: run_async(analyze_all_sensors))

    print("[INFO] 스케줄러 시작됨")

    while True:
        schedule.run_pending()
        time.sleep(1)