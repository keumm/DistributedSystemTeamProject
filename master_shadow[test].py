from flask import Flask
import os
import random
import logging
import argparse
import json
import socket
import select
import time
import threading
# import otherfunctions.server5000 as server5000
# import otherfunctions.PortForwarding as PortForwarding

# Need to put When server is ON or not
PORT = 5000


# [Issue] When turning up the Shadow master server, need to turns up the other chunk servers which are in the heart beat lists.
# Automatically


def update_hearbeat(data):

    current_time = time.time()
    # print('Current time: {0}'.format(current_time))

    f = open("heartbeat.txt", "r")
    aList = f.read()
    aList = aList.replace('', '').split(" ")
    a_dict = {}
    for i in aList:
        if i:
            a_dict[i.split(":")[0]] = i.split(":")[1]
    # data = 'server5'

    # a_set = set()
    a_dict[data] = str(time.time())
    # if data not in a_dict.keys():
    #     a_dict[data] = str(time.time())
    # else:
    #      a_dict[data] = str(time.time())

    write_list = []
    print('------------------')
    # print(write_list)
    for k, v in a_dict.items():
        # If the server didn't get the signal from the chunk servers, POWER OFF! means, drop the server in the list.
        if (current_time - float(v) > 20):
            print('SERVER DOWN')
        else:
            write_list.append(k+':'+v)

    print(' '.join(write_list))  # make a string
    print(write_list)
    with open("heartbeat.txt", "w") as output:
        output.write(' '.join(write_list))


# Reference : Tcp Port Forwarding (Reverse Proxy)
# Author : WangYihang <wangyihanger@gmail.com>
# Edited : Sub
'''
 +-----------------------------+         +---------------------------------------------+         +--------------------------------+
 |     My Laptop (Alice)       |         |            Intermediary Server (Bob)        |         |    Internal Server (Carol)     |
 +-----------------------------+         +----------------------+----------------------+         +--------------------------------+
 | $ ssh -p 1022 carol@1.2.3.4 |<------->|    IF 1: 1.2.3.4     |  IF 2: 192.168.1.1   |<------->|       IF 1: 192.168.1.2        |
 | carol@1.2.3.4's password:   |         +----------------------+----------------------+         +--------------------------------+
 | carol@hostname:~$ whoami    |         | $ python pf.py --listen-host 1.2.3.4 \      |         | 192.168.1.2:22(OpenSSH Server) |
 | carol                       |         |                --listen-port 1022 \         |         +--------------------------------+
 +-----------------------------+         |                --connect-host 192.168.1.2 \ |
                                         |                --connect-port 22            |
                                         +---------------------------------------------+
'''

# With the loggin we could do someething useful. I guess.
format = '%(asctime)s - %(filename)s:%(lineno)d - %(levelname)s: %(message)s'
logging.basicConfig(level=logging.INFO, format=format)


def handle(buffer, direction, src_address, src_port, dst_address, dst_port):
    '''
    intercept the data flows between local port and the target port
    '''
    if direction:
        logging.debug(
            f"{src_address, src_port} -> {dst_address, dst_port} {len(buffer)} bytes")
    else:
        logging.debug(
            f"{src_address, src_port} <- {dst_address, dst_port} {len(buffer)} bytes")
    return buffer


def transfer(src, dst, direction):
    src_address, src_port = src.getsockname()
    dst_address, dst_port = dst.getsockname()
    while True:
        try:
            buffer = src.recv(4096)
            if len(buffer) > 0:
                dst.send(handle(buffer, direction, src_address,
                         src_port, dst_address, dst_port))
        except Exception as e:
            logging.error(repr(e))
            break
    logging.warning(f"Closing connect {src_address, src_port}! ")
    src.close()
    logging.warning(f"Closing connect {dst_address, dst_port}! ")
    dst.close()


# Input will be several ports, depend on the server status.
# If the server is down, switch the servers.

# Input will be remote port.
# Need to use multithreads.


# Want to run this Port Forwarding server do loop.
# Keeping do port forwarding??
# How to switch the port forward?
# [ISSUE] Need to change the port forwarding .
def server():
    port = ExtractHearbeatIntoList()
    local_host = '127.0.0.1'
    local_port = PORT
    remote_host = '127.0.0.1'
    remote_port = port

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((local_host, local_port))

    server_socket.listen(0x40)

    print('I am listening on port')
    # ExecutingPSandCS.main()

    # I can try something with the log.

    logging.info(f"Server started {local_host, local_port}")
    logging.info(
        f"Connect to {local_host, local_port} to get the content of {remote_host, remote_port}")

    while True:
        remote_port = ExtractHearbeatIntoList()
        src_socket, src_address = server_socket.accept()

        logging.info(
            f"[Establishing] {src_address} -> {local_host, local_port} -> ? -> {remote_host, remote_port}")
        print('when connected')
        try:
            dst_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            dst_socket.connect((remote_host, remote_port))
            logging.info(
                f"[OK] {src_address} -> {local_host, local_port} -> {dst_socket.getsockname()} -> {remote_host, remote_port}")
            # E = threading.Thread(target=ExecutingPSandCS.main)
            s = threading.Thread(target=transfer, args=(
                dst_socket, src_socket, False))
            r = threading.Thread(target=transfer, args=(
                src_socket, dst_socket, True))

            s.start()
            # print('s -------------------start')
            r.start()
            # print('r ---------------------start')
            # time.sleep(2)
            print('----------------------------------------')

        except Exception as e:
            logging.error(repr(e))


def ExtractHearbeatIntoList():
    f = open("heartbeat.txt", "r")
    aList = f.read()
    aList = aList.replace('', '').split(" ")
    a_dict = {}
    for i in aList:
        if i:
            a_dict[i.split(":")[0]] = i.split(":")[1]

    new_list = []
    for key in a_dict.keys():
        # print(key)
        # new_list.append(key+':'+a_dict[key])
        new_list.append(key)

    i = random.randint(0, len(new_list)-1)

    result = int(new_list[i])  # String to Integer
    return result


def ExtractHeartbeatIntoFullList():

    f = open("heartbeat.txt", "r")
    aList = f.read()
    aList = aList.replace('', '').split(" ")
    a_dict = {}
    for i in aList:
        if i:
            a_dict[i.split(":")[0]] = i.split(":")[1]

    new_list = []
    for key in a_dict.keys():
        # print(key)
        # new_list.append(key+':'+a_dict[key])
        new_list.append(key)

    print(new_list)

    new_int_list = []

    for i in range(len(new_list)):
        new_int_list.append(int(new_list[i]))

    result = new_int_list
    return result


# Feed the port number into the portforwarding.
# Server will be opened by chunk server


# [ISSUE] This PortForwarding system need a rule when do portforwarding.

def Isserverokay():
    print('Ready for listening')
    # port = random.randint(5001, 5005)
    port = ExtractHearbeatIntoList()
    # Need to open server(port) first and top of that opening os.system() & runremoteserver(port)

    t1 = threading.Thread(target=server, args=(port,))
    # t2 = threading.Thread(target=originserver)
    # t3 = threading.Thread(target=runremoteserver1, args=(port,))

    t1.start()
    time.sleep(2)
    # t2.start()
    # time.sleep(1)
    # t3.start()

    t1.join()
    # t2.join()
    # t3.join()

    # & os.system('&') & ExecutingPSandCS.main(port)


globaluserlist = 'globaluserlist.json'


def InternalSocketPart_ServerSide():

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    # Set the socket to non-blocking mode
    server_socket.setblocking(False)

    server_address = ('localhost', 12345)
    server_socket.bind(server_address)
    server_socket.listen(5)   # Maximum number of connections

    # List of sockets to be monitored by select
    sockets_to_monitor = [server_socket]

    print("Server is ready to accept connections...")

    # [ISSUE] When client disconnects in not a regular way, server got an error and turn off automatically.
    while True:
        # Use select to get the list of sockets ready for reading
        ready_to_read, _, _ = select.select(sockets_to_monitor, [], [])

        for sock in ready_to_read:
            if sock == server_socket:
                # A new client connection is ready to be accepted
                client_socket, client_address = server_socket.accept()
                print(f"Connected to ChunkServer {client_address}")
                sockets_to_monitor.append(client_socket)
            else:
                # An existing client sent data or closed the connection
                # Update by append?
                # How to update the global user list?
                data = sock.recv(1024)
                if data:
                    # print(f"Received data from client {client_address}: {data}")
                    # This format will be json format

                    # [ISSUE] How to save the data into globaluserlist.json ?
                    if data.startswith(b'{'):
                        data = data.decode('utf-8')
                        with open(globaluserlist, 'w') as f:
                            json.dump(data, f)
                        data = data.encode('utf-8')
                        sock.sendall(data)
                    # If the data is start with nothing. (which means heartbeat data)
                    elif data.startswith(b''):
                        # Send the data to the client
                        update_hearbeat(data.decode())
                        sock.sendall(data)
                else:
                    print(
                        f"Connection closed by ChunkServer {client_address}")
                    sock.close()
                    sockets_to_monitor.remove(sock)


#################################################################################################################################
# This Web page (port :5000 ) for portforwarding

app = Flask(__name__)


@app.route('/')
# ‘/’ URL is bound with hello_world() function.
def hello_world():
    return 'Welcome, This is the port number 5000. This is Master server, If you see this page, something is wrong.....'


def OpenWebpage():
    app.run(host='127.0.0.1', port=PORT)


def SendDataToShadowMaster():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    # Set the socket to non-blocking mode
    server_socket.setblocking(False)

    server_address = ('localhost', 54321)
    server_socket.bind(server_address)
    server_socket.listen(1)   # Maximum number of connections

    # List of sockets to be monitored by select
    sockets_to_monitor = [server_socket]

    print("Server is ready to accept connections...")

    # [ISSUE] When client disconnects in not a regular way, server got an error and turn off automatically.
    while True:
        # Use select to get the list of sockets ready for reading
        ready_to_read, _, _ = select.select(sockets_to_monitor, [], [])

        for sock in ready_to_read:
            if sock == server_socket:
                # A new client connection is ready to be accepted
                client_socket, client_address = server_socket.accept()
                print(f"Connected by Shadowserver {client_address}")
                sockets_to_monitor.append(client_socket)
            else:
                # An existing client sent data or closed the connection
                # Update by append?
                # How to update the global user list?
                data = sock.recv(1024)
                if data:
                    # print(f"Received data from client {client_address}: {data}")
                    # This format will be json format

                    # [ISSUE] How to save the data into globaluserlist.json ?
                    if data.startswith(b'{'):
                        # data = data.decode('utf-8')
                        # with open(globaluserlist, 'w') as f:
                        #     json.dump(data, f)
                        # data = data.encode('utf-8')
                        # sock.sendall(data)
                        # If the data is start with nothing. (which means heartbeat data)
                        print('{ data')
                    elif data.startswith(b''):
                        # # Send the data to the client
                        # update_hearbeat(data.decode())
                        # sock.sendall(data)
                        print(' data')
                else:
                    print(
                        f"Connection closed by Shadowserver {client_address}")
                    sock.close()
                    sockets_to_monitor.remove(sock)


# Shadow master will get the data and saves it there database.
def ShadowMasterServer_ClientSide():
    print('Hi, I am a shadow Master')


# Normal Master Mode
#########################################################################################
def WhenServerIsOn():
    t1 = threading.Thread(target=InternalSocketPart_ServerSide)
    t2 = threading.Thread(target=OpenWebpage)
    t3 = threading.Thread(target=server)
    t4 = threading.Thread(target=SendDataToShadowMaster)

    t1.start()
    t2.start()
    t3.start()
    t4.start()
###########################################################################################
# Here is the OFF , Shadow master functions


# This is Client Side Mode
def ConnectingAndGetDataFromMaster():
    HOST = "127.0.0.1"  # The server's hostname or IP address
    PORT = 54321  # The port used by the server
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        while True:

            s.send(b'Hi could you send me data?')
            # print('Connected!')
            # time.sleep(5)
            # print('Current time is :', time.time())
            # time.sleep(5)
            # print("Socket Connection is closed")
            data = s.recv(1024)
            if data.startswith(b'{'):
                # data = s.recv(1024)
                print('json data')
                print(data)
                # data = data.decode('utf-8')
                # with open(globaluserlist, 'w') as f:
                #     json.dump(data, f)
                # data = data.encode('utf-8')
                # sock.sendall(data)
                # If the data is start with nothing. (which means heartbeat data)
            elif data.startswith(b''):
                # Send the data to the client
                # update_hearbeat(data.decode())
                # sock.sendall(data)
                # data = s.recv(1024)
                print('text data')
                print(data)

    # This Functions are should run when connection is closed accidently

    ChangeTheMode()   # Switch Shadow to master
    RunChunkServerScript()


def ChangeTheMode():

    os.system('python master_shadow[test].py --verbose &')


def RunChunkServerScript():
    ports = ExtractHeartbeatIntoFullList()
    for i in range(len(ports)):
        print(ports[i])
        os.system('python chunk_server{}.py &'.format(ports[i]))
        print('chunkserver{} opened'.format(ports[i]))

    #  When this message get
    # 'ConnectionResetError: [WinError 10054] An existing connection was forcibly closed by the remote host'


# Shadow Master Mode
###############################################################################
def WhenServerIsOff():

    t1 = threading.Thread(target=ConnectingAndGetDataFromMaster)
    t1.start()
################################################################################


def main():

    # This is for distinguish the main running server and backup server.

    parser = argparse.ArgumentParser()
    parser.add_argument("--verbose", action="store_true",
                        help="increase output verbosity")
    args = parser.parse_args()
    if args.verbose:
        print("Starting the Master")
        WhenServerIsOn()

    else:
        print("Starting the shadow Master")
        WhenServerIsOff()


if __name__ == "__main__":
    main()
