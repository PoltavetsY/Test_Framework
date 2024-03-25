from time import sleep
from conftest import wait


def test_sanity(
    get_sensor_info,
    get_sensor_reading,
    set_sensor_name,
    set_sensor_reading_interval,
    reset_sensor_to_factory,
    update_sensor_firmware,
    reboot_sensor,
):
    sensor_info = get_sensor_info()

    sensor_name = sensor_info.get("name")
    assert isinstance(sensor_name, str), "Sensor name is not a string"

    sensor_hid = sensor_info.get("hid")
    assert isinstance(sensor_hid, str), "Sensor hid is not a string"

    sensor_model = sensor_info.get("model")
    assert isinstance(sensor_model, str), "Sensor model is not a string"

    sensor_firmware_version = sensor_info.get("firmware_version")
    assert isinstance(
        sensor_firmware_version, int
    ), "Sensor firmware version is not a int"

    sensor_reading_interval = sensor_info.get("reading_interval")
    assert isinstance(
        sensor_reading_interval, int
    ), "Sensor reading interval is not a string"

    sensor_reading = get_sensor_reading()
    assert isinstance(
        sensor_reading, float
    ), "Sensor doesn't seem to register temperature"

    print("Sanity test passed")


def test_reboot(get_sensor_info, reboot_sensor):
    """Steps:
    1. Get original sensor info
    2. Reboot sensor
    3. Wait for sensor to come back online
    4. Get current sensor info
    5. Validate that info from Step 1 is equal to info from Step 4
    """

    # print('Get original sensor info')
    sensor_info_before_reboot = get_sensor_info()
    # print('Reboot sensor')
    reboot_response = reboot_sensor()
    assert reboot_response == "rebooting", "Sensor did not reboot"

    # print('Wait for sensor to come back online')
    sensor_info_after_reboot = wait(
        func=get_sensor_info,
        condition=lambda x: isinstance(x, dict),
        tries=10,
        timeout=1,
    )

    # print('Get current sensor info')
    sensor_info_after_reboot = get_sensor_info()

    # print('Validate that info from Step 1 is equal to info from Step 4')
    assert (
        sensor_info_before_reboot == sensor_info_after_reboot
    ), "Sensor info after reboot does not match sensor info before reboot"
    print("test_reboot passed")


def test_set_sensor_name(get_sensor_info, set_sensor_name):
    """
    1. Set sensor name to "new_name".
    2. Get sensor_info.
    3. Validate that current sensor name matches the name set in Step 1.
    """

    new_sensor_name = set_sensor_name("new_name").get("name")

    sensor_info = get_sensor_info()
    current_sensor_name = sensor_info.get("name")

    assert new_sensor_name == current_sensor_name, "Sensor name did not change"

    print("test_set_sensor_name passed")


def test_set_sensor_reading_interval(
    get_sensor_info, set_sensor_reading_interval, get_sensor_reading
):
    """
    1. Set sensor reading interval to 1.
    2. Get sensor info.
    3. Validate that sensor reading interval is set to interval from Step 1.
    4. Get sensor reading.
    5. Wait for interval specified in Step 1.
    6. Get sensor reading.
    7. Validate that reading from Step 4 doesn't equal reading from Step 6.
    """

    set_sensor_reading_interval(1)

    assert (
        get_sensor_info().get("reading_interval") == 1
    ), "sensor reading interval is not set to interval from Step 1"

    sensor_reading_before_wait = get_sensor_reading()
    sleep(1)
    sensor_reading_after_wait = get_sensor_reading()

    assert (
        sensor_reading_before_wait != sensor_reading_after_wait
    ), "reading interval is same"

    print("test_set_sensor_reading_interval passed")


def test_update_sensor_firmware(get_sensor_info, update_sensor_firmware):
    """
    1. Get original sensor firmware version.
    2. Request firmware update.
    3. Get current sensor firmware version.
    4. Validate that current firmware version is +1 to original firmware version.
    5. Repeat steps 1-4 until sensor is at max_firmware_version - 1.
    6. Update sensor to max firmware version.
    7. Validate that sensor is at max firmware version.
    8. Request another firmware update.
    9. Validate that sensor doesn't update and responds appropriately.
    10. Validate that sensor firmware version doesn't change if it's at maximum value.
    """

    max_firmware_version = 15

    def update_firmware():
        original_sensor_firmware_version = get_sensor_info().get("firmware_version")
        update_sensor_firmware()

        wait(
            func=get_sensor_info,
            condition=lambda x: isinstance(x, dict),
            tries=13,
            timeout=1,
        )
        current_sensor_firmware_version = get_sensor_info().get("firmware_version")

        assert (
            current_sensor_firmware_version == original_sensor_firmware_version + 1
        ), "Firmware update is not successful"

        return current_sensor_firmware_version

    current_sensor_firmware_version = update_firmware()

    while current_sensor_firmware_version < max_firmware_version - 1:
        current_sensor_firmware_version = update_firmware()

    current_sensor_firmware_version = update_firmware()

    assert (
        current_sensor_firmware_version == max_firmware_version
    ), "Sensor is not at max firmware version"

    another_firmware_update = update_sensor_firmware()
    lasted_firmware_version_update = get_sensor_info().get("firmware_version")

    assert (
        another_firmware_update == "already at latest firmware version"
    ), "Sensor does not respond properly"
    assert (
        current_sensor_firmware_version == lasted_firmware_version_update
    ), "Error when updating the maximum version of the sensor firmware"

    print("test_update_sensor_firmware passed")
