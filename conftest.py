import pytest
from enum import Enum
import requests
from time import sleep

class SensorMethod(Enum):
    GET_INFO = "get_info"
    GET_READING = "get_reading"
    SET_NAME = "set_name"
    GET_METHODS = "get_methods"
    SET_READING_INTERVAL = "set_reading_interval"
    RESET_TO_FACTORY = "reset_to_factory"
    UPDATE_FIRMWARE = "update_firmware"
    REBOOT = "reboot"


def make_valid_payload(
    method: SensorMethod, params: dict | None = None
) -> dict:
    payload = {"method": method, "jsonrpc": "2.0", "id": 1}

    if params:
        payload["params"] = params

    return payload


def pytest_addoption(parser):
    parser.addoption(
        "--sensor-host",
        action="store",
        default="http://127.0.0.1",
        help="Sensor host",
    )
    parser.addoption(
        "--sensor-port", action="store", default="9898", help="Sensor port"
    )
    parser.addoption(
        "--sensor-pin", action="store", default="0000", help="Sensor pin"
    )


@pytest.fixture(scope="session")
def sensor_host(request):
    return request.config.getoption("--sensor-host")


@pytest.fixture(scope="session")
def sensor_port(request):
    return request.config.getoption("--sensor-port")


@pytest.fixture(scope="session")
def sensor_pin(request):
    return request.config.getoption("--sensor-pin")


@pytest.fixture(scope="session")
def send_post(sensor_host, sensor_port, sensor_pin):
    def inner(
        method: SensorMethod | None = None,
        params: dict | None = None,
        jsonrpc: str | None = None,
        id: int | None = None,
    ):
        request_body = {}

        if method:
            request_body["method"] = method.value

        if params:
            request_body["params"] = params

        if jsonrpc:
            request_body["jsonrpc"] = jsonrpc

        if id:
            request_body["id"] = id

        request_headers = {"Authorization": sensor_pin}
        res = requests.post(
            f"{sensor_host}:{sensor_port}/rpc",
            json=request_body,
            headers=request_headers,
        )

        return res.json()

    return inner


@pytest.fixture(scope="session")
def make_valid_request(send_post):
    def inner(method: SensorMethod, params: dict | None = None) -> dict:
        payload = make_valid_payload(method=method, params=params)
        sensor_response = send_post(**payload)
        return sensor_response.get("result", {})

    return inner


@pytest.fixture(scope="session")
def get_sensor_info(make_valid_request):
    def inner():
        return make_valid_request(SensorMethod.GET_INFO)

    return inner


@pytest.fixture
def get_sensor_reading(make_valid_request):
    def inner():
        return make_valid_request(SensorMethod.GET_READING)

    return inner


@pytest.fixture
def set_sensor_name(make_valid_request):
    def inner(name: str):
        return make_valid_request(SensorMethod.SET_NAME, {"name": name})

    return inner


@pytest.fixture
def get_sensor_methods(make_valid_request):
    def inner():
        return make_valid_request(SensorMethod.GET_METHODS)

    return inner


@pytest.fixture
def set_sensor_reading_interval(make_valid_request):
    def inner(reading_interval: int):
        return make_valid_request(SensorMethod.SET_READING_INTERVAL, {"interval": reading_interval})

    return inner


@pytest.fixture(scope="session")
def reset_sensor_to_factory(make_valid_request):
    def inner():
        return make_valid_request(SensorMethod.RESET_TO_FACTORY)

    return inner


@pytest.fixture
def update_sensor_firmware(make_valid_request):
    def inner():
        return make_valid_request(SensorMethod.UPDATE_FIRMWARE)

    return inner


@pytest.fixture
def reboot_sensor(make_valid_request):
    def inner():
        return make_valid_request(SensorMethod.REBOOT)

    return inner


@pytest.fixture(autouse=True, scope="session")
def setup_test_session(reset_sensor_to_factory, get_sensor_info):
    print("Resetting sensor to factory settings before test session")
    reset_sensor_to_factory()
    sensor_info = wait(get_sensor_info, lambda x: isinstance(x, dict), tries=15, timeout=1)
    if not sensor_info:
        raise RuntimeError("Sensor didn't reset to factory property")
    

def wait(func: callable, condition: callable, tries: int, timeout: int, **kwargs):
    for _ in range(tries):
        try: 
            result = func(**kwargs)

            if condition(result):
                return result
        except Exception as e:
            sleep(timeout)    