# test_config_yaml_reader.py
import pytest
from unittest.mock import mock_open, patch, MagicMock
from config_parser import ConfigYamlReader, DeviceBuilder, ProgramBuilder
import yaml
from factory import Factory


@pytest.fixture
def mock_yaml_content():
    return """
    pins:
      humidity_1: &sensor_hum_1 14
      buzzer: &buzzer_pin 26
      relay:
        power_relay_pin: &rel_pwr_pin 19
        cooler_relay_pin: &rel_cool_pin 13
        valve_1_relay_pin: &valve_1_pin 6
        valve_2_relay_pin: &valve_2_pin 5
    one-wire:
      temperature:
        sensor_1: &t1_id 28-0214811929ff
        sensor_2: &t2_id 28-0417301b9dff
    devices:
      - type: Relay
        name: power_relay 
        pin: *rel_pwr_pin
      - type: Relay
        name: cooler_relay
        pin:  *rel_cool_pin
      - type: Relay
        name: valve_1_relay
        pin: *valve_1_pin
      - type: Relay
        name: valve_2_relay
        pin: *valve_2_pin
      - type: Buzzer
        name: buzzer
        pin: *buzzer_pin
      - type: TemperatureSensor
        name: termo_1
        device_id: *t1_id
      - type: TemperatureSensor
        name: termo_2
        device_id: *t2_id
      - type: HumidityLevelSensor
        name: humidity
        pin: *sensor_hum_1
      - type: MessengerFile
        name: messenger
        filename: state.txt
    programms:
      producer: 
        - command: recurring
          type: RecurringCommand
          commands:
            - command: producer
              type: ProducerCommand
              termo_1: termo_1
              termo_2: termo_2
              humidity_1: humidity
              buzzer_1: buzzer
              relay_pwr: power_relay
              relay_clr: cooler_relay
              relay_v1: valve_1_relay
              relay_v2: valve_2_relay
              messenger: messenger
          repeat_times: Null
    """


@pytest.fixture
def mock_config_reader(mock_yaml_content):
    with patch(
        "config_parser.ConfigYamlReader.get_config_data",
        return_value=yaml.safe_load(mock_yaml_content),
    ):
        yield


def test_device_factory():
    device1 = Factory().create_device("TemperatureSensor", device_id="XYZ")
    device2 = Factory().create_device("Relay", pin=23)
    device3 = Factory().create_device("MessengerFile", filename="filename.csv")
    assert device1.device_id == "XYZ"
    assert device2.pin == 23
    assert device3.filename == "filename.csv"


def test_device_builder(mock_yaml_content):
    with patch.object(
        ConfigYamlReader,
        "get_config_data",
        return_value=yaml.safe_load(mock_yaml_content),
    ):
        device_builder = DeviceBuilder("config_file.yaml")
        devices_list = device_builder.config_data["devices"]
        assert len(devices_list) == 9
        assert devices_list[0]["name"] == "power_relay"
        assert devices_list[0]["pin"] == 19
        assert devices_list[1]["name"] == "cooler_relay"
        assert devices_list[1]["pin"] == 13
        assert devices_list[2]["name"] == "valve_1_relay"
        assert devices_list[2]["pin"] == 6
        assert devices_list[3]["name"] == "valve_2_relay"
        assert devices_list[3]["pin"] == 5
        assert devices_list[4]["name"] == "buzzer"
        assert devices_list[4]["pin"] == 26
        assert devices_list[5]["name"] == "termo_1"
        assert devices_list[5]["device_id"] == "28-0214811929ff"
        assert devices_list[6]["name"] == "termo_2"
        assert devices_list[6]["device_id"] == "28-0417301b9dff"
        assert devices_list[7]["name"] == "humidity"
        assert devices_list[7]["pin"] == 14
        assert devices_list[8]["name"] == "messenger"
        assert devices_list[8]["filename"] == "state.txt"
        devices_objs = device_builder.build_devices()
        print(devices_objs["termo_1"].get_value())
        assert devices_objs["termo_1"].device_id == "28-0214811929ff"


@pytest.fixture
def test_sensor_value_patching():
    val_termo_1 = {"status_code": 200, "value": 26, "message": "OK"}
    val_termo_2 = {"status_code": 200, "value": 26, "message": "OK"}
    val_humidity = {"status_code": 200, "value": 60, "message": "OK"}
    val_pwr_relay = {"status_code": 200, "value": 0, "message": "OK"}
    val_clr_relay = {"status_code": 200, "value": 0, "message": "OK"}
    val_v1_relay = {"status_code": 200, "value": 0, "message": "OK"}
    val_v2_relay = {"status_code": 200, "value": 0, "message": "OK"}
    devices = []
    with patch(
        "sensor.temperature.TemperatureSensor.get_value", return_value=val_termo_1
    ):
        device1 = Factory().create_device("TemperatureSensor", device_id="XYZ")
        devices.append(device1)

    with patch(
        "sensor.temperature.TemperatureSensor.get_value", return_value=val_termo_2
    ):
        device2 = Factory().create_device("TemperatureSensor", device_id="ABC")
        devices.append(device2)

    with patch(
        "sensor.humidity.HumidityLevelSensor.get_value", return_value=val_humidity
    ):
        device3 = Factory().create_device("HumidityLevelSensor", pin=11)
        devices.append(device3)

    device4 = Factory().create_device("Relay", pin=21)
    device4.set_state(0)
    devices.append(device4)

    device5 = Factory().create_device("Relay", pin=22)
    device5.set_state(0)
    devices.append(device5)

    device6 = Factory().create_device("Relay", pin=23)
    device6.set_state(0)
    devices.append(device6)
    device7 = Factory().create_device("Relay", pin=24)
    device7.set_state(0)
    devices.append(device7)

    return devices


def test_patched_devices(test_sensor_value_patching):
    devices = test_sensor_value_patching
    assert len(devices) == 7
    # assert devices[0].get_value() == {"status_code": 200, "value": 26, "message": "OK"}
    # assert devices[1].get_value() == {"status_code": 200, "value": 26, "message": "OK"}
    # assert devices[2].get_value() == {"status_code": 200, "value": 60, "message": "OK"}
    # assert devices[3].get_value() == {"status_code": 200, "value": 0, "message": "OK"}
    # assert devices[4].get_value() == {"status_code": 200, "value": 0, "message": "OK"}
    # assert devices[5].get_value() == {"status_code": 200, "value": 0, "message": "OK"}
    # assert devices[6].get_value() == {"status_code": 200, "value": 0, "message": "OK"}
    for device in devices:
        print(device.get_value())


def test_get_config_data_success(mock_yaml_content):
    with patch("builtins.open", mock_open(read_data=mock_yaml_content)):
        reader = ConfigYamlReader()
        config_data = reader.get_config_data("dummy_path")

        assert config_data == {
            "pins": {
                "humidity_1": 14,
                "buzzer": 26,
                "relay": {
                    "power_relay_pin": 19,
                    "cooler_relay_pin": 13,
                    "valve_1_relay_pin": 6,
                    "valve_2_relay_pin": 5,
                },
            },
            "one-wire": {
                "temperature": {
                    "sensor_1": "28-0214811929ff",
                    "sensor_2": "28-0417301b9dff",
                }
            },
            "devices": [
                {"type": "Relay", "name": "power_relay", "pin": 19},
                {"type": "Relay", "name": "cooler_relay", "pin": 13},
                {"type": "Relay", "name": "valve_1_relay", "pin": 6},
                {"type": "Relay", "name": "valve_2_relay", "pin": 5},
                {"type": "Buzzer", "name": "buzzer", "pin": 26},
                {
                    "type": "TemperatureSensor",
                    "name": "termo_1",
                    "device_id": "28-0214811929ff",
                },
                {
                    "type": "TemperatureSensor",
                    "name": "termo_2",
                    "device_id": "28-0417301b9dff",
                },
                {"type": "HumidityLevelSensor", "name": "humidity", "pin": 14},
                {"type": "MessengerFile", "name": "messenger", "filename": "state.txt"},
            ],
            "programms": {
                "producer": [
                    {
                        "command": "recurring",
                        "type": "RecurringCommand",
                        "commands": [
                            {
                                "command": "producer",
                                "type": "ProducerCommand",
                                "termo_1": "termo_1",
                                "termo_2": "termo_2",
                                "humidity_1": "humidity",
                                "buzzer_1": "buzzer",
                                "relay_pwr": "power_relay",
                                "relay_clr": "cooler_relay",
                                "relay_v1": "valve_1_relay",
                                "relay_v2": "valve_2_relay",
                                "messenger": "messenger",
                            }
                        ],
                        "repeat_times": None,
                    }
                ]
            },
        }
