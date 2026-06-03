#include <ArduinoModbus.h>
#include <Ethernet.h>

byte mac[] = { 0xDE, 0xAD, 0xBE, 0xEF, 0xFE, 0xED };
IPAddress ip(192, 168, 40, 20);

ModbusTCPServer modbusTCPServer;

const int sensorPin = A0;

float voltaje = 0;
float corriente = 0;
float temperatura = 0;

void setup() {

  Serial.begin(9600);

  Ethernet.begin(mac, ip);

  Serial.print("IP: ");
  Serial.println(Ethernet.localIP());

  if (!modbusTCPServer.begin()) {
    Serial.println("ERROR: Modbus no inicia");
    while (1);
  }

  modbusTCPServer.configureHoldingRegisters(0, 10);
}

void loop() {

  modbusTCPServer.poll();

  int adc = analogRead(sensorPin);

  voltaje = adc * (10.0 / 1023.0);
  corriente = voltaje / 490.0;

  temperatura =
    ((corriente - 0.004) * 200.0 / 0.016) - 50.0;

  modbusTCPServer.holdingRegisterWrite(
    0,
    (int)(temperatura * 10)
  );

  delay(50);
}