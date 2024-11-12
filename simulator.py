import paho.mqtt.client as mqtt
import certifi
from time import sleep

global mqtt_client

mqtt_client = None

def on_connect( client, userdata, flags, rc):
        print("Connected with result code " + str(rc))
        # Subscribing in on_connect() means that if we lose the connection and
        # reconnect then subscriptions will be renewed.
        client.subscribe("teclado_espiao/routine")

    # The callback for when a PUBLISH message is received from the server.
def on_message( client, userdata, msg):
    topic = str(msg.topic)
    message = str(msg.payload.decode("utf-8"))
    print(topic + " " + message)


def start_mqtt():
    global mqtt_client
    print("starting mqtt...")
    mqtt_client = mqtt.Client()
    mqtt_client.tls_set(certifi.where())
    mqtt_client.username_pw_set(username="aula", password= "zowmad-tavQez")
    mqtt_client.on_connect = on_connect
    mqtt_client.on_message = on_message

    mqtt_client.connect("mqtt.janks.dev.br", 8883, 60)
    #mqtt_client.connect("mqtt.janks.dev.br", 1883, 70)
    #step_mqtt()

def step_mqtt():
    global mqtt_client
    mqtt_client.loop_read()
    mqtt_client.loop_write()
    mqtt_client.loop_misc()

start_mqtt()
while True:
    step_mqtt()
    sleep(0.1)