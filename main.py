import time
from machine import Pin, ADC
import ubinascii
import json
import dht
import ujson as json
import time
import ubinascii
from mqtt import MQTTClient
import urequests
import json
import dht
import openweather as ow
import machine
import gc
import readsensordata as rsd


fully_dry = 44490  # 0% wet
fully_wet = 16500  # 100% wet
webhook_url = "https://discord.com/api/webhooks/1118471807377346592/SyTomR8MQRTJVds3mfL_pIfAIQFSEB_lgiLI97WHnJD9TrQAQhRMC5wPau5BNCevGR6G"
gc.enable()

mqtt_broker_address = "15f912e25fc747329333d0fc573f7f59.s2.eu.hivemq.cloud"
client_id = ubinascii.hexlify(machine.unique_id())
mqtt_topic_signal = "topic/signal"
mqtt_topic_moisture_sensor = "topic/moisture_sensor"
green_light = Pin(14, Pin.OUT)
yellow_light = Pin(13, Pin.OUT)
red_light = Pin(16, Pin.OUT)
green_light.value(0) # debug
yellow_light.value(0) # debug 
red_light.value(0) # debug



soil_adc_pin1 = ADC(Pin(26))
temp_humidity_sensor = Pin(27)
dht_sensor = dht.DHT11(temp_humidity_sensor)
time.sleep(3)

last_sent_time = 0
time_interval = 2 * 60 * 60  # 3 hours

auto_wattering = False

mqtt_client = None

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
    moisture_perc1 = rsd.get_soil_moisture_percentage(adc1, fully_dry, fully_wet)
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
        time.sleep(5)


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
    moisture_perc1 = rsd.get_soil_moisture_percentage(adc1, fully_dry, fully_wet)
    payload = {
        "content": f"Watering has been completed! Your plant is now happy! :)\nNew soil moisture percentage is:{moisture_perc1}%"
    }
    headers = {
        "Content-Type": "application/json"
    }
    response = urequests.post(webhook_url, data=json.dumps(payload), headers=headers)
    if response.status_code == 204:
        print("Sent to Discord:", response.text)
    else:
        print("Failed to send to Discord:", response.text)


def run():
    green_light.value(1) # debuging purposes
    machine.idle()
    print ("Starting the main function")
    starting_time = time.localtime()
    starting_hour = (starting_time[3] + 2) % 24
    starting_minute = starting_time[4]
    print("Starting hour:", starting_hour)
    print("Starting minute:", starting_minute)
    mqtt_client.check_msg()
    adc1 = soil_adc_pin1.read_u16()
    indoor_temp, indoor_humidity = rsd.read_temp_sensor_data(dht_sensor)
    outdoor_temp = ow.get_temperature()
    outdoor_humidity = ow.get_humidity()
    living_room_stats_sent = False
    moist_warning_sent = False
    while True:
        print("Starting the loop")
        yellow_light.value(1) # debuging purposes
        mqtt_client.check_msg()
        moisture_perc1 = rsd.get_soil_moisture_percentage(adc1, fully_dry, fully_wet)
        live_time = time.localtime()
        live_hour = (live_time[3] + 2) % 24
        live_minute = live_time[4]
        if live_hour >= 22 or live_hour < 8:
            print("Sleeping for 10 hours")
            machine.deepsleep(3600000) # 60 minutes
        else:
            mqtt_client.check_msg()
            #if starting_hour + 1 == live_hour: # every hour
            if starting_minute < 30 and (starting_minute + 30 == live_minute) or starting_minute >= 30 and (starting_minute - 30 == live_minute): # every 30 minutes
                red_light.value(1) # debuging purposes
                mqtt_client.publish(topic=mqtt_topic_moisture_sensor, msg=str(moisture_perc1))
                time.sleep(0.1)
                print("Moisture percentage sent to MQTT broker.")
                mqtt_client.publish(topic="topic/outdoor_temp", msg=str(outdoor_temp))
                time.sleep(0.1)
                print("Outdoor temperature sent to MQTT broker.")
                mqtt_client.publish(topic="topic/indoor_humidity", msg=str(indoor_humidity))
                time.sleep(0.1)
                print("Indoor humidity sent to MQTT broker.")
                mqtt_client.publish(topic="topic/indoor_temp", msg=str(indoor_temp))
                time.sleep(0.1)
                print("Indoor temperature sent to MQTT broker.")
                mqtt_client.publish(topic="topic/outdoor_humidity", msg=str(outdoor_humidity))
                time.sleep(0.1)
                print("Stats sent to MQTT broker.")
                time.sleep(5)
                machine.reset()
            if auto_wattering == True:
                do_auto_wattering()
            if starting_hour == 9 and not living_room_stats_sent:
                send_living_room_stats_to_discord(indoor_temp, indoor_humidity, outdoor_temp, outdoor_humidity, moisture_perc1)
                living_room_stats_sent = True
                print("Living room stats sent to Discord")
            if live_hour % 4 == 0 and not moist_warning_sent:
                send_moist_warning_to_discord(moisture_perc1)
                moist_warning_sent = True
                print("Moisture warning sent to Discord")
            mqtt_client.check_msg()
            time.sleep(5)
            mqtt_client.check_msg()

try:
    connect_to_mqtt_broker()
    run()
except Exception as e:
    print("Exception occurred:", e)
    machine.reset()
