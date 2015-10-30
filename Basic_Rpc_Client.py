import pika


class Basic_Rpc_Client(object):
    def __init__(self, url):
        """Connects to a rabbitmq server"""
        parameters = pika.URLParameters(url)
        self.connection = pika.BlockingConnection(parameters)
    
        self.channel = self.connection.channel()
    
        result = self.channel.queue_declare(exclusive=True)
        self.callback_queue = result.method.queue
    
        self.channel.basic_consume(self.on_response, no_ack=True, queue=self.callback_queue)

    def on_response(self, ch, method, properties, body):
        """Callback function for server response"""
        if self.corr_id == properties.correlation_id:
            self.response = body
    
    def call(self, message, queue_name, msg_id):
        """
            Send data to a particular queue name with a unique message
            id
        """
        self.response = None
        self.corr_id = msg_id

        properties = pika.BasicProperties(reply_to=self.callback_queue, correlation_id=self.corr_id)
        self.channel.basic_publish(exchange='', routing_key=queue_name, properties=properties, body=message)
    
        while self.response is None:
            self.connection.process_data_events()
        return self.response
