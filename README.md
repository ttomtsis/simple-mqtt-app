# Simple mqtt app
Simple python app leveraging the eclipse paho-mqtt library and The Things Network in order to control a local Arduino device. The device has a built-in light sensor as well as a light-bulb, and we aim to turn on the light bulb only in situations where the surrounding light is insufficient. The Arduino device communicates with the mqtt app over the Things Network. The app fetches the sensor's readings from TTN and stores them in a local MySQL Database, when the sensor's readings are below a specified threshold the app issues a "turn lightbulb on" command to the device.

## Features
* Python 3.10
* Eclipse Paho MQTT
* The Things Network v3 API

## Gettings started
The only things you will require are MySQL, python and the paho-mqtt library properly installed and configured.

* First clone the project from GitHub `git clone https://github.com/ttomtsis/simple-mqtt-app`
* Navigate to the project directory
* Initialize the MySQL Database with the `DB_init.sql` script provided 
* Use python3 to execute the program `python3 main.py`

