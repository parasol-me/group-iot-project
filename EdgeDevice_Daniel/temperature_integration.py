import jsonpickle
import paho.mqtt.client as mqtt
from shared_state import THINGSBOARD_HOST, attributeState, attributeStateProcessUpdate

TEMPERATURE_ACCESS_TOKEN = 'Lwk3HImfyOcrrQxfyD5h'
client = mqtt.Client()

rpcRequestTopic = 'v1/devices/me/rpc/request/'

methodKey = 'method'
paramsKey = 'params'
setValueMethod = 'setValue'

def on_connect(client, userdata, flags, rc):
  print("Connected to temperature mqtt broker with result code " + str(rc))
  client.subscribe(rpcRequestTopic + '+')

def on_disconnect(client, userdata, rc):
  print("Disconnected from temperature mqtt broker reason " + str(rc))

def on_message(client, userdata, msg):
  payload = jsonpickle.decode(msg.payload.decode())
  global attributeState
  global attributeStateProcessUpdate
  if (msg.topic.startswith(rpcRequestTopic) and payload[methodKey] == setValueMethod):
    temperatureFanStatus = payload[paramsKey]
    attributeState.temperatureFanStatus = temperatureFanStatus
    attributeStateProcessUpdate.temperatureFanStatus = True


        

def startTemperatureClient():
  # connect to mqtt broker of temperature device
  client.on_connect = on_connect
  client.on_disconnect = on_disconnect
  client.on_message = on_message
  client.username_pw_set(TEMPERATURE_ACCESS_TOKEN)
  client.connect(THINGSBOARD_HOST, 1883, 60)
  client.loop_start()