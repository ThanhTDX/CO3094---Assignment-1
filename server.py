import os
import socket

IP = "127.0.0.1"
PORT = 4456
SIZE = 1024
FORMAT = "utf"


def handle_client_connection(conn, addr):
    print(f"[NEW CONNECTION] {addr} connected.\n")

    # Receive folder name
    folder_name = conn.recv(SIZE).decode(FORMAT)

    # Create the folder if it doesn't exist
    folder_path = os.path.join("folder_in_server", folder_name)
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
        conn.send(f"Folder ({folder_name}) created.".encode(FORMAT))
    else:
        conn.send(f"Folder ({folder_name}) already exists.".encode(FORMAT))

    # Receive files
    while True:
        msg = conn.recv(SIZE).decode(FORMAT)
        cmd, data = msg.split(":")

        match cmd:
            case "FILENAME":
            # Receive the file name
                print(f"[CLIENT] Received the filename: {data}.")

                file_path = os.path.join(folder_path, data)
                file = open(file_path, "w")
                conn.send("Filename received.".encode(FORMAT))

            case "DATA":
            # Receive data from client
                print(f"[CLIENT] Receiving the file data.")
                file.write(data)
                conn.send("File data received".encode(FORMAT))

            case "FINISH":
            # Close the file and send confirmation
                file.close()
                print(f"[CLIENT] {data}.\n")
                conn.send("The data is saved.".encode(FORMAT))

            case "CLOSE":
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
        handle_client_connection(conn, addr)


if __name__ == "__main__":
    main()
