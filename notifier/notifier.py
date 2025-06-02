import requests
import logging
from config import config

ruleEngineUrl = config.RULE_ENGINE_URL

def notify_rule_engine(gateway_id):
    payload = {
        "gateway_id": gateway_id,
        "status": "threshold_ready"
    }
    try:
        response = requests.post(f"http://{ruleEngineUrl}/rule_engine/webhook/threshold_complete", json=payload)
        response.raise_for_status()
        logging.info(f"[WEBHOOK] ruleEngine 통보 완료: {response.status_code}")
    except requests.exceptions.RequestException as e:
        logging.error(f"[ERROR] ruleEngine 통보 실패: {e}", exc_info=True)