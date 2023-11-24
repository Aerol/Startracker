#define NUM_PINS 4
#define NUM_STEPS 8

int allPins[NUM_PINS] = {D1, D2, D3, D4};

// from manufacturers datasheet
int STEPPER_SEQUENCE[NUM_STEPS][NUM_PINS] = {{1,0,0,1},
                                             {1,0,0,0},
                                             {1,1,0,0},
                                             {0,1,0,0},
                                             {0,1,1,0},
                                             {0,0,1,0},
                                             {0,0,1,1},
                                             {0,0,0,1}};
int stepNum = 0;

void setup() {
  Serial.begin(115200);
  setup_gpio();
}

void setup_gpio() {
  for (int i=0;i<NUM_PINS+1;i++) {
     pinMode(allPins[i], OUTPUT);
  }
  all_pins_off();
}

void all_pins_off() {
  for (int i=0;i<NUM_PINS+1;i++) {
    digitalWrite(allPins[i], HIGH); 
  }
}

int *currentStep;
void loop() {
  
 currentStep = STEPPER_SEQUENCE[stepNum];
  for (int i=0;i<NUM_PINS+1;i++) {
     if (currentStep[i] == 1) {
        digitalWrite(allPins[i], HIGH);
     }
     else {
        digitalWrite(allPins[i], LOW);
     }
  }
  delay(5);
  stepNum +=2;  // double-stepping. Faster and shakier. 
  stepNum %= NUM_STEPS;
}