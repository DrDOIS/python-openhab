import datetime
import pytz

from openhab.rule import Rule

class TestRule(Rule):

    # @Override
    def setup(self, openhab, rc):
        self.sunrise = openhab.get_item('Astro_Sunrise')
        self.is_holiday_switch = openhab.get_item('Holiday')

        rc.receivedCommand(self, self.is_holiday_switch, "ON")
        rc.changed(self, self.sunrise)
        rc.receivedCommand(self, self.is_holiday_switch)

    # @Override
    def when(self):
        return self.is_after_sunrise() and self.no_work()

    def no_work(self):
        return self.is_holiday() or self.is_weekend()

    def is_after_sunrise(self):
        sunrise_time = self.sunrise.state.replace(tzinfo=None) # get rid of timezone-awareness
        now = datetime.datetime.now()
        return now > sunrise_time

    def is_holiday(self):
        return self.is_holiday_switch.state == 'ON'

    def is_weekend(self):
        return datetime.datetime.today().weekday() >= 5

    # @Override
    def then(self):
        pass

    # @Override
    def test(self):
        pass
