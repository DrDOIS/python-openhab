import abc


class Rule:

    def setup(self, openhab, rc):
        # All initialisation like registration goes here
        pass

    @abc.abstractmethod
    def when(self):
        return False

    @abc.abstractmethod
    def then(self):
        pass

    def test(self):
        pass
