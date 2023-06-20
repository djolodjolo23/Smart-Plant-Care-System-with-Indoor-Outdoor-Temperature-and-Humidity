import urequests
import json
import time

fully_dry = 44490  # 0% wet
fully_wet = 16500  # 100% wet
webhook_url = "https://discord.com/api/webhooks/1118471807377346592/SyTomR8MQRTJVds3mfL_pIfAIQFSEB_lgiLI97WHnJD9TrQAQhRMC5wPau5BNCevGR6G"

ADAFRUIT_IO_USERNAME = "djolodjolo"
ADAFRUIT_IO_KEY = "aio_MFoi10Z8EuG91Jfuv0Gr3cnnRQAQ"


last_sent_time = 0
time_interval = 3 * 60 * 60  # 3 hours


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