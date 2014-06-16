/*
  Helium Volume Monitor
 
 written by David Weber
 */

long volume = 0;         // helium volume in liter
int volume_index = 0;
int volume_max_index = 255;
//long volumes[255] ;       // stores volumes at different times
long derivatives[] = { 0,0,0};             // derivatives
int der_times[] = { 10,100,1000};

long time = 0;
unsigned long wait_until=0;  // used for the clock
int serial_in = 0;      // received serial byte
int last_state = 0;
long last_switching = 0;
int key_state = 0;
#define debounce_time 15

// verbose mode periodically displays debug data
int verbose = 0;


void setup()
{
  // start serial port at 9600 bps:
  Serial.begin(115200);
  fdevopen( &my_putc, 0);

  pinMode(2, INPUT);   // Helium counter on pin 2 to pin 3 (GND)
  pinMode(3, OUTPUT);  // Can be used for helium switch
  //pinMode(13, OUTPUT);  // LED
  digitalWrite(2, HIGH);   // Pull up on
  digitalWrite(3, LOW);    // GND
  
  last_state = digitalRead(2);
}

void loop()
{
  if (Serial.available() > 0) {
    serial_in = Serial.read();
    if (serial_in == 'R')
      send_volume();
      volume = 0;
    if (serial_in == 'V')
      verbose ^= 1;
    if (serial_in == 'D')
    {
      char buf[30];
      ltoa(volume, buf, 10);
      printf("Volume: %s\n",buf);
      printf("last_switching: %i\n",(int)last_switching);
      
    }
  }

  int recent_state = digitalRead(2);
  if (recent_state != last_state)
  {
    last_switching = millis();
    last_state = recent_state;
  }
  else
  {
    if (last_switching != -1)
    { // if not already registered event
      if (millis() - last_switching > debounce_time)
      { // true event
        // printf("+++\n");
        if (recent_state)
          volume += 10;
        last_switching = -1;
      }
    }
  }

#define wait_time 1000
  if ((unsigned long)(millis() - wait_until) >= wait_time) // check for rollover
  { 
    digitalWrite(13, !digitalRead(13));
    //volume++;
    time++;
    wait_until += wait_time; // wait another interval cycle
    
    if (verbose)
      send_volume();
  }

  delay(2); // delay in ms
}

void send_volume()
{
  char buf[30];
  ltoa(volume, buf, 10);
  printf("%s\n",buf);
}

void send_integer(int value)
{
  char buf[12];  // holds the number    
  // write volume
  itoa(value, buf, 10);
  Serial.write(buf);
  Serial.write(';');
  Serial.write('\n');
}

int my_putc( char c, FILE *t) {
  Serial.write( c );
}



