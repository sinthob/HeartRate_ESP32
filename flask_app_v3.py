from flask import Flask , render_template
from flask_socketio import SocketIO
from flask_mqtt import Mqtt
from flask_mysqldb import MySQL
import math
import re

bpmList = []
spo2List = []
count = 0

def create_app():
    app = Flask(__name__ , template_folder='www/')
    app.config['SECRET_KEY'] = 'secret_key'

    # MySQL Configure
    app.config['MYSQL_HOST'] = 'localhost'
    app.config['MYSQL_USER'] = 'root'
    app.config['MYSQL_PASSWORD'] = 'dew2533449'
    app.config['MYSQL_DB'] = 'mydb'
    return app

app = create_app()

socketio = SocketIO(app)

app.config['MQTT_BROKER_URL'] = '192.168.4.2' 
app.config['MQTT_BROKER_PORT'] = 1883  
app.config['MQTT_USERNAME'] = ''  
app.config['MQTT_PASSWORD'] = ''
app.config['MQTT_KEEPALIVE'] = 300 
app.config['MQTT_TLS_ENABLED'] = False
topic = "+"
mqtt = Mqtt(app)

def clear_data(input_str):
    new_data = re.findall(r'[-+]?\d*\.\d+|\d+', input_str)
    return new_data

def send_data(bpm , spo2):    
    return {
        'heart_rate': bpm,
        'spo2': spo2
    }

@mqtt.on_connect()
def handle_connect(client, userdata, flags, rc):
    print("connect with result code" + str(rc))
    client.subscribe(topic)

@mqtt.on_message()
def handle_mqtt_message(client, userdata, message):
    msg = message.payload.decode()
    print(message.topic + " " + str(msg))
    data = clear_data(msg)
    socketio.emit('send_data', send_data(data[0], data[1]), namespace='/')

@socketio.on('connect')
def handle_connect():
    print('Client connected')
    socketio.emit('message', 'Connected to server')

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')
    socketio.emit('message', 'state: disconnected')

@socketio.on('message')
def handle_message(message):
    print('Received message:', message)
    
@app.route("/")
def index():
    return render_template("heart2.html")

if __name__ == "__main__":
    socketio.run(app, host='0.0.0.0' , port=5000)