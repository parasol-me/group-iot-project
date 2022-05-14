
//LED pin
int redLEDPin = 9;

//Sound Sensor pin
int micPin = A0;
//int digitalPin = 11;
int sensorValue = 0;
int DigitalState = 0;

void setup() {
  //Baud rate
  Serial.begin(9600);

  //LED
  pinMode(redLEDPin, OUTPUT);
  //Set intial LED state
  digitalWrite(redLEDPin, LOW);

}

void loop() {


  //---- Sound Sensor Siren -----
  sensorValue = analogRead(micPin);
  //DigitalState = digitalRead(digitalPin);
  Serial.println (sensorValue, DEC); //analogueRead from microphone sound sensor

  if(sensorValue > 522) //if sound analogue detects highvoltage (eg. loud sounds) then turn red light on
    {
      digitalWrite(redLEDPin, HIGH);
    } else
    {
      digitalWrite(redLEDPin, LOW);
    }
  delay(1000);


}
