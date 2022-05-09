import serial
import paho.mqtt.publish as publish

ser = serial.Serial('/dev/ttyS0',9600)
print("Publishing Data to the Cloud via MQTT")
while True:
  line = ser.readline()
  publish.single("/edge_device_jason/data", line, hostname="192.168.1.26")
