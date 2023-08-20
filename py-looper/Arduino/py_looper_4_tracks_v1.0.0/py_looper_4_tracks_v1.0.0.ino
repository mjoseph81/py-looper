/* 
 *  FILE    :   py_looper_4_tracks_v1.0.0.ino
 *  AUTHOR  :   Matt Joseph
 *  DATE    :   8/17/2023
 *  VERSION :   1.0.0
 *  
 *
 *  DESCRIPTION
 *  https://www.instructables.com/id/DIY-Chewie-Monsta-Looper-Based-on-Ed-Sheerans/
 *  
 *  
 *  
 *  REV HISTORY
 *  1.0)  Initial release
 *  
  */



#define NUM_BUTTONS  9

//UNO or MEGA 2650 PIN ASSIGNMENTS
//GPIO Pin assignments for each button
const uint8_t btn_rec_play  = 3;  //REC-PLAY
const uint8_t btn_reset     = 4;  //RESET
const uint8_t btn_mult_stop = 5;  //MULT-STOP
const uint8_t btn_clear     = 6;  //CLEAR
const uint8_t btn_track1    = 7;  //TRACK 1
const uint8_t btn_track2    = 8;  //TRACK 2
const uint8_t btn_track3    = 9;  //TRACK 3
const uint8_t btn_mode      = 10; //MODE
const uint8_t btn_track4    = 11; //TRACK 4

/*
const uint8_t volLED = 12;

const uint8_t t1_green_led  = 48;
const uint8_t t1_red_led    = 49;
const uint8_t t2_green_led  = 50;
const uint8_t t2_red_led    = 51;
const uint8_t t3_green_led  = 52;
const uint8_t t3_red_led    = 53;

const uint8_t recLED        = 43;
const uint8_t playLED       = 42;
*/


//array for the button pins
const uint8_t buttons[NUM_BUTTONS] = {btn_mode, btn_reset, btn_clear, btn_rec_play, btn_mult_stop, btn_track1, btn_track2, btn_track3, btn_track4};

//MIDI values for each button
const uint8_t btn_press_cmd[NUM_BUTTONS] = {90, 91, 92, 93, 94, 95, 96, 97, 98};

uint8_t btnEval[NUM_BUTTONS] = {0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF};
uint8_t priorBtnEval[NUM_BUTTONS] = {0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF};


// Retrigger and debouce
const int minRetriggerTime = 250;  //Min millis between 2 button press
unsigned long btnLastPressTime[NUM_BUTTONS] = {0,0,0,0,0,0,0,0,0};  
unsigned long modeLastPressTime = 0;

/*
* Check if the current press is a valid and not a bounce of signal
* Ignore button press before minRetriggerTime ms
*/
bool retriggerTimeExpired(unsigned long lastPressTime)
{
    if(millis() - lastPressTime >= minRetriggerTime)
    {
        return true;
    }else{
        return false;
    }
}

/* 
 *  Sends a MIDI control command. Doesn't check to see that cmd is greater than 127, or that data values are less than 127:
 *  first parameter is the event type, combined with the channel.
 *  Second parameter is the control number number (0-119).
 *  Third parameter is the control value (0-127).
*/

void sendCmd(uint8_t channel, uint8_t command, int8_t value) {
  Serial.write(0xB0 | (channel-1));
  Serial.write(command);
  Serial.write(value);
}

void setup() {
  // Set MIDI baud rate:
  Serial.begin(31250);
  
  // set up buttons, they are "active-low" so set to "PULLUP"
  for (int i = 0; i < NUM_BUTTONS; i++){
      pinMode(buttons[i], INPUT_PULLUP);
  }
  
  /*
  // set the LED pins as output:
  pinMode(recLED, OUTPUT);
  pinMode(playLED, OUTPUT);

  // set up the TRACK LEDs
  pinMode(t1_green_led, OUTPUT);
  pinMode(t1_red_led, OUTPUT);
  pinMode(t2_green_led, OUTPUT);
  pinMode(t2_red_led, OUTPUT);
  pinMode(t3_green_led, OUTPUT);
  pinMode(t3_red_led, OUTPUT);

  //Track LEDs are "active-low" so init to HIGH so they are OFF
  digitalWrite(t1_green_led, HIGH);
  digitalWrite(t1_red_led, HIGH);
  digitalWrite(t2_green_led, HIGH);
  digitalWrite(t2_red_led, HIGH);
  digitalWrite(t3_green_led, HIGH);
  digitalWrite(t3_red_led, HIGH);
  */

}

void loop() {
  // put your main code here, to run repeatedly:
  readButtons();
}


void readButtons()
{
  //Save copy of last button evaluated values
  memcpy(priorBtnEval, btnEval, NUM_BUTTONS*sizeof(uint8_t));    

  //Read the rest of the buttons
  for (int i = 0; i < NUM_BUTTONS; i++)
  {
      btnEval[i] = digitalRead(buttons[i]);                       
  }

  //Check for button presss and send correct MIDI control command
  for( int i=0;i<NUM_BUTTONS;i++){
     if (btnEval[i] == 0 && retriggerTimeExpired(btnLastPressTime[i])){
        if(btnEval[i] != priorBtnEval[i]){
            sendCmd(1, btn_press_cmd[i], 127);
            //Serial.println("Button " + (String)i + " pressed");
        }
        btnLastPressTime[i] = millis();
     }
  }
  
  delay(5); 
}
