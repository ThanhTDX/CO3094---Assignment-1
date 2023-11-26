import os
import socket
import threading

IP = "127.0.0.1"
PORT = 4456
SIZE = 1024
FORMAT = "utf"

# Dictionary to store client addresses and associated filenames
client_file_dict = {}

def print_current_files():
    print("\n[SERVER] Current Files:")
    for addr, filename in client_file_dict.items():
        print(f"Client Address: {addr}, Filename: {filename}")
    print("")

def handle_client_connection(conn, addr):
    print(f"[NEW CONNECTION] {addr} connected.\n")

    # Receive folder name
    msg = conn.recv(SIZE).decode(FORMAT)
    cmd, folder_name = msg.split(":")
    
    # Create the folder if it doesn't exist
    folder_path = os.path.join("folder_in_server", folder_name)
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
        conn.send(f"Folder ({folder_name}) created.".encode(FORMAT))
    else:
        conn.send(f"Folder ({folder_name}) already exists.".encode(FORMAT))

    # Receive and handle commands
    while True:
        msg = conn.recv(SIZE).decode(FORMAT)
        cmd, data = msg.split(":")

        if cmd == "FILENAME":
            # Receive the file name
            print(f"[CLIENT] Received the filename: {data}.")

            file_path = os.path.join(folder_path, data)
            conn.send("Filename received.".encode(FORMAT))

        elif cmd == "LIST":
            # Send the list of filenames to the client
            file_list = os.listdir(folder_path)
            conn.send(":".join(file_list).encode(FORMAT))

        elif cmd == "PUSH_FILENAME":
            # Receive the pushed filename and store in the dictionary
            client_file_dict[addr] = data
            conn.send(f"Filename ({data}) pushed and stored.".encode(FORMAT))

        elif cmd == "SHOW_FILES":
            # Print the current file names and associated client addresses
            print_current_files()

        elif cmd == "CLOSE":
            # Close the connection
            conn.close()
            print(f"[CLIENT] {data}")
            break


def main():
    print("[STARTING] Server is starting.\n")

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((IP, PORT))
    server.listen()
    print("[LISTENING] Server is waiting for clients.")

    while True:
        conn, addr = server.accept()

        # Create a new thread for each client
        client_thread = threading.Thread(target=handle_client_connection, args=(conn, addr))
        client_thread.start()


if __name__ == "__main__":
    main()
