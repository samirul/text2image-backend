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
from celery import shared_task
from diffusers import StableDiffusionPipeline
from api import text2image
from api.producers import publish

class Text2Image:
    """Intializing some required parameters"""
    def __init__(self, text, payload):
        self.model = "sd-legacy/stable-diffusion-v1-5"
        self.pipe = StableDiffusionPipeline.from_pretrained(self.model, torch_dtype=torch.float16)
        self.trained_on = self.pipe.to("cuda")
        self.text = text
        self.payload = payload

    def generate(self):
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
            if not self.payload:
                raise ValueError("User is not logged in, not user information has been found.")
            if not self.text:
                raise ValueError("No text is found.")
            image = self.trained_on(self.text).images[0]
            text = str(self.text).split()
            buffer = BytesIO()
            image.save(buffer, format="PNG")
            img = base64.b64encode(buffer.getvalue()).decode('utf-8')
            data = text2image.insert_one({'image_name': str(self.text), "image_data": img, "user_id": uuid.UUID(self.payload['user_id'])})
            inserted_id = data.inserted_id
            data_inserted = text2image.find_one({"_id": inserted_id})
            path = os.path.join('images', f"result_txt_2_img_{'_'.join(text)}.png")
            image.save(path)

            if isinstance(data_inserted["user_id"], uuid.UUID):
                data_inserted["user_id"] = str(data_inserted["user_id"])

            publish(method="created_new_image", body=data_inserted)
            return "Done"
        except Exception as e:
            print(f"Something is Wrong: {e}")
            return e
        
@shared_task(ignore_result=False)
def task_generate(text, payload):
    """Function for warping up celery "shared_task" for excecuting celery task

    Args:
        text (String): Information we send to the model for generate related image from the text.
        payload (auth, sting, uuid): Getting user id from the access token after login from django
        application youtools.

    Returns:
        Returns: Return done if task run successfully, else will thow error if task failed to execute.
    """
    try:
        txt2img = Text2Image(text=text, payload=payload)
        txt2img.generate()
        return "Done"
    except Exception as e:
        print(f"Something is Wrong ->: {e}")
        return e