import RPi.GPIO as GPIO
from .abstract_two_pin import AbstractTwoPin, TwoPinValue
from logger import logger
from time import sleep


class Relay(AbstractTwoPin):
    def __init__(self, pin):
        self.pin = pin
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.pin, GPIO.OUT)
        self.set_state(0)

    def set_state(self, new_state):
        try:
            state = self.get_value()
            if new_state != state:
                GPIO.output(self.pin, new_state)
                state = self.get_value()
                if new_state == state.value:
                    logger.info(f"RELAY: {self.pin} set to {new_state}")
                    return TwoPinValue(200, state.value, "OK")
                return TwoPinValue(500, state.value, "NOK")
            return TwoPinValue(200, state, "OK")
        except Exception as e:
            logger.error(f"RELAY: {self.pin} failed to set to {new_state}")
            return TwoPinValue(500, state.value, str(e))

    def get_value(self) -> TwoPinValue:
        try:
            state_pin = GPIO.input(self.pin)
            return TwoPinValue(200, state_pin, "OK")
        except Exception as e:
            return TwoPinValue(500, str(e), "NOK")


# to test this file use comand: python -m output.two_pin.relay
if __name__ == "__main__":
    r1 = Relay(5)
    r2 = Relay(6)
    r3 = Relay(13)
    r4 = Relay(19)
    r5 = Relay(23)
    r6 = Relay(24)
    # while True:
    #     try:
    #         r6.set_state(1)
    #         sleep(2)
    #         r6.set_state(0)
    #         sleep(1)
    #     except KeyboardInterrupt:
    #         GPIO.cleanup()
    #         break



    r_list = [r1, r2, r3, r4, r5, r6]
    for r in r_list:
        r.set_state(1)
        print(r.pin, r.get_value())
        sleep(2)
        r.set_state(0)
        print(r.pin, r.get_value())
        sleep(1)
    GPIO.cleanup()
