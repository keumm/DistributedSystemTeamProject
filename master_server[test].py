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
ListeningChunkServersPort = 12345
ListeningShadowMasterSserverPort = 54321


# Updating heartbeat on txt file
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

            r.start()

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


# Feed the port number into the portforwarding.
# Server will be opened by chunk server
# [ISSUE - Solved] This PortForwarding system need a rule when do portforwarding.

def Isserverokay():
    print('Ready for listening')
    port = ExtractHearbeatIntoList()
    # Need to open server(port) first and top of that opening os.system() & runremoteserver(port)

    t1 = threading.Thread(target=server, args=(port,))
    t1.start()

    t1.join()
    # t2.join()
    # t3.join()

    # & os.system('&') & ExecutingPSandCS.main(port)

#######################################################################################################################################


globaluserlist = 'GlobalUserList.json'


def InternalSocketPart_ServerSide():

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    # Set the socket to non-blocking mode
    server_socket.setblocking(False)

    server_address = ('localhost', ListeningChunkServersPort)
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
                print(f"Connected from ChunkServer {client_address}")
                sockets_to_monitor.append(client_socket)
            else:
                # An existing client sent data or closed the connection
                # Update by append?
                # How to update the global user list?
                data = sock.recv(1024)
                if data:
                    print(
                        f"Received data from client {client_address}: {data}")
                    # This format will be json format

                    # [ISSUE - Solved] How to save the data into globaluserlist.json ?
                    # JSON data format starts with {, if got {this sending to json
                    if data.startswith(b'{'):
                        data = data.decode('utf-8')
                        # time.sleep(5)
                        try:

                            with open(globaluserlist, 'r') as file_object:
                                databasejson = json.load(file_object)

                                for i, databasejson[i] in databasejson.items():
                                    if (databasejson[i]["name"] == json.loads(data)["name"]):
                                        if (databasejson[i]["timestamp"] == json.loads(data)["timestamp"]):
                                            print(
                                                'Drop the packet, because it is already logged!')
                                            sock.send(
                                                b'Server: This data alreadt logged I do not need this thank you!')
                                            break
                                        else:
                                            print('Time to logging')

                                            with open(globaluserlist, 'w') as file_object:
                                                Resultpoint = int(
                                                    databasejson[i]["points"]) + json.loads(data)["points"]
                                                CurrentTimeStamp = json.loads(data)[
                                                    "timestamp"]
                                                databasejson[i] = {"name": json.loads(
                                                    data)["name"], "points": Resultpoint, "timestamp": CurrentTimeStamp}
                                                json.dump(
                                                    databasejson, file_object)
                                                sock.send(
                                                    b'Server: Yes, I logged!')
                                                print('Point modified!')
                                                break
                                    else:
                                        # print('NO')
                                        if (int(i) == len(databasejson)-1):
                                            # print(i)
                                            with open(globaluserlist, 'w') as file_object:

                                                databasejson[len(databasejson)] = json.loads(
                                                    data)
                                                json.dump(
                                                    databasejson, file_object)
                                                sock.send(
                                                    b'Server: Yes, I logged!')
                                                print('New User Created')
                                                break

                        except:
                            print('error')

                    # If the data starts with nothing. (which means heartbeat data)
                    elif data.startswith(b''):
                        # Send the data to the client
                        update_hearbeat(data.decode())
                        # Don't need to send back? I think?
                        # sock.sendall(data)
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

    server_address = ('localhost', ListeningShadowMasterSserverPort)  # 54321
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
                jsonfileopen = open('GlobalUserList.json')
                result = json.load(jsonfileopen)
                Globaluserlistdata = str(result)         # Change into string.

                data = sock.recv(1024)
                # Once you got initialization data from the shadow master, start sending the globaruser list and hearbeat regularlly

                if data:
                    # print(data)
                    sock.send(Globaluserlistdata.encode())
                    print('Successfully sent json')
                    # # data = sock.recv(1024)
                    # # print(data)
                    with open('heartbeat.txt') as textfileopen:
                        contents = textfileopen.read()
                        # print(contents)

                    sock.send(contents.encode())
                    print('Successfully sent text')
                    # data = sock.recv(1024)
                    # print(data)
                    time.sleep(20)

                else:
                    print(
                        f"Connection closed by Shadowserver {client_address}")
                    sock.close()
                    sockets_to_monitor.remove(sock)


# Shadow master will get the data and saves it there database.
def ShadowMasterServer_ClientSide():
    print('Hi, I am a shadow Master')

# [Issue] What is the join() for?


def WhenServerIsOn():
    t1 = threading.Thread(target=InternalSocketPart_ServerSide)
    t2 = threading.Thread(target=OpenWebpage)
    t3 = threading.Thread(target=server)
    t4 = threading.Thread(target=SendDataToShadowMaster)

    t1.start()

    t2.start()

    t3.start()

    t4.start()
    t1.join()

    t4.join()


def WhenServerIsOff():
    print('Server is Off')


if __name__ == "__main__":
    # This is for distinguish the main running server and backup server.
    IsServerRunningOnMain = True

    if (IsServerRunningOnMain == True):
        WhenServerIsOn()
    else:
        WhenServerIsOff()
