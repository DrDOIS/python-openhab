import abc

# Template for rules. Don't forget to import your modules somewhere

class Rule:
    def setup(self, openhab, rc):
        # All initialisation like registration goes here
        pass

    @abc.abstractmethod
    def when(self):
        # Check if certain conditions are met
        return False

    @abc.abstractmethod
    def then(self):
        # Perform actions
        pass

    def test(self):
        # Check if actions were performed correctly/successfully
        pass
