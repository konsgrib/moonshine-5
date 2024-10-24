from .abstract_messenger import AbstractMessenger


class MessengerFile(AbstractMessenger):
    def __init__(self, filename):
        self.filename = filename

    def get_message(self):
        try:
            with open(self.filename, "r") as file:
                last_line = None
                for line in file:
                    last_line = line if line else "-:-"
                if ":" not in last_line:
                    last_line = "-:-"
                return last_line
        except:
            return "-:-"

    def send_message(self, message):
        with open(self.filename, "a") as file:
            file.write(message)
            file.write("\n")
