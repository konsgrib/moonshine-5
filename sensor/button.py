import RPi.GPIO as GPIO
from .abstract_sensor import AbstractSensor, SensorValue


class Button(AbstractSensor):
    def __init__(self, pin) -> None:
        self.pin = pin
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    def get_value(self):
        try:
            current_value = GPIO.input(self.pin)
            if current_value:
                return SensorValue(200, 0, "OK")
            return SensorValue(200, 1, "OK")
        except Exception as e:
            return SensorValue(500, -1, "NOK")

    def is_pressed(self):
        try:
            current_value = GPIO.input(self.pin)
            if current_value:
                return 0
            return 1
        except Exception as e:
            return -1


# to test this file use comand: python -m sensor.button
if __name__ == "__main__":
    try:
        ss = Button(11)
        print("Button state:", ss.get_value())
    except Exception as e:
        print("Error:", e)
    finally:
        GPIO.cleanup()  # Ensure GPIO is cleaned up
