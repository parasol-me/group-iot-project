import serial
import time
import paho.mqtt.client as mqtt

client = mqtt.Client()

def on_connect(client, userdata, flags, rc):
  print("Connected to mqtt broker with result code " + str(rc))
  client.subscribe("/edge_device_daniel/data")

def on_disconnect(client, userdata, rc):
    print("Disconnected from to mqtt broker reason " + str(rc))

def on_message(client, userdata, msg):
    print(msg.topic + " " + str(msg.payload))

    # TODO: publish should be caused by user mutation via API
    # this is just for testing
    if (msg.topic == "/edge_device_daniel/data"):
      client.publish("/edge_device_daniel/control", "5")

if __name__ == '__main__':
    # connect to mqtt broker
    client.on_connect = on_connect
    client.on_disconnect = on_disconnect
    client.on_message = on_message
    client.connect("192.168.0.152", 1883, 60)
    client.loop_forever()

    # TODO start API server