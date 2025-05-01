import requests

def notify_rule_engine(gateway_id):
    payload = {
        "gateway_id": gateway_id,
        "status": "threshold_ready"
    }
    response = requests.post("http://rule-engine/api/webhook/threshold-complete", json=payload)
    print(f"[WEBHOOK] ruleEngine 통보 완료: {response.status_code}")