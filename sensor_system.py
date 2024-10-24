from time import sleep
import RPi.GPIO as GPIO
import threading
from sensor.button import Button
from sensor.humidity import HumidityLevelSensor
from sensor.temperature import TemperatureSensor
from sensor.water import WaterLevelSensor
from display.display import LcdDisplay
from output.two_pin.relay import Relay
from output.two_pin.buzzer import Buzzer
from messenger.messenger_file import MessengerFile
from config_reader import ConfigReader
from program_executor import ProgramExecutor


class SensorSystem:
    def __init__(self):
        # Load configuration and programs
        config_reader = ConfigReader("config.yaml", "programs.yaml")
        self.config = config_reader.config
        self.programs = config_reader.programs

        # Initialize sensors and display using configuration
        self.sensors = {
            "termo_1": TemperatureSensor(
                self.config["sensors"]["temperature_sensors"]["ts1"]
            ),
            "termo_2": TemperatureSensor(
                self.config["sensors"]["temperature_sensors"]["ts2"]
            ),
            "humidity_1": HumidityLevelSensor(
                self.config["sensors"]["humidity_sensor"]["hs"]
            ),
            "button_1": Button(self.config["sensors"]["buttons"]["bt1"]),
            "button_2": Button(self.config["sensors"]["buttons"]["bt2"]),
            "button_3": Button(self.config["sensors"]["buttons"]["bt3"]),
            "message": MessengerFile(
                self.config["sensors"]["messenger_file"]["file_path"]
            ),
            "water_1": WaterLevelSensor(
                self.config["sensors"]["water_level_sensors"]["ws1"]
            ),
            "water_2": WaterLevelSensor(
                self.config["sensors"]["water_level_sensors"]["ws2"]
            ),
        }
        self.relays = {
            "relay_pwr": Relay(self.config["sensors"]["relays"]["power"]),
            "relay_clr": Relay(self.config["sensors"]["relays"]["cooler"]),
            "relay_v1": Relay(self.config["sensors"]["relays"]["valve_1"]),
            "relay_v2": Relay(self.config["sensors"]["relays"]["valve_2"]),
            "relay_up": Relay(self.config["sensors"]["relays"]["power_up"]),
            "relay_down": Relay(self.config["sensors"]["relays"]["power_down"]),
        }
        self.buzzer = Buzzer(self.config["sensors"]["buzzer"]["buz"])
        self.display = LcdDisplay(
            self.config["sensors"]["display"]["data_pin"],
            self.config["sensors"]["display"]["clk_pin"],
            self.config["sensors"]["display"]["reset_pin"],
        )

        # Initialize messenger
        self.messenger = MessengerFile(
            self.config["sensors"]["messenger_file"]["file_path"]
        )

        # Dictionary to hold sensor data
        self.data = {key: None for key in self.sensors.keys()}
        self.data.update(
            {key: 0 for key in self.relays.keys()}
        )  # Initialize relay states to 0
        self.data["message"] = "0:0"

        # Initialize program executor
        self.program_executor = ProgramExecutor(
            self.sensors,
            self.relays,
            self.buzzer,
            self.sensors["humidity_1"],
            self.config,
            self.messenger,
            self.data,
        )

        # Flag to indicate if data has changed
        self.data_changed = False

        # Variable to track the previous state of the humidity sensor
        self.previous_humidity_high = False

        # Event to track if the program execution thread is running
        self.program_running_event = threading.Event()

        # Create threads for each sensor and button
        self.threads = []
        for sensor_name, sensor in self.sensors.items():
            thread = threading.Thread(
                target=self.read_sensor, args=(sensor_name, sensor)
            )
            thread.daemon = (
                True  # Allows the thread to exit when the main program exits
            )
            self.threads.append(thread)
            thread.start()

        # Start the display update thread
        display_thread = threading.Thread(target=self.update_display)
        display_thread.daemon = (
            True  # Allows the thread to exit when the main program exits
        )
        display_thread.start()

    def handle_button_press(self, button_name):
        if button_name == "button_1" and not self.program_running_event.is_set():
            threading.Thread(target=self.run_program, args=("program1",)).start()
        elif button_name == "button_2" and not self.program_running_event.is_set():
            threading.Thread(target=self.run_program, args=("program2",)).start()

    def run_program(self, program_name):
        self.program_running_event.set()  # Set the event to indicate the program is running

        # Reload configuration and programs
        self.config_reader = ConfigReader("config.yaml", "programs.yaml")
        self.config = self.config_reader.config
        self.programs = self.config_reader.programs

        program = self.programs.get(program_name)
        if program:
            self.program_executor.execute_program(
                program, program_name[-1]
            )  # Pass the last character of the program name as the program ID

        self.program_running_event.clear()  # Clear the event to indicate the program has finished

    def read_sensor(self, sensor_name, sensor):
        while True:
            if isinstance(sensor, Button):
                value = sensor.is_pressed()
                if value:
                    self.handle_button_press(sensor_name)
            elif isinstance(sensor, MessengerFile):
                value = sensor.get_message()
            else:
                value = sensor.get_value().value

            if self.data[sensor_name] != value:
                self.data[sensor_name] = value
                self.data_changed = True  # Set flag to indicate data has changed

                # Check the humidity sensor value and control the buzzer
                if sensor_name == "humidity_1":
                    if value > 70:
                        self.buzzer.set_state(1)
                        self.previous_humidity_high = True
                    elif value <= 70 and self.previous_humidity_high:
                        self.buzzer.set_state(0)
                        self.previous_humidity_high = False

            sleep(0.1)  # Adjust the sleep time as needed

    def update_display(self):
        while True:
            if self.data_changed:  # Check if data has changed
                self.display.show_data(self.data)  # Update the display
                self.data_changed = False  # Reset the flag
            sleep(1)  # Adjust sleep time as needed

    def run(self):
        try:
            while True:
                if self.data_changed:  # Check if data has changed
                    print(self.data)
                sleep(1)
        except KeyboardInterrupt:
            print("Program terminated by user.")
            GPIO.cleanup()


if __name__ == "__main__":
    system = SensorSystem()
    system.run()
