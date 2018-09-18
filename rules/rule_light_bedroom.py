import datetime

from openhab.rule import Rule

WARM = 100
WARM_WHITE = 50
COLD_WHITE = 0


def switch_light(brightness_dimmer, color_temperature_dimmer, movement_sensor, brightness_sensor):
    if not movement(movement_sensor):
        switch_light_off(brightness_dimmer)
    else:
        switch_light_on(brightness_dimmer, color_temperature_dimmer, brightness_sensor)

def movement(movement_sensor):
    return movement_sensor.state == 'ON'

def switch_light_off(brightness_dimmer):
    brightness_dimmer.command(0)

def switch_light_on(brightness_dimmer, color_temperature_dimmer, brightness_sensor):
    light_color = WARM
    light_brightness = 50

    if (is_during_night()):
        light_color = WARM
    else:
        light_color = COLD_WHITE

    if brightness_sensor is not None:
        if (light_required(brightness_sensor)):
            light_brightness = get_adequate_brightness(brightness_sensor)

    color_temperature_dimmer.command(light_color)
    brightness_dimmer.command(light_brightness)
    print("Switched light to " + str(light_brightness))

def is_during_night():
    current_hour = datetime.datetime.now().hour
    return current_hour >= 22 or current_hour < 7

def light_required(brightness_sensor):
    return brightness_sensor.state < 800

def get_adequate_brightness(brightness_sensor):
    return mapFromTo(brightness_sensor.state, 0,900,0,100)

def mapFromTo(sensor_val, in_min, in_max, out_min, out_max):
   y= (sensor_val - in_min) / (in_max - in_min) * (out_max - out_min) + out_min
   return y



class LightBedroomRule(Rule):
    # @Override
    def setup(self, openhab, rc):
        self.movement_bedroom = openhab.get_item('gD_P_H_ES_AS')
        self.Light_Bed_brightness = openhab.get_item('Light_Bed_brightness')
        self.Light_Bed_temperature = openhab.get_item('Light_Bed_temperature')

        rc.received_command(self, self.movement_bedroom)

    # @Override
    def when(self):
        return True

    # @Override
    def then(self):
        switch_light(self.Light_Bed_brightness, self.Light_Bed_temperature, self.movement_bedroom, None)

    # @Override
    def test(self):
        pass

class LightPcRoomRule(Rule):
    # @Override
    def setup(self, openhab, rc):
        self.movement_pcroom = openhab.get_item('gD_P_H_ES_PC')
        self.Light_PcRoom_brightness = openhab.get_item('Light_PcRoom_brightness')
        self.Light_PcRoom_temperature = openhab.get_item('Light_PcRoom_temperature')
        self.Lightsensor_PcRoom = openhab.get_item('Lightsensor_PcRoom')

        rc.received_command(self, self.movement_pcroom)

    # @Override
    def when(self):
        return True

    # @Override
    def then(self):
        switch_light(self.Light_PcRoom_brightness, self.Light_PcRoom_temperature, self.movement_pcroom,  self.Lightsensor_PcRoom)

    # @Override
    def test(self):
        pass