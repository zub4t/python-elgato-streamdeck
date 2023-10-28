import abc
class CommandInterface(abc.ABC):
    @abc.abstractmethod
    def command(self):
        pass

 
