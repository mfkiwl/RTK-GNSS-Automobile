import socket
import RPi.GPIO as GPIO
import time
import sys
import smbus

sys.path.append('/home/gunpi5/Project')
from py_qmc5883l import QMC5883L

# Server setup
HOST = '0.0.0.0'  # Listen on all network interfaces
PORT = 5000       # Port TCP Server

I2C_BUS = 1
DEVICE_ADDRESS = 0x0D

sensor = QMC5883L(I2C_BUS, DEVICE_ADDRESS)
sensor.calibration = [
    [1.0, 0.0, 0.0],  #x
    [0.0, 1.0, 0.0],  #y
    [0.0, 0.0, 1.0]   #z
]

# Compass setup (QMC5883L)
def degrees_to_heading(degrees):
    if degrees < 0:
        degrees += 360
    headings = ['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW']
    idx = round(degrees / 45) % 8
    return headings[idx]

# TCP/IP control
def handle_control(conn, addr):
    print(f"Connected by {addr}")
    with conn:
        while True:
            try:
                data = conn.recv(1024)
                if not data:
                    print(f"Client {addr} disconnected.")
                    break
                command = data.decode('utf-8').strip()
                
                # Handle compass request
                if command == 'get_compass':
                    try:
                        bearing = sensor.get_bearing()
                        #heading = degrees_to_heading(bearing)
                        conn.sendall(f"{bearing}".encode('utf-8'))
                    except Exception as e:
                        print(f"Compass error: {e}")
                        conn.sendall(b"Compass error")
            except Exception as e:
                print(f"Command handling error: {e}")
                break

# Start the server
def start_server():
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('0.0.0.0', 5000))
            s.listen()
            print(f"Server listening on {HOST}:{PORT}")
            while True:
                conn, addr = s.accept()
                handle_control(conn, addr)
    except Exception as e:
        print(f"Server error: {e}")
    finally:
        GPIO.cleanup()

# Main execution
if __name__ == "__main__":
    start_server()
