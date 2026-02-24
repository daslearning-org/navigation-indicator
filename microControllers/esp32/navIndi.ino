#include <FastLED.h>

#define NUM_LEDS 64
#define DATA_PIN 4
CRGB leds[NUM_LEDS];
bool ledState = false;

String Overtake[8] = {"00001110", "00001100", "01101010", "01100010", "01100010", "01100010", "00000100", "00001000"};
String RightIn[8] = {"00000000", "00000000", "00000100", "00000010", "11111111", "00000010", "00000100", "00000000"};
String UTurnRight[8] = {"00000000", "00111000", "01000100", "01000100", "01000100", "01010101", "01001110", "01000100"};
String UTurnLeft[8] = {"00000000", "00011100", "00100010", "00100010", "00100010", "10101010", "01110010", "00100010"};
String StopIn[8] = {"00000000", "00011000", "00111100", "01111110", "01111110", "00111100", "00011000", "00000000"};

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

void setup(){
  // Serial port for debugging purposes
  Serial.begin(115200);
  FastLED.addLeds<WS2812,DATA_PIN,GRB>(leds,NUM_LEDS);
  FastLED.clear();
  FastLED.setBrightness(3);
}

void loop(){
    // The main loop
    String modeSelected = "u-right";
    if (ledState){
        if (modeSelected == "right"){
            setLED(RightIn, CRGB::Orange);
        }
        else if (modeSelected == "allow-overtake"){
            setLED(Overtake, CRGB::Green);
        }
        else if (modeSelected == "u-right"){
            setLED(UTurnRight, CRGB::Orange);
        }
        FastLED.show();
    }
    else {
        FastLED.clear();
        FastLED.show();
    }

    ledState = !ledState;
    delay(500);
}
