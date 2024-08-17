import torch
from celery import shared_task
from diffusers import StableDiffusionPipeline


class Text2Image:
    def __init__(self, text):
        self.model = "runwayml/stable-diffusion-v1-5"
        self.pipe = StableDiffusionPipeline.from_pretrained(self.model, torch_dtype=torch.float16)
        self.trained_on = self.pipe.to("cuda")
        self.text = text

    def generate(self):
        image = self.trained_on(self.text).images[0]
        text = str(self.text).split()
        return image.save(f"result_txt_2_img_{'_'.join(text)}.png")
        
@shared_task(ignore_result=False)
def task_generate(text):
    txt2img = Text2Image(text)
    return txt2img.generate()