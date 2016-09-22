#Jessica Bailey, Cory Kucera, Roxyn Dively
import socket
import sys
import os
import glob
import zlib
from Crypto.Cipher import ARC4
enc = ARC4.new('AKEY2016')

encryptFlag = 0
compressFlag = 0
binaryFlag = 0


buff = 1024
s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
host = '172.20.10.2'
port = 12345
address = (host, port)
s.connect(('127.0.0.1',port))
print "Socket successfully connected"
s.send(host) #send message 1
print s.recv(buff) #receive message 2



#Reusable function used to send files to the client	
def Upload_File(filename, encryptFlag, compressFlag, binaryFlag):
	s.send(filename) #send filename to upload
	s.recv(buff) #receive acknowledgement of filename
	if os.path.exists(filename):
		s.send("Correct")
		file = open(filename, 'r')
		contents = file.read()
		if encryptFlag == 1:
			contents = Encryption(contents)
		if compressFlag == 1:
			contents = zlib.compress(contents)
		s.send(str(encryptFlag))
		s.recv(buff) #ack
		s.send(str(compressFlag))
		s.recv(buff) #ack
		s.send(str(binaryFlag))
		s.recv(buff)
		s.sendall(contents)
		file.close()
		print "File %s uploaded to server.\n" %(filename)
	else:
		s.send("Incorrect")
		print "File %s does not exist on the Client. \n" %(filename)
		
#Reusable function to ask user if they want to encrypt or compress the files being sent and received	
def FileOptions_Menu(filename, encryptFlag, compressFlag, binaryFlag, IDflag):
	os.system("clear")
	encrypt = raw_input("Would you like to encrypt %s? (y/n)\n" %(filename))
	encrypt.lower()
	if encrypt == 'y':
		encryptFlag = 1
	os.system("clear")
	compress = raw_input("Would you like to compress %s? (y/n)\n" %(filename))
	compress.lower()
	if compress == 'y':
		compressFlag = 1
	os.system("clear")
	binary = raw_input("Would you like to change %s to binary? (y/n)\n" %(filename))
	binary.lower()
	if binary == 'y':
		binaryFlag = 1
	os.system("clear")
	if IDflag == "U":
		#s.send("n")
		Upload_File(filename, encryptFlag, compressFlag, binaryFlag)
	elif IDflag == "D":
		#s.send("n")
		Download_File(filename, encryptFlag, compressFlag, binaryFlag)
	else:
		print "Bad IDflag."
#Reusable function used to retrieve files from the server			
def Download_File(filename, encryptFlag, compressFlag, binaryFlag):
	s.send(filename) #send filename for download
	s.recv(buff)
	cont = s.recv(buff)
	if cont == "Correct":
		s.send(str(encryptFlag))
		s.recv(buff)
		s.send(str(compressFlag))
		s.recv(buff)
		s.send(str(binaryFlag))
		contents = s.recv(1073741824)
		if compressFlag == 1:
			contents = zlib.decompress(contents)
		if encryptFlag == 1:
			contents = Decryption(contents) 
		#contents = s.recv(1073741824)
		file = open(filename, 'w+')
		file.write(contents)
		file.close()
	elif cont == "Incorrect":
		print s.recv(buff)
	else:
		print "Bad Cont identifier: %s" %(cont)

#Reusable function that holds the main menu after login is successful
def Main_Menu(user, encryptFlag, compressFlag, binaryFlag):
	os.system("clear")
	print "Welcome %s!" %(user) + "\n" 
	online = True
	menu = {}
	menu['1'] = "List Sources (ls)"
	menu['2'] = "Change Directory (cd)"
	menu['3'] = "Make Directory (mkdir)"
	menu['4'] = "dir"
	menu['5'] = "Upload File to Server (put)"
	menu['6'] = "Download File from Server (get)"
	menu['7'] = "Download Multiple Files from Server (mget)"
	menu['8'] = "Upload Multiple Files to Server (mput)"
	menu['Q'] = "Quit"
	while online:
		options = menu.keys()
		options.sort()
		for entry in options:
			print entry, menu[entry]
		
		selection = raw_input("Please select an option: \n")
		selection = selection.lower()
		if selection == '1':
			os.system('clear')
			s.send('ls') #send ls identifier
			s.recv(buff)
			os.system('clear')
			print s.recv(buff)
		elif selection == '2':
			os.system('clear')
			s.send('cd') #send identifier
			s.recv(buff) #receive ack
			currentpath = s.recv(buff)
			name = raw_input("What directory would you like to change to? \n Your current path is: %s \n"%(currentpath))
			s.send(name) #send name
			print s.recv(buff) #receive message
			print "\n"
			#print s.recv(buff)
			Main_Menu(user, encryptFlag, compressFlag, binaryFlag)
		elif selection == '3':
			os.system('clear')
			name = raw_input("What would you like to name your new directory? \n")
			s.send("make dir") #send identifier for make directory
			s.recv(buff) #receive acknowledgement for identifier
			s.send(name) #send name for new directory
			print s.recv(buff) #print message
		elif selection == '4':
			os.system('clear')
			s.send("dir")
			s.recv(buff)
			os.system('clear')
			dir_output = s.recv(buff)
			print dir_output
			#s.recv(buff)
			#s.send("dir")
		elif selection == '5':
			os.system('clear')
			s.send('upload') #send identifier 'upload'
			IDflag = 'U'
			s.recv(buff) #receive acknowledgement of identifier
			filename = raw_input("What file would you like to Upload: \n")
			FileOptions_Menu(filename, encryptFlag, compressFlag, binaryFlag, IDflag)
		elif selection == '6':
			os.system('clear')
			contents = [ ]
			s.send('download') #send identifier 'download'
			IDflag = "D"
			s.recv(buff) #receive acknowledgement of identifier
			filename = raw_input("What file would you like to Download: \n")
			FileOptions_Menu(filename, encryptFlag, compressFlag, binaryFlag, IDflag)
			print "File %s downloaded from server." %(filename)
		elif selection == '7':
			s.send("mget") #send menu identifier to server
			s.recv(buff)
			os.system('clear')
			x = raw_input("Would you like to list files (f) or use wildcard (w)? \n")
			x.lower()
			if x == 'f':
				s.send('list')
				number = raw_input("How many files would you like to download?\n")
				s.send(number) 
				number = int(number)
				s.recv(buff)
				IDflag = "D"
				while number != 0:
					filename = raw_input("Enter file you would like to download: \n")
					FileOptions_Menu(filename, encryptFlag, compressFlag, binaryFlag, IDflag)
					number -= 1
			elif x == 'w':
				s.send('search')
				search = raw_input("What would you like to search for? \n")
				s.send(search)
				files = s.recv(buff)
				files.rstrip(" ")
				filenames = files.split("/")
				IDflag = "D"
				for file in filenames:
					if file != '':
						file = file.strip(" ")
						FileOptions_Menu(file, encryptFlag, compressFlag, binaryFlag, IDflag)
			print "Files downloaded from server.\n"
		elif selection == '8':
			s.send("mput") #send menu identifier to server
			s.recv(buff)
			os.system('clear')
			x = raw_input("Would you like to list files (f) or use wildcard (w)? \n")
			x.lower()
			if x == 'f':
				s.send('list')
				number = raw_input("How many files would you like to Upload? \n")
				s.send(number)
				number = int(number)
				s.recv(buff)
				IDflag = "U"
				while number != 0:
					filename = raw_input("Enter file you would like to Upload: \n")
					FileOptions_Menu(filename, encryptFlag, compressFlag, binaryFlag, IDflag)
					number -= 1
			elif x == 'w':
				s.send("search")
				search = raw_input("What would you like to search for? \n")
				path = os.getcwd()
				path = str(path)
				files = glob.glob1(path, search)
				stringlist = ''
				for file in files:
					stringlist += file
					stringlist += "/"
				s.send(stringlist)
				IDflag = "U"
				for file in files:
					if file != '':
						FileOptions_Menu(file, encryptFlag, compressFlag, binaryFlag, IDflag)
			print "Files Uploaded to Server. \n"
		elif selection == 'q':
			os.system('clear')
			print "Disconnecting"
			s.send("disconnect")
			s.close()
			online = False
			return False
		else:
			os.system('clear')
			print "Option not valid.  Choose again."
 #The next 4 lines set up the user login loop.  Will loop until the user name and password are accepted
connection = True
login_menu = {}
login_menu['1'] = "Login"
login_menu['2'] = "Create new user"
while connection:
	choice = login_menu.keys()
	choice.sort()
	for entry in choice:
		print entry, login_menu[entry]
	login_input = raw_input("Select a Login option: ")
	if login_input == '1':
		os.system("clear")
		print "Enter login information: \n"
		s.send("login") #send message for login
		s.recv(buff) #receive logging in user... ack
		user = raw_input("Enter user name: ")
		s.send(user) #send username
		s.recv(buff) #receive username ack
		passwd = raw_input("Enter password: ")
		s.send(passwd)#send password
		s.recv(buff) #receive password ack
		s.send("Logging in user...") #send login message
		login = s.recv(1024) #receive accept or deny for authentication
		s.send('ack4') #send ack for accept or deny
		if login == "accept":
			os.system('clear')
			print "Logging in user %s." %(user) + "\n"
			connection = False
		else:
			os.system('clear')
			print "User name and password do not match." + "\n"
	elif login_input == '2':
		os.system("clear")
		print "Enter new user information: \n"
		s.send("create") #send message for creation
		s.recv(buff) #receive 
		user = raw_input("Enter the Username you would like to use: ")
		s.send(user) #create user, send user name
		s.recv(buff) #receive username ack
		new_password = raw_input("Please select a password: ")
		s.send(new_password) #create user, send password
		s.recv(buff) #receive password ack
		s.send("Creating new user...") #send validation for user creation
		login = s.recv(buff) #receive accept or deny for authentication
		s.send('ack5') #send ack for accept or deny
		if login == "deny":
			os.system('clear')
			print "User name %s already taken. " %(user) + "\n"
		else:
			os.system('clear')
			print "User created. Logging in user %s. " %(user) + "\n"
			connection = False
	else:
		os.system('clear')
		print ("Please select a valid option. ")
s.recv(buff) #receive intermediate ack2
#Once login is accepted the main menu function is called
if login == "accept":
	disconnect = Main_Menu(user, encryptFlag, compressFlag, binaryFlag)
	if disconnect == False:
		s.close()
		connection = False
#This else statement catches any kind of issue that may occur with login
else:
	os.system('clear')
	print "Unknown Error has occurred at %s. " %(login)
	
