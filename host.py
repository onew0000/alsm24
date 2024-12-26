from flask import Flask, render_template, jsonify, send_from_directory, url_for
import threading
import time
import os
import serial
from datetime import datetime

app = Flask(__name__)
app.static_folder = 'static'

current_distance = 0
current_color = "red"

def read_bluetooth():
    global current_distance, current_color
    try:
        ser = serial.Serial('/dev/tty.HC-05', 9600, timeout=1)
        while True:
            if ser.in_waiting:
                try:
                    data = ser.readline().decode().strip()
                    if data in ("red", "green", "other"):
                        current_color = data
                except Exception as e:
                    print(f"Bluetooth reading error: {e}")
            time.sleep(0.1)
    except Exception as e:
        print(f"Serial connection error: {e}")

@app.route('/')
def index():
    return render_template('host.html', distance=current_distance, color=current_color)

@app.route('/get_distance_and_color')
def get_distance_and_color():
    return jsonify({
        'distance': current_distance,
        'color': current_color,
    })

@app.route('/static/<path:filename>')
def serve_static(filename):
    return send_from_directory(app.static_folder, filename)

if __name__ == '__main__':
    os.makedirs(app.static_folder, exist_ok=True)
    bluetooth_thread = threading.Thread(target=read_bluetooth)
    bluetooth_thread.daemon = True
    bluetooth_thread.start()
    app.run(host='127.0.0.1', port=8100, debug=True)