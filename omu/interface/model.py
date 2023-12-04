import abc


class Model[T](abc.ABC):
    @abc.abstractmethod
    def json(self) -> T:
        ...

    @abc.abstractmethod
    def __str__(self) -> str:
        ...

    def __repr__(self) -> str:
        return str(self)
