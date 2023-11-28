import socket
import os
import threading
from client_util import *

from p2p import *

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

def handle_incoming_request(client_socket):
    while True:
        data = client_socket.recv(1024).decode()
        if not data:
            break
        # Process and handle the request from the other client
        parts = data.split()
        if parts[0] == "FETCH":
            # Handle FETCH request here
            file_path = CLIENT_NAME + "/" + parts[1]
            send_file(client_socket, file_path)
            pass
        if parts[0] == "PING":
            # Handle PING request here
            # Check for this while loop working
            client_socket.send("PONG".encode())
            pass
        # Add more handlers for other request types
    client_socket.close()

def listen_for_server():
    # Client connects to the server and starts sending request
    # but before that they have to process their request (publish, fetch)
    while True:
        command = input("Enter a command (publish, fetch): ").strip().split()
        if command[0] == "publish":
            # Implement the logic to publish a file here
            # client_id = 127.0.0.1:12346
            # command[1] : client file
            # command[2] : end result file
            '''
                CLIENT_ID is redundant, the end result it will be terminated
            '''
            try:
                publish_file(CLIENT_ID, command[1], command[2], client_socket)
            except Exception as e:
                print(f"Error publishing file: {e}")
                
        elif command[0] == "fetch":
            # Fetch client has file
            try:
                target_clients = fetch_file_locations(command[1])
                if(target_clients == "none"): raise Exception("file not founed")
                target_clients = target_clients.split(' ')
                fetch_handler = threading.Thread(target=fetch_and_receive_file, args=(command[1], target_clients[0]))
                fetch_handler.start()
            except Exception as e:
                print(f"Error requesting to fetch file: {e}")
            
        else:
            print("Invalid command. Supported commands: CONNECT, PUBLISH, FETCH")

def fetch_and_receive_file(file_name, client_id, client_socket):
    ip_address, port = client_id.split(':')
    port = int(port)
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((ip_address, port))
    
    fetch_request = f"FETCH {file_name}"
    client_socket.send(fetch_request.encode())

    repository_path = CLIENT_NAME + "/"
    repository_path = os.path.join(repository_path, file_name)
    os.makedirs(os.path.dirname(repository_path), exist_ok=True)
    with open(repository_path, 'wb') as file:
        while True:
            data = client_socket.recv(1024)  # Receive 1 KB at a time (adjust as needed)
            if not data:
                break
            file.write(data)

    inform_fetched_file(CLIENT_ID, file_name)
    print("FETCH SUCCESSFUL")

# Function to publish a file
# Command line: publish lname fname
# lname: 
# fname: 
def publish_file(client_id, lname, fname, client_socket):
    # Check if the file exists in the specified local path (lname)
    if os.path.exists(lname):
        # Copy the file to the client's repository (you need to define a path for the repository)
        # This will create a folder with name CLIENT_NAME
        repository_path = CLIENT_NAME + "/"
        os.makedirs(repository_path, exist_ok=True)

        # The existing or newly created folder directory will merge with the file, making it in the directory
        target_file_path = os.path.join(repository_path, fname)

        with open(lname, "rb") as source_file, open(target_file_path, "wb") as target_file:
            target_file.write(source_file.read())
        
        # Send a "PUBLISH" request to inform the server
        request = f"PUBLISH {client_id} {fname}"
        send_request(request, client_socket)
    else:
        print("The specified file does not exist in the local path.")

def main():
    # Client create a Thread to listen_for_server
    connect_thread = threading.Thread(target=listen_for_server)
    connect_thread.start()

    # # Server send client's id information, including its current port
    # inaddr = client_socket.recv(BYTE).decode(FORMAT)
    # connect_port = retrieve_connect_port(inaddr)

    # 2nd socket for client host (file sharing)
    client_host_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # https://stackoverflow.com/questions/1365265/on-localhost-how-do-i-pick-a-free-port-number
    # OS will create a random free port for client to bind
    client_host_socket.bind((CLIENT_SERVER_IP, 0))  
    # limit to 5 concurrent users
    client_host_socket.listen(5)

    # client send their name and 2nd server port to server
    client_socket.send(CLIENT_NAME.encode())
    client_socket.send(str(client_host_socket.getsockname()[1]).encode())

    while True:
        conn, addr = client_host_socket.accept()
        print(f"Accepted connection from {conn.getpeername()[0]}:{conn.getpeername()[1]}")
        request_handler = threading.Thread(target=handle_incoming_request, args=(conn, addr))
        request_handler.start()

# Start the main thread to listen for incoming connections from other clients
if __name__ == "__main__":
    main()