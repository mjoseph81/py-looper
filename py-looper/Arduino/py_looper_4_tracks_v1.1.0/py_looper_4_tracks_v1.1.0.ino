/* 
 *  FILE    :   py_looper_4_tracks_v1.1.0.ino
 *  AUTHOR  :   Matt Joseph
 *  DATE    :   8/21/2023
 *  VERSION :   1.1.0
 *  
 *
 *  DESCRIPTION
 *  https://www.instructables.com/Py-Looper
 *  
 *  
 *  
 *  REV HISTORY
 *  1.0.0)  Initial release
 *  1.1.0)  Added support to Rx MIDI messages to get LED info
 *  
  */



#define NUM_BUTTONS  9
#define OFF     0
#define GREEN   1
#define RED     2
#define AMBER   3




//MEGA 2650 PIN ASSIGNMENTS
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



const uint8_t t1_green_led  = 48;
const uint8_t t1_red_led    = 49;
const uint8_t t2_green_led  = 50;
const uint8_t t2_red_led    = 51;
const uint8_t t3_green_led  = 52;
const uint8_t t3_red_led    = 53;
const uint8_t t4_green_led  = 46;
const uint8_t t4_red_led    = 47;

const uint8_t recLED        = 43;
const uint8_t playLED       = 42;



//array for the button pins
const uint8_t buttons[NUM_BUTTONS] = {btn_mode, btn_reset, btn_clear, btn_rec_play, btn_mult_stop, btn_track1, btn_track2, btn_track3, btn_track4};

//MIDI values for each button
const uint8_t btn_press_cmd[NUM_BUTTONS] = {90, 91, 92, 93, 94, 95, 96, 97, 98};
const uint8_t LED_CC = 10;

//Evaluate buffers for each button
uint8_t btnEval[NUM_BUTTONS] = {0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF};
uint8_t priorBtnEval[NUM_BUTTONS] = {0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF,0xFF};

//buffer for incoming LED message
uint8_t MIDI_MSG[4] = {0,0,0,0};

//array to store LED values from serial msg
uint8_t LED_VALS[5] = {0,0,0,0,0};

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
  pinMode(t4_green_led, OUTPUT);
  pinMode(t4_red_led, OUTPUT);

  //Track LEDs are "active-low" so init to HIGH so they are OFF
  digitalWrite(t1_green_led, HIGH);
  digitalWrite(t1_red_led, HIGH);
  digitalWrite(t2_green_led, HIGH);
  digitalWrite(t2_red_led, HIGH);
  digitalWrite(t3_green_led, HIGH);
  digitalWrite(t3_red_led, HIGH);
  digitalWrite(t4_green_led, HIGH);
  digitalWrite(t4_red_led, HIGH);
  digitalWrite(recLED, HIGH);
  digitalWrite(playLED, HIGH);
  

}

void loop() {
  // put your main code here, to run repeatedly:

  //check if there is data on the serial channel and read it.  If not then read the buttons.
  if(Serial.available()){
      recMidiCmd();
  }
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


void recMidiCmd(){
  do{
    if(Serial.available()){
      //read 4 bytes for the full LED serial msg
      Serial.readBytes(MIDI_MSG, 4);

      parse_led_bytes(MIDI_MSG[2],MIDI_MSG[3]);

        if(MIDI_MSG[1]==LED_CC){
            setTrackLED(9, LED_VALS[0]);    //set MODE LED
            setTrackLED(0, LED_VALS[1]);    //set T1 LED
            setTrackLED(1, LED_VALS[2]);    //set T2 LED
            setTrackLED(2, LED_VALS[3]);    //set T3 LED
            setTrackLED(3, LED_VALS[4]);    //set T4 LED
        }
    }
  }
  while(Serial.available() >3);
}

void setTrackLED(int track_index, int color){
  //track_index:  0=track1, 1=track2, 2=track3, 3=track4, 9=mode
  //color: 0=OFF, 1=GREEN, 2=RED, 3=AMBER

  //Track 1
  if(track_index==0){
      if(color==OFF){
          digitalWrite(t1_green_led, HIGH);
          digitalWrite(t1_red_led, HIGH);
      }else if(color==GREEN){
          digitalWrite(t1_green_led, LOW);
          digitalWrite(t1_red_led, HIGH);
      }else if(color==RED){
          digitalWrite(t1_green_led, HIGH);
          digitalWrite(t1_red_led, LOW);
      }else if(color==AMBER){
          digitalWrite(t1_green_led, LOW);
          digitalWrite(t1_red_led, LOW);
      }else{
          digitalWrite(t1_green_led, HIGH);
          digitalWrite(t1_red_led, HIGH);
      }
  //Track 2
  }else if(track_index==1){
      if(color==OFF){
          digitalWrite(t2_green_led, HIGH);
          digitalWrite(t2_red_led, HIGH);
      }else if(color==GREEN){
          digitalWrite(t2_green_led, LOW);
          digitalWrite(t2_red_led, HIGH);
      }else if(color==RED){
          digitalWrite(t2_green_led, HIGH);
          digitalWrite(t2_red_led, LOW);
      }else if(color==AMBER){
          digitalWrite(t2_green_led, LOW);
          digitalWrite(t2_red_led, LOW);
      }else{
          digitalWrite(t2_green_led, HIGH);
          digitalWrite(t2_red_led, HIGH);
      }
  //Track 3
  }else if(track_index==2){
      if(color==OFF){
          digitalWrite(t3_green_led, HIGH);
          digitalWrite(t3_red_led, HIGH);
      }else if(color==GREEN){
          digitalWrite(t3_green_led, LOW);
          digitalWrite(t3_red_led, HIGH);
      }else if(color==RED){
          digitalWrite(t3_green_led, HIGH);
          digitalWrite(t3_red_led, LOW);
      }else if(color==AMBER){
          digitalWrite(t3_green_led, LOW);
          digitalWrite(t3_red_led, LOW);
      }else{
          digitalWrite(t3_green_led, HIGH);
          digitalWrite(t3_red_led, HIGH);
      }
      //Track 4
  }else if(track_index==3){
      if(color==OFF){
          digitalWrite(t4_green_led, HIGH);
          digitalWrite(t4_red_led, HIGH);
      }else if(color==GREEN){
          digitalWrite(t4_green_led, LOW);
          digitalWrite(t4_red_led, HIGH);
      }else if(color==RED){
          digitalWrite(t4_green_led, HIGH);
          digitalWrite(t4_red_led, LOW);
      }else if(color==AMBER){
          digitalWrite(t4_green_led, LOW);
          digitalWrite(t4_red_led, LOW);
      }else{
          digitalWrite(t4_green_led, HIGH);
          digitalWrite(t4_red_led, HIGH);
      }
  //MODE
  }else if(track_index==9){
      if(color==OFF){
          digitalWrite(recLED, HIGH);
          digitalWrite(playLED, HIGH);
      }else if(color==GREEN){
          digitalWrite(recLED, HIGH);
          digitalWrite(playLED, LOW);
      }else if(color==RED){
          digitalWrite(recLED, LOW);
          digitalWrite(playLED, HIGH);
      }else if(color==AMBER){
          digitalWrite(recLED, LOW);
          digitalWrite(playLED, LOW);
      }else{
          digitalWrite(recLED, HIGH);
          digitalWrite(playLED, HIGH);
      }
  }else {
      //do nothing
  }
}

void parse_led_bytes(uint8_t mode_byte, uint8_t track_byte){
    LED_VALS[0] = mode_byte;                      //MODE LED
    LED_VALS[1] = (track_byte & B00000011);       //T1 LED
    LED_VALS[2] = (track_byte & B00001100) >> 2;  //T2 LED
    LED_VALS[3] = (track_byte & B00110000) >> 4;  //T3 LED
    LED_VALS[4] = (track_byte & B11000000) >> 6;  //T4 LED
}
