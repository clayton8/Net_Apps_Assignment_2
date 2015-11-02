from zeroconf import *
import socket
import time
import json

class Service_Listener(object):
    def __init__(self):
        self.r = Zeroconf()
        self.connection_found = False
        self.connection_info = {}

    def add_service(self, zeroconf, service_type, name):
        print "[x] Found one service:"
        print "    Service ", name, " added" 
        print "        Type is", service_type
        info = self.r.get_service_info(service_type, name)
        if info:
            print("        Address: %s:%d" % (socket.inet_ntoa(info.address), info.port))
            print("        Weight: %d, priority: %d" % (info.weight, info.priority))
            print("        Server: %s" % (info.server,))
            if info.properties:
                print("        Properties are:")
                # Grab conneciton info
                for key, value in info.properties.items():
                    print("            %s: %s" % (key, value))
            else:
                print("        No properties")
        else:
            print("        No info")
        print('\n')
        if "Team 8 Server" in name:
            self.connection_found = True
            self.connection_info['IP'] = socket.inet_ntoa(info.address)
            self.connection_info['PORT'] = info.port

    def remove_service(self, service_type, name, state_change):
        print
        print "Service ", name, " removed"


if __name__ == '__main__':
    r = Zeroconf()
    type_connect = "_http._tcp.local."
    listener = Service_Listener()
    print "\n\nLooking for a service\n\n"
    browser = ServiceBrowser(r, type_connect, listener=listener)
    # Search for devices for 40 seconds. 
    while listener.connection_found == False:
        i = 1
    r.close()
    connect_browser = listener.connection_info
    json_pretty = json.dumps(connect_browser, sort_keys=True, indent=4)
    print "\n\nConnecting:\n", json_pretty




