import requests
import logging
from config import config

gateway_url = config.GATEWAY_SERVICE_URL

def notify_rule_engine(gateway_id):
    try:
        response = requests.put(f"{gateway_url}/gateways/threshold-status", json=gateway_id)
        response.raise_for_status()
        logging.info(f"[WEBHOOK] gateway-service update threshold status 통보 완료: {response.status_code}")
    except requests.exceptions.RequestException as e:
        logging.error(f"[ERROR] gateway-service update threshold status 통보 실패: {e}", exc_info=True)