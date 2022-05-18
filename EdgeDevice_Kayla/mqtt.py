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

lightState = False

class SoundPayload:
    def __init__(self, soundDetected):
        self.soundDetected = soundDetected
   
#callback when client receives a CONNACK response from server   
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        #subscribe on_connect mean if we lose connection, reconnect sibscriptions are renewed
        print("connect to mqtt broker with result code " + str(rc))
    else:
        print("Bad connection Returned code=", rc)

def on_disconnect(client, userdata, rc):
    print("Disconnected from mqtt broker reason " + str(rc))

def on_message(client, userdata, msg):
    payload = jsonpickle.decode(msg.payload.decode())
    print("message received", str(payload))
        

def read_serial():
    while True:
        if (ser.inWaiting() > 0):
            try:
                soundResult = ser.readline().decode().strip()#strip removes end characters, decode turn to string, serial
                soundPayload = SoundPayload(soundResult)
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
    
    read_serial()
