import time
from machine import Pin, ADC
import ubinascii
import json
import dht
import ujson as json
import time
import ubinascii
import json
import dht
import machine
import gc
from secrets import webhook_url, mqtt_broker_address, ssl_params
import readsensordata as rsd
import sh1106


fully_dry = 44490  # 0% wet
fully_wet = 16500  # 100% wet
can_be_watered = 30700 # sort of dry, one more day needed
webhook_url = webhook_url["url"]
gc.enable()

i2c = machine.I2C(0, scl=machine.Pin(17), sda=machine.Pin(16))
display = sh1106.SH1106_I2C(128, 64, i2c)
display.init_display()



client_id = ubinascii.hexlify(machine.unique_id())
green_light = Pin(14, Pin.OUT)
yellow_light = Pin(13, Pin.OUT)
red_light = Pin(12, Pin.OUT)
green_light.value(0) # debug
yellow_light.value(0) # debug 
red_light.value(0) # debug

lights = [green_light, yellow_light, red_light]



soil_adc_pin1 = ADC(Pin(26))
time.sleep(3)

last_sent_time = 0
time_interval = 2 * 60 * 60  # 3 hours

auto_wattering = False
mqtt_client = None


def water_the_plant():
    for light in lights:
        light.value(1)
    relay_pump_pin = Pin(15, Pin.OUT)
    print("watering the flower...")
    time.sleep(4) # on for 3 sec
    display.show()
    relay_pump_pin.init(Pin.IN) # off

# create a linked list of lights
def create_linked_list():
    head = None
    for light in lights:
        if head is None:
            head = light
        else:
            head.next = light
    return head




# create a 30 sec timer and show it on the display
def start_watering_timer(seconds, cycle):
    display.fill(0)
    timer = seconds
    adc1 = soil_adc_pin1.read_u16()
    moisture_perc = rsd.get_soil_moisture_percentage(adc1, fully_dry, fully_wet)
    moisture_perc = round(moisture_perc, 2)
    while timer != 0:
        display.text("Watering in: " + str(timer), 0, 0, 1)
        display.text("Cycle: " + str(cycle) + "/6", 0, 10, 1)
        # display moisture percentage bellow the text
        display.text("Current Moisture: ", 0, 20, 1)
        display.text(str(moisture_perc) + "%", 0, 30, 1)
        if ((seconds - timer) % 3 == 0):
            red_light.value(1)
            yellow_light.value(0)
            green_light.value(0)
        elif ((seconds - timer) % 3 == 1):
            red_light.value(0)
            yellow_light.value(1)
            green_light.value(0)
        else:
            red_light.value(0)
            yellow_light.value(0)
            green_light.value(1)
        print("Watering in: " + str(timer))
        timer -= 1
        time.sleep(1)
        display.show()
        display.fill(0)
    display.text("Watering the", 0, 0, 1)
    display.text("flower...", 0, 10, 1)
    display.show()
    for light in lights:
        light.value(0)
    water_the_plant()

def check_if_watering_is_needed():
    adc1 = soil_adc_pin1.read_u16()
    moisture_perc1 = rsd.get_soil_moisture_percentage(adc1, fully_dry, fully_wet)
    # round the moisture percentage to 2 decimal places
    moisture_perc1 = round(moisture_perc1, 2)
    if moisture_perc1 <= 17:
        display.text("Watering is", 0, 0, 1)
        display.text("needed!", 0, 10, 1)
        print("Watering is needed!")
        display.show() 
        for i in range(5): # 3 times
            start_watering_timer(30, i + 1)
        time.sleep(3)
        display.fill(0)
        display.text("Watering", 0, 0, 1)
        display.text("finished!", 0, 10, 1)
        display.show()
        time.sleep(6)
        machine.reset()

    else:
        green_light.value(1)
        display.fill(0)
        time.sleep(1)
        display.text("No watering", 0, 0, 1)
        display.text("needed!", 0, 10, 1)
        # display moisture percentage bellow the text
        display.text("Moisture:" , 0, 20, 1)
        display.text(str(moisture_perc1) + "%", 0, 30, 1)
        print("No watering needed!")
        display.show()
        time.sleep(6)
        display.fill(0)
        display.show()
        for light in lights:
            light.value(0)
        machine.deepsleep(3000000) # 1 hourc


try:
    check_if_watering_is_needed() # 10 * 3 sec needed for 0.5 liter of water
except Exception as e:
    print("Exception occurred:", str(e))
    machine.reset()
