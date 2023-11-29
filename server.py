import socket
import time
import threading

IP = "127.0.0.1"
PORT = 4456
SIZE = 1024
FORMAT = "utf"

client_list = {}    # Store client id with respective address (id - connection)
file_list = {}      # Store list of client's id that have corresponding file (file - [id])
blue_lock = threading.Lock()

def remove_client(client_id):
    del client_list[client_id]
    for _, value in file_list.items():
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
    sender_list = file_list.get(fname, [])
    send_message(receiver_id, str(sender_list))
    return (len(sender_list) > 0)
        

def check_valid_sender(client_id, fname):
    sender_list = file_list[fname]
    if (client_id in sender_list) and ping_client(client_id):
        return True
    else:
        return False

def send_message(client_id, message = ""):
    '''
    Send message to specific client
    '''
    message_length = len(message)
    send_length = str(message_length).encode(FORMAT)
    send_length+= b' '*(SIZE-len(send_length))

    conn = client_list[client_id]
    conn.send(send_length)
    conn.send(message)


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


def handle_upload_file(client_id, fname):
    file_list[fname] = file_list.get(fname, []) + [client_id]
    print("Client {} successfully upload file {}".format(client_id, fname))


def handle_commands():
    while True:
        command = input()
        func = command.split()[0]

        if func == 'discover':
            hostname = command.split()[1]
            files = []
            for fname, client_list in file_list.items():
                for client_id in client_list:
                    if hostname == client_id:
                        files.append(fname)
                        break
            print("Files of current hostname {}:".format(hostname))
            print(files)

        elif func == 'ping':
            hostname = command.split()[1]
            ping_client(hostname)

        else:
            print("Invalid argument.")


def handle_client_connection(conn, addr):
    '''
    The receiving cmd must be in the following format:
    <function> <fname> where:
    <function> can be: ['publish', 'fetch']
    <fname> can be any filename
    Example: 
        publish test.txt
        fetch test.txt
    '''
    with blue_lock:
        client_list[addr] = conn

    while True:
        message_length = conn.recv(SIZE).decode(FORMAT) # convert bytes format -> string 
        if message_length:
            
            # Received a message's length (message_length != 0)
            message_length = int(message_length)
            message = conn.recv(message_length).decode(FORMAT)
            func, fname = message.split()
            if func == 'publish':
                handle_upload_file(addr, fname)
            elif func == 'fetch':
                handle_fetch_file(addr, fname)    
    

def main():
    '''
    Please note that the sending message always begin with an
    empty byte string as notification
    Example can be seen in ping_client()'s implementation

    '''
    print("[STARTING] Server is starting.\n")

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((IP, PORT))
    server.listen()
    print("[LISTENING] Server is waiting for clients.")

    command_thread = threading.Thread(target=handle_commands)
    command_thread.start()
    
    while True:
        conn, addr = server.accept()

        # Create a new thread for each client
        client_thread = threading.Thread(target=handle_client_connection, args=(conn, addr))
        client_thread.start()


if __name__ == "__main__":
    main()
