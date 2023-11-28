import socket

if __name__ == "__main__":
    host = socket.gethostname()
    port = 22236
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((host, port))
    client_ip = client_socket.recv(1024).decode('utf-8')
    client_port = client_socket.recv(1024).decode('utf-8')
    print(client_ip, client_port)
    client_socket.close()