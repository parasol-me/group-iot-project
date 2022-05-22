#include <dht.h>
dht DHT;

void setup() {
  Serial.begin(9600);
  pinMode(4,OUTPUT);
}

void loop() {
  int chk = DHT.read11(2); //Reads from pin 2
  Serial.println(DHT.temperature);
  Serial.println(DHT.humidity);
  delay(1000);
  
  int message = Serial.read();
  if(message == '1'){
      digitalWrite(4,HIGH);
    }else if(message == '2'){
      digitalWrite(4,LOW);
    } 
}
