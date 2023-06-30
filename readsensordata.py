

def read_temp_sensor_data(dht_sensor):
    dht_sensor.measure()
    temperature = dht_sensor.temperature()
    humidity = dht_sensor.humidity()
    return temperature, humidity


def get_soil_moisture_percentage(adc_value, fully_dry, fully_wet):
    adc_range = fully_dry - fully_wet
    moisture_range = 100
    moisture_percentage = (fully_dry - adc_value) / adc_range * moisture_range
    return moisture_percentage