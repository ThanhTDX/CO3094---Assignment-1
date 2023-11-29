import socket
import time
import threading

IP = "127.0.0.1"
PORT = 4456
SIZE = 1024
FORMAT = "utf-8"

client_list = {}    # store dict of id with format {port} : (username, ip, client_server_port)
file_list = {}      # Store list of client's id that have corresponding file (file - [id])
blue_lock = threading.Lock()

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

def remove_client(client_id):
    del client_list[client_id]
    for key, value in file_list.items():
        if client_id in value:
            value.remove(client_id)

def ping_client(client_id):
    message = 'ping' + " " + str(client_id)
    send_message(client_id, message)
    conn = client_list[client_id]

    time.sleep(0.1) # wait time for client to respond
    message_length = conn.recv(SIZE).decode(FORMAT) 
    if message_length:
        message_length = int(message_length)
        message = conn.recv(message_length).decode(FORMAT)
        print(message)
        return True
    else:
        remove_client(client_id)
        return False


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
        

def check_valid_sender(client_id, fname):
    sender_list = file_list[fname]
    if (client_id in sender_list) and ping_client(client_id):
        return True
    else:
        return False




def handle_fetch_file(receiver_id, fname):
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
    conn = client_list[receiver_id]
    valid_sender = send_avail_sender_list(receiver_id, fname)
    if not valid_sender:
        send_message(receiver_id, "invalid fetchfile")
    else:
        while True:
            # Get message from fetching client
            message_length = conn.recv(SIZE).decode(FORMAT) 
            if message_length:
                message_length = int(message_length)
                sender_id = conn.recv(message_length).decode(FORMAT)
                if check_valid_sender(sender_id, fname):
                    send_message(receiver_id, "valid sender_id")
                    break


        # Notify receiver
        re_message = str(sender_id)
        se_message = str(receiver_id) + " " + fname
        send_message(receiver_id, se_message)
        send_message(sender_id, re_message)


# Function for server when client publish file
def handle_publish_file(client_conn, file_name):
    # file_list saves all usernames and their client_server_port
    # eg: file_list["a.txt"] saves [(thanh, 4402), (an, 3054), etc.]

    # get username and its client_server_port from client_conn
    username = client_list[client_conn.getpeername()[1]][0]
    client_server_port = client_list[client_conn.getpeername()[1]][2]

    file_list[file_name] = file_list.get(file_name, []) + [(username, client_server_port)]

    print(f"Client {username} upload file {file_name}")

# Function for server to discover and ping clients
def handle_commands():
    while True:
        # func : action
        # hostname : username
        command = input()
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
                files =  [k for k, v in file_list.items() if v[0] == hostname]
                print(f"Files of current hostname {hostname}")
                print(files)
            except Exception as e:
                print(f"Error discovering user: {e} ")
        
        elif func == 'ping':
            try:
                ping_client(hostname)
            except Exception as e:
                print(f"Error pinging user: {e} ")

        elif func == 'quit':
            break


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
    except Exception as e:
        client_conn.close()
                  
    

def main():
    # Text
    print("[STARTING] Server is starting.\n")

    # Server creates a socket with static IP and PORT for connection 
    # IP = 127.0.0.1, PORT = 4456
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((IP, PORT))

    # Limits listening clients to 20
    server_socket.listen(20)

    # Text
    print("[LISTENING] Server is waiting for clients.")

    # A thread is created for server's self command (ping, discover)
    command_thread = threading.Thread(target=handle_commands)
    command_thread.start()
    
    while True:
        client_conn, client_addr = server_socket.accept()

        # send back client's id (including ip and current port)
        client_conn.send(str(client_addr).encode(FORMAT))

        client_ip = client_conn.getpeername()[0]
        client_port = client_conn.getpeername()[1]

        # Client send their name and 2nd server's port (i hate pier-to-pier)
        username = client_conn.recv(SIZE).decode(FORMAT)
        client_server_port = client_conn.recv(SIZE).decode(FORMAT)

        # server will save in client_list which port is being connected to who
        # Eg: user thanh is connected with ip 127.0.0.1, port 13456 and client_server_port 4402
        # then client_list[13456] and client_list[4402] stores (thanh, 127.0.0.1, 4402)
        client_list[client_port] = (username, client_port, client_server_port)
        client_list[client_server_port] = (username, client_port, client_server_port)

        # finally server will notify in terminal
        print(f"User {username}, IP: {client_ip}, Port: {client_port} connected.")

        # and create a new thread for the client (publish, fetch)
        client_thread = threading.Thread(target=handle_client_connection, args=(client_conn, client_addr))
        client_thread.start()


if __name__ == "__main__":
    main()
