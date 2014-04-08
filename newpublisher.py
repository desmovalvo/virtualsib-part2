#requirements
import sys
import json
import random
import uuid
from termcolor import *
import socket, select, string, sys


if(len(sys.argv) < 2) :
    print colored("newpublisher> ", "red", attrs=["bold"]) + 'Usage : python newpublisher.py owner'
    sys.exit()
    
# real sib information
owner = sys.argv[1]

sib_id = str(uuid.uuid4())

# socket to the manager process
manager = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
manager.settimeout(2)
     
# connect to the manager
try :
    manager.connect((manager_host, manager_port))
except :
    print colored("newpublisher> ", "red", attrs=['bold']) + 'Unable to connect to the manager'
    sys.exit()    

print colored("newtpublisher> ", "blue", attrs=['bold']) + 'Connected to the manager. Sending register request!'

# build request message 
register_msg = {"command":"NewRemoteSib", "sibID":sib_id, "owner":owner}
# print register_msg
# print type(register_msg)

request = json.dumps(register_msg)
# print request
# print type(request)

manager.send(request)

# newmsg = json.loads(request)

# print newmsg
# print type(newmsg)

# print register_msg["command"]
# print newmsg["command"]

while 1:
    confirm_msg = manager.recv(4096)
    if confirm_msg:
        print colored("newpublisher> ", "red", attrs=["bold"]) + 'Received the following message:'
        print confirm_msg
        break

confirm = json.loads(confirm_msg)
if confirm["return"] == "ok":
    print colored("newpublisher> ", "red", attrs=["bold"]) + 'Sib is now reachable!'
    
elif confirm["return"] == "fail":
    print colored("newpublisher> ", "red", attrs=["bold"]) + 'Registration failed!'


