# Q1. For Master server and Shadow need a DB? also in the local?

-> It is okay to use one file for each

# Q2. Need to unify the format, how to unify the format in json.

1. localuserlist.json
   -> Each server's localuserlist is different.
   -> server5001's userlist, server5002's userlist.

2. globaluserlist.json (need to using different name?)
   -> This file going to be shared between Master and shadow. Need a copy of the data Master and Shadow

3. heartbeat.txt
   -> This file going to be shared

# Q3. When upload the new data or retrive the data. should get it from the Web by sending a data HTTP request. using flask!

# Q4. Through socket, data will be sent in 'string format' and Like a heartbeat machanism, If user is on the json, just upload the points.

ex) If user data is already existed on the list, just upload the point only,
or If the user is not on the list, add user and upload the point.

# Q5. Need Redis? : When retrive the userlist from the Master server, this user list should be stored in the redis? or?

# Q6. Spanner?

# Q7. How to turn on the chunk server's by using os.system(command), or using subprocess?

==============================================================================================================================================

# Things to do

# Master Server

1. Sending data to the Shadow Master
2. When Shadow Master turning back from the failure then turning on the chunk servers based on the heart beat list
3. When chunkserver turns off, Also the master turns off..

# Chunk server

1. Connecting to the front end page
2. sending data from the frontend and then saves data into localuserlist then send it to the master server.
3. When turning off the chunk server, not forcefully, do some thing.

# How to make a partition like multiple chunkserver folders, master server folder.

# When Multiple chunk servers connected to the master, what it happens? is there any error?
# DistributedSystemTeamProject
