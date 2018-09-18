# -*- coding: utf-8 -*-
import threading
import time
import datetime
from os.path import dirname, basename, isfile
import glob
from openhab.rule import Rule
import openhab.mqtt_client as mqtt

class Condition:
    def __init__(self, rule):
        self.rule = rule
        self.condition = ""

    def set_condition(self, condition: str):
        self.condition = condition

    def matches_condition(self, condition: str):
        if self.condition == "":
            return True # Every command
        return condition == self.condition

    def get_rule(self):
        return self.rule


class RuleController:
    rule_list = [] # List of all rules

    # Structure of lists: Item_name: [rule_to_trigger1, rule_to_trigger2]
    commmand_events = {} # All events registered by .received_command(...)
    status_events = {} # All events registered by .changed(...)
    timer_events = {}

    previous_item_state = {} # All item states are "" before receiving an update

    def __init__(self, client):
        self.client = client
        self.mqtt_client = None

    # Initializes an mqtt client. If you want to use your own, just call item_received_command and item_changed directly
    def enable_mqtt_client(self, broker, port, statePublishTopic, commandPublishTopic, item_string = "${item}"):
        self.mqtt_client = mqtt.MqttClient()
        self.mqtt_client.set_broker(broker)
        self.mqtt_client.set_port(port)

        command_item_index = self.__get_topic_index(commandPublishTopic, item_string)
        state_item_index = self.__get_topic_index(statePublishTopic, item_string)

        state_subscription_topic = statePublishTopic.replace(item_string, "+")
        command_subscription_topic = commandPublishTopic.replace(item_string, "+")
        self.mqtt_client.subscribe_item_status(state_subscription_topic, state_item_index, self.item_changed)
        self.mqtt_client.subscribe_item_command(command_subscription_topic, command_item_index, self.item_received_command)

    def __get_topic_index(self, topic, item_string):
        topic_segments = topic.split("/")
        counter = 0
        for segment in topic_segments:
            if segment == item_string:
                return counter
            counter += 1
        return -1

    # Returns the mqtt_client. Is None if enable_mqtt_client was not called before!
    # You can change the on_message callback, but then you must call item_received_command and item_changed yourself
    def get_mqtt_client(self):
        return self.mqtt_client

    # Called when an item received a command
    def item_received_command(self, item_name, command):
        print("Item " + item_name + " received command: " + command)
        for item_name_rule in self.commmand_events:
            if item_name == item_name_rule:
                self.__trigger_events(self.commmand_events[item_name], command)

    # Called when an item changed
    def item_changed(self, item_name, new_state):
        if item_name not in self.previous_item_state:
            self.previous_item_state[item_name] = new_state
        else:
            if self.previous_item_state[item_name] == new_state:
                return

        print("Item " + item_name + " updated status to: " + new_state)
        for item_name_rule in self.status_events:
            if item_name == item_name_rule:
                self.__trigger_events(self.status_events[item_name], new_state)

    def __trigger_events(self, event_list, command: str):
        for event in event_list:
            if event.matches_condition(command):
                self.__execute_rule(event.get_rule())

    def __register_rule(self, rule: Rule):
        try:
            rule.setup(self.client, self)
            self.rule_list.append(rule)
        except Exception as e:
            if rule is not None:
                print("Setup of rule " + str(rule.__class__.__name__) + " threw an error: " + str(e))
            else:
                print("The registered rule is null")

    def run_forever(self, update_intervall = 60): # in seconds
        self.run()
        while True:
            time.sleep(update_intervall)
            # TODO update items?

    def run(self):
        self.load_rules()

        if self.mqtt_client is not None:
            self.mqtt_client.connect()

    def load_rules(self):
        modules = glob.glob("rules/*.py")
        __all__ = [basename(f)[:-3] for f in modules if isfile(f) and not f.endswith('__init__.py')]
        for rule in __all__:
            globals()[rule] = __import__("rules." + rule)

        rules = [cls() for cls in Rule.__subclasses__()]
        for rule in rules:
            self.__register_rule(rule)
            print("Rule '" + str(rule.__class__.__name__) + "' registered.")


    def __execute_rule(self, rule: Rule):
        try:
            if (rule.when()):
                rule.then()
                rule.test()
        except Exception as e:
            if rule is not None:
                print("Execution of rule " + str(rule.__class__.__name__) + " threw an error: " + str(e))
            else:
                print("The registered rule is null")


# Rule triggers. Called by the Rule subclasses
    def received_command(self, rule_to_trigger: Rule, item, command=""):
        condition = Condition(rule_to_trigger)
        condition.set_condition(command)
        if item.name not in self.commmand_events:
            self.commmand_events[item.name] = []
        self.commmand_events[item.name].append(condition)

    def changed(self, rule_to_trigger: Rule, item, status=""):
        condition = Condition(rule_to_trigger)
        condition.set_condition(status)
        if item.name not in self.status_events:
            self.status_events[item.name] = []
        self.status_events[item.name].append(condition)

    # Not sure if cron will be implemented or if a simpler approach should be used

    # Defines the time the rule should be triggerd.
    # Only triggers once, so make sure to recall this function if it should trigger periodically
    def trigger_at(self, rule_to_trigger: Rule, time: datetime):
        time_to_trigger = time.replace(tzinfo=None)
        now = datetime.datetime.now()
        delay = (time_to_trigger - now).total_seconds()
        if (delay <= 0):
            print("The trigger time for rule " + str(rule_to_trigger.__class__.__name__) + " is in the past!")
        else:
            threading.Timer(delay, self.__execute_rule(rule_to_trigger)).start()