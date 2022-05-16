#define LDRLEDPIN 4
#define LDRPIN A0
int timerCount = 0;
int sensorReadFrequencySeconds = 5;
bool readSensors = false;

const String ldrLedFlagPrefix = "ldrLedFlag:";
const String ldrUpdateFrequencySecondsPrefix = "ldrUpdateFrequencySeconds:";

void setup() {
  pinMode(LDRLEDPIN, OUTPUT);
  Serial.begin(9600);

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
  sei();                     //Enable back the interrupts
}

void loop() {
  // read serial from edge device if available
  if (Serial.available() > 0) {

    // Read serial input
    String input = Serial.readStringUntil('\n');

    if (input.startsWith(ldrLedFlagPrefix)) {
      input.replace(ldrLedFlagPrefix, "");
      int ldrLedFlag = input.toInt();

      // turn on/off lights based on flag
      if (ldrLedFlag == 1) {
        digitalWrite(LDRLEDPIN, HIGH);
      } else if (ldrLedFlag == 0) {
        digitalWrite(LDRLEDPIN, LOW);
      }
    }

    if (input.startsWith(ldrUpdateFrequencySecondsPrefix)) {
      input.replace(ldrUpdateFrequencySecondsPrefix, "");
      int newSensorReadFrequencySeconds = input.toInt();

      // set the new frequency
      sensorReadFrequencySeconds = newSensorReadFrequencySeconds;
    }
  }

  if (readSensors) {
    // get ldr voltage from analogue sensor
    int ldrVoltage = analogRead(LDRPIN);

    // send to edge device
    Serial.println(ldrVoltage);

    readSensors = false;
  }
}

// 1000ms ISR
ISR(TIMER1_COMPA_vect){
  TCNT1  = 0; //First, set the timer back to 0 so it resets for next interrupt

  // by using a counter we can multiply the delay by {sensorReadFrequencySeconds} which is configurable
  if (timerCount < (sensorReadFrequencySeconds - 1)) {
    timerCount++;
    return;    
  }
  // reset counter now that the right delay is reached
  timerCount = 0;

  // use a flag to read sensor in the main loop instead
  readSensors = true;
}