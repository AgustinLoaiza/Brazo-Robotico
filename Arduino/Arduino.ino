#include <Servo.h>
Servo shoulder;
Servo elbow;
Servo base;
Servo gripper;

// ─── VELOCIDAD ────────────────────────────────────────────────────────────────
const int SPEED_STEPS = 100;
const int SPEED_DELAY = 30;

// ─── POSICIÓN SEGURA DE TRÁNSITO ─────────────────────────────────────────────
const float SAFE_SHOULDER = 100.0;
const float SAFE_ELBOW    = 90.0;

// ─── GRADOS EXTRA AL HOMBRO ANTES DE SUBIR ───────────────────────────────────
const float SHOULDER_ANTICHOQ = 13.0;  // ajusta si necesitas más o menos 1-4
bool recogiendo = false;
bool en_casilla = false;

void setup() {
  Serial.begin(9600);
  shoulder.attach(8);
  elbow.attach(7);
  base.attach(10);
  gripper.attach(12);
  rest();
  Serial.println("init");
}

// ─── MOVIMIENTO SIMULTÁNEO ────────────────────────────────────────────────────
void comboMove(float bTarget, float sTarget, float eTarget, int steps, int stepDelay) {
  float bPos = base.read();
  float sPos = shoulder.read();
  float ePos = elbow.read();

  float sTargetAdj = (sTarget >= 0) ? (180.0 * sTarget / 270.0) : sPos;
  float bTargetAdj = (bTarget >= 0) ? bTarget : bPos;
  float eTargetAdj = (eTarget >= 0) ? eTarget : ePos;

  float bStep = (bTargetAdj - bPos) / steps;
  float sStep = (sTargetAdj - sPos) / steps;
  float eStep = (eTargetAdj - ePos) / steps;

  for (int i = 1; i <= steps; i++) {
    base.write(    round(bPos + bStep * i) );
    shoulder.write(round(sPos + sStep * i) );
    elbow.write(   round(ePos + eStep * i) );
    delay(stepDelay);
  }
}

// ─── MOVIMIENTO SEGURO EN 3 FASES ────────────────────────────────────────────
void comboMoveSafe(float bTarget, float sTarget, float eTarget, int steps, int stepDelay) {
  // Fase 1: subir shoulder y elbow — base NO se mueve
  float bActual = base.read();
  comboMove(bActual, SAFE_SHOULDER, SAFE_ELBOW, steps, stepDelay);
  //delay(100);

  // Fase 2: girar SOLO la base
  comboMove(bTarget, SAFE_SHOULDER, SAFE_ELBOW, steps, stepDelay);
  //delay(100);

  // Fase 3: bajar al punto destino
  
  // Fase 3a: subir codo 15° extra antes de bajar
  float ePreBajada2 = max(shoulder.read() - 10.0, 0.0);
  for (float e = shoulder.read(); e >= ePreBajada2; e -= 0.5) {
    shoulder.write(round(e));
    delay(25);
  } 
  float ePreBajada = min(elbow.read() + 35.0, 180.0);
  for (float e = elbow.read(); e <= ePreBajada; e += 0.5) {
    elbow.write(round(e));
    delay(25);
  }
 
  /*// Fase 3a: mover hombro -10° y codo +35° simultáneamente
  float sPreBajada = max(shoulder.read() - 10.0, 0.0);
  float ePreBajada = min(elbow.read()    + 35.0, 180.0);
  float bActual2   = base.read();
  comboMove(bActual2, sPreBajada, ePreBajada, 60, 25);
 */
  //delay(150);
  comboMove(bTarget, sTarget, eTarget, steps, stepDelay);
}

// ─── ANTICHOQUE HOMBRO (filas 1-4) ───────────────────────────────────────────
void antichoqueHombro() {
  float sActual = shoulder.read();
  float sAntichoq = min(sActual + SHOULDER_ANTICHOQ, 180.0);
  for (float s = sActual; s <= sAntichoq; s += 0.5) {
    shoulder.write(round(s));
    delay(30);
  }
  delay(200);
}

// ─── ANTICHOQUE CODO (filas 5-8) ─────────────────────────────────────────────
void antichoqueCodo() {
  // Paso 1: subir codo 10° suave
  float eActual = elbow.read();
  float eAntichoq = min(eActual + 9, 180.0);
  for (float e = eActual; e <= eAntichoq; e += 0.5) {
    elbow.write(round(e));
    delay(30);
  }
  //delay(200);

  // Paso 2: subir hombro 20° suave
  float sActual = shoulder.read();
  float sAntichoq = min(sActual + 30.0, 180.0);
  for (float s = sActual; s <= sAntichoq; s += 0.5) {
    shoulder.write(round(s));
    delay(30);
  }
 // delay(200);
}

// ─── HOME INTERMEDIO (punto de pausa para recorridos largos) ─────────────────
void restMedio() {
  // Misma altura que HOME pero base en el centro del tablero
  comboMoveSafe(120, 100, 90, SPEED_STEPS, SPEED_DELAY);
}

// ─── SERVOS INDIVIDUALES ──────────────────────────────────────────────────────
void shoulderTo(float target) {
  target = 180.0 * target / 270.0;
  float pos = shoulder.read();
  float step = (pos <= target) ? 1 : -1;
  for (; (step > 0) ? (pos <= target) : (pos >= target); pos += step) {
    shoulder.write(round(pos));
    delay(30);
  }
}

void elbowTo(float target) {
  float pos = elbow.read();
  float step = (pos <= target) ? 1 : -1;
  for (; (step > 0) ? (pos <= target) : (pos >= target); pos += step) {
    elbow.write(round(pos));
    delay(20);
  }
}

void baseTo(float target) {
  float pos = base.read();
  float step = (pos <= target) ? 1 : -1;
  for (; (step > 0) ? (pos <= target) : (pos >= target); pos += step) {
    base.write(round(pos));
    delay(20);
  }
}

void gripperTo(float target) {
  float pos = gripper.read();
  float step = (pos <= target) ? 1 : -1;
  for (; (step > 0) ? (pos <= target) : (pos >= target); pos += step) {
    gripper.write(round(pos));
    delay(10);
  }
}

// ─── POSES ────────────────────────────────────────────────────────────────────
void rest() {
  gripperTo(50);
  comboMoveSafe(112, 110, 100, SPEED_STEPS, SPEED_DELAY);
}

void rest1() {
  //gripperTo(120);
  comboMoveSafe(112, 110, 100, SPEED_STEPS, SPEED_DELAY);
}

void cubeta() {
  comboMoveSafe(30, 40, 110, SPEED_STEPS, SPEED_DELAY);
  gripperTo(50);
}

void grasp() {
  gripperTo(100);//CERRADO
  delay(1000);
  recogiendo = true;
  en_casilla = true;   // ← está abajo, necesita antichoque al subir
}

void drop() {
  gripperTo(50);//ABIERTO
  delay(1000);
  recogiendo = false;
  en_casilla = true;   // ← también necesita antichoque al subir
}

// ─── LOOP ──────────────────────────────────────────
void loop() {
  if (Serial.available() > 0) {
    String msg = Serial.readStringUntil('\n');
    msg.trim();

    // ── HOME seguro ─────────────────────────────────────
    if (msg == "HOME") {
      rest();
      Serial.println("done");
      return;
    }
    if (msg == "HOME1") {
      rest1();
      Serial.println("done");
      return;
    }

    // ── Comando combo: "B120,S90,E90" ───────────────────────────
    if (msg.startsWith("B") && msg.indexOf(',') > 0) {
      int idxS = msg.indexOf('S');
      int idxE = msg.indexOf('E');
      float bVal = msg.substring(1, idxS).toFloat();
      float sVal = msg.substring(idxS + 1, idxE).toFloat();
      float eVal = msg.substring(idxE + 1).toFloat();
      comboMoveSafe(bVal, sVal, eVal, SPEED_STEPS, SPEED_DELAY);
      delay(1000);
      Serial.println("done");
      return;
    }

    // ── Comandos individuales ────────────────────────────────────
    float x = msg.toFloat();
    if (x == 190) rest();
    if (x == 191) grasp();
    if (x == 192) drop();
    if (x == 194) cubeta();
    if (x == 195) antichoqueHombro();  // ← filas 1-4
    if (x == 196) antichoqueCodo();    // ← filas 5-8
    if (x == 197) restMedio();          // ← HOME intermedio
    if (x >= 0   && x <= 180) shoulderTo(x);
    if (x >= 200 && x <= 380) elbowTo(x - 200);
    if (x >= 400 && x <= 580) baseTo(x - 400);
    Serial.println("done");
  }
}
