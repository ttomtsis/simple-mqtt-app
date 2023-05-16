# Simple mqtt app

Simple python app leveraging paho-mqtt library to communicate with an Arduino device over
the Things Network. The app fetches the sensor's readings from TTN and stores them in a local MySQL
Database, when the sensor's readings are below a specified threshold the app issues a turn lightbulb on
command to the device
