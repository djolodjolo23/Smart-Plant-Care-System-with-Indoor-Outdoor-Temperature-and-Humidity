import urequests as requests
import ujson

# OpenWeatherMap API key and city name
API_KEY = "b0f8cc0c19ce85fd145946f87ccd3837"
CITY_NAME = "Vaxjo"
COUNTRY_CODE = "SE"

# API endpoint URL
URL = f"http://api.openweathermap.org/data/2.5/weather?q={CITY_NAME},{COUNTRY_CODE}&appid={API_KEY}"

# Make a GET request to the API
response = requests.get(URL)

# Parse the JSON response
data = ujson.loads(response.text)

def make_request():
    response = requests.get(URL)
    data = ujson.loads(response.text)
    return data


def kelvin_to_celsius(kelvin):
    return kelvin - 273.15

def get_temperature():
    temperature = make_request()['main']['temp']
    return kelvin_to_celsius(temperature)

def get_humidity():
    return make_request()['main']['humidity']