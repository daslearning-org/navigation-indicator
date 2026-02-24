#include <FastLED.h>

#define NUM_LEDS 64
#define DATA_PIN 4
CRGB leds[NUM_LEDS];
bool ledState = false;
bool awake = false;
bool blink = true;
unsigned long previousMillis = 0;
int interval = 800; // Can be changed programatically
String modeSelected = "none";

String Overtake[8] = {"00001110", "00001100", "00001010", "01100001", "01100001", "01100001", "01100010", "00000100"};
String RightIn[8] = {"00000000", "00000100", "00000010", "11111111", "10000010", "10000100", "10000000", "10000000"};
String LeftIn[8] = {"00000000", "00100000", "01000000", "11111111", "01000001", "00100001", "00000001", "00000001"};
String UTurnRight[8] = {"00000000", "00111000", "01000100", "01000100", "01000100", "01010101", "01001110", "01000100"};
String UTurnLeft[8] = {"00000000", "00011100", "00100010", "00100010", "00100010", "10101010", "01110010", "00100010"};
String StopIn[8] = {"00000000", "00011000", "00111100", "01111110", "01111110", "00111100", "00011000", "00000000"};
String ParkIn[8] = {"01111000", "01111100", "01100100", "01111100", "01111000", "01100000", "01100000", "01100000"};


void setLED(String *chosen, const CRGB& color){
    // Set LEDs
    for(int i=0; i<8; i++){
      for(int j=0; j<8; j++){
        if(chosen[i][j] == '1'){
          leds[(8*i)+j] = color;
        }
      }
    }
}

void stopLED(){
    FastLED.clear();
    FastLED.show();
}

void setup(){
  // Serial port for debugging purposes
  Serial.begin(115200);
  FastLED.addLeds<WS2812,DATA_PIN,GRB>(leds,NUM_LEDS);
  FastLED.clear();
  FastLED.setBrightness(3);
}

void loop(){
    // The main loop
    if (ledState && awake){
        if (modeSelected == "right"){
            setLED(RightIn, CRGB::Orange);
        }
        else if (modeSelected == "left"){
            setLED(LeftIn, CRGB::Orange);
        }
        else if (modeSelected == "allow-overtake"){
            setLED(Overtake, CRGB::Green);
        }
        else if (modeSelected == "no-overtake"){
            setLED(Overtake, CRGB::Red);
        }
        else if (modeSelected == "u-right"){
            setLED(UTurnRight, CRGB::Orange);
        }
        else if (modeSelected == "u-left"){
            setLED(UTurnLeft, CRGB::Orange);
        }
        else if (modeSelected == "park"){
            setLED(ParkIn, CRGB::Orange);
        }
        FastLED.show();
    }
    else {
        FastLED.clear();
        FastLED.show();
    }

    // Debug: read from serial, will be replaced with actual api/ws
    if (Serial.available()) {
        modeSelected = Serial.readStringUntil('\n'); // Read until newline
        modeSelected.trim();
        modeSelected.toLowerCase();
        Serial.println("Entered text: " + modeSelected);
        if (modeSelected == "right" || modeSelected == "left" || 
            modeSelected == "allow-overtake" || modeSelected == "no-overtake" || 
            modeSelected == "u-right" || modeSelected == "u-left" || 
            modeSelected == "park"){
            stopLED();
            awake = true;
        }
        else if(modeSelected == "no-blink"){
            blink = false;
            ledState = true;
        }
        else if(modeSelected == "blink"){
            blink = true;
        }
    }

    // Timer loop
    unsigned long currentMillis = millis();
    if ((currentMillis - previousMillis >= interval) && blink) {
        previousMillis = currentMillis;
        ledState = !ledState;
    }
}
