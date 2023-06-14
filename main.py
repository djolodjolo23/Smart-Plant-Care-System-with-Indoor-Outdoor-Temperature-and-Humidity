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
    soil_adc = ADC(Pin(26))
    while True:
        adc = soil_adc.read_u16()
        moisture_perc = get_soil_moisture_percentage(adc)
        mqtt_client.publish(topic="djolodjolo/feeds/moisture-sensor", msg=str(moisture_perc))
        print('Sent to Adafruit IO: ', moisture_perc)
        time.sleep(5)


get_capacitator_measurements()