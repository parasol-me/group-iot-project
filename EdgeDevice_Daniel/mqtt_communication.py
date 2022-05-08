import serial
import time
import paho.mqtt.client as mqtt
import paho.mqtt.publish as publish

ser = serial.Serial('/dev/ttyS0', 9600)
cloudClient = mqtt.Client()

def on_connect(client, userdata, flags, rc):
  print("Connected with result code " + str(rc))
  cloudClient.subscribe("/cloud_platform/control")

def on_message(client, userdata, msg):
    print(msg.topic + " " + str(msg.payload))

def read_serial():
    while True:
        if (ser.inWaiting() > 0):
            try:
                line = ser.readline().decode("utf-8").strip()
                # TODO: change ip address to that of cloud server
                publish.single("/cloud_platform/data", line, hostname="0.0.0.0")
                print(line)
            except Exception as e:
                print(e)
            
        time.sleep(0.01)

if __name__ == '__main__':
    cloudClient.on_connect = on_connect
    cloudClient.on_message = on_message
    # TODO: change ip address to that of cloud server
    cloudClient.connect("0.0.0.0", 1883, 60)
    cloudClient.loop_start()
    read_serial()