import RPi.GPIO as GPIO
import time

data_pin = 7  # Replace with your GPIO pin number
clk_pin = 8  # Replace with your GPIO pin number
reset_pin = 25  # Replace with your GPIO pin number

if __name__ == "__main__":
    try:
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(data_pin, GPIO.OUT)
        GPIO.setup(clk_pin, GPIO.OUT)
        GPIO.setup(reset_pin, GPIO.OUT)

        GPIO.output(data_pin, True)
        GPIO.output(clk_pin, True)
        GPIO.output(reset_pin, True)
        time.sleep(1)
        print("GPIO pins are set up correctly.")
    except RuntimeError as e:
        print("Error:", e)
    except Exception as e:
        print("An unexpected error occurred:", e)
    finally:
        GPIO.cleanup()
