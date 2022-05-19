import jsonpickle
import time
import paho.mqtt.client as mqtt
from state import (
  LdrPayload, THINGSBOARD_HOST, ACCESS_TOKEN, attributeState, 
  attributeStateProcessUpdate, attributeUpdatesTopic, attributeResponseSubscribeTopic, 
  attributeRequestTopic,sharedKeysKey, ldrLowerBoundKey, ldrUpdateFrequencySecondsKey,
  attributeResponseMessageTopic, sharedAttributesKey, ldrLedFlagPrefix,
  ldrLedStatusKey, ser, client, ldrUpdateFrequencySecondsPrefix, telemetryTopic, 
  ldrLowerBoundPrefix, rpcRequestTopicPrefix, methodKey, setValueMethod, paramsKey
)

def writeToNode(prefix, value):
  ser.write("{}{}\n".format(prefix, value).encode())

def on_connect(client, userdata, flags, rc):
  print("Connected to mqtt broker with result code " + str(rc))

  # subscribe to attribute updates
  client.subscribe(attributeUpdatesTopic)

  # get initial attribute values on startup
  client.subscribe(attributeResponseSubscribeTopic)
  client.publish(attributeRequestTopic, '{{"{}": "{},{}"}}'.format(sharedKeysKey, ldrLowerBoundKey, ldrUpdateFrequencySecondsKey))

  # subscribe to rpc requests to switch the led manually
  client.subscribe(rpcRequestTopicPrefix + '+')

def on_disconnect(client, userdata, rc):
  print("Disconnected from mqtt broker reason " + str(rc))

def on_message(client, userdata, msg):
  payload = jsonpickle.decode(msg.payload.decode())
  global attributeState
  global attributeStateProcessUpdate

  # recieve attribute updates and save to state
  if (msg.topic == attributeUpdatesTopic):
    attributes = payload
    if ldrLowerBoundKey in payload:
      attributeState.ldrLowerBound = int(attributes[ldrLowerBoundKey])
      print(ldrLowerBoundKey + " updated to " + str(attributeState.ldrLowerBound))

      # set flag for serial thread to process updates
      attributeStateProcessUpdate.ldrLowerBound = True
    if ldrUpdateFrequencySecondsKey in attributes:
      attributeState.ldrUpdateFrequencySeconds = int(attributes[ldrUpdateFrequencySecondsKey])
      print(ldrUpdateFrequencySecondsKey + " updated to " + str(attributeState.ldrUpdateFrequencySeconds))

      # set flag for serial thread to process updates
      attributeStateProcessUpdate.ldrUpdateFrequencySeconds = True

  # recieve intial attribute values and save to state on startup
  if (msg.topic == attributeResponseMessageTopic):
    attributes = payload[sharedAttributesKey]
    attributeState.ldrLowerBound = int(attributes[ldrLowerBoundKey])
    attributeState.ldrUpdateFrequencySeconds = int(attributes[ldrUpdateFrequencySecondsKey])
    print(ldrLowerBoundKey + " initial value is " + str(attributeState.ldrLowerBound))
    print(ldrUpdateFrequencySecondsKey + " initial value is " + str(attributeState.ldrUpdateFrequencySeconds))

    # set flag for serial thread to process updates
    attributeStateProcessUpdate.ldrLowerBound = True
    attributeStateProcessUpdate.ldrUpdateFrequencySeconds = True

  if (msg.topic.startswith(rpcRequestTopicPrefix) and payload[methodKey] == setValueMethod):
    ldrLedFlag = payload[paramsKey]
    writeToNode(ldrLedFlagPrefix, int(ldrLedFlag))


def process_attribute_updates():
  global attributeStateProcessUpdate
  global attributeState

  # ldr lower bound state is stored on the iot node, update it on change
  if (attributeStateProcessUpdate.ldrLowerBound):
    writeToNode(ldrLowerBoundPrefix, attributeState.ldrLowerBound)
    # reset update flag
    attributeStateProcessUpdate.ldrLowerBound = False

  # update frequency state is stored on the iot node, update it on change
  if (attributeStateProcessUpdate.ldrUpdateFrequencySeconds):
    writeToNode(ldrUpdateFrequencySecondsPrefix, attributeState.ldrUpdateFrequencySeconds)
    # reset update flag
    attributeStateProcessUpdate.ldrUpdateFrequencySeconds = False

def read_serial():
  while True:
    if (ser.inWaiting() > 0):
      try:
        message = ser.readline().decode().strip()

        if (message.startswith(ldrLedFlagPrefix)):
          ldrLedFlag = int(message.replace(ldrLedFlagPrefix, ''))

          # keep cloud server informed on the state of the led
          client.publish(attributeUpdatesTopic, '{{"{}": {}}}'.format(ldrLedStatusKey, bool(ldrLedFlag)))
        else:
          newLdr = int(message)
          ldrPayload = LdrPayload(newLdr)

          # publish ldr sensor data to cloud
          client.publish(telemetryTopic, jsonpickle.encode(ldrPayload, unpicklable=False))
          print(newLdr)
      except Exception as e:
        print(e)
    # write the result of changed attrributes to iot node
    process_attribute_updates()

    # avoid high cpu usage by allowing the process scheduler to switch context when nothing is happening
    time.sleep(0.01)

if __name__ == '__main__':
  # connect to mqtt broker
  client.on_connect = on_connect
  client.on_disconnect = on_disconnect
  client.on_message = on_message
  client.username_pw_set(ACCESS_TOKEN)
  client.connect(THINGSBOARD_HOST, 1883, 60)
  client.loop_start()

  # read and write serial to/from iot node
  read_serial()