#!/usr/bin/env python 
import pika


#####################################################################
################## CALLBACK SERVER FUNCTIONS ########################
def callback( ch, method, properties, body ): 
    print " [x] Received %r" % (body,)

def on_request(ch, method, props, body):
    print " [x] Received %r" % (body) 
    
    return_properties = pika.BasicProperties(correlation_id=props.correlation_id)
    
    ch.basic_publish(exchange='', routing_key=props.reply_to, properties=return_properties, body=body)
    
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
IP_ADDRESS = "172.30.39.155"
VHOST = "team_8"
USER = "clayton"
PASSWORD = "clayton"
RABBITMQ_URL = "amqp://" + USER + ":" + PASSWORD + "@" + IP_ADDRESS + ":5672/" + VHOST
QUEUE_NAME = "team_8"
########################### Constants ##########################
#################################################################




channel = connect_rabbitmq_url( RABBITMQ_URL, QUEUE_NAME)

print ' [*] Waiting for messages. To exit press CTRL+C'
rabbitmq_consume_rpc( channel, QUEUE_NAME )

#rabbitmq_consume_basic( channel, QUEUE_NAME )

