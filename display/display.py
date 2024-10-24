from .abstract_display import AbstractDisplay
from lcd.lcd import Lcd
import RPi.GPIO as GPIO


class LcdDisplay(AbstractDisplay):
    def __init__(self, data_pin, clk_pin, reset_pin):
        self.data_pin = data_pin
        self.clk_pin = clk_pin
        self.reset_pin = reset_pin
        self.display = Lcd(self.data_pin, self.clk_pin, self.reset_pin)
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.data_pin, GPIO.OUT)  # (pin 26 = GPIO7)   = DATA
        GPIO.setup(self.clk_pin, GPIO.OUT)  # (pin 24 = GPIO8)   = CLOCK
        GPIO.setup(self.reset_pin, GPIO.OUT)  # (pin 22 = GPIO25)  = RESET

    def show_data(self, data):
        self.display.clear()
        self.display.display_text("Pr Pm C V1 V2 St".ljust(16, " "), 0, 0)
        step = f"{data['message'].split(':')[1].strip()}"
        if len(step) == 1:
            step = f"0{step}"
        self.display.display_text(
            (
                f"{data['message'].split(':')[0]}  "
                f"{data['relay_pwr']}  "
                f"{data['relay_clr']}  "
                f"{data['relay_v1']}  "
                f"{data['relay_v2']} "
                f"{step}"
            ).ljust(16, " "),
            0,
            1,
        )
        self.display.display_text(f"Temp1:{data['termo_1']}  HUM".ljust(16, " "), 0, 2)
        self.display.display_text(
            f"Temp2:{data['termo_2']}  {data['humidity_1']}".ljust(16, " "), 0, 3
        )


# to test this file use comand: python -m display.display
if __name__ == "__main__":
    data_pin = 7  # Replace with your GPIO pin number
    clk_pin = 8  # Replace with your GPIO pin number
    reset_pin = 25  # Replace with your GPIO pin number
    ds = LcdDisplay(data_pin, clk_pin, reset_pin)
    data = {
        "termo_1": 22.4,
        "termo_2": 22.8,
        "humidity_1": 47.3,
        "buzzer_1": 0,
        "relay_pwr": 0,
        "relay_clr": 0,
        "relay_v1": 0,
        "relay_v2": 0,
        "message": "1:1",
    }
    ds.show_data(data)
