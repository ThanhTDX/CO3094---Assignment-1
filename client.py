from client_util import *

def handle_incoming_request(conn, addr):
    while True:
        data = conn.recv(1024).decode()
        if not data:
            break
        # Process and handle the request from the other client
        parts = data.split()
        if parts[0].upper() == "FETCH":
            # Handle FETCH request here
            file_path = CLIENT_NAME + "/" + parts[1]
            send_file(conn, file_path)
            pass
        if parts[0].upper() == "PING":
            # Handle PING request here
            # Check for this while loop working
            conn.send("PONG".encode())
            pass
        # Add more handlers for other request types
        conn.close()

def listen_for_server():
    # Client connects to the server and starts sending request
    # but before that they have to process their request (publish, fetch)
    while True:
        command = input("Enter a command (publish, fetch): ").lower().strip().split()
        if command[0] == "publish":
            # command[1] : client file
            # command[2] : end result file
            try:
                publish_file(command[1], command[2])
            except Exception as e:
                print(f"Error publishing file: {e}")
                
        elif command[0] == "fetch":
            # Fetch client has file
            # command[1] : file
            try:
                # Client ask server about file and server returns clients with file
                # Format [(username1, client_server_port1),(username2, client_server_port2),etc.]
                target_clients = fetch_file_locations(command[1])
                # if server returns none raise exception
                if(target_clients == "none"): raise Exception("file not found")
                # Print only client name for user to see
                print("Currently available client:\n")
                for client in target_clients:
                    print(client[0], '\n')
                
                # ask user which user they want to get file from
                while True:
                    sender_client = input("Which user do you want to fetch? (type Quit to quit.)")
                    for client in target_clients:
                        # if client is found then thread is open to get file
                        if sender_client.lower() == client[0]:
                            fetch_handler = threading.Thread(target=fetch_and_receive_file, args=(command[1], client))
                            fetch_handler.start()
                            break
                        # if user want to quit
                        if sender_client.lower() == "quit":
                            break
                        # else nothing is found and return back
                        else:
                            print("User not found, try again.\n")

            except Exception as e:
                print(f"Error requesting to fetch file: {e}")
        if command[0] == "quit":    
            break
        else:
            print("Invalid command. Supported commands: CONNECT, PUBLISH, FETCH")

# Function for client to connect to a different client and ask for file
def fetch_and_receive_file(file_name, client_server):
    try:
        ip_address = client_server[0]
        port = int(client_server[1])
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((ip_address, port))
        
        # Send request name FETCH for handle_incoming_request
        fetch_request = f"FETCH {file_name}"
        client_socket.send(fetch_request.encode())

        # Create repository with username if not existed
        repository_path = CLIENT_NAME + "/"
        repository_path = os.path.join(repository_path, file_name)
        os.makedirs(os.path.dirname(repository_path), exist_ok=True)
        
        with open(repository_path, 'wb') as file:
            while True:
                data = client_socket.recv(1024)  # Receive 1 KB at a time (adjust as needed)
                if not data:
                    break
                file.write(data)

        # inform_fetched_file(file_name, client_server)
        print("FETCH SUCCESSFUL")
    except Exception as e:
        print(f"Error between client fetching file: {e}")

# Function to publish a file
def publish_file(lname, fname):
    # Check if the file exists in the specified local path (lname)
    if os.path.exists(lname):
        # Copy the file to the client's repository

        # Create a folder with name CLIENT_NAME
        # or ignore if it already exists
        repository_path = CLIENT_NAME + "/"
        os.makedirs(repository_path, exist_ok=True)

        # The existing or newly created folder directory will merge with the file, 
        # making it in the directory
        target_file_path = os.path.join(repository_path, fname)

        with open(lname, "rb") as source_file, open(target_file_path, "wb") as target_file:
            target_file.write(source_file.read())
        
        # Send a "PUBLISH" request to inform the server

        request = f"PUBLISH {fname}"
        send_request(request)
        print (f"Publish {fname} succesful!")
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