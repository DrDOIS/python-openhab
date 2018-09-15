#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#
# Georges Toth (c) 2016-present <georges@trypill.org>
#
# python-openhab is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# python-openhab is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with python-openhab.  If not, see <http://www.gnu.org/licenses/>.
#

import openhab.mqtt_client
from rule_light_bedroom import * # import required to find the rule subclasses
import test_rule # import required to find the rule subclasses

base_url = 'http://192.168.10.6:8080/rest'

openhab = openhab.OpenHAB(base_url)

# fetch all items
items = openhab.fetch_all_items()

# fetch all things
things = openhab.fetch_all_things()

#print all items which get data from things that are offline
# for item_name in items:
#
#     item_instance = items[item_name]
#     if item_instance.has_associated_thing():
#         thing = item_instance.get_associated_thing()
#
#         if not thing.is_online():
#             print("Item " + item_instance.name + " has offline thing. (" + thing.name + ")")

print("Testing ruleController...")


# test rule controller
ruco = openhab.get_rule_controller()

statePublishTopic="eventBus/state/${item}"
commandPublishTopic="eventBus/command/${item}"
ruco.enable_mqtt_client("192.168.10.6", 1883, statePublishTopic, commandPublishTopic)



ruco.run_forever()