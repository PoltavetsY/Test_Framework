import requests
from requests.exceptions import JSONDecodeError
# from typing import Optional


# def make_valid_payload(method: str, params: Optional[dict] = None) -> dict:
def make_valid_payload(method: str, params: dict | None = None) -> dict:
    payload = {"method": method, "jsonrpc": "2.0", "id": 1}

    if params:
        payload["params"] = params

    return payload


def make_valid_request(method: str, params: dict | None = None) -> dict:
    payload = make_valid_payload(method=method, params=params)
    sensor_response = send_post(**payload)
    return sensor_response.get("result", {})


# def send_post(method: Optional[str] = None, params: Optional[dict] = None, jsonrpc: Optional[str] = None, id: Optional[int] = None):
def send_post(method: str| None = None, params: dict | None = None, jsonrpc: str |None = None, id: int | None = None):
    request_body = {}

    if method:
        request_body["method"] = method

    if params:
        request_body["params"] = params

    if jsonrpc:
        request_body["jsonrpc"] = jsonrpc

    if id:
        request_body["id"] = id

    request_headers = {"Authorization": "0000"}
    res = requests.post("http://127.0.0.1:9898/rpc", json=request_body, headers=request_headers)

    try:
        return res.json()
    except JSONDecodeError:
        return {}


def get_sensor_info():
    return make_valid_request("get_info")


def get_sensor_reading():
    return make_valid_request("get_reading")
    


def test_sanity():
    sensor_info = get_sensor_info()

    sensor_name = sensor_info.get("name")
    assert isinstance(sensor_name, str), "Sensor name is not a string"

    sensor_hid = sensor_info.get("hid")
    assert isinstance(sensor_hid, str), "Sensor hid is not a string"

    sensor_model = sensor_info.get("model")
    assert isinstance(sensor_model, str), "Sensor model is not a string"

    sensor_firmware_version = sensor_info.get("firmware_version")
    assert isinstance(sensor_firmware_version, int), "Sensor firmware version is not a int"

    sensor_reading_interval = sensor_info.get("reading_interval")
    assert isinstance(sensor_reading_interval, int), "Sensor reading interval is not a string"

    sensor_reading = get_sensor_reading()
    assert isinstance(sensor_reading, float), "Sensor doesn't seem to register temperature"

    print("Sanity test passed")