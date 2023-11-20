import socket

HOST = "localhost"  # Change this to your actual IP address if needed
PORT = 4456
BUFFER_SIZE = 1024

def main():
    try:
        # Create a TCP socket
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
            # Bind the socket to the specified IP and port
            server_socket.bind((HOST, PORT))
            # Listen for incoming connections
            server_socket.listen()

            print(f"[SERVER] Listening for connections on {HOST}:{PORT}")

            while True:
                # Accept an incoming connection
                client_socket, client_address = server_socket.accept()
                print(f"[SERVER] Connected to {client_address}")

                # Handle file transfer with the connected client
                handle_file_transfer(client_socket)

                # Close the connection with the client
                client_socket.close()
                print(f"[SERVER] Disconnected from {client_address}")
    except Exception as e:
        print(f"[SERVER] Error: {e}")

def handle_file_transfer(client_socket):
    while True:
        # Receive command and data from the client
        command_and_data = client_socket.recv(BUFFER_SIZE).decode('utf-8')

        if command_and_data:
            # Split the command and data
            command, data = command_and_data.split(':')

            if command == 'FILENAME':
                # Receive the filename
                filename = data
                print(f"[SERVER] Received filename: {filename}")

                # Construct the file path
                file_path = os.path.join('server_folder', filename)

                # Send a message to the client indicating filename reception
                client_socket.send('Filename received'.encode('utf-8'))

                # Open the file for writing
                with open(file_path, 'wb') as file:
                    # Receive file data from the client
                    while True:
                        data = client_socket.recv(BUFFER_SIZE)

                        if not data:
                            break

                        file.write(data)

                    # Send a message to the client indicating data reception
                    client_socket.send('File data received'.encode('utf-8'))

                # Print a message indicating file transfer completion
                print(f"[SERVER] File transfer completed: {filename}")

            elif command == 'CLOSE':
                # Close the connection
                break

if __name__ == '__main__':
    main()
