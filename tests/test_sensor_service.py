import unittest
from requests.exceptions import RequestException
from unittest.mock import patch
from service import sensor_service
from tests.dummy_data import (
    get_dummy_analysis_result,
    get_dummy_gateway_list,
    get_dummy_sensor_list
)


class SensorServiceTests(unittest.TestCase):
    # 1. 최근 임계치 조회 - 정상 케이스
    @patch("service.sensor_service.requests.get")
    def test_get_recent_thresholds_success(self, mock_get):
        dummy_response = [{"threshold_min": 10, "threshold_max": 20, "threshold_avg": 15}]
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = dummy_response

        result = sensor_service.get_recent_thresholds("G1", "TEMP-01", "temperature", limit=1)

        mock_get.assert_called_once()
        assert "storage-service/api/threshold" in mock_get.call_args[0][0]
        assert result == dummy_response

    # 2. 최근 임계치 조회 - 예외 발생 시 빈 리스트 반환
    @patch("service.sensor_service.requests.get")
    def test_get_recent_thresholds_failure(self, mock_get):
        mock_get.side_effect = RequestException("연결 실패")

        result = sensor_service.get_recent_thresholds("G1", "TEMP-01", "temperature")
        assert result == []

    # 3. 임계치 저장 - 정상 케이스
    @patch("service.sensor_service.requests.post")
    def test_save_result_post_called(self, mock_post):
        mock_post.return_value.status_code = 200
        result = get_dummy_analysis_result()

        sensor_service.save_result("G1", "TEMP-01", "temperature", result)

        payload = mock_post.call_args[1]["json"]
        for key in result.keys():
            assert key in payload
        assert payload["ready"] is True
        assert payload["count"] == 60
        assert isinstance(payload["calculated_at"], str)

    # 4. 임계치 저장 - 예외 발생 시 로깅만
    @patch("service.sensor_service.requests.post")
    def test_save_result_failure(self, mock_post):
        mock_post.side_effect = RequestException("저장 실패")

        sensor_service.save_result("G1", "TEMP-01", "temperature", get_dummy_analysis_result())
        mock_post.assert_called_once()

    # 5. 게이트웨이 전체 조회 - 정상 케이스
    @patch("service.sensor_service.requests.get")
    def test_get_all_gateway_id_with_dummy(self, mock_get):
        dummy = get_dummy_gateway_list()
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = dummy

        result = sensor_service.get_all_gateway_id()

        mock_get.assert_called_once_with("http://sensor-service/gateways")
        assert result == dummy

    # 6. 게이트웨이 전체 조회 - 실패 시 빈 리스트 반환
    @patch("service.sensor_service.requests.get")
    def test_get_all_gateway_id_failure(self, mock_get):
        mock_get.side_effect = RequestException("게이트웨이 조회 실패")

        result = sensor_service.get_all_gateway_id()
        assert result == []

    # 7. 센서 상태 기반 조회 - 정상 케이스
    @patch("service.sensor_service.requests.get")
    def test_get_sensor_list_by_state_str(self, mock_get):
        dummy = get_dummy_sensor_list("pending")
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = dummy

        result = sensor_service.get_sensor_list_by_state("pending")

        mock_get.assert_called_once_with("http://sensor-service/sensors", params={"state": "pending"})
        assert result == dummy

    # 8. 센서 상태 기반 조회 - 실패 시 빈 리스트 반환
    @patch("service.sensor_service.requests.get")
    def test_get_sensor_list_by_state_failure(self, mock_get):
        mock_get.side_effect = RequestException("상태 조회 실패")

        result = sensor_service.get_sensor_list_by_state("pending")
        assert result == []

    # 9. 게이트웨이별 센서 조회 - 정상 케이스
    @patch("service.sensor_service.requests.get")
    def test_get_sensor_list_by_gateway_id_with_dummy(self, mock_get):
        full_dummy = get_dummy_sensor_list("completed")
        dummy = [s for s in full_dummy if s["gateway_id"] == "G1"]

        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = dummy

        result = sensor_service.get_sensor_list_by_gateway_id("G1")

        mock_get.assert_called_once_with("http://sensor-service/gateways/G1/sensors")
        assert all(sensor["gateway_id"] == "G1" for sensor in result)
        assert result == dummy

    # 10. 게이트웨이별 센서 조회 - 실패 시 빈 리스트 반환
    @patch("service.sensor_service.requests.get")
    def test_get_sensor_list_by_gateway_id_failure(self, mock_get):
        mock_get.side_effect = RequestException("게이트웨이 센서 조회 실패")

        result = sensor_service.get_sensor_list_by_gateway_id("G1")
        assert result == []

    # 11. 센서 상태 업데이트 - 정상 케이스
    @patch("service.sensor_service.requests.patch")
    def test_update_sensor_state_success(self, mock_patch):
        mock_patch.return_value.status_code = 200

        sensor_service.update_sensor_state("G1", "TEMP-01", "temperature", "completed")

        mock_patch.assert_called_once()
        assert mock_patch.call_args[0][0] == "http://sensor-service/gateways/G1/sensors/TEMP-01/types/temperature"
        assert mock_patch.call_args[1]["json"] == {"state": "completed"}

    # 12. 센서 상태 업데이트 - 예외 발생 시 로깅
    @patch("service.sensor_service.requests.patch")
    def test_update_sensor_state_failure(self, mock_patch):
        mock_patch.side_effect = RequestException("패치 실패")

        sensor_service.update_sensor_state("G1", "TEMP-01", "temperature", "abandoned")
        mock_patch.assert_called_once()
