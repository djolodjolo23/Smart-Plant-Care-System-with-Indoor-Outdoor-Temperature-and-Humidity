import time
from machine import Pin, ADC
from mqtt import MQTTClient


fully_dry = 44490  # 0% wet
fully_wet = 16500  # 100% wet

ADAFRUIT_IO_USERNAME = "djolodjolo"
ADAFRUIT_IO_KEY = "aio_MFoi10Z8EuG91Jfuv0Gr3cnnRQAQ"

mqtt_client = MQTTClient("", "io.adafruit.com", user=ADAFRUIT_IO_USERNAME, password=ADAFRUIT_IO_KEY)
mqtt_client.connect()



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
        if not first_iteration:
            mqtt_client.publish(topic="djolodjolo/feeds/1st_moisture_sensor", msg=str(moisture_perc1))
            print('Sent to 1st moisture sensor feed : ', moisture_perc1)
            mqtt_client.publish(topic="djolodjolo/feeds/2nd_moisture_sensor", msg=str(moisture_perc2))
            print('Sent to 2nd moisture sensor feed : ', moisture_perc2)
        first_iteration = False
        time.sleep(10)


get_capacitator_measurements()