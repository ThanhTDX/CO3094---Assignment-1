import socket

# Function to send requests to the server
def send_request(request, client_socket):
    client_socket.send(request.encode())
    response = client_socket.recv(1024).decode()
    print("Server response:", response)
    return response

def retrieve_connect_port(msg):
    haddr, paddr = msg[1:-1].split(", ")
    haddr = haddr[1:-1]
    paddr = int(paddr)
    return paddr

def send_file(client_socket, file_path):
    with open(file_path, 'rb') as file:
        data = file.read(1024)  # Read 1 KB at a time (adjust as needed)
        while data:
            client_socket.send(data)
            data = file.read(1024)

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