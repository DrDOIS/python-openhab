import paho.mqtt.client as mqtt

class MqttClient:

    def __init__(self):
        self.broker = None
        self.port = 1883
        self.subscription_list = []
        self.callback = None

        self.status_item_index = None
        self.status_topic = None
        self.status_callback = None

        self.command_item_index = None
        self.command_topic = None
        self.command_callback = None

    # The callback for when the client receives a CONNACK response from the server.
    def on_connect(self, client, userdata, flags, rc):
        for topic in self.subscription_list:
            client.subscribe(topic)


    # The callback for when a PUBLISH message is received from the server.
    def on_message(self, client, userdata, msg):
        topic_segments = msg.topic.split("/")

        if (mqtt.topic_matches_sub(self.status_topic, msg.topic)):
            item_name = topic_segments[self.status_item_index]
            self.status_callback(item_name, msg.payload.decode('utf-8'))
        elif (mqtt.topic_matches_sub(self.command_topic, msg.topic)):
            item_name = topic_segments[self.command_item_index]
            self.command_callback(item_name, msg.payload.decode('utf-8'))

    def set_broker(self, broker):
        self.broker = broker

    def set_port(self, port):
        self.port = port

    def subscribe(self, topic):
        self.subscription_list.append(topic)

    def subscribe_item_status(self, status_topic, name_index, status_callback):
        self.status_topic = status_topic
        self.status_item_index = name_index
        self.status_callback = status_callback
        self.subscribe(status_topic)

    def subscribe_item_command(self, command_topic, name_intex, command_callback):
        self.command_topic = command_topic
        self.command_item_index = name_intex
        self.command_callback = command_callback
        self.subscribe(command_topic)

    def set_callback(self, callback):
        self.callback = callback

    def connect(self):
        client = mqtt.Client()
        client.on_connect = self.on_connect
        client.on_message = self.on_message
        retval = client.connect(self.broker, self.port, 60)
        client.loop_start()
        if retval != 0:
            print("Error connecting to MQTT-Broker")
        return client