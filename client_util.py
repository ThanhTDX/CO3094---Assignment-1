import socket
import os
import threading

'''
Client Configuration
''' 
CLIENT_NAME = input("Enter your name: ")
SERVER_IP = "127.0.0.1"
SERVER_PORT = 4456

CLIENT_SERVER_IP = "127.0.0.1"
CLIENT_SERVER_PORT = 12346

CLIENT_ID = "127.0.0.1:12346"
BYTE = 1024
FORMAT = 'utf-8'

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((SERVER_IP, SERVER_PORT))

# Function to send requests to the server
def send_request(request):
    client_socket.send(request.encode())
    response = client_socket.recv(1024).decode()
    # print("Server response:", response)
    return response

def send_file(conn, file_path):
    with open(file_path, 'rb') as file:
        data = file.read(1024)  # Read 1 KB at a time (adjust as needed)
        while data:
            conn.send(data)
            data = file.read(1024)

# Function to fetch target clients for a file
# Returns: dict of available client username and their ports
def fetch_file_locations(file_name):
    request = f"FETCH {file_name}"
    return send_request(request)

# Unecessary
# Function to fetch a file
def fetch_file(file_name):
    request = f"FETCH FILE {file_name}"
    send_request(request)

# Necessary?
# Function to inform the server about a fetched file
def inform_fetched_file(file_name, client_id):
    request = f"INFORM {client_id} {file_name}"
    send_request(request)

def retrieve_connect_port(msg):
    haddr, paddr = msg[1:-1].split(", ")
    haddr = haddr[1:-1]
    paddr = int(paddr)
    return paddr