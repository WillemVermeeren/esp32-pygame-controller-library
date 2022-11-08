#include <BluetoothSerial.h>

#include <ArduinoJson.h>


#if !defined(CONFIG_BT_ENABLED) || !defined(CONFIG_BLUEDROID_ENABLED)
#error Bluetooth is not enabled! Please run `make menuconfig` to and enable it
#endif


#define upPin 12
#define downPin 14
#define leftPin 27
#define rightPin 26
#define aPin 25
#define bPin 33

String receivedCommand = "";

BluetoothSerial SerialBT; // i know normal bluetooth is better but this is easier

DynamicJsonDocument keys(120); // creates a json doc that has all the keys because it's easier to send this way
void setup() {
  keys["up"] = false; // set all the keys to false
  keys["down"]   = false;
  keys["left"] = false;
  keys["right"] = false;
  keys["a"] = false;
  keys["b"] = false;

  pinMode(upPin, INPUT_PULLUP);
  pinMode(downPin, INPUT_PULLUP);
  pinMode(leftPin, INPUT_PULLUP);
  pinMode(rightPin, INPUT_PULLUP);
  pinMode(aPin, INPUT_PULLUP);
  pinMode(bPin, INPUT_PULLUP);
  
  Serial.begin(115200);
  SerialBT.begin("controller"); //Bluetooth device name
  Serial.println("The device started, now you can pair it with bluetooth!");
}

void loop() {
  receivedCommand = "";
  
  while(SerialBT.available()>0){
    char newValue = SerialBT.read();
    receivedCommand+=newValue;
  }


  if(receivedCommand=="keys"){
    updateKeys();
    String keysString;
    serializeJson(keys, keysString);
    SerialBT.print(keysString);
    Serial.println(keysString);
  }
  
  delay(20);
}

void updateKeys(){
  keys["up"] = (digitalRead(upPin) != HIGH); // updates the keys json. You could probably just directly use the digitalRead functions but i dont trust that HIGH LOW stuff
  keys["down"]   = (digitalRead(downPin) != HIGH);
  keys["left"] = (digitalRead(leftPin) != HIGH);
  keys["right"] = (digitalRead(rightPin) != HIGH);
  keys["a"] = (digitalRead(aPin) != HIGH);
  keys["b"] = (digitalRead(bPin) != HIGH);
}
