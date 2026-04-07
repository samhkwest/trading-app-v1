import subprocess
import time
import socket
import os

OPEND_PATH = r"C:\Program Files\Futu_OpenD\Futu_OpenD.exe"
HOST = "127.0.0.1"
PORT = 11111


def is_port_open(host, port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        return sock.connect_ex((host, port)) == 0


def start_opend():

    if is_port_open(HOST, PORT):
        print("OpenD already running.")
        return True

    if not os.path.exists(OPEND_PATH):
        print("OpenD executable not found.")
        return False

    print("Starting OpenD...")
    subprocess.Popen(OPEND_PATH)

    # Wait up to 15 seconds
    for _ in range(15):
        time.sleep(1)
        if is_port_open(HOST, PORT):
            print("OpenD started successfully.")
            return True

    print("OpenD failed to start.")
    return False