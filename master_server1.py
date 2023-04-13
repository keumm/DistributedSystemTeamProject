from flask import Flask, send_from_directory
import os
import random
import logging
import argparse
import json
import socket
import select
import time
import threading
import sys

# Need to put When server is ON or not


# Resources that the Master server using
PORT = 5000
# Maximum number of connection of chunk servers that can connecting to the master
MAXIMUM = 7
# Maximum number of connection to shadow master
M_MAXIMUM = 1
ListeningChunkServersPort = 12345        # Open the socket for 5 listening
ListeningShadowMasterSserverPort = 54321  # Oepn the socket for 1 listening
heartbeatfile = './heartbeat.txt'
# Updating heartbeat on txt file


# This function is for updating chunk server's heartbeat every 10 seconds
# Writing the new heartbeat into heartbeat text file
def update_hearbeat(data):

    current_time = time.time()
    f = open(heartbeatfile, "r")
    aList = f.read()
    aList = aList.replace('', '').split(" ")
    a_dict = {}
    for i in aList:
        if i:
            a_dict[i.split(":")[0]] = i.split(":")[1]

    a_dict[data] = str(time.time())

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
    with open(heartbeatfile, "w") as output:
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


# This server using ExtractHeartbeatInoList() for do port forwarding
# With the list, the server can do portforwarding according to the server list in the heartbeat.
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
            s = threading.Thread(target=transfer, args=(
                dst_socket, src_socket, False))
            r = threading.Thread(target=transfer, args=(
                src_socket, dst_socket, True))

            s.start()
            r.start()
            print(
                '------------------------------------------------------------------------------')

        except Exception as e:
            logging.error(repr(e))


def ExtractHearbeatIntoList():
    f = open(heartbeatfile, "r")
    aList = f.read()
    aList = aList.replace('', '').split(" ")
    a_dict = {}
    for i in aList:
        if i:
            a_dict[i.split(":")[0]] = i.split(":")[1]

    new_list = []
    for key in a_dict.keys():
        new_list.append(key)

    i = random.randint(0, len(new_list)-1)

    result = int(new_list[i])  # String to Integer
    return result


#######################################################################################################################################


def update_global_user_list(user_name, consume_point, timestamp):
    with open(globaluserlist, 'r') as file_object:
        db = json.load(file_object)

    user_found = False
    for key, user in db.items():
        if user['name'] == user_name:
            user['points'] += int(consume_point)
            user['timestamp'] = timestamp
            user_found = True
            break

    if not user_found:
        db[len(db)] = {'name': user_name, 'points': int(
            consume_point), 'timestamp': timestamp}

    with open(globaluserlist, 'w') as file_object:
        json.dump(db, file_object)


def update_global_user_historylist(user_name, consume_point, timestamp):
    with open(globaluserhistorylist, 'r') as file_object1:
        db = json.load(file_object1)
        db[len(db)] = {
            'name': user_name,
            'points': int(consume_point),
            'timestamp': timestamp
        }

    with open(globaluserhistorylist, 'w') as file_object1:
        json.dump(db, file_object1)

#######################################################################################################################################


globaluserlist = './localuserlist.json'
globaluserhistorylist = './LocaldataHistory.json'


def InternalSocketPart_ServerSide():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    server_address = ('localhost', ListeningChunkServersPort)
    server_socket.bind(server_address)
    server_socket.listen(5)  # Maximum number of connections

    sockets_to_monitor = [server_socket]

    print("Server is ready to accept connections...")

    while True:
        try:
            ready_to_read, _, _ = select.select(sockets_to_monitor, [], [])

            for sock in ready_to_read:
                if sock == server_socket:
                    client_socket, client_address = server_socket.accept()
                    print(f"Connected from ChunkServer {client_address}")
                    sockets_to_monitor.append(client_socket)
                else:
                    data = sock.recv(1024)
                    if data:
                        print(
                            f"Received data from client {client_address}: {data}")

                        # Process the received data
                        try:
                            message = data.decode()
                            if message.isdigit():
                                # Handle integer messages (e.g., port numbers) here
                                pass
                            else:

                                message = data.decode()
                                message = json.loads(message)
                                user_name = message.get('name')
                                consume_point = message.get('points')
                                timestamp = message.get('timestamp')

                                if user_name and consume_point and timestamp:
                                    # Process the user update message
                                    update_global_user_list(
                                        user_name, consume_point, timestamp)
                                    update_global_user_historylist(
                                        user_name, consume_point, timestamp)
                                    # You can add the code for updating the global user list here
                                    pass
                        except json.JSONDecodeError:
                            # It's not a JSON message, assuming it's a heartbeat message
                            pass
                    else:
                        print(
                            f"Connection closed by ChunkServer {client_address}")
                        sock.close()
                        sockets_to_monitor.remove(sock)
        except IOError:
            print('Disconnected')
            break


#################################################################################################################################
# This Web page (port :5000 ) for portforwarding
# app = Flask(__name__)


# @app.route('/')
# # ‘/’ URL is bound with hello_world() function.
# def hello_world():
#     return 'Welcome, This is the port number 5000. This is Master server, If you see this page, something is wrong.....'


# def OpenWebpage():
#     app.run(host='127.0.0.1', port=PORT)


def SendDataToShadowMaster():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    # Set the socket to non-blocking mode
    # server_socket.setblocking(False)

    server_address = ('localhost', ListeningShadowMasterSserverPort)  # 54321
    server_socket.bind(server_address)
    server_socket.listen(M_MAXIMUM)       # Maximum number of connections

    # List of sockets to be monitored by select
    sockets_to_monitor = [server_socket]

    print("Server is ready to accept connections...")

    # [ISSUE] When client disconnects in not a regular way, server got an error and turn off automatically.
    while True:
        # for i in range(0, 10):
        # Use select to get the list of sockets ready for reading
        ready_to_read, _, _ = select.select(sockets_to_monitor, [], [])

        for sock in ready_to_read:
            if sock == server_socket:
                # A new client connection is ready to be accepted
                client_socket, client_address = server_socket.accept()
                print(f"Connected by Shadowserver {client_address}")
                sockets_to_monitor.append(client_socket)
            else:
                jsonfileopen = open(
                    './GlobalUserList.json')
                result = json.load(jsonfileopen)
                Globaluserlistdata = str(result)         # Change into string.

                data = sock.recv(1024)
                # Once you got initialization data from the shadow master, start sending the globaruser list and hearbeat regularlly
                # Sending Globaluserlist file and heartbeat text file to the shadow server
                try:
                    if data:
                        # print(data)
                        sock.send(Globaluserlistdata.encode())
                        print('Successfully sent json to ShadowMaster')
                        print(Globaluserlistdata)
                        time.sleep(1)

                        with open(heartbeatfile) as textfileopen:
                            contents = textfileopen.read()

                        sock.send(contents.encode())
                        print('Successfully sent text to ShadowMaster')
                        print(contents)
                        # do this every 10 seconds
                        time.sleep(10)

                    else:
                        print(
                            f"Connection closed by Shadowserver {client_address}")
                        sock.close()
                        sockets_to_monitor.remove(sock)
                except IOError:  # IOError,
                    print('Disconnected')
                    return None


def WhenServerIsOn():
    t1 = threading.Thread(target=InternalSocketPart_ServerSide)

    t3 = threading.Thread(target=server)
    t4 = threading.Thread(target=SendDataToShadowMaster)

    t1.start()

    t3.start()

    t4.start()
    # t1.join()

    # t4.join()


# This list is using for get back from the failure of the Master
def ExtractHeartbeatIntoFullList():

    f = open(heartbeatfile, "r")
    aList = f.read()
    aList = aList.replace('', '').split(" ")
    a_dict = {}
    for i in aList:
        if i:
            a_dict[i.split(":")[0]] = i.split(":")[1]

    new_list = []
    for key in a_dict.keys():
        new_list.append(key)

    print(new_list)

    new_int_list = []

    for i in range(len(new_list)):
        new_int_list.append(int(new_list[i]))

    result = new_int_list
    return result


# This is Client Side Mode - ShadowMaster does this
def ConnectingAndGetDataFromMaster():
    HOST = "127.0.0.1"  # The server's hostname or IP address
    PORT = 54321  # The port used by the server

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))

        while (1):

            try:
                # Keep Asking to the Master server every 20 seconds
                s.send(b'Hi could you send me data?')

                data = s.recv(2048)
                if data.startswith(b'{'):
                    # print('json data')
                    data = data.decode('utf-8')

                    try:

                        with open(globaluserlist, 'r') as file_object:
                            databasejson = json.load(file_object)

                            for i, databasejson[i] in databasejson.items():
                                if (databasejson[i]["name"] == json.loads(data)["name"]):
                                    if (databasejson[i]["timestamp"] == json.loads(data)["timestamp"]):
                                        print(
                                            'Drop the packet, because it is already logged!')
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

                                            break
                                else:

                                    if (int(i) == len(databasejson)-1):
                                        with open(globaluserlist, 'w') as file_object:
                                            databasejson[len(databasejson)] = json.loads(
                                                data)
                                            json.dump(
                                                databasejson, file_object)

                                            break
                    except:
                        print('error')

                elif data.startswith(b''):

                    print('text data')
                    update_hearbeat(data.decode())

            except IOError:  # IOError,
                print('Disconnected')
                print('ChangeThe mode!')
                ChangeTheMode()   # Switch Shadow to master

                return None


def ChangeTheMode():

    # Running shadow for opposite -> running as a main
    os.system('python master_server1.py --verbose & ')
    # time.sleep(2)

    print('RUNCHUNKSERVER?========================================')
    ports = ExtractHeartbeatIntoFullList()
    for i in range(len(ports)):
        print(ports[i])
        os.system(
            "gnome-terminal -e 'bash -c \"npx kill-port {}\"'".format(ports[i]))
        time.sleep(3)
        os.system(
            "gnome-terminal -e 'bash -c \"python chunk_server{}.py\"'".format(ports[i]))
        print('chunkserver{} opened'.format(ports[i]))


# # This is Client Side Mode
# def ConnectingAndGetDataFromMaster():
#     HOST = "127.0.0.1"  # The server's hostname or IP address
#     PORT = 54321  # The port used by the server

#     with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
#         s.connect((HOST, PORT))

#         while (1):

#             try:
#                 # Keep Asking to the Master server every 20 seconds
#                 s.send(b'Hi could you send me data?')

#                 data = s.recv(1024)
#                 if data.startswith(b'{'):
#                     # data = s.recv(1024)
#                     print('json data')
#                     print(data)

#                 elif data.startswith(b''):

#                     print('text data')
#                     print(data)

#             except IOError:  # IOError,
#                 print('Disconnected')
#                 print('ChangeThe mode!')
#                 ChangeTheMode()   # Switch Shadow to master

#                 return None

#     # This Functions are should run when connection is closed accidently

#     # ChangeTheMode()   # Switch Shadow to master
#     # RunChunkServerScript()


# def ChangeTheMode():

#     # Running shadow for opposite -> running as a main
#     os.system('python master_shadow[test].py --verbose & ')
#     time.sleep(2)
#     os.system("gnome-terminal -e 'bash -c \"python chunk_server5001.py\"'")
#     print('RUNNING CHUNKSERVER!!')


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
        WhenServerIsOff()

    else:
        print("Starting the shadow Master")
        # WhenServerIsOff()
        WhenServerIsOn()


if __name__ == "__main__":
    # This is for distinguish the main running server and backup server.
    # IsServerRunningOnMain = True

    # if (IsServerRunningOnMain == True):
    #     WhenServerIsOn()
    # else:
    #     WhenServerIsOff()
    main()
