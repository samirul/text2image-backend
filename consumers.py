
'''
    Function for Saving user information in MongoDB using RabbitMq
'''

import json
import os
import pika
from pika.exceptions import AMQPConnectionError
from api import user

# RabbitMQ connection parameters
params = pika.URLParameters(os.environ.get('RABBITMQ_URL'))


def connect_consumer():
    '''
        Connect to RabbitMQ Queue and get message from producers 
        for saving user information from other apps
    '''
    # Establish connection
    try:
        connection = pika.BlockingConnection(params)
        channel = connection.channel()
        channel.queue_declare(queue='send_data_flasks')

        def callback(ch, method, properties, body):
            try:
                print("message receiving....")
                if properties.type == 'user_is_created':
                    print("Task executing, please wait....")
                    data = json.loads(body)
                    user.insert_one({'_id': data['id'], 'username': data['username'], 'email': data['email']})
                    print("User inserted successfully")
            
            except Exception as e:
                # Log or handle errors during message processing
                print(f"Error processing message: {e}")

        # Start consuming messages from 'django_app' queue
        channel.basic_consume(queue='send_data_flasks', on_message_callback=callback, auto_ack=True)
        print('Waiting for messages....')
        channel.start_consuming()

    except AMQPConnectionError as e:
        print(f"Failed to connect to RabbitMQ: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")

    finally:
        # Ensure the channel and connection are closed if they were opened
        if 'channel' in locals() and channel.is_open:
            channel.close()
        if 'connection' in locals() and connection.is_open:
            connection.close()


if __name__ == '__main__':
    connect_consumer()