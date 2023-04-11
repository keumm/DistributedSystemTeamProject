import json
from flask import Flask
import UserConnectedSocket
# import OpenWebPage


import socket
import time
import threading
import os

os.system('python chunk_server5001.py')
# Sending regular heartbeat
# format looks like this:
# 5003(port number) : 12940821094.12414 (current timestamp)
# With those values, Master server will know which chunk servers break down.


#########################################################################################################################
# This part is for an internal Socket


# [Issue] Need to connect with front end page and this sendingMessage function.
# Using Flask?

# [Issue] Heart beat and Master server reply socket must be defferent???
def sending_heartbeat(socket):
    print('hi')
    while (1):

        # This number is the server port number.
        # It is going to be useful to open up the new port server in the Master server.

        # what is the difference between send and sendall?
        # When I send a heart beat by using send, It has a collision with sending message.
        socket.sendall(b"5003")
        time.sleep(10)
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

def SendMessage(socket):
    t_end = time.time() + 3
    # msg = 'MARK'
    # msg = '{"name": "Jeremiah", "points": 3}'
    # msg = '{"name": "Oscar", "points": 12, "timestamp": 1780909832.773651 }'

    current_time = time.time()
    # Sending a message with the cuerrent time as well
    msg = '{"name": "chilly", "points": 13, "timestamp": %f }' % current_time
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


def MultiThreadingClient(socket):

    t1 = threading.Thread(target=SendBufferData, args=(socket,))
    t2 = threading.Thread(target=SendMessage, args=(socket,))

    t1.start()
    t2.start()
    t1.join()
    t2.join()

# Sending an updated userlist to master.


# Message comes from FrontEnd and recording on the localuserlist.json
# Then send a message to the master server.

def localuserlistupdate(socket):
    # How to send a data? Which format do we need?
    # [ISSUE] MSG FORMAT : How we are going to send a format of this meesage?

    MultiThreadingClient(socket)
    # print('Succeccfuly sent')


def connections():
    HOST = "127.0.0.1"  # The server's hostname or IP address
    PORT = 12345  # The port used by the server
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        # Connection to socket
        t1 = threading.Thread(target=sending_heartbeat, args=(s,))
        t2 = threading.Thread(target=localuserlistupdate, args=(s,))
        t1.start()
        t2.start()

        # wait until thread 1 is completely executed
        t1.join()
        # wait until thread 2 is completely executed
        t2.join()

        # both threads completely executed
        print("Done! All of the Thread processes are completed.")


########################################################################################################################
# This part is for running web page
app = Flask(__name__)


# Every transaction will happends on this page.
# [ISSUE] HOW TO CONNECT THIS BACKEND API TO FRONTEND?


userlistjson = 'localuserlist.json'


@app.route('/')
# ‘/’ URL is bound with hello_world() function.
def hello_world():
    return 'Welcome, This is the CHunk server 5003 '

# Showing up the whole list of the database.


@app.route('/showuserlist', methods=['GET'])
def ShowingAllList():

    with open(userlistjson, 'r') as file_object:
        db = json.load(file_object)
    return db

# Get the user name from the frontend. ,method will be 'POST'

# This will be button and searchbar.


# @app.route('/createuser', methods=['GET'])
# def CreateUser():

#     with open(userlistjson, 'r') as file_object:
#         db = json.load(file_object)
#         print(db)
#         createuser = input('Enter New users name!:')
#         db[len(db)] = {'name': createuser, 'points': 0}

#     with open(userlistjson, 'w') as file_object:
#         json.dump(db, file_object)  # converting dictionary to json file.
#     return 'Created successfully!'  # + str(db)


# # It is going to be POST
# @ app.route('/increasepoints', methods=['GET'])  # ['POST']
# def IncreasingPoints():

#     result = ' '
#     with open(userlistjson, 'r') as file_object:
#         db = json.load(file_object)

#         # createuser = input('Enter your name!:')
#         # opendb[len(opendb)] = {'name': createuser, 'points': 0}
#         search_name = input('Enter your name!:')
#         for i, db[i] in db.items():
#             if (db[i]['name'] == search_name):
#                 # Put the result into the result variable.
#                 # result = str(db[i]['name']) + ' ' + str(db[i]['points'])
#                 print(str(db[i]['name']) + ' ' + str(db[i]['points']))
#                 print('How many points increase?')
#                 input_points = int(input('Enter points:'))
#                 # If deacrese do
#                 Resultpoints = int(db[i]['points']) + input_points
#                 # print(Resultpoints)
#                 result = str(db[i]['name']) + ' ' + str(Resultpoints)
#                 db[i] = {'name': search_name, 'points': Resultpoints}
#                 break
#             else:
#                 return 'Not found user'

#     with open(userlistjson, 'w') as file_object:
#         json.dump(db, file_object)  # converting dictionary to json file.

#     return result  # How to bring up the json file into WEB?


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
