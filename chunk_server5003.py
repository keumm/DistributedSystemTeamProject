import threading
import time
import socket
import json
import os
from flask import Flask, jsonify, request, send_from_directory
from datetime import datetime
import UserConnectedSocket
# import OpenWebPage
global s
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


# Sending regular heartbeat
# format looks like this:
# With those values, Master server will know which chunk servers break down.


#########################################################################################################################
# This part is for an internal Socket


# [Issue] Need to connect with front end page and this sendingMessage function.
# Using Flask?

# [Issue] Heart beat and Master server reply socket must be defferent???
def sending_heartbeat(socket):
    print('hi')
    while (1):

        try:
            socket.sendall(b"5003")
            time.sleep(10)
        except IOError:  # IOError,
            print('Disconnected')
            return None
    # data = socket.recv(1024)

    # print(f"Heartbeat: {data!r}")


# When Data fail to logged or sending to Master, It saves into buffer and send it again until success.
Buffer = []

# receive data from the server and decoding to get the string.
# If something is in the Buffer
# Sending data in the buffer,

# If send a data from the Buffer, but if there is no answer, save in the Buffer again.


def SendBufferData(socket):

    # If Buffer is an empty... let's move on to the next level
    if not Buffer:
        print('Nothing is in the Buffer.....')

    # If data is in the Buffer.
    # CHeck the buffer one by one.
    else:
        # If don't receive a message within a 3 seconds, store the data into buffer.
        t_end = time.time() + 3
        print('Somthing in the BUffer', Buffer)
        # Checking the inside of the Buffer, What is in the buffer from the first to last
        for i in range(len(Buffer)):
            data = Buffer[i]
            print('whatisthis', data)
            # Sending the data what is in the buffer.
            socket.sendall(data.encode())
            # Recieve the ok sign from the Master
            result = socket.recv(1024).decode()

            # If you got the message within a time (3 seconds) with the message from the server,
            # Remove the data which is in the buffer.
            if ((time.time() < t_end) & (result != '')):

                print(result)
                Buffer.pop(0)
                print(
                    'Got the Data and Logged Successfully in the server. Buffer:', Buffer)

            else:
                # Else, just keep the data in the buffer....
                print('Failed to sent, Data is stayed in the Buffer. Buffer:', Buffer)


# Sending, name and point
# def sendMessage(name, number = default false.)
# -> when name is only come, just do name .....

def SendMessage(socket, user_name, consume_point):
    # The rest of the SendMessage() function code

    t_end = time.time() + 3
    # msg = 'MARK'
    # msg = '{"name": "Jeremiah", "points": 3}'
    # msg = '{"name": "Oscar", "points": 12, "timestamp": 1780909832.773651 }'

    current_time = time.time()
    # Sending a message with the cuerrent time as well
    msg = f'{{"name": "{user_name}", "points": {consume_point}, "timestamp": {current_time:.6f} }}'
    # time.sleep(2)
    socket.sendall(msg.encode())
    result = socket.recv(1024).decode()

    # time.sleep(2)
    if ((time.time() < t_end) & (result != '')):

        print(result)
        print('Got the Data and Logged Successfully in the server')

    else:
        Buffer.insert(0, msg)
        print('Data is failed to stored in the log of Master server')
        print('Data is left in the Buffer', Buffer)


class MultiThreadingClient:
    def __init__(self, socket):
        self.socket = socket

    def send_user_list_update(self, user_name, consume_point, timestamp):
        user_data = json.dumps(
            {"name": user_name, "points": consume_point, 'timestamp': timestamp})
        try:
            self.socket.sendall(user_data.encode())
        except BrokenPipeError:
            print("Broken pipe error encountered. Attempting to reconnect...")
            self.reconnect()
            self.socket.sendall(user_data.encode())

    def reconnect(self):
        global s
        s.close()
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        HOST = "127.0.0.1"  # The server's hostname or IP address
        PORT = 12345  # The port used by the server
        s.connect((HOST, PORT))


# Sending an updated userlist to master.


# Message comes from FrontEnd and recording on the localuserlist.json
# Then send a message to the master server.

def localuserlistupdate(s, user_name, consume_point, timestamp):
    # Connection to socket
    client = MultiThreadingClient(s)
    client.send_user_list_update(user_name, consume_point, timestamp)


def connections():
    global s
    HOST = "127.0.0.1"  # The server's hostname or IP address
    PORT = 12345  # The port used by the server

    s.connect((HOST, PORT))

    # Connection to socket
    t1 = threading.Thread(target=sending_heartbeat, args=(s,))
    t1.start()

    # wait until thread 1 is completely executed
    t1.join()

    # both threads completely executed
    print("Done! All of the Thread processes are completed.")


########################################################################################################################
# This part is for running web page
app = Flask(__name__)


# Every transaction will happends on this page.
# [ISSUE] HOW TO CONNECT THIS BACKEND API TO FRONTEND?


userlistjson = '/Users/klsg/Desktop/distributed/Backend/localuserlist.json'
userhistoryjson = '/Users/klsg/Desktop/distributed/Backend/LocaldataHistory.json'


app = Flask(
    __name__, static_folder='/Users/klsg/Desktop/distributed/Backend/static/distributed-front')

# Serve Angular app as static files


@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_angular_app(path):
    if path != "" and os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    else:
        return send_from_directory(app.static_folder, 'index.html')


@app.route('/api/update_userlist', methods=['POST'])
def update_userlist():
    data = request.json
    user_name = data['userName']
    consume_point = data['consumePoint']
    timestamp = data['timestamp']

    localuserlistupdate(s, user_name, consume_point, timestamp)
    # Update the JSON file with the new data
    with open(userlistjson, 'r') as file_object:
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

    with open(userlistjson, 'w') as file_object:
        json.dump(db, file_object)

        # Update the JSON file with the new data

    with open(userhistoryjson, 'r') as file_object1:
        db = json.load(file_object1)
        db[len(db)] = {
            'name': user_name,
            'points': int(consume_point),
            'timestamp': timestamp
        }

    with open(userhistoryjson, 'w') as file_object1:
        json.dump(db, file_object1)

        # Update the history JSON file with the new data

    response = {'status': 'success', 'message': 'User list updated'}
    return jsonify(response), 200


globaluserlist = '/Users/klsg/Desktop/distributed/Backend/GlobalUserList.json'


@app.route('/users/<username>', methods=['GET'])
def get_user_consume_point(username):
    with open(globaluserlist, 'r') as file_object:
        db = json.load(file_object)

    user_found = False
    for key, user in db.items():
        if user['name'] == username:
            user_found = True
            return jsonify({'name': user['name'], 'consume_point': user['points']})

    if not user_found:
        return jsonify({'error': 'User not found'}), 404


@app.route('/api/transaction_history', methods=['GET'])
def get_transaction_history():
    username = request.args.get('username')

    if not username:
        return jsonify({'error': 'Username is required'}), 400

    try:
        with open(userhistoryjson, 'r') as file_object:
            all_transactions = json.load(file_object)
    except FileNotFoundError:
        return jsonify({'error': 'Transaction history not found'}), 404

    user_transactions = [transaction for transaction in all_transactions.values(
    ) if transaction['name'] == username]

    return jsonify(user_transactions), 200


def openWebPage():
    app.run(host='127.0.0.1', port=5003)


#############################################################################################################
# Running chunkserver

if __name__ == '__main__':
    # [ISSUE] IS IT OKAY TO RUN THOSE TASKES IN THREADING?

    # 1) InternalSocket : Sending heartbeats(.text) and user list update(.json)
    #                     user list format : {"0":{"name":"per","points":15, timestamp: 000 },"1":{"name":"john","points":0, timestampe: 000}}
    t1 = threading.Thread(target=connections)

    # 2) User connected Socket : Ask to Master server to get a global user list(.json)
    # This .json saves into Redis. Becuase, global user list is rarely searched compared to local user list.

    # [ISSUE] HOW TO GET THE DATA FROM THE MASTER SERVER?
    # t2 = threading.Thread(target=UserConnectedSocket)

    # 3) Opening WEB page for server by using flask
    t3 = threading.Thread(target=openWebPage)

    t1.start()
   # t2.start()
    t3.start()

    t1.join()
   # t2.join()
    t3.join()

    # both threads completely executed
    print("Done! All of the Thread processes are completed.")
