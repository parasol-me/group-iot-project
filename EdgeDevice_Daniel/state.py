import paho.mqtt.client as mqtt
import serial

class AttributeState:
  def __init__(self, ldrLowerBound, ldrUpdateFrequencySeconds):
    self.ldrLowerBound = ldrLowerBound
    self.ldrUpdateFrequencySeconds = ldrUpdateFrequencySeconds

class LdrPayload:
  def __init__(self, ldr):
    self.ldr = ldr

THINGSBOARD_HOST = 'mqtt.thingsboard.cloud'
ACCESS_TOKEN = 'UHMYqEpthrVOHQn1PAr7'

attributeUpdatesTopic = 'v1/devices/me/attributes'
attributeRequestTopic = 'v1/devices/me/attributes/request/1'
attributeResponseSubscribeTopic = 'v1/devices/me/attributes/response/+'
attributeResponseMessageTopic = 'v1/devices/me/attributes/response/1'
telemetryTopic = 'v1/devices/me/telemetry'
rpcRequestTopicPrefix = 'v1/devices/me/rpc/request/'

ldrLedFlagPrefix = 'ldrLedFlag:'
ldrLowerBoundPrefix = 'ldrLowerBound:'
ldrUpdateFrequencySecondsPrefix = 'ldrUpdateFrequencySeconds:'

ldrLowerBoundKey = 'ldrLowerBound'
ldrUpdateFrequencySecondsKey = 'ldrUpdateFrequencySeconds'

ldrLedStatusKey = 'ldrLedStatus'
sharedKeysKey = 'sharedKeys'
sharedAttributesKey = 'shared'

methodKey = 'method'
paramsKey = 'params'
setValueMethod = 'setValue'

ser = serial.Serial('/dev/ttyS0', 9600)
client = mqtt.Client()

attributeState = AttributeState(150, 5)
attributeStateProcessUpdate = AttributeState(True, True)