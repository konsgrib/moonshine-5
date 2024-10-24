from abc import ABC, abstractmethod


class TwoPinValue:
    def __init__(self, status_code, value, message):
        self.status_code = status_code
        self.value = value
        self.message = message

    def __repr__(self):
        return str(self.__dict__)


class AbstractTwoPin(ABC):
    @abstractmethod
    def set_state(self, new_state):
        pass

    @abstractmethod
    def get_value(self) -> TwoPinValue:
        pass
