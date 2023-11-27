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
    for key, value in file_list.items():
        if client_id in value:
            value.remove(client_id)

def ping_client(conn):
    message = f'PING'
    message_length = len(message)
    send_length = str(message_length).encode(FORMAT)
    send_length+= b' '*(SIZE-len(send_length))
    conn.send(send_length)
    conn.send(message)

    time.sleep(0.1) # wait time for client to respond
    message_length = connection.recv(HEADER).decode(FORMAT) # convert bytes format -> string 
    if message_length:
        # Received a message's length (message_length != 0)
        message_length = int(message_length)
        message = connection.recv(message_length).decode(FORMAT)
        print(message)
    else:
        remove_client(client_id)

def get_selection_from_list(fname):
    pass

def check_valid_sender(client_id, fname):
    pass

def notify_client(client_id, fname = None):
        
    message = str(client_id)
    if fname is not None:
        message = message + " " + fname
    message_length = len(message)
    send_length = str(message_length).encode(FORMAT)
    send_length+= b' '*(SIZE-len(send_length))

    conn = client_list[client_id]
    conn.send(send_length)
    conn.send(message)

def handle_fetch_file(client_id, fname):
    '''
    The sender will receive message in the following format from the server:
    <receiver_id> <fname>
    Example:
        ('192.168.1.105', 62563) test.txt

    The receiver will receive message in the following format from the server:
    <sender_id>
    Example:
        ('192.168.1.105', 62563)
    '''
    while True:
        client_id = get_selection_from_list(fname)
        if check_valid_sender(client_id, fname):
            break
    notify_client(receiver_id, fname)
    notify_client(sender_id)
        
def handle_upload_file(client_id, fname):
    file_list[fname] = file_list.get(fname, []) + [(client_id, lname)]
    print("Client {} successfully upload file {}".format(client_id, fname))

def handle_commands():
    while True:
        command = input()
        func, hostname = command.split()
        # Add logic to handle server-side commands
        if func == 'discover':
            files = []
            for fname, client_list in file_list.items():
                for client_id, lname in client_list:
                    if hostname == client_id:
                        files.append(fname)
                        break
            print("List of files of current hostname {}:".format(hostname))
            print(files)
        elif func == 'ping':
            ping_client(hostname)
        else:
            print("Invalid argument.")


def handle_client_connection(conn, addr):
    '''
    The receiving message must be in the following format:
    <function> <fname> where:
    <function> can be: ['publish', 'fetch']
    <fname> can be any filename
    Example: 
        publish test.txt
        fetch test.txt
    '''
    with bluelock:
        client_list[addr] = conn

    while True:
        message_length = connection.recv(HEADER).decode(FORMAT) # convert bytes format -> string 
        if message_length:
            
            # Received a message's length (message_length != 0)
            message_length = int(message_length)
            message = connection.recv(message_length).decode(FORMAT)
            func, fname = message.split()
            if func == 'publish':
                handle_upload_file(find_addr(connection), fname)
            elif func == 'fetch':
                handle_fetch_file(find_addr(connection), fname)    
    

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
