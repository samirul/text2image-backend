"""
    Using celery task for genering images from text
    using pretrained stable-diffusion-v1-5 models from
    hugging face. After then saving results on MongoDB
    and converting to API using flask.
"""
import os
import uuid
import base64
from io import BytesIO
import torch
import time
from celery import shared_task
from diffusers import StableDiffusionPipeline
from api import text2image, cache
from api.producers import publish


@shared_task(ignore_result=False, bind=True)
def generate(self, text, payload):
    """Function for responsible executing celery task within class member.

    Raises:
        ValueError: raises payload error if user is not logged in before executing the task.
        ValueError: raises text error if required text is not provided before executing the task.

    Returns:
        returns: It execute and run task of text to images
        and save data on MongoDB and then returns Done, else will throw
        an exception.
    """
    try:
        self.update_state(state='PENDING', meta={'current': 0, 'total': 0})
        model = "sd-legacy/stable-diffusion-v1-5"
        pipe = StableDiffusionPipeline.from_pretrained(model, torch_dtype=torch.float16)
        trained_on = pipe.to("cuda")
        pipe.enable_model_cpu_offload()
        self.update_state(state='RUNNING', meta={'current': 1, 'total': 5})
        time.sleep(5)
        if not payload:
            raise ValueError("User is not logged in, not user information has been found.")
        if not text:
            raise ValueError("No text is found.")
        
        self.update_state(state='RUNNING', meta={'current': 2, 'total': 5})
        time.sleep(5)
        image = trained_on(text).images[0]
        text_splited = str(text).split()
        buffer = BytesIO()
        image.save(buffer, format="PNG")
        img = base64.b64encode(buffer.getvalue()).decode('utf-8')
        self.update_state(state='RUNNING', meta={'current': 3, 'total': 5})
        time.sleep(5)
        data = text2image.insert_one({'image_name': str(text), "image_data": img, 'mimeType': 'image/png' , "user_id": uuid.UUID(payload['user_id'])})
        cache.delete(f"text2image_all_data_{payload['user_id']}")
        inserted_id = data.inserted_id
        data_inserted = text2image.find_one({"_id": inserted_id})
        path = os.path.join('/vol/images/', f"result_txt_2_img_{'_'.join(text_splited)}_{inserted_id}.png")
        self.update_state(state='RUNNING', meta={'current': 4, 'total': 5})
        time.sleep(5)
        image.save(path)

        if isinstance(data_inserted["user_id"], uuid.UUID):
            data_inserted["user_id"] = str(data_inserted["user_id"])

        publish(method="created_new_image", body=data_inserted)
        self.update_state(state='RUNNING', meta={'current': 5, 'total': 5})
        time.sleep(2)
        return {'current': 100, 'total': 100, 'status': 'Task completed!'}
    except Exception as e:
        print(f"Something is Wrong: {e}")
        return e
        