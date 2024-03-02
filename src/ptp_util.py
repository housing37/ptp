
# imports
from openai import OpenAI  # OpenAI Python library to make API calls
# import requests  # used to download images
import os  # used to access filepaths
from PIL import Image  # used to print and edit images
from _env import env

client = OpenAI(api_key=env.OPENAI_KEY)

def gen_img_mask(image_dir'./'):
    # create a mask
    width = 1024
    height = 1024
    mask = Image.new("RGBA", (width, height), (0, 0, 0, 1))  # create an opaque image mask

    # set the bottom half to be transparent
    for x in range(width):
        for y in range(height // 2, height):  # only loop over the bottom half of the mask
            # set alpha (A) to zero to turn pixel transparent
            alpha = 0
            mask.putpixel((x, y), (0, 0, 0, alpha))

    # save the mask
    mask_name = "bottom_half_mask.png"
    mask_filepath = os.path.join(image_dir, mask_name)
    mask.save(mask_filepath)
    return mask, mask_filepath


def edit_img():
    # edit an image

    # call the OpenAI API
    edit_response = client.images.edit(
        image=open(generated_image_filepath, "rb"),  # from the generation section
        mask=open(mask_filepath, "rb"),  # from right above
        prompt=prompt,  # from the generation section
        n=1,
        size="1024x1024",
        response_format="url",
    )

    # print response
    print(edit_response)