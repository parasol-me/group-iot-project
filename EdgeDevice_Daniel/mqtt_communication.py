import jsonpickle
import jsonpickle.unpickler as unpickler
import jsonpickle.util as util
import jsonpickle.tags as tags
import serial
import time
import paho.mqtt.client as mqtt
import paho.mqtt.publish as publish

class AttributeState:
  def __init__(self, ldrLowerBound, ldrUpdateFrequencySeconds):
    self.ldrLowerBound = ldrLowerBound
    self.ldrUpdateFrequencySeconds = ldrUpdateFrequencySeconds

class LdrPayload:
  def __init__(self, ldr):
    self.ldr = ldr

ser = serial.Serial('/dev/ttyS0', 9600)
client = mqtt.Client()

ldrLedFlagPrefix = 'ldrLedFlag:'
ldrUpdateFrequencySecondsPrefix = 'ldrUpdateFrequencySeconds:'

ldrLowerBoundKey = 'ldrLowerBound'
ldrUpdateFrequencySecondsKey = 'ldrUpdateFrequencySeconds'

ldrLedStatusKey = 'ldrLedStatus'
sharedKeysKey = 'sharedKeys'
sharedAttributesKey = 'shared'

attributeState = AttributeState(150, 5)
ldrPayload = LdrPayload(0)
attributeStateProcessUpdate = AttributeState(True, True)

def on_connect(client, userdata, flags, rc):
  print("Connected to to mqtt broker with result code " + str(rc))

  # subscribe to attribute updates
  client.subscribe("v1/devices/me/attributes")

  # get initial attribute values on startup
  client.subscribe('v1/devices/me/attributes/response/+')
  client.publish('v1/devices/me/attributes/request/1', '{{"{}": "{},{}"}}'.format(sharedKeysKey, ldrLowerBoundKey, ldrUpdateFrequencySecondsKey))

def on_disconnect(client, userdata, rc):
    print("Disconnected from to mqtt broker reason " + str(rc))

def on_message(client, userdata, msg):
    attributes = jsonpickle.decode(msg.payload.decode("utf-8"))
    global attributeState
    global attributeStateProcessUpdate

    # process attribute updates
    if (msg.topic == "v1/devices/me/attributes"):
        if ldrLowerBoundKey in attributes:
            attributeState.ldrLowerBound = int(attributes[ldrLowerBoundKey])
            print(ldrLowerBoundKey + " updated to " + str(attributes[ldrLowerBoundKey]))
            attributeStateProcessUpdate.ldrLowerBound = True
        if ldrUpdateFrequencySecondsKey in attributes:
            attributeState.ldrUpdateFrequencySeconds = int(attributes[ldrUpdateFrequencySecondsKey])
            print(ldrUpdateFrequencySecondsKey + " updated to " + str(attributes[ldrUpdateFrequencySecondsKey]))
            attributeStateProcessUpdate.ldrUpdateFrequencySeconds = True

    # process intial attribute values
    if (msg.topic == "v1/devices/me/attributes/response/1"):
        attributes = attributes[sharedAttributesKey]
        attributeState.ldrLowerBound = int(attributes[ldrLowerBoundKey])
        attributeState.ldrUpdateFrequencySeconds = int(attributes[ldrUpdateFrequencySecondsKey])
        print(ldrLowerBoundKey + " initial value is " + str(attributes[ldrLowerBoundKey]))
        print(ldrUpdateFrequencySecondsKey + " initial value is " + str(attributes[ldrUpdateFrequencySecondsKey]))
        attributeStateProcessUpdate.ldrLowerBound = True
        attributeStateProcessUpdate.ldrUpdateFrequencySeconds = True

def read_serial():
    while True:
        global attributeStateProcessUpdate
        global attributeState
        global ldrPayload
        currentLdr = ldrPayload.ldr
        ldrLowerBound = attributeState.ldrLowerBound
        if (ser.inWaiting() > 0):
            try:
                newLdr = int(ser.readline().decode("utf-8").strip())
                global writeAttributeUpdates
                newLdrPayload = LdrPayload(newLdr)
                

                if (newLdr < ldrLowerBound and currentLdr >= ldrLowerBound):
                    ser.write("{}{}\n".format(ldrLedFlagPrefix, 1).encode("utf-8"))
                    client.publish("v1/devices/me/attributes", '{{"{}": {}}}'.format(ldrLedStatusKey, True))

                if (newLdr >= ldrLowerBound and currentLdr < ldrLowerBound):
                    ser.write("{}{}\n".format(ldrLedFlagPrefix, 0).encode("utf-8"))
                    client.publish("v1/devices/me/attributes", '{{"{}": {}}}'.format(ldrLedStatusKey, False))

                ldrPayload = newLdrPayload

                # publish ldr sensor data to cloud
                client.publish("v1/devices/me/telemetry", jsonpickle.encode(ldrPayload, unpicklable=False))
                print(newLdr)
            except Exception as e:
                print(e)

        if (currentLdr < ldrLowerBound and attributeStateProcessUpdate.ldrLowerBound):
            ser.write("{}{}\n".format(ldrLedFlagPrefix, 1).encode("utf-8"))
            client.publish("v1/devices/me/attributes", '{{"{}": {}}}'.format(ldrLedStatusKey, True))
            attributeStateProcessUpdate.ldrLowerBound = False

        if (currentLdr >= ldrLowerBound and attributeStateProcessUpdate.ldrLowerBound):
            ser.write("{}{}\n".format(ldrLedFlagPrefix, 0).encode("utf-8"))
            client.publish("v1/devices/me/attributes", '{{"{}": {}}}'.format(ldrLedStatusKey, False))
            attributeStateProcessUpdate.ldrLowerBound = False

        if (attributeStateProcessUpdate.ldrUpdateFrequencySeconds):
            ldrUpdateFrequencySeconds = attributeState.ldrUpdateFrequencySeconds
            ser.write("{}{}\n".format(ldrUpdateFrequencySecondsPrefix, ldrUpdateFrequencySeconds).encode("utf-8"))
            attributeStateProcessUpdate.ldrUpdateFrequencySeconds = False

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