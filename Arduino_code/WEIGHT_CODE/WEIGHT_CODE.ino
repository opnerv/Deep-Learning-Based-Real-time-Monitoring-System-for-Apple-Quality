#include "hx711.h"

Hx711 scale(A1, A0); // DOUT, SCK
float GRAM = 0;

void setup()
{
Serial.begin(9600);
}

void loop()
{
GRAM = scale.getGram();
//Serial.print("one reading:\t");
Serial.print(GRAM, 1);
//Serial.print(" g");
Serial.print("\n");
delay(10);
}