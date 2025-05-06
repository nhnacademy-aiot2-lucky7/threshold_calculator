from scheduler.base_scheduler import run_scheduler
import logging

logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("threshold.log"),
        logging.StreamHandler()
    ]
)

if __name__ == "__main__":
    run_scheduler()