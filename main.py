import time
from machine import Pin, ADC

fully_dry = 44490  # 0% wet
fully_wet = 16500  # 100% wet

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
        print("MOISTURE PERCENTAGE IS -> " + str(round(moisture_perc, 1)) + "%")
        time.sleep(1)


get_capacitator_measurements()