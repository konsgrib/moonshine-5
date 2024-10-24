from time import sleep, time
from threading import Thread, Event


class ProgramExecutor:
    def __init__(
        self, sensors, relays, buzzer, humidity_sensor, config, messenger, data
    ):
        self.sensors = sensors
        self.relays = relays
        self.buzzer = buzzer
        self.humidity_sensor = humidity_sensor
        self.config = config
        self.messenger = messenger
        self.data = data
        self.abort_event = Event()
        self.humidity_thread = Thread(target=self.monitor_humidity)
        self.humidity_thread.start()

    def monitor_humidity(self):
        while not self.abort_event.is_set():
            humidity_value = self.humidity_sensor.get_value().value
            if humidity_value > self.config["program_parameters"]["humidity_threshold"]:
                print(
                    "Humidity level > 80, aborting program and setting all relays to 0."
                )
                for relay_name, relay in self.relays.items():
                    relay.set_state(0)
                    self.data[relay_name] = 0  # Update relay state in data dictionary
                self.data["data_changed"] = True
                self.abort_event.set()
            sleep(0.1)

    def execute_program(self, program, program_id):
        def execute_steps(steps, program_id):
            for step_number, step in enumerate(steps, start=1):
                # Send status message
                self.messenger.send_message(f"{program_id}:{step_number}")

                # Check if the program should be aborted
                if self.abort_event.is_set():
                    return

                action = step["action"]
                if action == "set_relay":
                    relay_name = step["relay"]
                    state = step["state"]
                    relay = self.relays.get(relay_name)
                    if relay:
                        relay.set_state(state)
                        # Update relay state in data dictionary
                        self.data[relay_name] = state
                        print(
                            f"Set relay {relay_name} to state {state}"
                        )  # Debugging print
                elif action == "set_buzzer":
                    state = step["state"]
                    self.buzzer.set_state(state)
                elif action == "wait":
                    duration_key = step["duration"]
                    duration = self.config["program_parameters"]["wait_times"].get(
                        duration_key, duration_key
                    )
                    # Ensure the duration is a number
                    if isinstance(duration, str):
                        duration = float(duration)
                    print(f"Waiting for {duration} seconds")  # Debugging print

                    # Wait for the specified duration
                    end_time = time() + duration
                    while time() < end_time:
                        if self.abort_event.is_set():
                            return
                        sleep(0.1)

                    print(f"Finished waiting for {duration} seconds")  # Debugging print
                elif action == "repeat":
                    count = step["count"]
                    repeat_steps = step["steps"]
                    for _ in range(count):
                        execute_steps(repeat_steps, program_id)
                elif action == "wait_for_liquid_level":
                    sensor_name = step["sensor"]
                    state = step["state"]
                    while self.sensors[sensor_name].get_value().value != state:
                        sleep(1)
                elif action == "wait_for_temperature":
                    sensor_name = step["sensor"]
                    threshold_key = step["threshold"]
                    threshold = self.config["program_parameters"][
                        "temperature_thresholds"
                    ][threshold_key]
                    while self.sensors[sensor_name].get_value().value < threshold:
                        sleep(1)
                elif action == "wait_for_average_temp_greater_than":
                    sensor_name = step["sensor"]
                    values = []
                    cnt = 10
                    average_value = 0
                    for _ in range(cnt):
                        values.append(self.sensors[sensor_name].get_value().value)
                    average_value = sum(values) / len(values)

                    while (
                        self.sensors[sensor_name].get_value().value
                        < average_value + 0.3
                    ):
                        values.append(self.sensors[sensor_name].get_value().value)
                        average_value = sum(values) / len(values)
                        sleep(1)
                else:
                    print(f"Unknown action: {action}")

            # Send final message indicating program completion
            self.messenger.send_message("0:0")

        execute_steps(program["steps"], program_id)

    def stop(self):
        self.abort_event.set()
        self.humidity_thread.join()
