import time
from machine import Pin, ADC, I2C
import ubinascii
import urequests
import json
import dht
import framebuf
import ssd1306
import network
import usocket as socket
import ussl as ssl
import ujson as json
import time
import uos as os
import ubinascii
from mqtt import MQTTClient
import urequests
import json
import dht
import framebuf
import ssd1306


fully_dry = 44490  # 0% wet
fully_wet = 16500  # 100% wet
webhook_url = "https://discord.com/api/webhooks/1118471807377346592/SyTomR8MQRTJVds3mfL_pIfAIQFSEB_lgiLI97WHnJD9TrQAQhRMC5wPau5BNCevGR6G"

mqtt_broker_address = "15f912e25fc747329333d0fc573f7f59.s2.eu.hivemq.cloud"
client_id = ubinascii.hexlify(machine.unique_id())
#mqtt_broker_port = 1883
mqtt_topic_signal = "topic/signal"
mqtt_topic_moisture_sensor1 = "topic/data"

soil_adc_pin1 = ADC(Pin(26))
temp_humidity_sensor = Pin(27)
dht_sensor = dht.DHT11(temp_humidity_sensor)
time.sleep(3)

last_sent_time = 0
time_interval = 3 * 60 * 60  # 3 hours


mqtt_client = None


def on_message(topic, msg):
    print(f"Received message on topic: {topic} - Message: {msg}")
    if msg.decode() == "TURN THE 1st PUMP ON":
        relay_pump_pin = Pin(15, Pin.OUT)
        print("PUMP 1 IS ON!")
        time.sleep(5)
        relay_pump_pin.init(Pin.IN)
        print("PUMP 1 IS OFF!")
        time.sleep(5)
        send_confirmation_to_discord()


def connect_to_mqtt_broker():
    global mqtt_client
    mqtt_client = MQTTClient(client_id=client_id, server=mqtt_broker_address, port=0, user="djolodjolo", password="djordjekralj200294", keepalive=7200, ssl=True, ssl_params={'server_hostname' : '15f912e25fc747329333d0fc573f7f59.s2.eu.hivemq.cloud'})
    mqtt_client.set_callback(on_message)
    mqtt_client.connect()
    mqtt_client.subscribe(mqtt_topic_signal)
    print("Connected to MQTT broker")


def send_moist_warning_to_discord(value, sensor_name):
    global last_sent_time
    current_time = time.time()
    if value <= 10:
        if current_time - last_sent_time >= time_interval:
            payload = {
                "content": f"WARNING!: Soil moisture percentage on {sensor_name} is: {value}%"
            }
            headers = {
                "Content-Type": "application/json"
            }
            response = urequests.post(webhook_url, data=json.dumps(payload), headers=headers)
            if response.status_code == 204:
                print("Sent to Discord:", value)
                last_sent_time = current_time
            else:
                print("Failed to send to Discord:", response.text)
        else:
            print("Skipping message. Not enough time has passed since the last sent message.")


def send_confirmation_to_discord():
    adc1 = soil_adc_pin1.read_u16()
    moisture_perc1 = get_soil_moisture_percentage(adc1)
    payload = {
        "content": f"Watering has been completed! Now the plants are happy! :)\nNew soil moisture percentage is:{moisture_perc1}%"
    }
    headers = {
        "Content-Type": "application/json"
    }
    response = urequests.post(webhook_url, data=json.dumps(payload), headers=headers)
    if response.status_code == 204:
        print("Sent to Discord:", response.text)
    else:
        print("Failed to send to Discord:", response.text)


def read_temp_sensor_data():
    dht_sensor.measure()
    temperature = dht_sensor.temperature()
    humidity = dht_sensor.humidity()
    return temperature, humidity


def get_soil_moisture_percentage(adc_value):
    adc_range = fully_dry - fully_wet
    moisture_range = 100
    moisture_percentage = (fully_dry - adc_value) / adc_range * moisture_range
    return moisture_percentage


def get_capacitator_measurements():
    first_iteration = True
    time_sent = 0
    while True:
        mqtt_client.check_msg()
        adc1 = soil_adc_pin1.read_u16()
        moisture_perc1 = get_soil_moisture_percentage(adc1)
        indoor_temp, indoor_humidity = read_temp_sensor_data()
        print(indoor_temp, indoor_humidity)
        if not first_iteration:
            if time.time() - time_sent >= 600:
                mqtt_client.publish(topic=mqtt_topic_moisture_sensor1, msg=str(moisture_perc1))
                mqtt_client.publish(topic="YOUR_OUTDOOR_TEMP_TOPIC", msg=str(outdoor_temp))
                mqtt_client.publish(topic="YOUR_INDOOR_HUMIDITY_TOPIC", msg=str(indoor_humidity))
                mqtt_client.publish(topic="YOUR_INDOOR_TEMP_TOPIC", msg=str(indoor_temp))
                time_sent = time.time()
            mqtt_client.publish(topic="YOUR_OUTDOOR_HUMIDITY_TOPIC", msg=str(outdoor_humidity))
            print('Sent to 1st moisture sensor feed : ', moisture_perc1)
            send_moist_warning_to_discord(moisture_perc1, "1st sensor")
        first_iteration = False
        mqtt_client.check_msg()
        time.sleep(5)


connect_to_mqtt_broker()
get_capacitator_measurements()
