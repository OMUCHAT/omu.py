import abc


class Extension(abc.ABC):
    @abc.abstractmethod
    def initialize(self) -> None:
        ...

    @abc.abstractmethod
    def stop(self) -> None:
        ...
