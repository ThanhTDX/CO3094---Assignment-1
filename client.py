import socket
import threading

PORT = 23456
BUFFER_SIZE = 1024

# Function to receive messages from the server
def receive_messages(client_socket):
    while True:
        try:
            message = client_socket.recv(BUFFER_SIZE).decode()
            if not message:
                break
            print(message)
        except socket.error:
            # Handle socket errors (connection closed, etc.)
            print("Connection to the server closed.")
            break

# Function to get user input and send messages to the server
def send_messages(client_socket):
    while True:
        try:
            message = input("Enter text to send: ")
            client_socket.send(message.encode())
        except socket.error:
            # Handle socket errors (connection closed, etc.)
            print("Connection to the server closed.")
            break

# Set up the client socket
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect(('localhost', PORT))

# Start threads for receiving and sending messages
threading.Thread(target=receive_messages, args=(client_socket,)).start()
threading.Thread(target=send_messages, args=(client_socket,)).start()
