import jsonpickle
import serial
import paho.mqtt.client as mqtt

device = '/dev/ttyS0'
node = serial.Serial(device, 9600)
THINGSBOARD_HOST = 'mqtt.thingsboard.cloud'
ACCESS_TOKEN = 'Lwk3HImfyOcrrQxfyD5h'
client = mqtt.Client()

class TempPayload:
  def __init__(self, temp):
    self.temp = temp #change self.temp = temp to self.temp = 23(value) to test

def on_connect(client, userdata, flags, rc):
  print("Connected to to mqtt broker with result code " + str(rc))
  client.subscribe("v1/devices/me/1")

def on_disconnect(client, userdata, rc):
    print("Disconnected from to mqtt broker reason " + str(rc))

print("Publishing Data To the Cloud via MQTT")    
def read_serial():
    while True:
        if (node.inWaiting() > 0):
            try:
                temperature = node.readline().decode("utf-8").strip()
                humidity = node.readline().decode("utf-8").strip()
                tempPayload = TempPayload(temperature)
                client.publish("v1/devices/me/telemetry", jsonpickle.encode(tempPayload, unpicklable=False))        
                print(temperature)
            except Exception as e:
                print(e)

if __name__ == '__main__':
    client.on_connect = on_connect
    client.on_disconnect = on_disconnect
    client.username_pw_set(ACCESS_TOKEN)
    client.connect(THINGSBOARD_HOST, 1883, 60)
    client.loop_start()

    read_serial()
