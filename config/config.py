import os

MIN_REQUIRED_COUNT = os.getenv("MIN_REQUIRED_COUNT", 100)
INIT_ANALYSIS_DURATION = os.getenv("INIT_ANALYSIS_DURATION", 60)

INFLUXDB_URL = os.getenv("INFLUXDB_URL", "https://influx.luckyseven.live")
INFLUXDB_TOKNE = os.getenv("INFLUXDB_TOKEN", "4H10inTByRRj7JjoPZV_DP77rVhrrS7oN5QtOGCmU0ODs6LzeRaCgtL4_0ApNPzn4irvzNrE8Hp61kVNptNOzQ==")
INFLUXDB_ORG = os.getenv("INFLUXDB_ORG", "my-org")
INFLUXDB_BUCKET = os.getenv("INFLUXDB_BUCKET", "temporary-data-handler")

SENSOR_SERVICE_URL = os.getenv("SENSOR_SERVICE_URL", "http://team1-sensor-service:10238")
GATEWAY_SERVICE_URL = os.getenv("GATEWAY_SERVICE_URL", "http://team1-gateway-service:10241")