import socket
import os
import threading

# Client Configuration
SERVER_IP = "127.0.0.1"
SERVER_PORT = 4456

CLIENT_SERVER_IP = "127.0.0.1"
CLIENT_SERVER_PORT = 12346

CLIENT_ID = "127.0.0.1:12346"

# Function to send requests to the server
def send_request(request, client_socket):
    client_socket.send(request.encode())
    response = client_socket.recv(1024).decode()
    print("Server response:", response)
    return response

# Main thread line:
#   _main_
#       -> listen_for_server
#       -> Thread : st
# publish abc xyz


def handle_incoming_request(client_socket):
    while True:
        data = client_socket.recv(1024).decode()
        if not data:
            break
        # Process and handle the request from the other client
        parts = data.split()
        if parts[0] == "FETCH":
            # Handle FETCH request here
            file_path = "client_repository/" + parts[1]
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
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((SERVER_IP, SERVER_PORT))
    while True:
        command = input("Enter a command (publish, fetch): ").strip().split()
        if command[0] == "publish":
            # Implement the logic to publish a file here
            try:
                publish_file(CLIENT_ID, command[1], command[2], client_socket)
            except Exception as e:
                print(f"Error publishing file: {e}")
                
        elif command[0] == "fetch":
            # Fetch client has file
            try:
                target_clients = fetch_file_locations(command[1], client_socket)
                if(target_clients == "none"): raise Exception("file not founed")
                target_clients = target_clients.split(' ')
                fetch_handler = threading.Thread(target=fetch_and_receive_file, args=(command[1], target_clients[0]))
                fetch_handler.start()
            except Exception as e:
                print(f"Error requesting to fetch file: {e}")
            
        else:
            print("Invalid command. Supported commands: CONNECT, PUBLISH, FETCH")

def send_file(client_socket, file_path):
    with open(file_path, 'rb') as file:
        data = file.read(1024)  # Read 1 KB at a time (adjust as needed)
        while data:
            client_socket.send(data)
            data = file.read(1024)

def fetch_and_receive_file(file_name, client_id):
    ip_address, port = client_id.split(':')
    port = int(port)
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((ip_address, port))
    
    fetch_request = f"FETCH {file_name}"
    client_socket.send(fetch_request.encode())

    repository_path = "client_repository/"
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
        repository_path = "client_repository/"
        os.makedirs(repository_path, exist_ok=True)
        target_file_path = os.path.join(repository_path, fname)
        with open(lname, "rb") as source_file, open(target_file_path, "wb") as target_file:
            target_file.write(source_file.read())
        
        # Send a "PUBLISH" request to inform the server
        request = f"PUBLISH {client_id} {fname}"
        send_request(request, client_socket)
    else:
        print("The specified file does not exist in the local path.")

# Function to fetch target clients for a file
def fetch_file_locations(file_name, client_socket):
    request = f"FETCHCLIENT {file_name}"
    return send_request(request, client_socket)

# Function to fetch a file
def fetch_file(file_name):
    request = f"FETCHFILE {file_name}"
    send_request(request)

# Function to inform the server about a fetched file
def inform_fetched_file(client_id, file_name):
    request = f"INFORM {client_id} {file_name}"
    send_request(request)

def main():
    server_listener = threading.Thread(target=listen_for_server)
    server_listener.start()
    request_handling_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    request_handling_socket.bind((CLIENT_SERVER_IP, CLIENT_SERVER_PORT))  # Change the port as needed
    # Currect SERVER_IP : 127.0.0.1
    # Current SERVER_PORT : 4456

    request_handling_socket.listen(5)
    print("Listening for incoming requests on 127.0.0.1:12346")
    while True:
        client_socket, addr = request_handling_socket.accept()
        print(f"Accepted connection from {addr[0]}:{addr[1]}")
        request_handler = threading.Thread(target=handle_incoming_request, args=(client_socket,))
        request_handler.start()

# Start the main thread to listen for incoming connections from other clients
if __name__ == "__main__":
    main()