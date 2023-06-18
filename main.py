import time
from machine import Pin, ADC
from mqtt import MQTTClient
import urequests
import json


fully_dry = 44490  # 0% wet
fully_wet = 16500  # 100% wet
webhook_url = "https://discord.com/api/webhooks/1118471807377346592/SyTomR8MQRTJVds3mfL_pIfAIQFSEB_lgiLI97WHnJD9TrQAQhRMC5wPau5BNCevGR6G"

ADAFRUIT_IO_USERNAME = "djolodjolo"
ADAFRUIT_IO_KEY = "aio_MFoi10Z8EuG91Jfuv0Gr3cnnRQAQ"

last_sent_time = 0
time_interval = 3* 60 * 60  # 3 hours

mqtt_client_adafruit = MQTTClient("", "io.adafruit.com", user=ADAFRUIT_IO_USERNAME, password=ADAFRUIT_IO_KEY)
mqtt_client_adafruit.connect()
print("YES! Connected to Adafruit!")


def on_message(topic, msg):
    print(f"Received message on topic: {topic} - Message: {msg}")
    if msg.decode() == "TURN THE 1st PUMP ON":
        print("PUMP 1 IS ON!")
        time.sleep(5)
        print("PUMP 1 IS OFF!")
        time.sleep(2)
    elif msg.decode() == "TURN THE 2nd PUMP ON":
        print("PUMP 2 IS ON!")
        time.sleep(5)
        print("PUMP 2 IS OFF!")
        time.sleep(2)

mqtt_client_adafruit.set_callback(on_message)
mqtt_client_adafruit.subscribe("djolodjolo/feeds/Signal feed")

def send_to_discord(value, sensor_name):
    global last_sent_time
    current_time = time.time()

    if current_time - last_sent_time >= time_interval: # some problems here
        if value <= 10:
            if current_time - last_sent_time >= time_interval: # some problems here
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



def get_soil_moisture_percentage(adc_value):
    adc_range = fully_dry - fully_wet
    moisture_range = 100
    moisture_percentage = (fully_dry - adc_value) / adc_range * moisture_range
    return moisture_percentage


def get_capacitator_measurements():
    soil_adc_pin1 = ADC(Pin(26))
    soil_adc_pin2 = ADC(Pin(27))
    first_iteration = True
    while True:
        adc1 = soil_adc_pin1.read_u16()
        adc2 = soil_adc_pin2.read_u16()
        moisture_perc1 = get_soil_moisture_percentage(adc1)
        moisture_perc2 = get_soil_moisture_percentage(adc2)
        mqtt_client_adafruit.check_msg()
        if not first_iteration:
            mqtt_client_adafruit.publish(topic="djolodjolo/feeds/1st_moisture_sensor", msg=str(moisture_perc1))
            print('Sent to 1st moisture sensor feed : ', moisture_perc1)
            send_to_discord(moisture_perc1, "1st sensor")
            mqtt_client_adafruit.publish(topic="djolodjolo/feeds/2nd_moisture_sensor", msg=str(moisture_perc2))
            print('Sent to 2nd moisture sensor feed : ', moisture_perc2)
            send_to_discord(moisture_perc2, "2nd sensor")
        first_iteration = False
        time.sleep(5)


get_capacitator_measurements()