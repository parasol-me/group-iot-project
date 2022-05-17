import jsonpickle
import serial
import paho.mqtt.client as mqtt
import json

device = '/dev/ttyS0'
node = serial.Serial(device, 9600)
THINGSBOARD_HOST = 'mqtt.thingsboard.cloud'
ACCESS_TOKEN = 'Lwk3HImfyOcrrQxfyD5h'
client = mqtt.Client()
fan_state = "false"

class AttributeState:
    def __init__(self, fanToggle):
        self.fanToggle = fanToggle

class TempPayload:
  def __init__(self, temp):
    self.temp = temp #change self.temp = temp to self.temp = 23(value) to test

fanTogglePrefix = 'fanToggleFlag'
fanToggleKey = 'fanToggle'
fanToggleStatusKey = 'fanToggleStatus'
sharedKeysKey = 'sharedKeys'
sharedAttributesKey = 'shared'

attributeState = AttributeState(False)
fanPayload = TempPayload(0)
attributeStateProcessUpdate = AttributeState(True)

def on_connect(client, userdata, flags, rc):
  print("Connected to to mqtt broker with result code " + str(rc))
  client.subscribe("v1/devices/me/1")
  client.subscribe("v1/devices/me/rpc/request/+")

def on_disconnect(client, userdata, rc):
    print("Disconnected from to mqtt broker reason " + str(rc))

def on_message(client, userdata, msg):
#    print ('Topic: ' + msg.topic + '\nMessage: ' + str(msg.payload))
    data = json.loads(msg.payload)
    fanToggle = (data["params"]) 
    if (fanToggle == True):
        print("Fan override has been switched on")
        node.write(b"1")
        fanToggleCheck = 2
        
    elif (fanToggle == False):
        print ("Fan override is now off")
        node.write(b"2")
        fanToggleCheck = 2

print("Publishing Data To the Cloud via MQTT")    
def read_serial():
    check = ""
    fanToggleCheck = "1"
    while True:
        if (node.inWaiting() > 0):
            try:
                temperature = node.readline().decode("utf-8").strip()
                humidity = node.readline().decode("utf-8").strip()
                tempPayload = TempPayload(temperature)
                client.publish("v1/devices/me/telemetry", jsonpickle.encode(tempPayload, unpicklable=False))        
                print(temperature)
                
                if(temperature >= "24"):
                    node.write(b"1")
                    check = "true"
                    while fanToggleCheck == "1":
                        print("Temperature is greater than 24deg fan has been switched on")
                        fanToggleCheck += "1"
                elif(temperature <"24") and (check =="true"):
                    node.write(b"2")
                    print ("Temperature has return to normal levels fan is now off")
                    check = "false"
                    fanToggleCheck = "1"
            except Exception as e:
                print(e)

if __name__ == '__main__':
    client.on_connect = on_connect
    client.on_disconnect = on_disconnect
    client.on_message = on_message
    client.username_pw_set(ACCESS_TOKEN)
    client.connect(THINGSBOARD_HOST, 1883, 60)
    client.loop_start()

    read_serial()
