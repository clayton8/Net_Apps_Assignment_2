#!/usr/bin/env python 
import pika
import json
import shelve
import RPi.GPIO as GPIO


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
GPIO.setup(int(LED0), GPIO.LOW)
GPIO.setup(int(LED1), GPIO.OUT)
GPIO.setup(int(LED1), GPIO.LOW)
GPIO.setup(int(LED2), GPIO.OUT)
GPIO.setup(int(LED2), GPIO.LOW)
GPIO.setup(int(LED3), GPIO.OUT)
GPIO.setup(int(LED3), GPIO.LOW)

def forCounting(count):
    c = bin(count)
    if c[0] == "1":
        turnOn(LED0)
    else:
        turnOff(LED0)
    if c[1] == "1":
        turnOn(LED1)
    else:
        turnOff(LED1)
    if c[2] == "1":
        turnOn(LED2)
    else:
        turnOff(LED2)
    if c[3] == "1":
        turnOn(LED3)
    else:
        turnOff(LED3)

#####################################################################
################## CALLBACK SERVER FUNCTIONS ########################
def callback( ch, method, properties, body ): 
    print " [x] Received %r" % (body,)

count = 0;
#make shelf
#s = shelve.open('bottle!')

#end make shelf


def on_request(ch, method, props, body):
    print " [x] Received %r" % (body) 
    
    return_properties = pika.BasicProperties(correlation_id=props.correlation_id)

    s = shelve.open('bottle!')
#Below is putting the message recieved into a dictionary entry


    print "Body: ", body

    dict = json.loads(body)

    #dictionary = body;
    print "DICTIONARY: ", dict['Author']

    if dict['Action'] == "push":
        global count
        #count = count + 1;
        print "count: ", count
        #forCounting(count)
        key = str(count)
        count = count + 1
        send_message_list_of_dic = []
        try:
            s[key]=dict
        finally:
            s.close()
    elif dict['Action'] == "pull":
        try:
            age = dict['Age']
            message = dict['Message']
            subject = dict['Subject']
            author = dict['Author']
        
            returnlist = []
            rlcount = 0

            #count = count - 1
            #error checking for count?
            klist = list(s.keys())
            for i in range(0,len(klist)):
                rlcount = 0
                #test for qualities
                if klist[i]['Author'] == author:
                    #put into list to return to client
                    returnlist.append(klist[i])
                    rlcount = 1
                    del dict[author]
                if klist[i]['Subject'] == subject:
                    #put into list to return to client
                    if rlcount != 1:
                        returnlist.append(klist[i])
                        rlcount = 1
                if klist[i]['Message'] == message:
                    #put into list to return to client
                    if rlcount != 1:
                        returnlist.append(klist[i])
            
                greater = '>'
                less = '<'
                #if greater in klist[i]['Age']:
            
                for i in range (0,len(klist)):
                    send_message_list_of_dic[i] = json.loads(klist[i])    
        finally:
             s.close()
#    elif dict['Action'] == "pullr":
        #copy instead of remove
    else:
        print "Action is incorrect."
    

#end my code

    

    ##### KARA WHEN YOU SEND DTAT BACK SEND IT IN THIS FORMAT ########
    # FIRST MAKE A QUIRY FOR THE DATA (in this case I am quirying 
#    query_data_one = json.loads(body)
#    query_data_two = json.loads(body)
#    query_data_three = json.loads(body)
#    query_data_four = json.loads(body)

    # SECOND MAKE A LIST OF THE DICTIONARY (if no quereys found make a empty list
#    send_message_list_of_dic = [query_data_one, query_data_two, query_data_three, query_data_four]
    #send_message_list_of_dic = []
    
    # FINALLY DO A JSON.DUMPS ON THE LIST OF DICTIONARIES AND THEN SEND IT
    send_message_json = json.dumps(send_message_list_of_dic)
    
    ch.basic_publish(exchange='', routing_key=props.reply_to, properties=return_properties, body=send_message_json)
    
    ch.basic_ack(delivery_tag=method.delivery_tag)
################## CALLBACK SERVER FUNCTIONS ########################
#####################################################################




#####################################################################
################## SERVER SETUP FUNCTIONS ###########################
def connect_rabbitmq_url( url, queue_name ):
    """Connects to a rabbitmq server"""
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
IP_ADDRESS = "172.16.102.124"
VHOST = "T8"
USER = "claytonkara"
PASSWORD = "netapps"
RABBITMQ_URL = "amqp://" + USER + ":" + PASSWORD + "@" + IP_ADDRESS + ":5672/" + VHOST
QUEUE_NAME = "team_8"
########################### Constants ##########################
#################################################################




channel = connect_rabbitmq_url( RABBITMQ_URL, QUEUE_NAME)

print ' [*] Waiting for messages. To exit press CTRL+C'
rabbitmq_consume_rpc( channel, QUEUE_NAME )

#rabbitmq_consume_basic( channel, QUEUE_NAME )

