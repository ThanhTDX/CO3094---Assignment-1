import socket
import os
import threading
import json

'''
Client Configuration
''' 
CLIENT_NAME = input("Enter your name: ")
SERVER_IP = "10.128.158.121"
SERVER_PORT = 4456

CLIENT_SERVER_IP = "10.128.160.120"
CLIENT_SERVER_PORT = 12346

BYTE = 1024
FORMAT = 'utf-8'

# Main socket to connect to server
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((SERVER_IP, SERVER_PORT))

# 2nd socket for client host (file sharing)
client_host_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# https://stackoverflow.com/questions/1365265/on-localhost-how-do-i-pick-a-free-port-number
# OS will create a random free port for client to bind
client_host_socket.bind((CLIENT_SERVER_IP, 0))  
# limit to 5 concurrent users
client_host_socket.listen(5)

# Function to send requests to the server

def send_request(request):
    client_socket.send(request.encode())
    response = client_socket.recv(1024).decode(FORMAT)
    # print("Server response:", response)
    return response

def send_file(conn, file_path):
    with open(file_path, 'rb') as file:
        data = file.read(1024)  # Read 1 KB at a time (adjust as needed)
        while data:
            conn.send(data)
            data = file.read(1024)
def fetch_from_clients(file_name):
    request = f"FETCH {file_name}"
    return send_request(request)

def inform_fetched_file(file_name, client_id):
    request = f"INFORM {client_id} {file_name}"
    send_request(request)

def retrieve_connect_port(msg):
    haddr, paddr = msg[1:-1].split(", ")
    haddr = haddr[1:-1]
    paddr = int(paddr)
    return paddr