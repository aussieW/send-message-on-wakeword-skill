#from mycroft.messagebus.client.ws import WebsocketClient
#from mycroft.util import create_daemon, wait_for_exit_signal, reset_sigint_handler
#from adapt.intent import IntentBuilder
from mycroft.skills.core import MycroftSkill, intent_handler
from mycroft.util.log import getLogger
from mycroft.api import DeviceApi

from mycroft.messagebus.message import Message

#from urllib2 import urlopen  # <<< not sure if this is required
import paho.mqtt.client as mqtt

LOGGER = getLogger(__name__)

ws = None

class wakewordskill(MycroftSkill):

    def __init__(self):
        MycroftSkill.__init__(self)
#        super(wakewordskill, self).__init__(name="wakewordskill")

        self.default_location = self.room_name
       
        self.protocol = self.config["protocol"]
        self.mqttssl = self.config["mqtt-ssl"]
        self.mqttca = self.config["mqtt-ca-cert"]
        self.mqtthost = self.config["mqtt-host"]
        self.mqttport = self.config["mqtt-port"]
        self.mqttauth = self.config["mqtt-auth"]
        self.mqttuser = self.config["mqtt-user"]
        self.mqttpass = self.config["mqtt-pass"]


        self.add_event('recognizer_loop:record_begin', self.handle_listener_started)
        self.add_event('recognizer_loop:record_end', self.handle_listener_stopped)


#        global ws
#        ws = WebsocketClient()
#        ws.on('recognizer_loop:record_begin', self.handle_record_begin)
#        ws.on('recognizer_loop:record_end', self.handle_record_end)
#        ws.on('recognizer_loop:utterance', self.handle_utterance)

#        create_daemon(ws.run_forever)
#        wait_for_exit_signal()

        LOGGER.info('WakeWordSkill loaded ........')
    
    def initialize(self):
        pass
		
    def mqtt_connect(self, topic=None):
        self.mqttc = mqtt.Client("MycroftAI_" + self.default_location + "_" + type(self).__name__)  # make unique by appending the location and the skill name.
        if (self.mqttauth == "yes"):
            mqttc.username_pw_set(self.mqttuser,self.mqttpass)
        if (self.mqttssl == "yes"):
            mqttc.tls_set(self.mqttca)
        LOGGER.info("AJW - connect to: " + self.mqtthost + ":" + str(self.mqttport) + " as MycroftAI_" + self.default_location + "_" + type(self).__name__)
        self.mqttc.connect(self.mqtthost,self.mqttport,10)
	# if s topic is provided then set up a listene
        if topic:
            self.mqttc.on_message = self.on_message
            self.mqttc.loop_start()
            self.mqttc.subscribe(topic)

    def mqtt_disconnect(self):
        self.mqttc.disconnect()

#    def handle_utterance(self, event):
#        pass

    def handle_listener_started(self, event):
        LOGGER.info('Wakeword detected - recording begin')
        self.mqtt_connect()
        self.mqtt_publish('kitchen/display/wakeword', 'begin')
        self.mqtt_disconnect()
        return

    def handle_listener_stopped(self, event):
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
