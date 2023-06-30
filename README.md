# Living Room Stats with self-watering flower pot controllable through node-red and HiveMQ.
Project for the course Introduction to Applied IoT at Linnaeus University, Summer 2023.

Author: Djordje Dimitrov (dd222im)

# Project Description:

In this project, I will measure the current living room stats, including temperature and humidity, as well as the soil moisture of my lovely plant. I will be using the RPI Pico W as my microcontroller and setting up webhook messages to notify me when the soil moisture drops below 10 percent. In addition to that, I have set up a water pump that can be controlled either through node-red ui or set up to work automatically when the moisture is bellow a certain point. 
The amount of time it took me to complete this project was around 3 weeks as I had to wait for the parts to arrive and to test my code many times. If you have all the parts, the project can be finished in 6-8 hours.

# Objective

The idea for this project came with the interest of solving a problem that I have during summer days, as I am usually away for a couple of weeks and my flower is left alone.
I wanted to create a system where I can monitor the soil moisture and water the plant when needed, as well as monitor the temperature and humidity of the room. 

The main purpose when applied for the course is to learn how to use the microcontroller in order to create a system that can be used in real life. I always had a great interest in building a smart home system, and this is a great start for me to learn how to do it.

The insights that I gained from this project are that I can use the microcontroller to create a system that can be used in real life, and that I can use node-red to create a dashboard and control the system. I also learned how to set up webhook messages and how to use them to notify me when the soil moisture drops below a certain point.

# List of material

- Raspberry Pi Pico W
- Capacitive Soil Moisture Sensor
- DHT11 Temperature and Humidity Sensor
- A set of jumper wires (both m2m and m2f)
- Mini water pump 12V DC with 2m hose
- 12V DC or 9V DC power supply
- Relay module
- Micro USB cable
- Breadboard
  

<img src="images/full_setup.jpg" alt="Image" width="600" height="450">



|Name |  Specification        | Cost      |   Bought at  |
|-------|----------------|-------|------------|
|Raspberry Pi Pico W    |   A microcontroller             |    98 sek  | electrokit.se  |
|DHT11 Temperature and Humidity Sensor | The sensor outputs serial data that can be read with a microcontroller |49 sek | electrokit.se  |
| Capacitive Soil Moisture Sensor  |Ground moisture sensor hygrometer module V1.2   | 67.99 sek |amazon.se  |
|A set of jumper wires| jumper wires m2m and m2f, 10 each  | 29 sek * 2| electrokit.se  |
|Mini water pump 12V DC with 2m hose| 12V DC mini water pump with 2m hose | 164 sek | amazon.se  |
|12V DC power supply| 12V DC power supply or in my case 9V DC power supply|around 100 sek| I had a spare one at home|
|Relay module| 5V relay module | 54.99 sek | amazon.se  |
|Micro USB cable| Micro USB cable | 29 sek | electrokit.se  |
|Breadboard| Breadboard | 29 sek | electrokit.se  |

# Computer Setup

The computer setup is fairly simple as I used VSCode with PyMakr extension to work on my code. PyMark allows uploading of the code directly from the IDE to the microcontroller, which is a convinient solution for testing as it does not require constant plugging and unplugging of the microcontroller.

The code is uploaded through the PyMakr extension in VSCode. The workflow is as follows:
1. Connect the microcontroller to the computer through the USB cable
2. Open the project in VSCode
3. Install the PyMakr extension
4. In the bottom left corner, click on the PyMakr icon, the new window will open
5. Create a new project and name it
6. Click on the 'Connect device' button in the top right corner
7. Click on the 'Sync project to device' button in the top right corner
8. Click on the 'Hard reset device' button in the dropdown menu in the top right corner
9. Click on the 'Connect device' button again and the microcontroller should start executing the code in the main.py file

Some extra steps might be needed to install the libraries that are used in the code, such as urequests, dht, and time. The libraries can be easily installed through the terminal on the pico board, with mip (works very similar to pip for desktop python). For example:
1. import mip
2. mip.install('urequests')

Additional installations: 
- Node.js - https://nodejs.org/en
- Node-red - https://nodered.org/docs/getting-started/local
- Node-red dashboard - https://flows.nodered.org/node/node-red-dashboard


# Putting everything together

All of the components are connected to the breadboard, which is then connected to the microcontroller. Pico is responsible for controlling the components through the GPIO pins, and also providing power and ground to the components. I used 3V3OUT and GND (slot 36 and 38 on pico), to connect the side of the breadboard that is responsible for providing + and - to the components. 
GPIO pins are used to connect the components to the microcontroller. The pins that are used are:

- Soil moisture sensor - GPIO 26
- DHT11 - GPIO 27
- Relay - GPIO 15



# Platform

At first, I have used AdaFruitIO as my platform for storing data, as it was very easy to set up and it had it's own MQTT broker. However, in the last two weeks of the project I switched to Node-red and HiveMQ as I wanted to have more control over the data and the way it is presented. I also wanted to have a dashboard that I can use to control the system. Node-red provides much more funcionality and it's commonly used for smart home systems, so I decided to switch to it. I also tried setting up a local MQTT broker (mosquitto), but I had some issues with it because I could not connect pico to it. I will try to set it up again in the future, but for now I am using HiveMQ. HiveMQ is a cloud MQTT broker that is free to use for up to 25 connections, which is more than enough for my project. In addition to that, it allows up to 10 gigabytes of data to be stored, which is also more than enough for my project. Even with a higher scale project, if data sent is limited (for example once every one or two hours), it would be enough to store the data for a very long time.
Very convinient thing I also discovered on Node-red is that it is possible to create an 'app' on the phone (basically just a saved localhost page), to control and see the complete UI, as on desktop. I like it a lot!


# The code



# Transmitting the data / connectivity

# Presenting the data

# Finalizing the design


