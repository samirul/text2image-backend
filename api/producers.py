"""
    For sending messages to consumers of other apps using RabbitMQ
"""

import os
import ssl
import json
import logging
import pika
from bson import ObjectId
from pika.exceptions import ConnectionClosedByBroker, AMQPConnectionError

# RabbitMQ connection parameters/URLS
def connect():
    """For Connecting to RabbitMQ server and channel

    Returns:
        return: channel for make connections.
    """
    params = pika.URLParameters(os.environ.get('RABBITMQ_URL')) 
    connection = pika.BlockingConnection(params)
    channel = connection.channel()
    return channel

def publish(method, body):
    """Once connected to RabbitMq server then send the messages to consumers
        for saving generated images information to other app

    Args:
        method (string): Send custom string for identifying data by consumer.
        body (_type_): Sending json type body data to consumer.
    """
    channel = connect()
    # Convert ObjectId to string if found in the dictionary
    if isinstance(body, dict):
        body = {key: str(value) if isinstance(value, ObjectId) else value for key, value in body.items()}

    properties = pika.BasicProperties(type=method)

    try:
        # Publish the message to the 'django_app' queue
        channel.basic_publish(
            exchange='',
            routing_key='youtools-queue_text2image',
            body=json.dumps(body), 
            properties=properties 
        )
        print("Message published successfully")
    except (ConnectionClosedByBroker, AMQPConnectionError, ssl.SSLEOFError) as err:
            logging.error('Could not publish message to RabbitMQ: %s', err)
            # Reconnect to RabbitMQ
            channel = connect()
    except pika.exceptions.AMQPError as err:
        # Handle errors in publishing messages
        print(f"Failed to publish message: {err}")