import datetime
from enum import Enum

from openhab.rule import Rule


WARM = 100
WARM_WHITE = 50
COLD_WHITE = 0

class LightBedroomRule(Rule):

    # @Override
    def setup(self, openhab, rc):
        self.movement_bedroom = openhab.get_item('gD_P_H_ES_AS')
        self.Light_Bed_brightness = openhab.get_item('Light_Bed_brightness')
        self.Light_Bed_temperature = openhab.get_item('Light_Bed_temperature')

        rc.receivedCommand(self, self.movement_bedroom)

    # @Override
    def when(self):
        return True

    # @Override
    def then(self):
        if self.movement():
            self.switch_light_on()
        else:
            self.switch_light_off()

    def movement(self):
        return self.movement_bedroom.state == 'ON'

    def switch_light_on(self):
        light_color = WARM
        light_brightness = 0

        if (self.is_during_bedtime()):
            light_color = WARM
            light_brightness = 10
        else:
            light_color = COLD_WHITE
            light_brightness = 100

        self.Light_Bed_temperature.command(light_color)
        self.Light_Bed_brightness.command(light_brightness)

    def is_during_bedtime(self):
        current_hour = datetime.datetime.now().hour
        return current_hour >= 22 or current_hour < 7

    def switch_light_off(self):
        self.Light_Bed_brightness.command(0)

    # @Override
    def test(self):
        pass
