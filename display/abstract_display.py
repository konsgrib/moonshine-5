from abc import ABC, abstractmethod


class AbstractDisplay(ABC):
    @abstractmethod
    def show_data(self, data):
        pass
