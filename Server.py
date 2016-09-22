#Jessica Bailey, Cory Kucera, Roxyn Dively
import socket
import sys
import os
from subprocess import call
from subprocess import check_output
import glob
import zlib
import binascii
from Crypto.Cipher import ARC4
enc = ARC4.new('AKEY2016')
encryptFlag = 0
compressFlag = 0
binaryFlag = 0



#Function for Registered user login
def Login(user):
	passwd = c.recv(1024) #receive password
	c.send("Password received.") #send password ack
	c.recv(1024) #receive and print login message
	if users.has_key(user):
		if str(users[user]) == passwd:
			c.send("accept") #send accept authentication
			user_tracking.append(user)
			c.recv(1024) #receive ack for accept
			print "User %s connected to server." %(user)
			login_loop['login_switch'] = False
			#login_switch = False
			#return login_switch
		else:
			c.send("deny") #send deny authentication
			c.recv(1024) #receive ack for deny
	else: 
		c.send("deny") #send deny authentication
		c.recv(1024) #receive ack for deny
	
#Function to create a new registered user	
def Create_Login(user):
	passwd = c.recv(1024) #receive new password
	c.send("Password received")
	print c.recv(1024)
	if users.has_key(user):
		c.send("deny") #send deny authentication
		c.recv(1024) #receive ack for deny
	else:
		user_files = open('user_login.txt', 'a+')
		user_files.write(user+" "+passwd+"\n")
		c.send("accept") #send accept authentication
		c.recv(1024) #receive ack for accept
		print "User %s connected to server." %(user)
		user_tracking.append(user)
		login_loop['login_switch'] = False

#Reusable function to send files to the client	
def Send_File():
	filename = c.recv(1024) #receive filename for download
	c.send("ack1")
	#if os.path.exists(filename):
	#	c.send("Correct")
	file = open(filename, 'r')
	encryptFlag = c.recv(1024)
	c.send("ack2")
	compressFlag = c.recv(1024)
	c.send("ack20")
	binaryFlag = c.recv(1024)
	contents = file.read()
	encryptFlag = int(encryptFlag)
	compressFlag = int(compressFlag)
	binaryFlag = int(binaryFlag)
	if compressFlag == 1:
		contents = zlib.compress(contents)
	if encryptFlag == 1:
		contents = enc.encrypt(contents)
		#if binaryFlag == 1:
		#	
	c.sendall(contents)
	#else:
	#	c.send("Incorrect")
	#	message = "File %s does not exist on the Server. \n" %(filename)
	#	c.send(message)
	
#Reusable function to retrieve files from the client	
def Receive_File():
	filename = c.recv(1024) #receive filename
	c.send('ack1') #send ack for filename
	#cont = c.recv(1024) #receive file exists identifier
	#if cont == "Correct":
	encryptFlag = c.recv(1024) #receive encryption flag
	c.send("ack")
	compressFlag = c.recv(1024) #receive compression flag
	c.send("ack")
	binaryFlag = c.recv(1024)
	c.send("ack")
	contents = c.recv(1073741824) #receive contents of sent file
	compressFlag = int(compressFlag)
	encryptFlag = int(encryptFlag)
	binaryFlag = int(binaryFlag)
	filetest = open("ActualSent.txt", 'w+')
	filetest.write(contents)
	filetest.close()
	if compressFlag == 1:
		contents = zlib.decompress(contents)
	if encryptFlag == 1:
		contents = enc.decrypt(contents)
	#if binaryFlag == 1:
	file = open(filename, 'w+')
	file.write(contents)
	file.close()
	s.shutdown
	#elif cont == "Incorrect":
	#	m = 1
	#else:
	#	print "Bad Cont identifier: %s" %(cont)
	
#Function created to hold the code for making a new directory	
def Make_Directory():
	dir_name = c.recv(1024) #receive new directory name
	update_name = str(dir_name)
	call(['mkdir', update_name])
	message = "New directory %s created on Server." %(dir_name)#send acknowledgement for creation
	c.send(message)
	
#Function created to hold the code for changing the server directory path
#Allows access to files in different directories	
def Change_Directory():
	currentpath = os.getcwd()
	c.send(currentpath)
	name = c.recv(1024) #receive directory name
	dir_name = str(name)
	os.chdir(dir_name)
	message = "Changed to %s directory" %(name)
	c.send(message) #send message

host = '0.0.0.0'
port = 12345
address = (host, port)
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
print "Socket successfully created"

s.bind(address)
print "Socket successfully bound to %s" %(port)

s.listen(5)
print "Socket listening"

#Create a dictionary to house the user login data for login purposes
users = { }
login_loop = {'login_switch': True }

#Reads from a test file the current saved user data
if os.path.exists("user_login.txt"):
	user_file = open('user_login.txt', 'r+')
	for line in user_file:
		(username, password) = line.split()
		users[username] = password
else:
	user_file = open("user_login.txt", 'w')
	
#This list is used to track which users are currently connected to the server 
#It also allows for automatic closing of the server once the list is empty(last user has disconnected)	
user_tracking = [ ]

#These two lines set a while loop for the running of the server to allow connection
switch = True
while switch:
	c, addr = s.accept() #accepting connection from client
	client_name = c.recv(1024) #receive message 1
	print 'Got connection from', addr
	c.send("Successfully Connected to server.  Please Login:") #send message 2
	while login_loop['login_switch'] == True:
		login_choice = c.recv(1024) #receive login or create
		c.send("Logging in user...")#send logging in user ack
		if login_choice == 'login':
			user = c.recv(1024) #receive user name
			c.send("Username received") #send username ack
			Login(user)#pass username and password into login function
		else:
			user = c.recv(1024)	
			c.send("Username received")	
			Create_Login(user)
	c.send('ack2') #intermediate ack
	
	#These 2 lines allow for a while loop to keep the users inside the main menu until they want to exit
	toggle = True
	while toggle:
		main_menu_choice = c.recv(1024) #receive identifier
		c.send('ack3')
		if main_menu_choice == 'disconnect':
			c.close()
			print "User %s disconnected from server." %(user)
			user_tracking.remove(user)
			if not user_tracking:
				toggle = False
				switch = False
		elif main_menu_choice == 'ls':
			ls_output = check_output(["ls"])
			c.send(ls_output)
		elif main_menu_choice == 'cd':
			Change_Directory()
		elif main_menu_choice == 'make dir':
			Make_Directory()
		elif main_menu_choice == "dir":
			dir_output = check_output(["ls", "-C"])
			c.send(dir_output)
		elif main_menu_choice == 'upload':
			#file_choice = c.recv(1024) #receive file menu option identifier
			Receive_File()				
		elif main_menu_choice == 'download':
			Send_File()
		elif main_menu_choice == 'mget':
			g = c.recv(1024) #receive identifier for wildcard or file list
			if g == 'list':
				count = c.recv(1024)
				count = int(count)
				c.send("ack")
				while count != 0:
					Send_File()
					count -= 1
			elif g == 'search':
				search = c.recv(1024) #wildcard search string
				search = str(search)
				path = os.getcwd() #get path for current working directory
				path = str(path)
				files = glob.glob1(path, search) #search for files 
				#print files
				stringlist = ''
				for file in files:
					stringlist += file
					stringlist += "/"
				c.send(stringlist)
				for file in files:
					if file != '':
						Send_File()		
		elif main_menu_choice == 'mput':
			g = c.recv(1024)
			if g == 'list':
				count = c.recv(1024)
				count = int(count)
				c.send("ack")
				while count != 0:
					Receive_File()
					count -= 1
			elif g == 'search':
				filelist = c.recv(1024)
				filelist.rstrip(" ")
				filenames = filelist.split("/")
				for file in filenames:
					if file != '':
						file = file.strip(" ")
						Receive_File()
		#This else statement will close the server connection if the main menu identifier is unrecognized		
		else:
			toggle = False
			switch = False	
		
			
