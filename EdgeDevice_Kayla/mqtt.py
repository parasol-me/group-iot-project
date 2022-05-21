import jsonpickle
import jsonpickle.unpickler as unpickler
import jsonpickle.util as util
import jsonpickle.tags as tags
import serial
import time
import paho.mqtt.client as mqtt
import paho.mqtt.publish as publish
import requests, json #for weather app

from threading import Thread #for threading

ser = serial.Serial('/dev/ttyS0', 9600)
client = mqtt.Client()

lightState = False

rpcRequestTopicPrefix = 'v1/devices/me/rpc/request/'
rpcResponseTopicPrefix = 'v1/devices/me/rpc/response/'
methodKey = 'method'
paramsKey = 'params'
setValueMethod = 'setValue'
getValueMethod = 'getValue'

#-----------GETTING WEATHER OFF THE INTERNET-----------------------------
BASE_URL = "https://api.openweathermap.org/data/2.5/weather?" #base URL
CITY = "Melbourne,au" #{city name},{country code}
API_KEY = "5f9c2b109dfc3b3a2f8afdf0647e9ce6"
URL = BASE_URL + "q=" + CITY + "&appid=" + API_KEY + "&units=metric" #default is Kelvin units
    
    #if outside temperature is lower then inside, turn on yellow light
    #if (temperature < 0):
    #    ser.write(b"2") #turn on yellow light
    #else:
     #   ser.write(b"4") #turn on green light   


def getAndPublishExternalTemp():
    while True:
        response = requests.get(URL) #http request
        print(response) #getting error 401, lacks valid authentication credentials

        if response.status_code == 200: #checking status of code
            
            data = response.json() #getting data in json
            main = data['main'] #getting main dict block
            temperature = main['temp'] #getting temperature. round(temperature, 1) #rounds to 1 decimal point
            report = data['weather']
            
            #show info in shell
            print(f"{CITY:-^30}") #eg. ----Melbourne-----
            print(f"Temperature: {temperature}") #eg. Temperature: f means is string literal
            print(f"Weather Report: {report[0]['description']}") #eg. Weather Report: Windy
            
            outsideTempPayload = OutsideTempPayload(temperature)
            client.publish("v1/devices/me/telemetry", jsonpickle.encode(outsideTempPayload, unpicklable=False))
                               
        else:
            print("Error in HTTP request") #print error
        time.sleep(5) #delay. Update weather widget every 5 seconds


class SoundPayload:
    def __init__(self, soundDetected):
        self.soundDetected = soundDetected

class OutsideTempPayload:
    def __init__(self, outsideTemp):
        self.outsideTemp = outsideTemp


#callback when client receives a CONNACK response from server   
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        # subscribe to rpc requests to switch the led manually
        client.subscribe(rpcRequestTopicPrefix + '+')
        
        #subscribe on_connect mean if we lose connection, reconnect sibscriptions are renewed
        print("connect to mqtt broker with result code " + str(rc))
    else:
        print("Bad connection Returned code=", rc)


def on_disconnect(client, userdata, rc):
    print("Disconnected from mqtt broker reason " + str(rc))


def on_message(client, userdata, msg):
    global lightState
    payload = jsonpickle.decode(msg.payload.decode())
    print("message received", str(payload))
    
    if (msg.topic.startswith(rpcRequestTopicPrefix) and payload[methodKey] == setValueMethod):
        ledFlag = int(payload[paramsKey])        
        ser.write(str(ledFlag).encode()) #turn on/off red light
        lightState = payload[paramsKey]
        
    if (msg.topic.startswith(rpcRequestTopicPrefix) and payload[methodKey] == getValueMethod):
        requestId = msg.topic.replace(rpcRequestTopicPrefix, "")
        client.publish(rpcResponseTopicPrefix + requestId, jsonpickle.encode(lightState, unpicklable=False))

def read_serial():
    global lightState
    while True:
        if (ser.inWaiting() > 0):
            try:
                soundResult = ser.readline().decode().strip()#strip removes end characters, decode turn to string, serial
                soundPayload = SoundPayload(soundResult)
                
                if(soundResult == "1"):
                    lightState = True
                else:
                    lightState = False
                #pushes serial data from arduino to thingsBoard
                #publish topic, payload=None, qos=0, retain=False
                client.publish("v1/devices/me/telemetry", jsonpickle.encode(soundPayload, unpicklable=False))

                print(soundResult)
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
    
    thread = Thread(target = getAndPublishExternalTemp)
    thread.start()
    
    read_serial()
       