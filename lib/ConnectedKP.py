#!/usr/bin/python

# requirements
import socket

class ConnectedKP:

    # initialization: called on JOIN REQUEST
    def __init__(node_id, clientsock):
        self.node_id = node_id
        self.clientsock = clientsock
        self.status = "Waiting"
        self.active_subscriptions = {}

    # method called to set the status to the instance
    def set_status(status):
        if status in ["Waiting", "Joined", "Left", "Unreachable"]:
            self.status = status
            return True
        else:
            return False

    # method used to register a new subscription
    # should be called when we send a SUBSCRIBE CONFIRM to the KP
    def add_new_subscription(subscription_id, clientsocket):
        self.active_subscriptions[subscription_id] = clientsocket
            
    # remove_subscription should be called when we get an UNSUBSCRIBE CONFIRM
    def remove_subscription(subscription_id):
        if self.active_subscriptions.has_key(subscription_id):
            del self.active_subscriptions[subscription_id]
