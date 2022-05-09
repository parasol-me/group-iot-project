#include <dht.h>
dht DHT;

void setup() {
  Serial.begin(9600);
}

void loop() {
  int chk = DHT.read11(2); //Reads from pin 2
  Serial.print("Temperature = ");
  Serial.println(DHT.temperature);
  Serial.print("Humidity = ");
  Serial.println(DHT.humidity);
  delay(1000);
}
