import socket
from threading import Thread


def new_connection(conn, addr):
    client_info = conn.getpeername()
    print(client_info)
    conn.send(str(client_info[0]).encode('utf-8'))
    conn.send(str(client_info[1]).encode('utf-8'))


def server_program(host, port):
    serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serversocket.bind((host, port))

    serversocket.listen(10)
    while True:
        conn, addr = serversocket.accept()
        nconn = Thread(target=new_connection, args=(conn, addr))
        nconn.start()


if __name__ == "__main__":
    host = socket.gethostname()
    port = 22236
    server_program(host, port)