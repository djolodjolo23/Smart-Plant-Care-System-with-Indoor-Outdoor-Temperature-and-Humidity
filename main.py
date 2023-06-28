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
import utime
import uos as os
import ubinascii
from mqtt import MQTTClient
import urequests
import json
import dht
import framebuf
import ssd1306
import openweather as ow
import machine


fully_dry = 44490  # 0% wet
fully_wet = 16500  # 100% wet
webhook_url = "https://discord.com/api/webhooks/1118471807377346592/SyTomR8MQRTJVds3mfL_pIfAIQFSEB_lgiLI97WHnJD9TrQAQhRMC5wPau5BNCevGR6G"

mqtt_broker_address = "15f912e25fc747329333d0fc573f7f59.s2.eu.hivemq.cloud"
client_id = ubinascii.hexlify(machine.unique_id())
mqtt_topic_signal = "topic/signal"
mqtt_topic_moisture_sensor = "topic/moisture_sensor"


soil_adc_pin1 = ADC(Pin(26))
temp_humidity_sensor = Pin(27)
dht_sensor = dht.DHT11(temp_humidity_sensor)
time.sleep(3)

last_sent_time = 0
time_interval = 2 * 60 * 60  # 3 hours

auto_wattering = False

mqtt_client = None


def on_message(topic, msg):
    global auto_wattering
    print(f"Received message on topic: {topic} - Message: {msg}")
    if msg.decode() == "TURN THE 1st PUMP ON":
        relay_pump_pin = Pin(15, Pin.OUT)
        print("WATER PUMP IS ON!")
        time.sleep(5)
        relay_pump_pin.init(Pin.IN)
        print("WATER PUMP IS OFF!")
        time.sleep(5)
        send_confirmation_to_discord()
    elif msg.decode() == "auto wattering ON":
        auto_wattering = True
        print("Auto wattering is ON!")
    elif msg.decode() == "auto wattering OFF":
        auto_wattering = False
        print("Auto wattering is OFF!")


def do_auto_wattering():
    adc1 = soil_adc_pin1.read_u16()
    moisture_perc1 = get_soil_moisture_percentage(adc1)
    if moisture_perc1 <= 10:
        relay_pump_pin = Pin(15, Pin.OUT)
        print("WATER PUMP IS ON!")
        time.sleep(5)
        relay_pump_pin.init(Pin.IN)
        print("WATER PUMP IS OFF!")
        time.sleep(5)
        send_confirmation_to_discord()
    else:
        print("Soil moisture is above 10%")


def connect_to_mqtt_broker():
    global mqtt_client
    mqtt_client = MQTTClient(client_id=client_id, server=mqtt_broker_address, 
                             port=0, user="djolodjolo", password="djordjekralj200294", 
                             keepalive=7200, ssl=True, 
                             ssl_params={'server_hostname' : '15f912e25fc747329333d0fc573f7f59.s2.eu.hivemq.cloud'})
    mqtt_client.set_callback(on_message)
    mqtt_client.connect()
    mqtt_client.subscribe(mqtt_topic_signal)
    print("Connected to MQTT broker")


def send_moist_warning_to_discord(value):
    if value <= 10:
        payload = {
            "content": f"WARNING!: Soil moisture percentage on your flower is: {value} Please water it!"
        }
        headers = {
            "Content-Type": "application/json"
        }
        response = urequests.post(webhook_url, data=json.dumps(payload), headers=headers)
        if response.status_code == 204:
            print("Sent to Discord:", value)
        else:
            print("Failed to send to Discord:", response.text)



def send_living_room_stats_to_discord(indoor_temp, indoor_humidity, outdoor_temp, outdoor_humidity, moisture_perc1):
    payload = {
        "content": f"Your living room stats are:\nIndoor temperature: {indoor_temp} C\nIndoor humidity: {indoor_humidity}%\nOutdoor temperature: {outdoor_temp} C\nOutdoor humidity: {outdoor_humidity}%\nFlower soil moisture percentage: {moisture_perc1}%"
    }
    headers = {
        "Content-Type": "application/json"
    }
    response = urequests.post(webhook_url, data=json.dumps(payload), headers=headers)
    if response.status_code == 204:
        print("Sent to Discord:", payload)
    else:
        print("Failed to send to Discord:", response.text)




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
    last_sent_time = 0
    time_interval = 30 * 60  # 30 minutes
    machine.idle()
    while True:
        current_time = time.localtime()
        current_hour = current_time[3] + 2
        mqtt_client.check_msg()
        adc1 = soil_adc_pin1.read_u16()
        moisture_perc1 = get_soil_moisture_percentage(adc1)
        indoor_temp, indoor_humidity = read_temp_sensor_data()
        outdoor_temp = ow.get_temperature()
        outdoor_humidity = ow.get_humidity()
        if auto_wattering == True:
            do_auto_wattering()
        if time.time() - last_sent_time >= time_interval and current_hour < 22 and current_hour > 8:
            mqtt_client.publish(topic=mqtt_topic_moisture_sensor, msg=str(moisture_perc1))
            print("Published to moisture sensor feed:", moisture_perc1)
            mqtt_client.publish(topic="topic/outdoor_temp", msg=str(outdoor_temp))
            print("Published to outdoor temp feed:", outdoor_temp)
            mqtt_client.publish(topic="topic/indoor_humidity", msg=str(indoor_humidity))
            print("Published to indoor humidity feed:", indoor_humidity)
            mqtt_client.publish(topic="topic/indoor_temp", msg=str(indoor_temp))
            print("Published to indoor temp feed:", indoor_temp)
            mqtt_client.publish(topic="topic/outdoor_humidity", msg=str(outdoor_humidity))
            print("Published to outdoor humidity feed:", outdoor_humidity)
            send_living_room_stats_to_discord(indoor_temp, indoor_humidity, outdoor_temp, outdoor_humidity, moisture_perc1)
            send_moist_warning_to_discord(moisture_perc1)
            last_sent_time = time.time()
        if current_hour >= 22 and current_hour < 8:
            print("Sleeping for 10 hours")
            machine.lightsleep(100000)



connect_to_mqtt_broker()
get_capacitator_measurements()
