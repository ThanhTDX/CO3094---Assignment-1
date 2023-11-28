# import socket

# def client_host():
#     # client_1 will be host, sending file

#     client_send = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#     client_send.bind(("127.0.0.1", 0))
#     # https://stackoverflow.com/questions/1365265/on-localhost-how-do-i-pick-a-free-port-number

#     current_port = client_send.getsockname()[1]
#     pass

# def client_connect():
#     pass

# def create_connection(client_1_ID, client_2_ID):
    
#     client_receive = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#     client_receive.connect(("127.0.0.1", current_port))

# def client_send_file(file, target_client):
#     pass
    
# def client_receive_file(file, incoming_client):
#     pass