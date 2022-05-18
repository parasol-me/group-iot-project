import jsonpickle
import serial
import paho.mqtt.client as mqtt
import json

device = '/dev/ttyS0'
node = serial.Serial(device, 9600)
THINGSBOARD_HOST = 'mqtt.thingsboard.cloud'
ACCESS_TOKEN = 'Lwk3HImfyOcrrQxfyD5h'
client = mqtt.Client()
fan_state = False
thresholdValue = 24.00

ThresholdKey = 'Threshold'


class AttributeState:
    def __init__(self, fanToggle):
        self.fanToggle = fanToggle

class TempPayload:
  def __init__(self, temp):
    self.temp = temp #change self.temp = temp to self.temp = 23(value) to test

class TempThreshold:
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
sharedAttributesKey = 'shared'

def on_connect(client, userdata, flags, rc):
  print("Connected to to mqtt broker with result code " + str(rc))
  client.subscribe("v1/devices/me/attributes") #subscribes to 
  client.subscribe("v1/devices/me/rpc/request/+") #subscribes to the
  client.subscribe("v1/devices/me/attributes/response/+") #
  client.publish("v1/devices/me/attributes/request/1", '{{"{}": "{}"}}'.format(sharedKeysKey, ThresholdKey))   
  client.publish("v1/devices/me/telemetry", jsonpickle.encode(tempThreshold, unpicklable=False))
  
def on_disconnect(client, userdata, rc):
    print("Disconnected from to mqtt broker reason " + str(rc))

def on_message(client, userdata, msg):
    
    print ('Topic: ' + msg.topic + '\nMessage: ' + str(msg.payload))
    global thresholdValue
    global fan_state
    data = json.loads(msg.payload)
    if(msg.topic == 'v1/devices/me/attributes/response/1'):
        thresholdValue = float(data["shared"]["Threshold"])
        
        
        
    if(msg.topic == 'v1/devices/me/attributes'):
        if (ThresholdKey in data):
            thresholdValue = float(data["Threshold"])
    if(msg.topic.startswith("v1/devices/me/rpc/request/")):
        if(data["method"]=="getValue"):
            print(data)
            requestId = msg.topic.replace("v1/devices/me/rpc/request/", "")
            responseTopic = "v1/devices/me/rpc/response/" + requestId
            data["params"] = fan_state
            print(data)
            var1 = jsonpickle.encode(fan_state, unpicklable=False)
            print (var1)
            client.publish(responseTopic, var1)
            
        if(data["method"]=="setValue"):
            fanToggle = (data["params"])
            print(data)
            fan_state = fanToggle
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
    global fan_state
    check = ""
    fanToggleCheck = "1"
    while True:
        if (node.inWaiting() > 0):
            try:
                temperature = node.readline().decode("utf-8").strip()
                temperature = float(temperature)
                humidity = node.readline().decode("utf-8").strip()
                tempPayload = TempPayload(temperature)
                client.publish("v1/devices/me/telemetry", jsonpickle.encode(tempPayload, unpicklable=False))
                print("Temperature is: " + str(temperature))
                print("Threshold Value is: " + str(thresholdValue))
                print("\n")
                if(temperature >= thresholdValue):
                    node.write(b"1")
                    fan_state = True
                    check = "true"
                    while fanToggleCheck == "1":
                        print("Temperature is greater than " + str(thresholdValue) + " fan has been switched on")
                        fanToggleCheck += "1"
                elif(temperature < thresholdValue) and (check =="true"):
                    node.write(b"2")
                    fan_state = False
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
