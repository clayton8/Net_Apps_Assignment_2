import argparse
import json
import pika
import shelve
import time
from zeroconf import *
from Basic_Rpc_Client import Basic_Rpc_Client
from Shelve_Data import Shelve_Data
from Service_Listener import Service_Listener




#################################################################
########################### Constants ###########################
AGE = 23
AUTHOR = "Clayton Kuchta"



##################### BACKUP PLAN ###############################
# Kara's RabbitMQ
#IP_ADDRESS = "172.16.102.124"
#VHOST = "T8"
#USER = "claytonkara"
#PASSWORD = "netapps"
#QUEUE_NAME = "team_8"

# Clayton's RabbitMQ
#IP_ADDRESS = "172.16.102.136"
VHOST = "team_8"
USER = "clayton"
PASSWORD = "clayton"
QUEUE_NAME = "team_8"
#RABBITMQ_URL = "amqp://" + USER + ":" + PASSWORD + "@" + IP_ADDRESS + ":5672/" + VHOST
#print "\nURL BEFORE" + RABBITMQ_URL + "\n\n"
##################### BACKUP PLAN ###############################


###################### Zeroconfig ###############################

print "\n\nLooking for a service\n\n"
r = Zeroconf()
type_connect = "_http._tcp.local."
listener = Service_Listener()

browser = ServiceBrowser(r, type_connect, listener=listener)
while listener.connection_found == False:
    i = 1

connect_browser = listener.connection_info
#r.close()
json_pretty = json.dumps(connect_browser, sort_keys=True, indent=4)
print "\n\nFound Team 8 Connetion Connecting:\n", json_pretty, "\n\n"

###################### Zeroconfig ###############################



RABBITMQ_URL = "amqp://" + USER + ":" + PASSWORD + "@" + connect_browser['IP'] + ":" + str(connect_browser['PORT']) + "/" + VHOST

print "URL: " + RABBITMQ_URL + "\n\n"

DB_NAME = "pebble_db.db"
TEAM_NAME = "Team08"
EPOCH_SECONDS = time.mktime(time.localtime())
MSG_ID = TEAM_NAME + "_" + str(EPOCH_SECONDS)
########################### Constants ##########################
#################################################################



#################################################################
################## Set up all arguments to parse ################

parser = argparse.ArgumentParser(description="Load and store messages from a 'bottle.'")


# Set up groups to help user understand what goes together
group_action = parser.add_argument_group('group action')
group_push = parser.add_argument_group('group push')
group_pull = parser.add_argument_group('group pull')

# Action args
group_action.add_argument("-a", "--action", metavar='action', help="**REQUIRED** Action either push, pull, or pullr.")

# Push args
group_push.add_argument("-s", "--subject", metavar='subject', help="Subject of the pebble. **REQUIRED FOR PUSH**")
group_push.add_argument("-m","--message",  metavar='message', help="Message of the pebble. **REQUIRED FOR PUSH**")

# Pull args
group_pull.add_argument("-Qm", metavar='Qm', help="Query by message")
group_pull.add_argument("-Qs", metavar='Qs', help="Query by subject")
group_pull.add_argument("-Qa", metavar='Qa', help="Query by age of author")
group_pull.add_argument("-QA", metavar='QA', help="Query by name of author")
################## Set up all arguments to parse ################
#################################################################



#################################################################
#################### Parse the arguments########################
args = parser.parse_args()
#################### Parse the arguments########################
#################################################################


#################################################################
############# Open the server for communication #################

rpc_client = Basic_Rpc_Client(RABBITMQ_URL)

############# Open the server for communication #################
#################################################################

#################################################################
############# Open the loggin database for pebble ###############

pebble_database = Shelve_Data(DB_NAME)

############# Open the loggin database for pebble ###############
#################################################################


# JSON OBJECT TO BE SENT
data = {}
json_data = ""
response = ""

#################################################################
############# Parse arguments and send info to server ###########
if args.action ==  "pull":
    # User has entered the Pull
    data['Action']  = "pull"
    # Check to see what they want to query
    if args.QA:
        data['Author']  = args.QA
    if args.Qa:
        data['Age']     = args.Qa
    if args.Qs:
        data['Subject'] = args.Qs
    if args.Qm:
        data['Message'] = args.Qm
    json_data = json.dumps(data)
    print "PULL:\n\nPulling for this data: \n\n" + json_data + "\n\n"
    response = rpc_client.call(json_data, QUEUE_NAME, MSG_ID)


elif args.action == "pullr":
    # User want to do a pullr
    data['Action']  = "pullr"
    # Check to see what they want to query
    if args.QA:
        data['Author']  = args.QA
    if args.Qa:
        data['Age']     = args.Qa
    if args.Qs:
        data['Subject'] = args.Qs
    if args.Qm:
        data['Message'] = args.Qm
    json_data = json.dumps(data)
    print "PULLR:\n\nPulling for this data: \n\n" + json_data + "\n\n"
    response = rpc_client.call(json_data, QUEUE_NAME, MSG_ID)

elif args.action == "push":
    # User wants to do a push
    data['Action']  = "push"
    data['Author']  = AUTHOR
    data['Age']     = AGE
    data['MsgID'] = MSG_ID
    # Check user entered a subject and a message
    if args.subject:
        data['Subject'] = args.subject
    else:
        parser.print_help()
        exit()
        pebble_database.close()
    
    if args.message:
        data['Message'] = args.message
    else:
        parser.print_help()
        exit()
        pebble_database.close()

    json_data = json.dumps(data)

    print "PUSH:\n\nPushing this data: \n\n" + json_data + "\n\n"
    response = rpc_client.call(json_data, QUEUE_NAME, MSG_ID)

else:
    # Did not enter an action so print the help
    parser.print_help()
    pebble_database.close()
    exit()
############# Parse arguments and send info to server ###########
#################################################################

# Store information into database
# There was a valid json response from server
response_list = json.loads(response)


if len(response_list):
    
    key = MSG_ID
    print "There were " +  str(len(response_list)) + " JSON objects sent back:\n\n"
    response_dump = json.dumps(response_list, sort_keys=True, indent=4)
    print response_dump
    print
    print "Storing information with key: " + key
    
    pebble_database.push(response_list, key)
    """
    for dic in response_list:
        dic_dump = json.dumps(dic, sort_keys=True, indent=4)
        print dic_dump
        key = str(dic['MsgID'])
        print "\n"
        pebble_database.push(dic, key)
    """
    
    #pebble_database.push(response, key)
    #print "Response from the database: " + response + "\n\n"
else:
    print "There was no quiry found in the bottle: \n" + str(response) + "\n"
# Close the database and server
pebble_database.close()
