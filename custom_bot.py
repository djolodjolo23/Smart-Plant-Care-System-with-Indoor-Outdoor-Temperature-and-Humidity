import discord
from Adafruit_IO import MQTTClient
from secrets import discord_bot_token, adafruit_io_credentials

discord_bot_t = discord_bot_token['token']
adafruit_io_username = adafruit_io_credentials['username']
adafruit_io_key = adafruit_io_credentials['key']

mqtt_client_adafruit = MQTTClient(adafruit_io_username, adafruit_io_key)
mqtt_client_adafruit.connect()


intents = discord.Intents.all()
client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f'Bot: {client.user} is ready!')


@client.event
async def on_message(message):
    if message.author == client.user:
        return
    if message.content == 'pump on' or message.content == 'Pump on':
        # first pump
        await message.channel.send('Message received. Forwarding the message to Pico!')
        mqtt_client_adafruit.publish('Signal feed', 'TURN THE 1st PUMP ON')
        print('Sent to signal feed: ', message.content)
    elif message.content == 'yes, 2':
        # second pump
        await message.channel.send('Message received. Forwarding the message to Pico!')
        mqtt_client_adafruit.publish('Signal feed', 'TURN THE 2nd PUMP ON')
        print('Sent to signal feed: ', message.content)


client.run(discord_bot_t)
