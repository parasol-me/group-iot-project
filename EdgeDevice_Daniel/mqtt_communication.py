import serial
import time
import paho.mqtt.client as mqtt
import paho.mqtt.publish as publish

ser = serial.Serial('/dev/ttyS0', 9600)
client = mqtt.Client()

def on_connect(client, userdata, flags, rc):
  print("Connected to to mqtt broker with result code " + str(rc))
  client.subscribe("/edge_device_daniel/control")

def on_disconnect(client, userdata, rc):
    print("Disconnected from to mqtt broker reason " + str(rc))

def on_message(client, userdata, msg):
    print(msg.topic + " " + str(msg.payload))
    # TODO: set control variable for sending to IoT node via serial

def read_serial():
    while True:
        if (ser.inWaiting() > 0):
            try:
                line = ser.readline().decode("utf-8").strip()
                client.publish("/edge_device_daniel/data", line)
                print(line)
            except Exception as e:
                print(e)
            
        time.sleep(0.01)

if __name__ == '__main__':
    # connect to mqtt broker
    client.on_connect = on_connect
    client.on_disconnect = on_disconnect
    client.on_message = on_message
    client.connect("192.168.0.152", 1883, 60)
    client.loop_start()

    read_serial()