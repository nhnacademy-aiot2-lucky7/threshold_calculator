import pytest
from tests.dummy_data import (
    get_dummy_sensor_list,
    get_dummy_gateway_list,
    get_dummy_influx_data,
    get_dummy_analysis_result,
    get_dummy_analysis_fail_reason_data_count,
    get_dummy_analysis_fail_reason_invalid_data
)

@pytest.fixture
def dummy_sensors():
    return get_dummy_sensor_list()

@pytest.fixture
def dummy_gateways():
    return get_dummy_gateway_list()

@pytest.fixture
def dummy_influx_df():
    return get_dummy_influx_data()

@pytest.fixture
def dummy_analysis_result():
    return get_dummy_analysis_result()

@pytest.fixture
def dummy_fail_result_count():
    return get_dummy_analysis_fail_reason_data_count()

@pytest.fixture
def dummy_fail_result_invalid():
    return get_dummy_analysis_fail_reason_invalid_data()