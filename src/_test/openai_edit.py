# imports
from openai import OpenAI  # OpenAI Python library to make API calls
import requests  # used to download images
import os  # used to access filepaths
from PIL import Image  # used to print and edit images
from _env import env
# initialize OpenAI client
client = OpenAI(api_key=env.OPENAI_KEY)

#===================================================
# set a directory to save DALL·E images to
image_dir_name = "images"
image_dir = os.path.join(os.curdir, image_dir_name)

# create the directory if it doesn't yet exist
if not os.path.isdir(image_dir):
    os.mkdir(image_dir)

# print the directory to save to
print(f"Created / set save directory: {image_dir=}")

#===================================================
# create an image

# set the prompt
# prompt = "A cyberpunk monkey hacker dreaming of a beautiful bunch of bananas, digital art"
prompt = input('\n Enter image description to generate:\n > ')
print(f' prompt: {prompt}')
print('\nGenerating image...')
# call the OpenAI API
generation_response = client.images.generate(
    model = "dall-e-3",
    prompt=prompt,
    n=1,
    size="1024x1024",
    response_format="url",
)

# print response
# print(generation_response)
print('Generating image... DONE')
#===================================================
# save the image
# generated_image_name = "generated_image.png"  # any name you like; the filetype should be .png
generated_image_name = input('\n Enter image file to save to:\n > ')
print(f' file name: {generated_image_name}')
print('\nSaving file...')
generated_image_filepath = os.path.join(image_dir, generated_image_name)
generated_image_url = generation_response.data[0].url  # extract image URL from response
generated_image = requests.get(generated_image_url).content  # download the image

with open(generated_image_filepath, "wb") as image_file:
    image_file.write(generated_image)  # write the image to the file
print('Saving file... DONE')
#===================================================
# print the image
print(f'\ngenerated_image_filepath (OG): '+generated_image_filepath)
print('Opening OG image...')
Image.open(generated_image_filepath).show()
# display(Image.open(generated_image_filepath))


#===================================================
if False:
    var_cnt = 4
    print(f"\nCreating variations x{var_cnt} ...")
    # create variations

    # call the OpenAI API, using `create_variation` rather than `create`
    variation_response = client.images.create_variation(
        image=generated_image,  # generated_image is the image generated above
        n=var_cnt,
        size="1024x1024",
        response_format="url",
    )

    # print response
    # print(variation_response)
    print(f"Creating variations x{var_cnt} ... DONE")

    #===================================================
    # save the images
    print(f'\nSaving variations x{var_cnt} ...')
    variation_urls = [datum.url for datum in variation_response.data]  # extract URLs
    variation_images = [requests.get(url).content for url in variation_urls]  # download images
    variation_image_names = [f"variation_image_{i}.png" for i in range(len(variation_images))]  # create names
    variation_image_filepaths = [os.path.join(image_dir, name) for name in variation_image_names]  # create filepaths
    for image, filepath in zip(variation_images, variation_image_filepaths):  # loop through the variations
        with open(filepath, "wb") as image_file:  # open the file
            image_file.write(image)  # write the image to the file
    print(f'Saving variations x{var_cnt} ... DONE')

    #===================================================
    # print the original image
    # print(generated_image_filepath)
    # Image.open(generated_image_filepath).show()
    # display(Image.open(generated_image_filepath))

    # print the new variations
    print(f'printing variation_image_filepaths x{len(variation_image_filepaths)} ... ')
    for variation_image_filepaths in variation_image_filepaths:
        print(variation_image_filepaths)
        # Image.open(variation_image_filepaths).show()
        # display(Image.open(variation_image_filepaths))

#===================================================
print('\nCreating mask ...')
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
print(f'Saved mask: {mask_filepath}')

#===================================================
edit_prompt = input(f' Enter edit description to append:\n > ')
new_prompt = f'{prompt}. {edit_prompt}'
print(f' edit_prompt: {edit_prompt}')
print('\nEditing image ... (w/ OG and mask and prompts)')
print(f'      OG: {generated_image_filepath}')
print(f'    mask: {mask_filepath}')
print(f' OG prompt:\n  {prompt}')
print(f' edit_prompt:\n  {edit_prompt}')
print(f' new_prompt:\n  {new_prompt}')

# edit an image

# call the OpenAI API
edit_response = client.images.edit(
    image=open(generated_image_filepath, "rb"),  # from the generation section
    mask=open(mask_filepath, "rb"),  # from right above
    prompt=new_prompt,  # from the generation section
    n=1,
    size="1024x1024",
    response_format="url",
)

# print response
# print(edit_response)
print('Editing image ... (w/ OG and mask and prompts) _ DONE')

#===================================================
print('\nSaving edited image ...')
# save the image
edited_image_name = "edited_image.png"  # any name you like; the filetype should be .png
edited_image_filepath = os.path.join(image_dir, edited_image_name)
edited_image_url = edit_response.data[0].url  # extract image URL from response
edited_image = requests.get(edited_image_url).content  # download the image

with open(edited_image_filepath, "wb") as image_file:
    image_file.write(edited_image)  # write the image to the file

print(f'        OG image: {generated_image_filepath}')
print(f'    edited image: {edited_image_filepath}')

print('Saving edited image ... DONE')
#===================================================
# print('Opening OG image...')
print('Opening edited image...')
# print the original image
# print(f'OG image: {generated_image_filepath}')
# Image.open(generated_image_filepath).show()
# display(Image.open(generated_image_filepath))

# print edited image
# print(f'edited image: {edited_image_filepath}')
Image.open(edited_image_filepath).show()
# display(Image.open(edited_image_filepath))
print('__END__')