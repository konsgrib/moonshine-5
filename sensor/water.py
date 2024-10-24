import RPi.GPIO as GPIO
from .abstract_sensor import AbstractSensor, SensorValue


class WaterLevelSensor(AbstractSensor):
    def __init__(self, pin):
        self.pin = pin
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    def get_value(self) -> SensorValue:
        try:
            current_value = GPIO.input(self.pin)
            if current_value:
                return SensorValue(200, 0, "OK")
            return SensorValue(200, 1, "OK")
        except Exception as e:
            return SensorValue(500, -1, "NOK")


# to test this file use comand: python -m sensor.water
if __name__ == "__main__":
    ss = WaterLevelSensor(17)
    ss2 = WaterLevelSensor(27)
    print("17", " ", ss.get_value())
    print("27", " ", ss2.get_value())
