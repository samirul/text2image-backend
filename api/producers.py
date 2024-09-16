import os
import ssl
import pika
import json
import logging
from bson import ObjectId
from pika.exceptions import ConnectionClosedByBroker, AMQPConnectionError

# RabbitMQ connection parameters/URLS
def connection_rabbitMq():
    params = pika.URLParameters(os.environ.get('RABBITMQ_URL')) 
    connection = pika.BlockingConnection(params)
    channel = connection.channel()
    return channel

def publish(method, body):
    channel = connection_rabbitMq()
    # Convert ObjectId to string if found in the dictionary
    if isinstance(body, dict):
        body = {key: str(value) if isinstance(value, ObjectId) else value for key, value in body.items()}

    properties = pika.BasicProperties(type=method)

    try:
        # Publish the message to the 'django_app' queue
        channel.basic_publish(
            exchange='',
            routing_key='youtools_queue',
            body=json.dumps(body), 
            properties=properties 
        )
        print("Message published successfully")
    except (ConnectionClosedByBroker, AMQPConnectionError, ssl.SSLEOFError) as err:
            logging.error('Could not publish message to RabbitMQ: %s', err)
            # Reconnect to RabbitMQ
            channel = connection_rabbitMq()
    except pika.exceptions.AMQPError as err:
        # Handle errors in publishing messages
        print(f"Failed to publish message: {err}")