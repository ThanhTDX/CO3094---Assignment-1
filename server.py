import socket
import time
import threading
import json

IP = "10.128.160.120"
PORT = 4456
SIZE = 1024
FORMAT = "utf-8"

# This can be done with list (not sure about array) 
# They all have upsides and disadvantages
client_list = {}    # store dict of id with format {port} : (username, client_ip, client_server_port)
file_list = {}      # Store list of client's id that have corresponding file (file - [(name, client_server_port)])
# blue_lock = threading.Lock()


# # Automatic mass client ping to check connection
# def mass_ping_client():
#     while True:
#         time.sleep(15)
#         if client_list:
#             for key, value in client_list.items():
#                 ping_thread = threading.Thread(target=ping_client,args=value[0])
#                 ping_thread.start()

# Func to send message to client
def send_message(message, conn):
    # '''
    # Send message to specific client
    # '''
    # message_length = len(message)
    # send_length = str(message_length).encode(FORMAT)
    # send_length+= b' '*(SIZE-len(send_length))

    # conn = client_list[client_id]
    # conn.send(send_length)
    # conn.send(message)
    conn.send(message.encode())

# Remove client_list and all instance of file_list in server
def remove_client(client_id):
    # client_id: (username, client_server_port)
    
    # LEGACY CODE
    # del client_list[client_id]
    # for key, value in file_list.items():
    #     if client_id in value:
    #         value.remove(client_id)

    client_name = client_id[0]
    # Create new list and overwrite old client_list, removing keys with client_id in it
    new_client_list = { key : value
                    for key, value in client_list.items()
                    if value != client_id }
    client_list.clear()
    client_list.update(new_client_list)

    # Create new list and overwrite old file_list, removing values of deleted username
    new_file_list = {}
    for file, client_with_file in file_list.items():
        for client in client_with_file:
            if client[0] == client_name:
                client_with_file.remove(client)
        if file_list[file]:
            new_file_list[file] = file_list[file]

    file_list.clear() 
    file_list.update(new_file_list)
    print(f"User {client_name} has been removed.")


# Function to return client's name, ip and client_server_port
def get_client_information(name):
    found_client = False
    # Iterate through client_list to find name
    for key, value in client_list.items():
        # If found then returns (username, ip, client_server_port)
        # else, None
        if value[0] == name:
            found_client = True
            username, client_ip, client_server_port = value
            break
    if not found_client:
        return None
    else:
        return (username, client_ip, client_server_port)


def ping_client(hostname):
    # LEGACY CODE
    # message = 'ping' + " " + str(client_id)
    # send_message(client_id, message)
    # conn = client_list[client_id]

    # time.sleep(0.1) # wait time for client to respond
    # message_length = conn.recv(SIZE).decode(FORMAT) 
    # if message_length:
    #     message_length = int(message_length)
    #     message = conn.recv(message_length).decode(FORMAT)
    #     print(message)
    #     return True
    # else:
    #     remove_client(client_id)
    #     return False
    # END LEGACY CODE

    # If client_list is empty, return
    if not client_list:
        print("There's no user connecting right now.\n")
        return
    try:
        # Find the client
        client_info = get_client_information(hostname)
        # If client is not found print error and return
        if not client_info:
            print(f"{hostname} is not in the client list.")
            return
        
        username = client_info[0]
        user_ip = client_info[1]
        client_server_port = int(client_info[2])

        # Server will create a client socket to connect to 
        # the client_server_port where client has its own binding socket
        connect_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        connect_socket.connect((user_ip, client_server_port))
        connect_socket.settimeout(5)

        # Ping and wait
        connect_socket.send("Ping".encode())
        time.sleep(5)
        data = connect_socket.recv(SIZE).decode(FORMAT)

        # If client doesn't respond remove client
        if not data:
            remove_client((username, user_ip, client_server_port))
        else:
            print(f"User {username} still connecting.")
        # End connection
        connect_socket.close()
    except socket.error as e:
        remove_client((username, user_ip, client_server_port))
        return
    except Exception as e:
        return

# LEGACY CODE
def send_avail_sender_list(receiver_id, fname):
    '''
    The sending message follows this format:
    [<id1>, <id2>, ...]
    Example:
        [('192.168.1.105', 62563), ('192.168.1.105', 62564)]
        []
    '''
    conn = client_list[receiver_id]
    sender_list = file_list.get(fname, [])
    send_message(receiver_id, str(sender_list))
    return (len(sender_list) > 0)

# LEGACY CODE
def check_valid_sender(client_id, fname):
    sender_list = file_list[fname]
    if (client_id in sender_list) and ping_client(client_id):
        return True
    else:
        return False

def handle_fetch_file(client_conn, file_name):
    '''
    The client's message that used for dertermine source client
    must follow this format:
    <sender_id>
    Example:
        ('192.168.1.105', 62563)

    The sender will receive message in the following format from the server:
    <receiver_id> <fname>
    Example:
        ('192.168.1.105', 62563) test.txt

    The receiver will receive message in the following format from the server:
    <sender_id>
    Example:
        ('192.168.1.105', 62563)
    '''
    # Old logic ^

    # LEGACY CODE
    # conn = client_list[receiver_id]
    # valid_sender = send_avail_sender_list(receiver_id, fname)
    # if not valid_sender:
    #     send_message(receiver_id, "invalid fetchfile")
    # else:
    #     while True:
    #         # Get message from fetching client
    #         message_length = conn.recv(SIZE).decode(FORMAT) 
    #         if message_length:
    #             message_length = int(message_length)
    #             sender_id = conn.recv(message_length).decode(FORMAT)
    #             if check_valid_sender(sender_id, fname):
    #                 send_message(receiver_id, "valid sender_id")
    #                 break


    #     # Notify receiver
    #     re_message = str(sender_id)
    #     se_message = str(receiver_id) + " " + fname
    #     send_message(receiver_id, se_message)
    #     send_message(sender_id, re_message)

    # New Logic
    # 
    # Server searches in file_list 
    # sends request client list of client's with name and client_server_port
    # Format: [(client1, client_server_port1),(client1, client_server_port1), etc.]

    list_name = file_list[file_name]
    if not list_name :
        client_conn.send("none".encode()) 
    else:
        # This line of code encapsulates my insanity solving this
        # https://stackoverflow.com/questions/17796446/convert-a-list-to-a-string-and-back
        send_msg = json.dumps(list_name)
        client_conn.send(send_msg.encode())


# Function for server when client publish file
def handle_publish_file(client_conn, file_name):
    # file_list saves all usernames and their client_server_port
    # eg: file_list["a.txt"] saves [(thanh, 10.127.158.120, 4402), (an, 10.127.158.120, 3054), etc.]

    # get username, client_ip client_server_port from client_conn
    username = client_list[client_conn.getpeername()[1]][0]
    client_ip = client_list[client_conn.getpeername()[1]][1]
    client_server_port = client_list[client_conn.getpeername()[1]][2]

    file_list[file_name] = file_list.get(file_name, []) + [(username, client_ip , client_server_port)]

    send_message("Success", client_conn)
    print(f"Client {username} upload file {file_name}")

# Function for server to discover and ping clients
def handle_commands():
    while True:
        # func : action
        # hostname : username
        command = input()
        if command:
            func, hostname = command.split()

            # Discover client 
            if func == 'discover':
                try:
                    # files = []
                    # for fname, client_list in file_list.items():
                    #     for client_id in client_list:
                    #         if hostname == client_id:
                    #             files.append(fname)
                    #             break
                    files =  []
                    for file_name, list_name in file_list.items():
                        for client in list_name:
                            if client[0] == hostname:
                                files.append(file_name)
                    print(f"Files of current hostname {hostname}:")
                    print(files)
                except Exception as e:
                    print(f"Error discovering user: {e} ")
            
            elif func == 'ping':
                try:
                    ping_client(hostname)
                except Exception as e:
                    print(f"Error pinging user: {e} ")

def handle_client_connection(client_conn, client_addr):
    '''
    The receiving cmd must be in the following format:
    <function> <fname> where:
    <function> can be: ['publish', 'fetch']
    <fname> can be any filename
    Example: 
        publish test.txt
        fetch test.txt
    '''

    # with blue_lock:
    #     client_list[addr] = conn

    # Client only send 2 request
    # publish filename
    # fetch filename
    try:
        while True:
            message_length = client_conn.recv(SIZE).decode(FORMAT) 
            if message_length:
                
                # # Received a message's length (message_length != 0)
                # message_length = int(message_length)
                # message = conn.recv(message_length).decode(FORMAT)
                func, fname = message_length.split()
                if func.lower() == 'publish':
                    try:
                        handle_publish_file(client_conn, fname)
                    except Exception as e:
                        print(f"Error while publishing: {e}")
                elif func.lower() == 'fetch':
                    try:
                        handle_fetch_file(client_conn, fname)  
                    except Exception as e:
                        print(f"Error while fetching: {e}")
    # Handle exception, remove_client and disconnect them
    except Exception as e:
        # remove_client(client_list[client_conn.getpeername()[1]])
        client_conn.close()
                  
    

def main():
    # Text
    print("[STARTING] Server is starting.\n")

    # Server creates a socket with static IP and PORT for connection 
    # IP = https://www.tutorialspoint.com/python-program-to-find-the-ip-address-of-the-client
    # PORT = 4456
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    hostname = socket.gethostname()
    server_ip_address = socket.gethostbyname(hostname)
    server_socket.bind((server_ip_address, PORT))

    print(server_socket.getsockname()[0])

    # Limits listening clients to 20
    server_socket.listen(20)

    # Text
    print("[LISTENING] Server is waiting for clients.")

    # A thread is created for server's self command (ping, discover)
    command_thread = threading.Thread(target=handle_commands)
    command_thread.start()

    # # A 3rd thread to automatically ping all clients to check for connection
    # ping_thread = threading.Thread(target=mass_ping_client)
    # ping_thread.start()
    
    while True:
        client_conn, client_addr = server_socket.accept()

        # # send back client's id (including ip and current port)
        # client_conn.send(str(client_addr).encode(FORMAT))

        client_ip = client_conn.getpeername()[0]
        client_port = client_conn.getpeername()[1]

        # Client send their name and 2nd server's port (i hate pier-to-pier)
        username = client_conn.recv(SIZE).decode(FORMAT)
        client_server_port = int(client_conn.recv(SIZE).decode(FORMAT))

        # server will save in client_list which port is being connected to who
        # Eg: user thanh is connected with ip 127.0.0.1, port 13456 and client_server_port 4402
        # then client_list[13456] and client_list[4402] stores (thanh, 127.0.0.1, 4402)
        client_list[client_port] = (username, client_ip, client_server_port)
        client_list[client_server_port] = (username, client_ip, client_server_port)

        # finally server will notify in terminal
        print(f"User {username}, IP: {client_ip}, Port: {client_port} connected.")

        # and create a new thread for the client (publish, fetch)
        client_thread = threading.Thread(target=handle_client_connection, args=(client_conn, client_addr))
        client_thread.start()


if __name__ == "__main__":
    main()
