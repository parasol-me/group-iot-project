import jsonpickle
import serial
import time
import paho.mqtt.client as mqtt
from shared_state import THINGSBOARD_HOST, attributeState, attributeStateProcessUpdate
from temperature_integration import startTemperatureClient

class LdrPayload:
  def __init__(self, ldr):
    self.ldr = ldr

ACCESS_TOKEN = 'UHMYqEpthrVOHQn1PAr7'
ser = serial.Serial('/dev/ttyS0', 9600)
client = mqtt.Client()

attributeUpdatesTopic = 'v1/devices/me/attributes'
attributeRequestTopic = 'v1/devices/me/attributes/request/1'
attributeResponseSubscribeTopic = 'v1/devices/me/attributes/response/+'
attributeResponseMessageTopic = 'v1/devices/me/attributes/response/1'
telemetryTopic = 'v1/devices/me/telemetry'

ldrLedFlagPrefix = 'ldrLedFlag:'
temperatureFanFlagPrefix = 'temperatureFanFlag:'
ldrUpdateFrequencySecondsPrefix = 'ldrUpdateFrequencySeconds:'

ldrLowerBoundKey = 'ldrLowerBound'
ldrUpdateFrequencySecondsKey = 'ldrUpdateFrequencySeconds'

ldrLedStatusKey = 'ldrLedStatus'
sharedKeysKey = 'sharedKeys'
sharedAttributesKey = 'shared'

ldrPayload = LdrPayload(0)

def on_connect(client, userdata, flags, rc):
  print("Connected to mqtt broker with result code " + str(rc))

  # subscribe to attribute updates
  client.subscribe(attributeUpdatesTopic)

  # get initial attribute values on startup
  client.subscribe(attributeResponseSubscribeTopic)
  client.publish(attributeRequestTopic, '{{"{}": "{},{}"}}'.format(sharedKeysKey, ldrLowerBoundKey, ldrUpdateFrequencySecondsKey))

def on_disconnect(client, userdata, rc):
    print("Disconnected from mqtt broker reason " + str(rc))

def on_message(client, userdata, msg):
    attributes = jsonpickle.decode(msg.payload.decode())
    global attributeState
    global attributeStateProcessUpdate

    # process attribute updates
    if (msg.topic == attributeUpdatesTopic):
        if ldrLowerBoundKey in attributes:
            attributeState.ldrLowerBound = int(attributes[ldrLowerBoundKey])
            print(ldrLowerBoundKey + " updated to " + str(attributes[ldrLowerBoundKey]))
            attributeStateProcessUpdate.ldrLowerBound = True
        if ldrUpdateFrequencySecondsKey in attributes:
            attributeState.ldrUpdateFrequencySeconds = int(attributes[ldrUpdateFrequencySecondsKey])
            print(ldrUpdateFrequencySecondsKey + " updated to " + str(attributes[ldrUpdateFrequencySecondsKey]))
            attributeStateProcessUpdate.ldrUpdateFrequencySeconds = True

    # process intial attribute values
    if (msg.topic == attributeResponseMessageTopic):
        attributes = attributes[sharedAttributesKey]
        attributeState.ldrLowerBound = int(attributes[ldrLowerBoundKey])
        attributeState.ldrUpdateFrequencySeconds = int(attributes[ldrUpdateFrequencySecondsKey])
        print(ldrLowerBoundKey + " initial value is " + str(attributes[ldrLowerBoundKey]))
        print(ldrUpdateFrequencySecondsKey + " initial value is " + str(attributes[ldrUpdateFrequencySecondsKey]))
        attributeStateProcessUpdate.ldrLowerBound = True
        attributeStateProcessUpdate.ldrUpdateFrequencySeconds = True

def bool_to_binary_int(value: bool) -> int:
    return 1 if value else 0
    

def switch_ldr_led(value: bool):
    ser.write("{}{}\n".format(ldrLedFlagPrefix, bool_to_binary_int(value)).encode())
    client.publish(attributeUpdatesTopic, '{{"{}": {}}}'.format(ldrLedStatusKey, value))

def process_attribute_updates():
    global attributeStateProcessUpdate
    global attributeState
    global ldrPayload
    currentLdr = ldrPayload.ldr
    ldrLowerBound = attributeState.ldrLowerBound

    if (currentLdr < ldrLowerBound and attributeStateProcessUpdate.ldrLowerBound):
            switch_ldr_led(True)
            attributeStateProcessUpdate.ldrLowerBound = False

    if (currentLdr >= ldrLowerBound and attributeStateProcessUpdate.ldrLowerBound):
        switch_ldr_led(False)
        attributeStateProcessUpdate.ldrLowerBound = False

    if (attributeStateProcessUpdate.temperatureFanStatus):
        ser.write("{}{}\n".format(temperatureFanFlagPrefix, bool_to_binary_int(attributeState.temperatureFanStatus)).encode())
        attributeStateProcessUpdate.temperatureFanStatus = False

    if (attributeStateProcessUpdate.ldrUpdateFrequencySeconds):
        ldrUpdateFrequencySeconds = attributeState.ldrUpdateFrequencySeconds
        ser.write("{}{}\n".format(ldrUpdateFrequencySecondsPrefix, ldrUpdateFrequencySeconds).encode())
        attributeStateProcessUpdate.ldrUpdateFrequencySeconds = False

def read_serial():
    while True:
        global attributeState
        global ldrPayload
        currentLdr = ldrPayload.ldr
        ldrLowerBound = attributeState.ldrLowerBound
        if (ser.inWaiting() > 0):
            try:
                newLdr = int(ser.readline().decode().strip())
                newLdrPayload = LdrPayload(newLdr)
                
                if (newLdr < ldrLowerBound and currentLdr >= ldrLowerBound):
                    switch_ldr_led(True)

                if (newLdr >= ldrLowerBound and currentLdr < ldrLowerBound):
                    switch_ldr_led(False)

                ldrPayload = newLdrPayload

                # publish ldr sensor data to cloud
                client.publish(telemetryTopic, jsonpickle.encode(ldrPayload, unpicklable=False))
                print(newLdr)
            except Exception as e:
                print(e)
        process_attribute_updates()
        time.sleep(0.01)

if __name__ == '__main__':
    # connect to mqtt broker
    client.on_connect = on_connect
    client.on_disconnect = on_disconnect
    client.on_message = on_message
    client.username_pw_set(ACCESS_TOKEN)
    client.connect(THINGSBOARD_HOST, 1883, 60)
    client.loop_start()
    startTemperatureClient()

    read_serial()