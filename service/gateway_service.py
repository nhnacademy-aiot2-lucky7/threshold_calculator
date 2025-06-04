import logging
import requests
from config import config

gateway_url = config.GATEWAY_SERVICE_URL

# 모든 게이트웨이 id 조회
def get_all_gateway_id():
    try:
        response = requests.get(f"{gateway_url}/gateways/ids")
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logging.error(f"[ERROR] get_all_gateway_id 실패: {e}", exc_info=True)
        return []

