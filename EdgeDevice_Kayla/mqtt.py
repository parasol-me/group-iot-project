from typing import cast
import jsonpickle
import jsonpickle.unpickler as unpickler
import jsonpickle.util as util
import jsonpickle.tags as tags
import serial
import time
import paho.mqtt.client as mqtt
import paho.mqtt.publish as publish

ser = serial.Serial('/dev/ttyS0', 9600)
client = mqtt.Client()

#ldrLowerBoundKey = 'ldrLowerBound'
#ldrLoldrUpdateFrequencySecondsKey = 'ldrUpdateFrequencySecondsKey

#sharedAttributeKey = 'shared'

class SoundPayload:
    def __init__(self, sound):
        self.sound = sound
   
#callback when client receives a CONNACK response from server   
def on_connect(client, userdata, flags, rc):
    #subscribe on_connect mean if we lose connection, reconnect sibscriptions are renewed
    print("connect to mqtt broker with result code " + str(rc))
    #client.subscribe("v1/devices/me/attributes")
    #client.subscribe('v1/devices/me/attributes/response/+')
    #client.publish('v1/devices/me/attributes/request/1', '{sharedKeys":"' + ldrLowerBoundKey + ',' + ldrLoldrUpdateFrequencySecondsKey + '"}')
    #soundPayload = SoundPayload(45)
    #client.publish('v1/devices/me/telemetry', '{"sound":"' + soundPayload + '"}')
    #client.publish("v1/devices/me/telemetry", jsonpickle.encode(soundPayload, unpicklable=False))
    #client.subscribe("v1/devices/me/1")

def on_disconnect(client, userdata, rc):
    print("Disconnected from mqtt broker reason " + str(rc))

def on_message(client, userdata, msg):
    payload = jsonpickle.decode(msg.payload.decode("utf-8"))
    
    #if(msg.topic == "v1/devices/me/attributes"):
     #   if ldrLowerBoundKey in payload:
     #       print(ldrLowerBoundKey + " update to " + str(payload[ldrLoldrUpdateFrequencySecondsKey]))
     #   if  ldrLoldrUpdateFrequencySecondsKey in payload:   
     #       print(ldrLoldrUpdateFrequency + " intial vallue is " + str(attributes[ldrLoldrUpdateFrequencySecondsKey]))
    #if (msg.topic == "v1/devices/me/attributes/response/1"):
     #   attributes = payload[sharedAttributesKey]
    #    print(ldrLowerBoundKey + " intial value is " + str(attributes[ldrLowerBoundKey]))
     #   print(ldrLoldrUpdateFrequencySecondsKey + " intial value is " + str(attribute[ldrLoldrUpdateFrequencySecondsKey]))
        

def read_serial():
    while True:
        if (ser.inWaiting() > 0):
            try:
                line = ser.readline().decode("utf-8").strip()#strip removes end characters, decode turn to string, serial
                soundPayload = SoundPayload(line)
                client.publish("v1/devices/me/telemetry", jsonpickle.encode(soundPayload, unpicklable=False))
                print(line)
            except Exception as e:
                print(e)
                
            time.sleep(0.01)
            
if __name__ == '__main__':
    #connect to mqtt broker
    client.on_connect = on_connect
    client.on_disconnect = on_disconnect
    client.on_message = on_message
    client.username_pw_set("Xlmx6TEPeK68GIl9q4gz") #Access Token
    client.connect("mqtt.thingsBoard.cloud", 1883, 60)
    client.loop_start()
    
    read_serial()
