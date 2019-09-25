from mycroft.skills.core import MycroftSkill, intent_handler
from mycroft.util.log import getLogger
from mycroft.api import DeviceApi

from mycroft.messagebus.message import Message

import paho.mqtt.client as mqtt

LOGGER = getLogger(__name__)

ws = None

class wakewordskill(MycroftSkill):

    def __init__(self):
        MycroftSkill.__init__(self)

        self.default_location = self.room_name
       
        self.protocol = self.config["protocol"]
        self.mqttssl = self.config["mqtt-ssl"]
        self.mqttca = self.config["mqtt-ca-cert"]
        self.mqtthost = self.config["mqtt-host"]
        self.mqttport = self.config["mqtt-port"]
        self.mqttauth = self.config["mqtt-auth"]
        self.mqttuser = self.config["mqtt-user"]
        self.mqttpass = self.config["mqtt-pass"]


#        global ws
#        ws = WebsocketClient()
#        ws.on('recognizer_loop:record_begin', self.handle_record_begin)
#        ws.on('recognizer_loop:record_end', self.handle_record_end)
#        ws.on('recognizer_loop:utterance', self.handle_utterance)

#        create_daemon(ws.run_forever)
#        wait_for_exit_signal()

        LOGGER.info('WakeWordSkill loaded ........')
    
    def initialize(self):
        self.add_event('recognizer_loop:record_begin', self.handle_listener_started)
        self.add_event('recognizer_loop:record_end', self.handle_listener_stopped)
        self.add_event('recognizer_loop:utterance', self.handle_utterance)
        self.add_event('speak', self.handle_speak)

		
    def mqtt_connect(self, topic=None):
        self.mqttc = mqtt.Client("MycroftAI_" + self.default_location + "_" + type(self).__name__)  # make unique by appending the location and the skill name.
        if (self.mqttauth == "yes"):
            self.mqttc.username_pw_set(self.mqttuser,self.mqttpass)
        if (self.mqttssl == "yes"):
            self.mqttc.tls_set(self.mqttca)
        LOGGER.info("AJW - connect to: " + self.mqtthost + ":" + str(self.mqttport) + " as MycroftAI_" + self.default_location + "_" + type(self).__name__)
        self.mqttc.connect(self.mqtthost,self.mqttport,10)
	# if s topic is provided then set up a listene
        if topic:
            self.mqttc.on_message = self.on_message
            self.mqttc.loop_start()
            self.mqttc.subscribe(topic)

    def mqtt_disconnect(self):
        self.mqttc.disconnect()

    def handle_speak(self, message):
        LOGGER.info('Mycroft speech detected: ' + str(message.data.get('utterance')))
        self.mqtt_connect()
        self.mqtt_publish('kitchen/display/utterance', str(message.data.get('utterance')))
        self.mqtt_disconnect()
        return

    def handle_utterance(self, message):
        LOGGER.info('Utterance detected: ' + str(message.data.get('utterances')))
#        self.mqtt_connect()
#        self.mqtt_publish('kitchen/display/utterance', str(message.data.get('utterances')[0]))
#        self.mqtt_disconnect()
        return

    def handle_listener_started(self, message):
        LOGGER.info('Wakeword detected - recording begin')
        self.mqtt_connect()
        self.mqtt_publish('kitchen/display/wakeword', 'begin')
        self.mqtt_disconnect()
        return

    def handle_listener_stopped(self, message):
        self.mqtt_connect()
        self.mqtt_publish('kitchen/display/wakeword', 'end')
        self.mqtt_disconnect()
        return

    def mqtt_publish(self, topic, msg):
        LOGGER.info("AJW: Published " + topic + ", " + msg)
        self.mqttc.publish(topic, msg)
		
    # from steve-mycroft wink skill
    @property	
    def room_name(self):
        # assume the "name" of the device is the "room name"
        device = DeviceApi().get()
        return device['description'].replace(' ', '_')


def create_skill():
    return wakewordskill()
