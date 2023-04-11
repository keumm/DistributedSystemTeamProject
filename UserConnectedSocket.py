# [ISSUE] THIS part is send a request to the master server
# How to send a request to the master server?
# By HTTP [POST] or through socket?
# This requests starts from the chunkserver port 5001's search user button


import socket
import json

HOST, PORT = "localhost", 12345
message = {'name': 'mark', 'points': 5}


def sendingdata():
    # Why need a dumps?
    data = json.dumps(message)

    # Create a socket (SOCK_STREAM means a TCP socket)
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        # Connect to server and send data
        sock.connect((HOST, PORT))
        sock.sendall(bytes(data, encoding="utf-8"))

        # Receive data from the server and shut down
        received = sock.recv(1024)
        received = received.decode("utf-8")

    finally:
        sock.close()

    print("Sent:     {}".format(data))
    print("Received: {}".format(received))
