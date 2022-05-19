#define LDR_LED_PIN 4
#define LDR_SENSOR_PIN A0
int timerCount = 0;
int sensorReadFrequencySeconds = 5;
int ldrLowerBound = 150;
bool readSensor = false;
int ldr = 0;
bool overridePreviousLdrCheck = true;

const String ldrLedFlagPrefix = "ldrLedFlag:";
const String ldrUpdateFrequencySecondsPrefix = "ldrUpdateFrequencySeconds:";
const String ldrLowerBoundPrefix = "ldrLowerBound:";

void setup() {
  // initialise led pin and serial connection
  pinMode(LDR_LED_PIN, OUTPUT);
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

void writeFlagToDigitalOutPinAndPublish(int pin, bool value) {
  // turn on/off based on flag
  if (value) {
    digitalWrite(pin, HIGH);
  } else {
    digitalWrite(pin, LOW);
  }

  // publish changes to edge server via serial
  Serial.println(ldrLedFlagPrefix + value);
}

void evaluateLdrAndPublish() {
  // get ldr from analogue sensor
  int newLdr = analogRead(LDR_SENSOR_PIN);

  // turn led on/off dependant on lower bound and previous value to avoid wasted serial communication
  // overridePreviousLdrCheck can force an update, useful for startup and lower bound changes
  if (newLdr < ldrLowerBound && (overridePreviousLdrCheck || ldr >= ldrLowerBound)) {
    writeFlagToDigitalOutPinAndPublish(LDR_LED_PIN, true);
  } else if (newLdr >= ldrLowerBound && (overridePreviousLdrCheck || ldr < ldrLowerBound)) {
    writeFlagToDigitalOutPinAndPublish(LDR_LED_PIN, false);
  }

  // reset force update state
  overridePreviousLdrCheck = false;

  // update previous value with new
  ldr = newLdr;

  // send to edge device
  Serial.println(ldr);
}

void readAndProcessSerialInput() {
  // read serial from edge device if available
  if (Serial.available() > 0) {

    // Read serial input
    String input = Serial.readStringUntil('\n');

    // read the prefix to determine message intent
    // then strip the prefix and process the value
    if (input.startsWith(ldrLedFlagPrefix)) {
      input.replace(ldrLedFlagPrefix, "");
      bool ldrLedFlag = (bool)input.toInt();
      writeFlagToDigitalOutPinAndPublish(LDR_LED_PIN, ldrLedFlag);

    } else if (input.startsWith(ldrUpdateFrequencySecondsPrefix)) {
      input.replace(ldrUpdateFrequencySecondsPrefix, "");
      sensorReadFrequencySeconds = input.toInt();

    } else if (input.startsWith(ldrLowerBoundPrefix)) {
      input.replace(ldrLowerBoundPrefix, "");
      ldrLowerBound = input.toInt();

      // set override flag so that the new lower bound can override a manual toggle
      overridePreviousLdrCheck = true;
      evaluateLdrAndPublish();
    }
  }
}

void loop() {
  readAndProcessSerialInput();

  // update delay has past
  if (readSensor) {
    evaluateLdrAndPublish();
    // reset flag
    readSensor = false;
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

  // use a flag to publish sensor data in main loop instead
  readSensor = true;
}