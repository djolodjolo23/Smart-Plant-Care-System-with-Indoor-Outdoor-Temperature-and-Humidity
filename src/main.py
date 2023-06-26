import time
from machine import Pin, ADC, I2C
from mqtt import MQTTClient
import urequests
import json
import openweather as ow
import dht
import framebuf
import ssd1306


fully_dry = 44490  # 0% wet
fully_wet = 16500  # 100% wet
webhook_url = "https://discord.com/api/webhooks/1118471807377346592/SyTomR8MQRTJVds3mfL_pIfAIQFSEB_lgiLI97WHnJD9TrQAQhRMC5wPau5BNCevGR6G"

ADAFRUIT_IO_USERNAME = "djolodjolo"
ADAFRUIT_IO_KEY = "aio_MFoi10Z8EuG91Jfuv0Gr3cnnRQAQ"

soil_adc_pin1 = ADC(Pin(26))
temp_humidity_sensor = Pin(27)
dht_sensor = dht.DHT11(temp_humidity_sensor)
time.sleep(3)

last_sent_time = 0
time_interval = 3 * 60 * 60  # 3 hours

'''
width = 128
height = 64
i2c = I2C(0, sda=Pin(16), scl=Pin(17))
oled = ssd1306.SSD1306_I2C(width, height, i2c)

oled.fill(0)
oled.text('Hello,', 0, 0)
oled.text('peppe8o.com', 0, 16)
oled.text('readers!', 0, 32)

oled.show()
'''''

mqtt_client_adafruit = MQTTClient("", "io.adafruit.com", user=ADAFRUIT_IO_USERNAME, password=ADAFRUIT_IO_KEY)
mqtt_client_adafruit.connect()
print("YES! Connected to Adafruit!")


# logic for turning on the water pump, based on the soil moisture sensor
# and the signal feed from Adafruit IO
# to be implemented, right now only messages are printed to the console.
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


# subscribe to the signal feed from Adafruit IO
mqtt_client_adafruit.set_callback(on_message)
mqtt_client_adafruit.subscribe("djolodjolo/feeds/Signal feed")

def send_moist_warning_to_discord(value, sensor_name):
    global last_sent_time
    current_time = time.time()
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

# convert the ADC value to a percentage
def get_soil_moisture_percentage(adc_value):
    adc_range = fully_dry - fully_wet
    moisture_range = 100
    moisture_percentage = (fully_dry - adc_value) / adc_range * moisture_range
    return moisture_percentage

# get the measurements from the soil moisture sensors
def get_capacitator_measurements():
    first_iteration = True
    time_sent = 0
    while True:
        mqtt_client_adafruit.check_msg()
        adc1 = soil_adc_pin1.read_u16()
        moisture_perc1 = get_soil_moisture_percentage(adc1)
        outdoor_temp = ow.get_temperature()
        outdoor_humidity = ow.get_humidity()
        indoor_temp, indoor_humidity = read_temp_sensor_data()
        print(indoor_temp, indoor_humidity)
        if not first_iteration:
             # if there were more then 10 minutes since the last sent message, send outdoor humidity and temperature
            if time.time() - time_sent >= 600:
                mqtt_client_adafruit.publish(topic="djolodjolo/feeds/1st_moisture_sensor", msg=str(moisture_perc1))
                mqtt_client_adafruit.publish(topic="djolodjolo/feeds/Outdoor temperature", msg=str(outdoor_temp))
                mqtt_client_adafruit.publish(topic="djolodjolo/feeds/Indoor humidity", msg=str(indoor_humidity))
                mqtt_client_adafruit.publish(topic="djolodjolo/feeds/Indoor temperature", msg=str(indoor_temp))
                time_sent = time.time()
            mqtt_client_adafruit.publish(topic="djolodjolo/feeds/Outdoor humidity", msg=str(outdoor_humidity))
            print('Sent to 1st moisture sensor feed : ', moisture_perc1)
            send_moist_warning_to_discord(moisture_perc1, "1st sensor")
        first_iteration = False
        mqtt_client_adafruit.check_msg()
        time.sleep(5)


# run the program
get_capacitator_measurements()