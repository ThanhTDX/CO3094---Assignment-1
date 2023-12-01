import socket
import threading

PORT = 23456
BUFFER_SIZE = 1024
peers = []

# Function to broadcast a message to all connected peers
def broadcast(message, sender_socket):
    for peer_socket in peers:
        if peer_socket != sender_socket:
            try:
                peer_socket.send(message.encode())
            except socket.error:
                # Handle socket errors (connection closed, etc.)
                print("Error broadcasting message.")

# Function to handle incoming connections
def handle_connections():
    while True:
        client_socket, addr = server_socket.accept()
        peers.append(client_socket)
        print(f"Connection established with {addr}")

        # Send the list of connected peers to the new connection
        client_socket.send(','.join([str(peer.getpeername()) for peer in peers]).encode())

        # Start a thread to handle incoming messages from the new connection
        threading.Thread(target=handle_client, args=(client_socket,)).start()

# Function to handle incoming messages from a specific client
def handle_client(client_socket):
    while True:
        try:
            message = client_socket.recv(BUFFER_SIZE).decode()
            if not message:
                break
            print(f"Received: {message}")

            # Initiate the second round of broadcasting with the received text
            broadcast(f"Second round broadcast from {client_socket.getpeername()}: {message}", client_socket)

        except socket.error:
            # Handle socket errors (connection closed, etc.)
            print(f"Connection with {client_socket.getpeername()} closed.")
            peers.remove(client_socket)
            break

# Set up the server socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(('localhost', PORT))
server_socket.listen(5)

print("Server listening on port", PORT)

# Start a thread for handling connections
threading.Thread(target=handle_connections).start()
