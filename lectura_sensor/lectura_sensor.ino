#include <ArduinoModbus.h>
#include <Ethernet.h>

byte mac[] = { 0xDE, 0xAD, 0xBE, 0xEF, 0xFE, 0xED };

IPAddress ip(192, 168, 40, 20);

EthernetServer ethServer(502);
ModbusTCPServer modbusTCPServer;

// Pin analógico donde conectarás la señal
const int sensorPin = A0;

float voltaje = 0.0;
float temperatura = 0.0;

void setup() {

  Serial.begin(9600);

  // Iniciar Ethernet
  Ethernet.begin(mac, ip);

  Serial.print("IP: ");
  Serial.println(Ethernet.localIP());

  // Iniciar servidor Modbus TCP
  ethServer.begin();
  modbusTCPServer.begin();

  // Holding Registers
  modbusTCPServer.configureHoldingRegisters(0, 10);

}

void loop() {

  // =========================
  // LEER SENSOR
  // =========================

  int adc = analogRead(sensorPin);

  // Convertir ADC a voltaje
  // ADC 10 bits: 0-1023
  // Voltaje: 0-5V

  voltaje = adc * (5.0 / 1023.0);

  // Conversión 1-5V -> temperatura
  // Configuración interfaz:
  // 1V = -50°C
  // 5V = 150°C

  temperatura =
      ((voltaje - 1.0) * 200.0 / 4.0) - 50.0;

  // =========================
  // DEBUG SERIAL
  // =========================

  Serial.print("ADC: ");
  Serial.print(adc);

  Serial.print("  Voltaje: ");
  Serial.print(voltaje);

  Serial.print(" V  Temperatura: ");
  Serial.print(temperatura);

  Serial.println(" C");

  // =========================
  // MODBUS TCP
  // =========================

  EthernetClient client = ethServer.available();

  if (client) {

    modbusTCPServer.accept(client);

    while (client.connected()) {

      modbusTCPServer.poll();

      // Guardar temperatura en registro 0
      // Multiplicamos x10 para mantener decimales

      modbusTCPServer.holdingRegisterWrite(
          0,
          (int)(temperatura * 10)
      );

      delay(100);

    }
  }

  delay(500);
}
