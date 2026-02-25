#include <FastLED.h>
#include <WiFi.h>
#include <AsyncTCP.h>
#include <ESPAsyncWebServer.h>
#include <ArduinoJson.h>
#include "LittleFS.h"

#define NUM_LEDS 64
#define DATA_PIN 4

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

// web / api
AsyncWebServer server(80);
AsyncWebSocket ws("/ws");

// Flags
bool ledState = false;
bool awake = false;
bool blink = true;

// LED controls
CRGB leds[NUM_LEDS];
String modeSelected = "none";

// timer
unsigned long previousMillis = 0;
int interval = 800; // Can be changed programatically

// Display arrays for symbols
String Overtake[8] = {"00001110", "00001100", "00001010", "01100001", "01100001", "01100001", "01100010", "00000100"};
String RightIn[8] = {"00000000", "00000100", "00000010", "11111111", "10000010", "10000100", "10000000", "10000000"};
String LeftIn[8] = {"00000000", "00100000", "01000000", "11111111", "01000001", "00100001", "00000001", "00000001"};
String UTurnRight[8] = {"00000000", "00111000", "01000100", "01000100", "01000100", "01010101", "01001110", "01000100"};
String UTurnLeft[8] = {"00000000", "00011100", "00100010", "00100010", "00100010", "10101010", "01110010", "00100010"};
String StopIn[8] = {"00000000", "00011000", "00111100", "01111110", "01111110", "00111100", "00011000", "00000000"};
String ParkIn[8] = {"01111000", "01111100", "01100100", "01111100", "01111000", "01100000", "01100000", "01100000"};

//** Function definitions */

bool setupWiFi(String *ssid, String *password) {
  WiFi.softAPdisconnect(true); // stop hotspot

  WiFi.mode(WIFI_STA); // connect to router mode.
  WiFi.begin(ssid, password);
  Serial.print("Connecting");

  //while (WiFi.status() != WL_CONNECTED) {
  //  delay(300);
  //  Serial.print(".");
  //}

  for(int i=0, i<10, i++){ // try for 3 seconds
    delay(300);
    if(WiFi.status() == WL_CONNECTED){
      break;
    }
  }

  if(WiFi.status() == WL_CONNECTED){
    Serial.println();
    Serial.print("IP: ");
    Serial.println(WiFi.localIP());
    return true;
  }
  else{
    return false;
  }
}

void startAP() { // Hotspot mode
  WiFi.mode(WIFI_AP);
  WiFi.softAP("NavIndiESP32", "12345678");

  Serial.print("AP IP: ");
  Serial.println(WiFi.softAPIP());
}

void setupAPI() {
  server.on("/api/init", HTTP_POST,
    [](AsyncWebServerRequest *request){}, NULL,
    [](AsyncWebServerRequest *request, uint8_t *data, size_t len, size_t index, size_t total)
    {
      StaticJsonDocument<200> doc;
      DeserializationError err = deserializeJson(doc, data);

      if (err) {
        request->send(400, "application/json", "{\"status\":\"invalid json\"}");
        return;
      }

      appConfig.ssid = doc["ssid"] | "";
      appConfig.wifipass = doc["wifipass"] | "";
      appConfig.stearing = doc["stearing"] | "right";
      appConfig.mode = doc["mode"] | "";

      // set the wifi & other configs

      request->send(200, "application/json", "{\"status\":\"ok\"}");
    }
  );

  // Route for root / web page
  server.on("/", HTTP_GET, [](AsyncWebServerRequest *request) {
    request->send(LittleFS, "/index.html", "text/html");
  });
  server.serveStatic("/", LittleFS, "/");

  server.begin();
}

void initWebSocket() {
  ws.onEvent(onEvent);
  server.addHandler(&ws);
}

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

  // Allocate a buffer to store contents of the file.
  // Using a StaticJsonDocument is more memory efficient for small fixed-size JSONs.
  // For larger or unknown size JSONs, consider DynamicJsonDocument.
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

void handleClientMsg(void *arg, uint8_t *data, size_t len) { // handle the ws msg
  AwsFrameInfo *info = (AwsFrameInfo*)arg;
  if (info->final && info->index == 0 && info->len == len && info->opcode == WS_TEXT) {
    data[len] = 0;
    modeSelected = (char*)data;
    awake = true;
    ledState = true;
  }
}

void onEvent(AsyncWebSocket *server, AsyncWebSocketClient *client, AwsEventType type,
  void *arg, uint8_t *data, size_t len) { // When websocker msg is received
  switch (type) {
    case WS_EVT_CONNECT:
      Serial.printf("WebSocket client #%u connected from %s\n", client->id(), client->remoteIP().toString().c_str());
      break;
    case WS_EVT_DISCONNECT:
      Serial.printf("WebSocket client #%u disconnected\n", client->id());
      break;
    case WS_EVT_DATA:
      handleClientMsg(arg, data, len);
      break;
    case WS_EVT_PONG:
    case WS_EVT_ERROR:
      break;
  }
}

void setLED(String *chosen, const CRGB& color){
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

void setup(){
  // Setup the ESP32 board after boot
  Serial.begin(115200);
  FastLED.addLeds<WS2812,DATA_PIN,GRB>(leds,NUM_LEDS);
  FastLED.clear();
  FastLED.setBrightness(3);
  setupWiFi();
  setupAPI();
  initFS();
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
        else if(modeSelected == "off"){
            awake = false;
        }
    }
    // Debug / local test end here

    // Timer loop
    unsigned long currentMillis = millis();
    if ((currentMillis - previousMillis >= interval) && blink) {
        previousMillis = currentMillis;
        ledState = !ledState;
    }
}
