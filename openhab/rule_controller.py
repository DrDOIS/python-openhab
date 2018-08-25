# -*- coding: utf-8 -*-
import time
import sys


import openhab.rule as Rule
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

    rule_list = []
    triggers = {}

    commmand_events = {}

    previous_item_state = {} # All items are "uninitialized" before receiving an update
    status_events = {}

    def __init__(self, client):
        self.client = client
        self.mqtt_client = None

    # Initializes an mqtt client. If you want to use your own, just call item_received_command and item_changed directly
    def enable_mqtt_client(self, broker, port, statePublishTopic, commandPublishTopic, item_string = "${item}"):
        self.mqtt_client = mqtt.MqttClient()
        self.mqtt_client.set_broker(broker)
        self.mqtt_client.set_port(port)

        command_item_index = self.get_topic_index(commandPublishTopic, item_string)
        state_item_index = self.get_topic_index(statePublishTopic, item_string)

        state_subscription_topic = statePublishTopic.replace(item_string, "+")
        command_subscription_topic = commandPublishTopic.replace(item_string, "+")
        self.mqtt_client.subscribe_item_status(state_subscription_topic, state_item_index, self.item_changed)
        self.mqtt_client.subscribe_item_command(command_subscription_topic, command_item_index, self.item_received_command)

    def get_topic_index(self, topic, item_string):
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


    def item_received_command(self, item_name, command):
        print("Item " + item_name + " received command: " + command)
        for item_name_rule in self.commmand_events:
            if item_name == item_name_rule:
                self.trigger_events(self.commmand_events[item_name], command)

    def item_changed(self, item_name, new_state):
        if item_name not in self.previous_item_state:
            self.previous_item_state[item_name] = new_state
        else:
            if self.previous_item_state[item_name] == new_state:
                return

        print("Item " + item_name + " updated status to: " + new_state)
        for item_name_rule in self.status_events:
            if item_name == item_name_rule:
                self.trigger_events(self.commmand_events[item_name], new_state)

    def trigger_events(self, event_list, command: str):
        for event in event_list:
            if event.matches_condition(command):
                self.execute_rule(event.get_rule())

    def register_rule(self, rule: Rule):
        try:
            rule.setup(self.client, self)
            self.rule_list.append(rule)
        except Exception as e:
            if rule is not None:
                print("Setup of rule " + str(rule.__class__.__name__) + " threw an error: " + str(e))
            else:
                print("The registered rule is null")

    # Add trigger to list
    # Listformat:  itemname : [rule1, rule2...]
    def add_triggers(self, rule, trigger_list):
        for item in trigger_list:
            if not item.name in self.triggers:
                self.triggers[item.name] = []
            self.triggers[item.name].append(rule)

    def run(self):
        if self.mqtt_client is not None:
            self.mqtt_client.connect()

        while True:
            for rule in self.rule_list:
                pass
                #self.execute_rule(rule)
            print(".")
            time.sleep(1)


    def execute_rule(self, rule: Rule):
        if (rule.when()):
            rule.then()
            rule.test()

# Rule triggers
    def receivedCommand(self, rule_to_trigger: Rule, item, command=""):
        condition = Condition(rule_to_trigger)
        condition.set_condition(command)
        if item.name not in self.commmand_events:
            self.commmand_events[item.name] = []
        self.commmand_events[item.name].append(condition)

    # TODO make sure reveived state != previous state
    def changed(self, rule_to_trigger: Rule, item, status=""):
        condition = Condition(rule_to_trigger)
        condition.set_condition(status)
        if item.name not in self.status_events:
            self.status_events[item.name] = []
        self.status_events[item.name].append(condition)


