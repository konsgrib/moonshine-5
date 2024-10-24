from abc import ABC, abstractmethod


class AbstractMessenger(ABC):
    @abstractmethod
    def get_message(self):
        pass

    @abstractmethod
    def send_message(self):
        pass
