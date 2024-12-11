import os
import torch
import base64 
from io import BytesIO
from celery import shared_task
from diffusers import StableDiffusionPipeline
from api import text2image
from api.producers import publish

class Text2Image:
    def __init__(self, text, payload):
        self.model = "runwayml/stable-diffusion-v1-5"
        self.pipe = StableDiffusionPipeline.from_pretrained(self.model, torch_dtype=torch.float16)
        self.trained_on = self.pipe.to("cuda")
        self.text = text
        self.payload = payload

    def generate(self):
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
            data = text2image.insert_one({'image_name': str(self.text), "image_data": img, "user_id": self.payload['user_id']})
            inserted_id = data.inserted_id
            data_inserted = text2image.find_one({"_id": inserted_id})
            publish(method="created_new_image", body=data_inserted)
            path = os.path.join('images', f"result_txt_2_img_{'_'.join(text)}.png")
            image.save(path)
            return "Done"
        except Exception as e:
            print(f"Something is Wrong: {e}")
            return e
        
@shared_task(ignore_result=False)
def task_generate(text, payload):
    txt2img = Text2Image(text=text, payload=payload)
    return txt2img.generate()