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

lightState = False;

#ldrLowerBoundKey = 'ldrLowerBound'
#ldrLoldrUpdateFrequencySecondsKey = 'ldrUpdateFrequencySecondsKey



#class AttributeState:
#    def __init__(self, lightControl):
#        self.lightControl = lightControl

class SoundPayload:
    def __init__(self, sound):
        self.sound = sound
   
   
#lightControlPrefix = 'lightControlFlag'
#lightControlKey = 'lightControl'
#lightControlStatusKey = 'lightControlStatus'

#sharedKeysKey = 'sharedKeys'
#sharedAttributeKey = 'shared'

#attributeState = AttributeState(False)
#lightPayload = SoundPayload(0)
#attributeStateProcessUpdate = AttributeState(True)
   
   
#callback when client receives a CONNACK response from server   
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        #subscribe on_connect mean if we lose connection, reconnect sibscriptions are renewed
        print("connect to mqtt broker with result code " + str(rc))
        
        #subscribe to recieve RPC requests
        #client.subscribe("v1/devices/me/1")
        #client.subscribe("v1/devices/me/rpc/request/+")
    else:
        print("Bad connection Returned code=", rc)
    
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
    print("message received", str(payload))
    #for light control
    #if(lightControl == True):
     #   print("Light is on")
    #    node.write(b"1")
    #elif(lightControl == False):
     #   print("Light is off")
     #   node.write(b"2")
    #print("publishing data to cloud")    
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
                soundResult = ser.readline().decode("utf-8").strip()#strip removes end characters, decode turn to string, serial
                soundPayload = SoundPayload(soundResult)
                #pushes serial data from arduino to thingsBoard
                #oublish topic, payload=None, qos=0, retain=False
                client.subscribe("v1/devices/me/telemetry")
                client.publish("v1/devices/me/telemetry", jsonpickle.encode(soundPayload, unpicklable=False))
                #print(soundResult)
                
                #print("Pub")
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
