from flask import Flask, jsonify
import socket
import uuid
import psutil

app = Flask(__name__)

def get_device_info():
    ip_address = socket.gethostbyname(socket.gethostname())
    mac_address = ':'.join(['{:02x}'.format((uuid.getnode() >> ele) & 0xff) for ele in range(0, 48, 8)])
    
    return {
        "ip_address": ip_address,
        "cpu_usage": psutil.cpu_percent(interval=1),
        "RAM_usage": psutil.virtual_memory().percent,
        "MAC_Address": mac_address
    }

@app.route('/device_info', methods=['GET'])
def device_info():
    return jsonify(get_device_info())

if __name__ == '__main__':
    app.run(debug=True)