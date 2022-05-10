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

ldrLowerBoundKey = 'ldrLowerBound'
ldrLoldrUpdateFrequencySecondsKey = 'ldrUpdateFrequencySeconds'

sharedAttributesKey = 'shared'

class LdrPayload:
  def __init__(self, ldr):
    self.ldr = ldr

def on_connect(client, userdata, flags, rc):
  print("Connected to to mqtt broker with result code " + str(rc))
  client.subscribe("v1/devices/me/attributes")
  client.subscribe('v1/devices/me/attributes/response/+')
  client.publish('v1/devices/me/attributes/request/1', '{"sharedKeys":"' + ldrLowerBoundKey + ',' + ldrLoldrUpdateFrequencySecondsKey + '"}')
  client.subscribe("v1/devices/me/1")

def on_disconnect(client, userdata, rc):
    print("Disconnected from to mqtt broker reason " + str(rc))

def on_message(client, userdata, msg):
    payload = jsonpickle.decode(msg.payload.decode("utf-8"))
    if (msg.topic == "v1/devices/me/attributes"):
        if ldrLowerBoundKey in payload:
            print(ldrLowerBoundKey + " updated to " + str(payload[ldrLowerBoundKey]))
        if ldrLoldrUpdateFrequencySecondsKey in payload:
            print(ldrLoldrUpdateFrequencySecondsKey + " updated to " + str(payload[ldrLoldrUpdateFrequencySecondsKey]))
    if (msg.topic == "v1/devices/me/attributes/response/1"):
        attributes = payload[sharedAttributesKey]
        print(ldrLowerBoundKey + " initial value is " + str(attributes[ldrLowerBoundKey]))
        print(ldrLoldrUpdateFrequencySecondsKey + " initial value is " + str(attributes[ldrLoldrUpdateFrequencySecondsKey]))
    # TODO: set control variable for sending to IoT node via serial

def read_serial():
    while True:
        if (ser.inWaiting() > 0):
            try:
                line = ser.readline().decode("utf-8").strip()
                ldrPayload = LdrPayload(line)
                client.publish("v1/devices/me/telemetry", jsonpickle.encode(ldrPayload, unpicklable=False))
                print(line)
            except Exception as e:
                print(e)
            
        time.sleep(0.01)

if __name__ == '__main__':
    # connect to mqtt broker
    client.on_connect = on_connect
    client.on_disconnect = on_disconnect
    client.on_message = on_message
    client.username_pw_set("UHMYqEpthrVOHQn1PAr7")
    client.connect("mqtt.thingsboard.cloud", 1883, 60)
    client.loop_start()

    read_serial()