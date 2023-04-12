
# Python program to illustrate the concept
# of threading
# importing the threading module
# import threading
# import time
# import unusefile.menutest as menutest
# import InternalSocket
import json
from flask import Flask
# import OpenWebPage


import socket
import time
import threading
class ChunkServer:
    def __init__(self,port):
        self.PORT = port
        self.HOST = 


    # Sending regular heartbeat
    # format looks like this:
    # 5001(port number) : 12940821094.12414 (current timestamp)
    # With those values, Master server will know which chunk servers break down.


    #########################################################################################################################
    # This part is for an internal Socket


    def sending_heartbeat(self,socket):

        # This number is the server port number.
        # It is going to be useful to open up the new port server in the Master server.
        msg = str(self.PORT).encode()
        socket.sendall(msg)
        time.sleep(5)
        data = socket.recv(1024)
        print(f"Heartbeat: {data!r}")


    # Sending an updated userlist to master.
    def localuserlistupdate(self,socket):
        # How to send a data? Which format do we need?
        # [ISSUE] MSG FORMAT : How we are going to send a format of this meesage?

        socket.sendall(b"{\"name\": \"per\", \"points\": 15}")
        print('Succeccfuly sent')


    def connections(self):
        HOST = "127.0.0.1"  # The server's hostname or IP address
        PORT = 12345  # The port used by the server
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((HOST, PORT))
            # Connection to socket
            t1 = threading.Thread(target=self.sending_heartbeat, args=(s,))
            t2 = threading.Thread(target=self.localuserlistupdate, args=(s,))
            t1.start()
            t2.start()

            # wait until thread 1 is completely executed
            t1.join()
            # wait until thread 2 is completely executed
            t2.join()


    # # Concurrency : use Asynchronous I/O
    # # select() allows you to check for I/O completion on more than one socket.
    # # you have to use the GIL (Global Interpreter Lock)


    ########################################################################################################################
    # This part is for running web page
    app = Flask(__name__)


    # Every transaction will happends on this page.

    # [ISSUE] HOW TO CONNECT THIS BACKEND API TO FRONTEND?


    userlistjson = 'localuserlist.json'


    @app.route('/')
    # ‘/’ URL is bound with hello_world() function.
    def hello_world():
        return 'Welcome, This is server 5004 '

    # Showing up the whole list of the database.


    @app.route('/showuserlist', methods=['GET'])
    def ShowingAllList(self):

        with open(self.userlistjson, 'r') as file_object:
            db = json.load(file_object)
        return db

    # Get the user name from the frontend. ,method will be 'POST'

    # This will be button and searchbar.


    @app.route('/createuser', methods=['GET'])
    def CreateUser(self):

        with open(self.userlistjson, 'r') as file_object:
            db = json.load(file_object)
            print(db)
            createuser = input('Enter New users name!:')
            db[len(db)] = {'name': createuser, 'points': 0}

        with open(self.userlistjson, 'w') as file_object:
            json.dump(db, file_object)  # converting dictionary to json file.
        return 'Created successfully!'  # + str(db)


    # It is going to be POST
    @ app.route('/increasepoints', methods=['GET'])  # ['POST']
    def IncreasingPoints(self):

        result = ' '
        with open(self.userlistjson, 'r') as file_object:
            db = json.load(file_object)

            # createuser = input('Enter your name!:')
            # opendb[len(opendb)] = {'name': createuser, 'points': 0}
            search_name = input('Enter your name!:')
            for i, db[i] in db.items():
                if (db[i]['name'] == search_name):
                    # Put the result into the result variable.
                    # result = str(db[i]['name']) + ' ' + str(db[i]['points'])
                    print(str(db[i]['name']) + ' ' + str(db[i]['points']))
                    print('How many points increase?')
                    input_points = int(input('Enter points:'))
                    # If deacrese do
                    Resultpoints = int(db[i]['points']) + input_points
                    # print(Resultpoints)
                    result = str(db[i]['name']) + ' ' + str(Resultpoints)
                    db[i] = {'name': search_name, 'points': Resultpoints}
                    break
                else:
                    return 'Not found user'

        with open(self.userlistjson, 'w') as file_object:
            json.dump(db, file_object)  # converting dictionary to json file.

        return result  # How to bring up the json file into WEB?


    def openWebPage(self):
        self.app.run(host='127.0.0.1', port=self.PORT)
    def serverRun(self):
        # [ISSUE] IS IT OKAY TO RUN THOSE TASKES IN THREADING?

        # 1) InternalSocket : Sending heartbeats(.text) and user list update(.json)
        #                     user list format : {"0":{"name":"per","points":15},"1":{"name":"john","points":0}}

        t1 = threading.Thread(target=self.connections)
        # 2) User connected Socket : Ask to Master server to get a global user list(.json)
        # This .json saves into Redis. Becuase, global user list is rarely searched compared to local user list.

        # [ISSUE] HOW TO GET THE DATA FROM THE MASTER SERVER?
        # t2 = threading.Thread(target=UserConnectedSocket)

        # 3) Opening WEB page for server by using flask
        t3 = threading.Thread(target=self.openWebPage)
        t1.start()
    # t2.start()
        t3.start()
        t1.join()
    # t2.join()
        t3.join()




    #############################################################################################################
    # Running chunkserver

if __name__ == '__main__':
    
    chunkServer  = ChunkServer(5005)
    chunkServer.serverRun()
    # both threads completely executed
    print("Done! All of the Thread processes are completed.")
