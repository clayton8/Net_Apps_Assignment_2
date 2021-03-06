#!/usr/bin/env python 
import pika
import json
import shelve
import RPi.GPIO as GPIO
import ast
from Zeroconf_Service import Zeroconf_Service


################# LED/GPIO ###############
def turnOn(LED):
    GPIO.output(int(LED), GPIO.HIGH)
def turnOff(LED):
    GPIO.output(int(LED), GPIO.LOW)

LED0 = 11
LED1 = 12
LED2 = 13
LED3 = 15

GPIO.setmode(GPIO.BOARD)
GPIO.setup(int(LED0), GPIO.OUT)
GPIO.setup(int(LED1), GPIO.OUT)
GPIO.setup(int(LED2), GPIO.OUT)
GPIO.setup(int(LED3), GPIO.OUT)
GPIO.output(int(LED0), GPIO.LOW)
GPIO.output(int(LED1), GPIO.LOW)
GPIO.output(int(LED2), GPIO.LOW)
GPIO.output(int(LED3), GPIO.LOW)

def forCounting(count):
    c = bin(count)
    counter = c.replace("0b","")
    counter = counter.zfill(4)
    if counter[3] == "1":
        turnOn(LED0)
    else:
        turnOff(LED0)
    if counter[2] == "1":
        turnOn(LED1)
    else:
        turnOff(LED1)
    if counter[1] == "1":
        turnOn(LED2)
    else:
        turnOff(LED2)
    if counter[0] == "1":
        turnOn(LED3)
    else:
        turnOff(LED3)

#####################################################################
################## CALLBACK SERVER FUNCTIONS ########################
def callback( ch, method, properties, body ): 
    print " [x] Received %r" % (body,)

count = 0

def on_request(ch, method, props, body):
    print " [x] Received %r" % (body) 
    
    return_properties = pika.BasicProperties(correlation_id=props.correlation_id)

    s = shelve.open('bottle_database.db', writeback = True)

    print "Body: ", body

    dict = json.loads(body)
    global send_message_list_of_dic
    send_message_list_of_dic = []
    returnlist = []

    if dict['Action'] == "push":
        global count

        k = dict['MsgID']
        kstr = ast.literal_eval(json.dumps(k))
        count = count + 1
        try:
             s[kstr] = dict
             forCounting(count)
        finally:
             dict['Status'] = "Success"
             returnlist.append(dict)
             s.close()
    elif dict['Action'] == "pull":
        #copy instead of remove
        try:
            age = dict.get('Age','')
            message = dict.get('Message','')
            subject = dict.get('Subject','')
            author = dict.get('Author','')
            returnlist = []

            klist = list(s.keys())

            for i in range(0,len(klist)):
                r = s[klist[i]]
                testdict = ast.literal_eval(json.dumps(r))
                if (age == '' and message == '' and subject == '' and author == ''):
                    returnlist.append(testdict)
                    del s[klist[i]]
                else:
                    add_me = True
                    #test for qualities
                    if (testdict['Author'] != author and  author != ''):    
                       #put into list to return to client
                        add_me = False
                    if (testdict['Subject'] != subject and subject != ''):
                        #put into list to return to client
                        add_me = False
                    if (testdict['Message'] != message and message != ''):
                        #put into list to return to client
                        add_me = False
                    greater = '>'
                    less = '<'
                    if greater in age:
                        agefix = age.replace(">","")
                        a = int(agefix)
                        storea = testdict['Age']
                        istorea = int(storea)
                        if istorea <= a:
                            add_me = False
                    elif less in age:
                        agefix = age.replace("<","")
                        a = int(agefix)
                        storea = testdict['Age']
                        istorea = int(storea)
                        if istorea >= a:
                            add_me = False
                    elif age != '' and testdict['Age'] != int(age):
                        add_me = False
                    
                    if add_me:
                        del s[klist[i]]
                        count = count - 1
                        returnlist.append(testdict)
                
                forCounting(count)

        finally:
              s.close()
    elif dict['Action'] == "pullr":
        #copy instead of remove
        try:
            age = dict.get('Age','')
            message = dict.get('Message','')
            subject = dict.get('Subject','')
            author = dict.get('Author','')
            returnlist = []

            klist = list(s.keys())

            for i in range(0,len(klist)):
                r = s[klist[i]]
                testdict = ast.literal_eval(json.dumps(r))
                if (age == '' and message == '' and subject == '' and author == ''):
                    returnlist.append(testdict)
                else:
                    add_me = True
                    #test for qualities
                    if (testdict['Author'] != author and  author != ''):    
                       #put into list to return to client
                        add_me = False
                    if (testdict['Subject'] != subject and subject != ''):
                        #put into list to return to client
                        add_me = False
                    if (testdict['Message'] != message and message != ''):
                        #put into list to return to client
                        add_me = False
                    greater = '>'
                    less = '<'
                    if greater in age:
                        agefix = age.replace(">","")
                        a = int(agefix)
                        storea = testdict['Age']
                        istorea = int(storea)
                        if istorea <= a:
                            add_me = False
                    elif less in age:
                        agefix = age.replace("<","")
                        a = int(agefix)
                        storea = testdict['Age']
                        istorea = int(storea)
                        if istorea >= a:
                            add_me = False
                    elif age != '' and testdict['Age'] != int(age):
                        add_me = False
                    
                    if add_me:
                        returnlist.append(testdict)
                
                #forCounting(count)

        finally:
              s.close()
              print "done copy"
    else:
        print "Action is incorrect."
    
#end my code

    send_message_json = json.dumps(returnlist)   
    ch.basic_publish(exchange='', routing_key=props.reply_to, properties=return_properties, body=send_message_json)
    
    ch.basic_ack(delivery_tag=method.delivery_tag)
################## CALLBACK SERVER FUNCTIONS ########################
#####################################################################




#####################################################################
################## SERVER SETUP FUNCTIONS ###########################
def connect_rabbitmq_url( url, queue_name, port, service_name ):
    """Connects to a rabbitmq server"""
    service = Zeroconf_Service(name=service_name, port=port)
    service.publish()
    print
    parameters = pika.URLParameters(url)
    connection = pika.BlockingConnection(parameters)
    channel = connection.channel()
    channel.queue_declare(queue=queue_name)
    return channel

def rabbitmq_consume_rpc( channel, queue_name ):
    """Sets up consuming from queue and a response"""
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(on_request, queue=queue_name)
    channel.start_consuming()

def rabbitmq_consume_basic( channel, queue_name ):
    """Sets up consuming from queue and no response"""
    channel.basic_consume(callback, queue=queue_name, no_ack=True)
    channel.start_consuming()
    
################## SERVER SETUP FUNCTIONS ###########################
#####################################################################




#################################################################
########################### Constants ##########################
IP_ADDRESS = "172.16.102.136"
#VHOST = "T8"
#USER = "claytonkara"
#PASSWORD = "netapps"

VHOST = "team_8"
USER = "clayton"
PASSWORD = "clayton"

PORT = 5672
RABBITMQ_URL = "amqp://" + USER + ":" + PASSWORD + "@" + IP_ADDRESS + ":"+str(PORT)+ "/" + VHOST
QUEUE_NAME = "team_8"
SERVICE_NAME = "Team 8 Server"

########################### Constants ##########################
#################################################################




channel = connect_rabbitmq_url( RABBITMQ_URL, QUEUE_NAME, PORT, SERVICE_NAME)

print ' [*] Waiting for messages. To exit press CTRL+C'
rabbitmq_consume_rpc( channel, QUEUE_NAME,  )

#rabbitmq_consume_basic( channel, QUEUE_NAME )

