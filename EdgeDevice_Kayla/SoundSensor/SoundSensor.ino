
//LED pin
int redLEDPin = 9;
int yellowPin = 5;

//Sound Sensor pin
int micPin = A0;
int digitalPin = 2;
int sensorValue = 0;
int DigitalState = 0;
int Threshold = 522;

//Fan
int fanPin = 7;



void setup() {
  //Baud rate
  Serial.begin(9600);

  //Sound sensor
  pinMode(digitalPin, INPUT);

  //LED
  pinMode(redLEDPin, OUTPUT);
  pinMode(yellowPin, OUTPUT);
  //Set intial LED state
  digitalWrite(redLEDPin, LOW);
  digitalWrite(yellowPin, LOW);

  //Fan
  pinMode(fanPin, OUTPUT);

}

void loop() {


  //---- Sound Sensor Siren -----
  sensorValue = analogRead(micPin);
  DigitalState = digitalRead(digitalPin);
  //Serial.println (sensorValue, DEC); //analogueRead from microphone sound sensor

  //Serial.println(DigitalState);
  //digitalWrite(redLEDPin, DigitalState);

  if(DigitalState == 1)
  {
    Serial.println(DigitalState);
    //Serial.println(sensorValue);
    /*
    if(sensorValue > Threshold) //if sound analogue detects highvoltage (eg. loud sounds) then turn red light on
    {
      digitalWrite(redLEDPin, HIGH);
      
    } else
    {
      digitalWrite(redLEDPin, LOW);
    }
    //delay(250);
    */
  }

  
  //Fan
  digitalWrite(fanPin, LOW);

}
