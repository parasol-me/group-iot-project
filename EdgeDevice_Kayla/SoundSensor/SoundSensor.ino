//LED pin
int redLEDPin = 9;

//Sound Sensor pin
int digitalPin = 2;
int sensorValue = 0;
int DigitalState = 0;
int Threshold = 522;

//interupt
bool readSensors;

void setup() {
  //Baud rate
  Serial.begin(9600);

  //Sound sensor
  pinMode(digitalPin, INPUT);

  //LED
  pinMode(redLEDPin, OUTPUT);
  //Set intial LED state
  digitalWrite(redLEDPin, LOW);


  //INTERUPT
  // ISR setup from Week 6 Task 4 tutorial
  cli();                      //stop interrupts for till we make the settings
  /*1. First we reset the control register to make sure we start with everything disabled.*/
  TCCR1A = 0;                 // Reset entire TCCR1A to 0 
  TCCR1B = 0;                 // Reset entire TCCR1B to 0
 
  /*2. We set the prescalar to the desired value by changing the CS10 CS12 and CS12 bits. */  
  TCCR1B |= B00000100;        //Set CS12 to 1 so we get prescalar 256  
  
  /*3. We enable compare match mode on register A*/
  TIMSK1 |= B00000010;        //Set OCIE1A to 1 so we enable compare match A 
  
  /*4. Set the value of register A to 31250*/
  OCR1A = 65535;             //Finally we set compare register A to this value  
  sei();
}

void loop() {

//--For control on thingsBoard to turn LED on and off--
//Check if there is serial input data available. 
  if (Serial.available()>0)
  {
    //Read serial input
    int value = Serial.read();
    if (value == '1')
    {
      digitalWrite(9,HIGH); //turn on red pin
    }
    else if (value == '0')
    {
      digitalWrite(9,LOW);
    }
  }

  //-- Sounds detected --
  int newDigitalState = digitalRead(digitalPin);

  if(newDigitalState != DigitalState)
  {
    
    if(readSensors == true)
    {
      Serial.println(newDigitalState);
      //newDigitalState = 0;
      readSensors = false;

      if(newDigitalState == 1){
        Serial.println(0);
      } 
    }

    if(newDigitalState == 1){
      digitalWrite(redLEDPin, HIGH);
    } else
    {
      digitalWrite(redLEDPin, LOW);
    }
  }
  DigitalState = newDigitalState; 
}


// 1000ms ISR
ISR(TIMER1_COMPA_vect){

  TCNT1  = 0; //First, set the timer back to 0 so it resets for next interrupt

  // use a flag to read sensor in the main loop instead
  readSensors = true;
}
