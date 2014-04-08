#!/usr/bin/python

# requirements
import sys
from xml.etree import ElementTree as ET
import socket, select, string, sys
from termcolor import colored
import random
import uuid
from lib.SSAPLib import *

# basic info 
node_id = str(uuid.uuid4())
heading = "\n" + colored("Publisher> ", "blue", attrs=["bold"])
 
# requests
join_requests = {}
leave_requests = {}

#main function
if __name__ == "__main__":
     
    if(len(sys.argv) < 3) :
        print 'Usage : python publisher.py vsib_hostname vsib_port realsib_hostname realsib_port'
        sys.exit()
     
    vsib_host = sys.argv[1]
    vsib_port = int(sys.argv[2])
    realsib_host = sys.argv[3]
    realsib_port = int(sys.argv[4])
     
    vs = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    vs.settimeout(2)
     
    # connect to remote host
    try:
        vs.connect((vsib_host, vsib_port))
    except :
        print 'Unable to connect to the virtual sib'
        sys.exit()
     
    print 'Connected to remote host. Sending register request!'

    # building and sending the register request
    space_id = "X"
    transaction_id = random.randint(0, 1000)
    register_msg = SSAP_MESSAGE_REQUEST_TEMPLATE%(node_id,
                                                  space_id,
                                                  "REGISTER",
                                                  transaction_id, "")
    vs.send(register_msg)

    request_sockets = []
     
    # connect to the real sib specified as a parameter
    # rs = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # try :
    #     rs.connect((realsib_host, realsib_port))
    # except :
    #     print 'Unable to connect to the real sib'
    #     sys.exit()

    # # building and sending a join request to the real sib
    # join_msg = SSAP_MESSAGE_TEMPLATE%(node_id,
    #                                   space_id,
    #                                   "JOIN",
    #                                   transaction_id, "")
    # rs.send(join_msg)

    # main loop
    while 1:
        socket_list = [sys.stdin, vs]
        for i in request_sockets:
            socket_list.append(i)
         
        # Get the list sockets which are readable
        read_sockets, write_sockets, error_sockets = select.select(socket_list , [], [])
         
        for sock in read_sockets:

            # incoming message from the real sib or from the virtual sib
            if sock in read_sockets: # [vs, rs]:

                try:
                    ssap_msg = sock.recv(4096)
                    if ssap_msg and ssap_msg != " ":
                        print colored("Ricevuto un messaggio ", "red", attrs=["bold"])
    
                        #ssap_list = ssap_msg.split("\n")
                        #ssap_msg = "".join(ssap_list)
    
                        # parse the ssap message                                         
                        try:
                            root = ET.fromstring(ssap_msg)                        
    
                            info = {}
                            for child in root:
                                if child.attrib.has_key("name"):
                                    k = child.tag + "_" + str(child.attrib["name"])
                                else:
                                    k = child.tag
                                info[k] = child.text
    
                            #########################################################
                            ##
                            ## from the virtual sib to the real sib
                            ##
                            #########################################################

                            if sock == vs:
        
                                print colored("Il messaggio ci e' stato inviato dalla vsib", "red", attrs=["bold"])
                                print colored("Il messaggio e' una ", "red", attrs=["bold"]) + str(info["transaction_type"]) + " " + str(info["message_type"])
                                
                                ### NEW PART ###
    
                                if info["message_type"] == "REQUEST": # and info["transaction_type"] != "SUBSCRIBE":
                                    try :
                                        print "Creazione connessione"
                                        rs = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                                        rs.connect((realsib_host, realsib_port))
                                    except :
                                        print str(sys.exc_info())                    
                                        print 'Unable to connect to the real sib'
                                        sys.exit()
                                    request_sockets.append(rs)  
                                    
                                  
    
                                # if it's not a register confirmation, we have to forward the message 
                                # sent by the virtual sib to the real sib
                                print heading + "Received the following " + colored(info["message_type"], "blue", attrs=["bold"]) + " message from the " + colored("VIRTUAL SIB", "blue", attrs=["bold"])
                                print ssap_msg
                                if not(info["transaction_type"] == "REGISTER"):
                                    
                                    print "Invio alla sib reale"
                                    rs.send(ssap_msg)

                            #########################################################
                            ##
                            ## from the real sib to the virtual sib
                            ##
                            #########################################################
        
                            else: # sock in request_sockets:

                                print "Messaggio da una request socket (real sib)"

                                ### NEW PART                            
                                vs.send(ssap_msg)

                                if info["message_type"] == "CONFIRM" and info["transaction_type"] != "SUBSCRIBE":
                                    sock.close()                                
                                    request_sockets.remove(sock)

                                # rs.close()
                                # rs = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                                # try :
                                #     rs.connect((realsib_host, realsib_port))
                                # except :
                                #     print 'Unable to connect to the real sib'
                                #     sys.exit()
    
                                # if it's not a register confirmation, we have to forward the message 
                                # sent by the virtual sib to the real sib
                                print heading + "Received the following " + colored(info["message_type"], "blue", attrs=["bold"]) + " message from the " + colored("REAL SIB", "blue", attrs=["bold"])
                                print ssap_msg
        #                        if not(info["transaction_type"] in ["JOIN", "LEAVE"]):
                                print "send to vs"
                                # vs.send(ssap_msg)
    
                        except ET.ParseError:
                            print "Parse Error" + str(ssap_msg)
                            pass                    
    
                except socket.error:
                    print "Socket Error"
                    pass
