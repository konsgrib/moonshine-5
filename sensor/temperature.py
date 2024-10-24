import os
import glob
import time
from .abstract_sensor import AbstractSensor, SensorValue


class TemperatureSensor(AbstractSensor):
    def __init__(self, device_id):
        self.device_id = device_id
        self.base_dir = "/sys/bus/w1/devices/"
        # os.system("modprobe w1-gpio")
        # os.system("modprobe w1-therm")

    def _get_device_file(self):
        device_folder = glob.glob(self.base_dir + self.device_id)[0]
        device_file = device_folder + "/w1_slave"
        return device_file

    def _read_sensor_data_raw(self):
        device_file = self._get_device_file()
        with open(device_file, "r") as f:
            lines = f.readlines()
        return lines

    def get_value(self) -> SensorValue:
        try:
            lines = self._read_sensor_data_raw()
            while lines[0].strip()[-3:] != "YES":
                time.sleep(0.2)
                lines = self._read_sensor_data_raw()
            equals_pos = lines[1].find("t=")
            if equals_pos != -1:
                temp_string = lines[1][equals_pos + 2 :]
                temp_c = round(float(temp_string) / 1000.0, 1)

                return SensorValue(200, temp_c, "OK")
            else:
                return SensorValue(500, -1, "NOK")
        except Exception as e:
            return SensorValue(500, -1, str(e))


# to test this file use comand: python -m sensor.temperature
if __name__ == "__main__":
    ss = TemperatureSensor("28-42f7d445552f")
    ss2 = TemperatureSensor("28-5be6d445359c")
    print("28-42f7d445552f", " ", ss.get_value())
    print("28-5be6d445359c", " ", ss2.get_value())
