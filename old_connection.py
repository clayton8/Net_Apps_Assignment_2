import pika
import json




################################################################
#################### SETUP CLIENT FUNCIONS #####################
def connect_rabbitmq_url( url, queue_name ):
    """Connects to a rabbitmq server"""
    parameters = pika.URLParameters(url)
    connection = pika.BlockingConnection(parameters)
    channel = connection.channel()
    channel.queue_declare(queue=queue_name)
    return channel

def change_rabbitmq_queue( channel, new_name):
    channel.queue_declare(queue=new_name)
    return channel
#################### SETUP CLIENT FUNCIONS #####################
################################################################



################################################################
#################### SETUP CLIENT FUNCIONS #####################
def connect_rabbitmq_url( url, queue_name ):
    """Connects to a rabbitmq server"""
    parameters = pika.URLParameters(url)
    connection = pika.BlockingConnection(parameters)
    channel = connection.channel()
    channel.queue_declare(queue=queue_name)
    return channel

def change_rabbitmq_queue( channel, new_name):
    channel.queue_declare(queue=new_name)
    return channel
#################### SETUP CLIENT FUNCIONS #####################
################################################################



server_connection = connect_rabbitmq_url( RABBITMQ_URL, QUEUE_NAME )
send_rabbitmq_message(server_connection, json_data, QUEUE_NAME)
