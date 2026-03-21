#include <FastLED.h>
#include <ArduinoJson.h>
#include <BLEDevice.h>
#include <BLEUtils.h>
#include <BLEServer.h>

#include "LittleFS.h"

#define NUM_LEDS 64
#define DATA_PIN 2 // D2 on Seeed Studio ESP32-C3 (tiny)
#define SERVICE_UUID        "4fafc201-1fb5-459e-8fcc-c5c9c331914b"
#define CHARACTERISTIC_UUID "beb5483e-36e1-4688-b7f5-ea07361b26a8"

//** Global variables */

// configs
const char* CONFIG_FILE = "/config.json";

struct Config {
  String ssid;
  String wifipass;
  String stearing;
  String mode;
};
Config appConfig;

// Flags
bool ledState = false;
bool awake = false;
bool blink = true;

// LED controls
CRGB leds[NUM_LEDS];
String modeSelected = "none";
String bleValue = "none";

// timer
unsigned long previousMillis = 0;
int interval = 800; // Can be changed programatically

// Display arrays for symbols
const String Overtake[] PROGMEM = {"00001110", "00001100", "00001010", "01100001", "01100001", "01100001", "01100010", "00000100"};
const String RightIn[] PROGMEM = {"00000000", "00000100", "00000010", "11111111", "10000010", "10000100", "10000000", "10000000"};
const String LeftIn[] PROGMEM = {"00000000", "00100000", "01000000", "11111111", "01000001", "00100001", "00000001", "00000001"};
const String UTurnRight[] PROGMEM = {"00000000", "00111000", "01000100", "01000100", "01000100", "01010101", "01001110", "01000100"};
const String UTurnLeft[] PROGMEM = {"00000000", "00011100", "00100010", "00100010", "00100010", "10101010", "01110010", "00100010"};
const String StopIn[] PROGMEM = {"10000001", "01000010", "00100100", "00011000", "00011000", "00100100", "01000010", "10000001"};
const String ParkIn[] PROGMEM = {"01111000", "01111100", "01100100", "01111100", "01111000", "01100000", "01100000", "01100000"};
const String OkIn[] PROGMEM = {"00000000", "01001001", "10101010", "10101100", "10101010", "01001001", "00000000", "00000000"};

//** Function definitions */

// Initialize the LittleFS
void initFS(){
  if (!LittleFS.begin()) {
  Serial.println("An error has occurred while mounting LittleFS!");
  }
  else{
  Serial.println("LittleFS mounted successfully");
  }
}

// Function to read the configuration from LittleFS
bool readConfigFile() {
  File configFile = LittleFS.open(CONFIG_FILE, "r");
  if (!configFile) {
    Serial.println("Failed to open config file for reading. File might not exist.");
    return false;
  }

  size_t size = configFile.size();
  if (size == 0) {
    Serial.println("Config file is empty.");
    configFile.close();
    return false;
  }

  StaticJsonDocument<256> doc; // Adjust size based on your JSON's complexity

  // Deserialize the JSON document
  DeserializationError error = deserializeJson(doc, configFile);
  configFile.close(); // Close the file after reading

  if (error) {
    Serial.print(F("deserializeJson() failed: "));
    Serial.println(error.f_str());
    return false;
  }

  // Extract values from the JSON document
  appConfig.ssid = doc["ssid"] | "";
  appConfig.wifipass = doc["wifipass"] | "";
  appConfig.stearing = doc["stearing"] | "right";
  appConfig.mode = doc["mode"] | "";

  return true;
}

// Function to save the configuration to LittleFS
bool saveConfigFile() {
  File configFile = LittleFS.open(CONFIG_FILE, "w"); // Open in write mode, will create if not exists or overwrite
  if (!configFile) {
    Serial.println("Failed to open config file for writing.");
    return false;
  }

  StaticJsonDocument<256> doc; // Adjust size based on your JSON's complexity

  // Populate the JSON document from the config struct
  doc["ssid"] = appConfig.ssid;
  doc["wifipass"] = appConfig.wifipass;
  doc["stearing"] = appConfig.stearing;
  doc["mode"] = appConfig.mode;

  // Serialize JSON to file
  if (serializeJson(doc, configFile) == 0) {
    Serial.println(F("Failed to write to file"));
    configFile.close();
    return false;
  }
  configFile.close();
  return true;
}

// bluetooth
class MyCallbacks: public BLECharacteristicCallbacks {
  void onWrite(BLECharacteristic *pCharacteristic) {
    String value = pCharacteristic->getValue();

    if (value.length() > 0) {
      bleValue = value;
    }
  }
};

class MyServerCallbacks: public BLEServerCallbacks {
  void onConnect(BLEServer* pServer) {
    Serial.println("Client Connected");
  }

  void onDisconnect(BLEServer* pServer) {
    Serial.println("Client Disconnected");
    BLEDevice::startAdvertising();   // this starts the BLE server again
  }
};

// Set LEDs
void setLED(const String *chosen, const CRGB& color){
  // for actual symbol display
  for(int i=0; i<8; i++){
    for(int j=0; j<8; j++){
      if(chosen[i][j] == '1'){
        leds[(8*i)+j] = color;
      }
    }
  }
}

void stopLED(){ // turn of the display
  FastLED.clear();
  FastLED.show();
}

void setDayNight(String timeFromBT){
  if (timeFromBT == "day"){
    FastLED.setBrightness(120);
  }
  else if (timeFromBT == "night"){
    FastLED.setBrightness(30);
  }
}

void setup(){
  // Setup the ESP32 board after boot
  Serial.begin(115200);
  Serial.println("Serial started");
  FastLED.addLeds<WS2812,DATA_PIN,GRB>(leds,NUM_LEDS);
  FastLED.clear();
  FastLED.setBrightness(50); // : default
  initFS();
  BLEDevice::init("NavEspBle");
  BLEServer *pServer = BLEDevice::createServer();
  pServer->setCallbacks(new MyServerCallbacks());

  BLEService *pService = pServer->createService(SERVICE_UUID);

  BLECharacteristic *pCharacteristic = pService->createCharacteristic(
                                         CHARACTERISTIC_UUID,
                                         BLECharacteristic::PROPERTY_READ |
                                         BLECharacteristic::PROPERTY_WRITE
                                       );

  pCharacteristic->setCallbacks(new MyCallbacks());
  pCharacteristic->setValue("Navigation Indicator");
  pService->start();
  BLEAdvertising *pAdvertising = BLEDevice::getAdvertising();
  pAdvertising->start();
  Serial.println("BLE Ready, now you can pair it with bluetooth! \n");
  if(readConfigFile()){
    Serial.println("App config: " + appConfig.mode); // to be used when config is needed
  }
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
    else if (modeSelected == "ok-overtake"){
      FastLED.clear();
      setLED(Overtake, CRGB::Green);
    }
    else if (modeSelected == "no-overtake"){
      FastLED.clear();
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
  else if(awake && modeSelected == "no-overtake"){
    FastLED.clear();
    setLED(StopIn, CRGB::Red);
    FastLED.show();
  }
  else if(awake && modeSelected == "ok-overtake"){
    FastLED.clear();
    setLED(OkIn, CRGB::Green);
    FastLED.show();
  }
  else {
    FastLED.clear();
    FastLED.show();
  }

  if (bleValue != "none") { // input from BLE
    bleValue.trim();
    bleValue.toLowerCase();
    Serial.println("Entered text: " + bleValue); // Debug
    if (bleValue == "right" || bleValue == "left" || 
      bleValue == "ok-overtake" || bleValue == "no-overtake" || 
      bleValue == "u-right" || bleValue == "u-left" || 
      bleValue == "park"){
      stopLED();
      awake = true;
      modeSelected = bleValue;
    }
    else if(bleValue == "off"){
      stopLED();
      awake = false;
    }
    else if(bleValue == "no-blink"){
      blink = false;
      ledState = true;
    }
    else if(bleValue == "blink"){
      blink = true;
    }
    else if(bleValue == "day" || bleValue == "night"){
      setDayNight(bleValue);
    }
    bleValue = "none";
  }

  // Timer loop
  unsigned long currentMillis = millis();
  if ((currentMillis - previousMillis >= interval) && blink) {
    previousMillis = currentMillis;
    ledState = !ledState;
  }
}
