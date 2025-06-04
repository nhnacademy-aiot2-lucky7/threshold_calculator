from scheduler.base_scheduler import run_scheduler
import logging
import os

log_path = "logs/threshold-calculator.log"
os.makedirs(os.path.dirname(log_path), exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_path),
        logging.StreamHandler()
    ]
)

if __name__ == "__main__":
    run_scheduler()