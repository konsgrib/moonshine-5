# gpio_stub.py
class GPIO:
    BOARD = None
    OUT = None
    IN = None
    HIGH = None
    LOW = None
    PUD_UP = None
    PUD_DOWN = None

    @staticmethod
    def setmode(mode):
        pass

    @staticmethod
    def setup(channel, state):
        pass

    @staticmethod
    def output(channel, state):
        pass

    @staticmethod
    def input(channel):
        return 0

    @staticmethod
    def cleanup():
        pass
