"""

A small Test application to show how to use Flask-MQTT.
Based on Flask-mqtt example:



"""
import eventlet
eventlet.monkey_patch()


import logging
import json
from flask import Flask, render_template
from flask_mqtt import Mqtt
from flask_socketio import SocketIO
from flask_bootstrap import Bootstrap
import os
from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)
app.config['SECRET'] = os.environ.get('SECRET')
app.config['TEMPLATES_AUTO_RELOAD'] = os.environ.get('TEMPLATES_AUTO_RELOAD') == 'True'
app.config['MQTT_BROKER_URL'] = os.environ.get('MQTT_BROKER_URL')
app.config['MQTT_BROKER_PORT'] = int(os.environ.get('MQTT_BROKER_PORT', 1883))
app.config['MQTT_USERNAME'] = os.environ.get('MQTT_USERNAME')
app.config['MQTT_PASSWORD'] = os.environ.get('MQTT_PASSWORD')
app.config['MQTT_KEEPALIVE'] = int(os.environ.get('MQTT_KEEPALIVE', 5))
app.config['MQTT_CLIENT_ID'] = os.environ.get('MQTT_CLIENT_ID')
app.config['MQTT_TLS_ENABLED'] = os.environ.get('MQTT_TLS_ENABLED') == 'True'
app.config['MQTT_LAST_WILL_TOPIC'] = os.environ.get('MQTT_LAST_WILL_TOPIC')
app.config['MQTT_LAST_WILL_MESSAGE'] = os.environ.get('MQTT_LAST_WILL_MESSAGE')
app.config['MQTT_LAST_WILL_QOS'] = int(os.environ.get('MQTT_LAST_WILL_QOS', 2))

# Parameters for SSL enabled
# app.config['MQTT_BROKER_PORT'] = 8883
# app.config['MQTT_TLS_ENABLED'] = True
# app.config['MQTT_TLS_INSECURE'] = True
# app.config['MQTT_TLS_CA_CERTS'] = 'ca.crt'

mqtt = Mqtt(app)
socketio = SocketIO(app)
bootstrap = Bootstrap(app)


@app.route('/')
def index():
    return render_template('index.html')


@socketio.on('publish')
def handle_publish(json_str):
    data = json.loads(json_str)
    mqtt.publish(data['topic'], data['message'], data['qos'])


@socketio.on('subscribe')
def handle_subscribe(json_str):
    data = json.loads(json_str)
    mqtt.subscribe(data['topic'], data['qos'])


@socketio.on('unsubscribe_all')
def handle_unsubscribe_all():
    mqtt.unsubscribe_all()


@mqtt.on_message()
def handle_mqtt_message(client, userdata, message):
    data = dict(
        topic=message.topic,
        payload=message.payload.decode(),
        qos=message.qos,
    )
    socketio.emit('mqtt_message', data=data)


@mqtt.on_log()
def handle_logging(client, userdata, level, buf):
    # print(level, buf)
    pass


if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, use_reloader=False, debug=True)