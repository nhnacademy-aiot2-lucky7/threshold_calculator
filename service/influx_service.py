from influxdb_client import InfluxDBClient
from config import config

# InfluxDB client 생성
client = InfluxDBClient(
    url=config.INFLUXDB_URL,
    token=config.INFLUXDB_TOKNE,
    org=config.INFLUXDB_ORG
)

query_api = client.query_api()

# 센서 데이터 개수 조회
def get_sensor_data_count(gateway_id: str, sensor_id: str, sensor_type: str) -> int:
    query = f'''
    from(bucket: "{config.INFLUXDB_BUCKET}")
        |> range(start: -30d)
        |> filter(fn: (r) => r["_measurement"] == "sensor_data")
        |> filter(fn: (r) => r["gateway_id"] == "{gateway_id}")
        |> filter(fn: (r) => r["sensor_id"] == "{sensor_id}")
        |> filter(fn: (r) => r["_field"] == "{sensor_type}")
        |> count()
    '''

    tables = query_api.query(query)
    for table in tables:
        for record in table.records:
            return record.get_value()
    return 0

# 센서 데이터 값, 시간 목록 조회 
def get_sensor_values_with_time(gateway_id: str, sensor_id: str, sensor_type: str, duration: str = "-1h"):
    query = f'''
    from(bucket: "{config.INFLUXDB_BUCKET}")
        |> range(start: {duration})
        |> filter(fn: (r) => r["_measurement"] == "sensor_data")
        |> filter(fn: (r) => r["gateway_id"] == "{gateway_id}")
        |> filter(fn: (r) => r["sensor_id"] == "{sensor_id}")
        |> filter(fn: (r) => r["_field"] == "{sensor_type}")
    '''

    tables = query_api.query(query)
    results = []
    for table in tables:
        for record in table.records:
            results.append({
                "time": record.get_time(),
                "value": record.get_value()
            })
    return results
