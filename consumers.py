
"""
    Function for Saving user information in MongoDB using RabbitMq
"""

import json
import os
import pika
from pika.exceptions import AMQPConnectionError
from bson import ObjectId
from api import user, text2image, cache
from delete_images.delete import delete_data_from_media_container

# RabbitMQ connection parameters
params = pika.URLParameters(os.environ.get('RABBITMQ_URL'))


def connect_consumer():
    """This function will Connect to the RabbitMQ Queue
        and then will get messages from the youtools
        producer. Tasks will get executed based on events
        and result will save on the mongoDB database.
    """
    # Establish connection
    try:
        connection = pika.BlockingConnection(params)
        channel = connection.channel()
        channel.queue_declare(queue='send_data_text2image')

        def callback(ch, method, properties, body):
            """Responsible for getting properties type and
                json data from producer and execute it in current consumer. 

            Args:
                ch (Parameter): Not used but needed.
                method (Parameter): Not used but needed.
                properties (Parameter): for getting properties type so can execute.
                specific task needed from producer to consumer.
                body (Parameter): json data from the producer.
            """
            try:
                print("message receiving....")
                if properties.type == 'user_is_created':
                    print("Task executing, please wait....")
                    data = json.loads(body)
                    user.insert_one({'_id': data['id'], 'username': data['username'], 'email': data['email']})
                    print("User inserted successfully")

                if properties.type == 'delete_images_from_database':
                    print("Task executing, please wait....")
                    try:
                        ids = json.loads(body)
                        if text2image.find_one({'_id': ObjectId(str(ids))}) is None:
                            print(f"Images {ids} is not found or successfully deleted from admin panel.")
                        else:
                            image = text2image.find_one({'_id': ObjectId(str(ids))})
                            image_name = str(image['image_name']).split()
                            image_name_joined = "_".join(image_name)
                            delete_data_from_media_container(f"/vol/images/result_txt_2_img_{image_name_joined}_{ids}.png")
                            text2image.delete_one({'_id': ObjectId(str(ids))})
                            cache.delete(f"text2image_all_data_{image['user_id']}")
                            print("Image deleted successfully")
                    except Exception as e:
                        print(f"Something is wrong: {e}")

            
            except Exception as e:
                # Log or handle errors during message processing
                print(f"Error processing message: {e}")

        # Start consuming messages from 'django_app' queue
        channel.basic_consume(queue='send_data_text2image', on_message_callback=callback, auto_ack=True)
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