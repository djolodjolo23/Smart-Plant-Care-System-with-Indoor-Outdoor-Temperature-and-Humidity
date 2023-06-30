import urequests
import json
from machine import Pin, ADC
import main



webhook_url = "https://discord.com/api/webhooks/1118471807377346592/SyTomR8MQRTJVds3mfL_pIfAIQFSEB_lgiLI97WHnJD9TrQAQhRMC5wPau5BNCevGR6G"
soil_adc_pin1 = ADC(Pin(26))

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
    moisture_perc1 = main.get_soil_moisture_percentage(adc1)
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