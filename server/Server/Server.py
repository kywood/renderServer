from abc import ABC, abstractmethod

class IServer(ABC):

    @abstractmethod
    def add_controller(self, controller) -> "IServer":
        ...

    @abstractmethod
    def build(self):
        ...