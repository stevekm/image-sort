#/usr/bin/env python
"""
Script to sort images based on HSV values (converted from RGB values)
"""
import os
import csv
import colorsys
from PIL import Image

def get_all_images():
    """
    Returns a list of all the image files at the assets location
    """
    all_images = []
    for root, dirs, files in os.walk("assets"):
        for file in files:
            if file.endswith(".jpg") and not file.endswith("thumbnail.jpg"):
                 all_images.append(os.path.join(root, file))
    return(all_images)

def get_img_avg_rgb(image):
    """
    Gets the average RGB of an image
    https://codegolf.stackexchange.com/questions/53621/force-an-average-on-an-image

    Parameters
    ----------
    image: str
        the path to an image file

    Returns
    -------
    list
        a list of three values; [r, g, b]


    Other resources
    ---------------
    http://pythonicprose.blogspot.com/2009/09/python-find-average-rgb-color-for-image.html
    https://www.hackzine.org/getting-average-image-color-from-python.html
    https://stackoverflow.com/questions/6208980/sorting-a-list-of-rgb-triplets-into-a-spectrum
    """
    img = Image.open(image).convert('RGB')
    pixels = img.load()
    avg = [0, 0, 0]
    for x in range(img.size[0]):
        for y in range(img.size[1]):
            for i in range(3):
                avg[i] += pixels[x, y][i]
    avg = tuple(c // (img.size[0] * img.size[1]) for c in avg)
    return(avg)

def save_all_image_data_csv(image_tups):
    """
    Saves a .csv file with the list of images and their RGB and HSV values

    Parameters
    ----------
    image_tups: list
        a list of tuples in the format [(filepath, (r, g, b), (h, s, v))]
    """
    output_file = "images.rgb.hsv.csv"
    with open(output_file, "w") as f:
        writer = csv.writer(f)
        for image_tup in image_tups:
            path = image_tup[0]
            rgb = image_tup[1]
            hsv = image_tup[2]
            red = rgb[0]
            green = rgb[1]
            blue = rgb[2]
            hue = hsv[0]
            saturation = hsv[1]
            value = hsv[2]
            writer.writerow([ path, red, green, blue, hue, saturation, value ])

def save_image_list_preview(images):
    """
    Create a horizontally concatenated filmstrip image of thumbnails of all the images

    Parameters
    ----------
    images: list
        a list of paths to image files


    https://stackoverflow.com/questions/30227466/combine-several-images-horizontally-with-python
    """
    new_images = []
    for image in images:
        resized = Image.open(image).resize((300, 300))
        new_images.append(resized)

    widths, heights = zip(*(i.size for i in new_images))
    total_width = sum(widths)
    max_height = max(heights)
    new_im = Image.new('RGB', (total_width, max_height))
    x_offset = 0
    for im in new_images:
        new_im.paste(im, (x_offset,0))
        x_offset += im.size[0]
    new_im.save('filmstrip.jpg')


def main():
    """
    Main control function for the program
    """
    # find all the images from the directory
    all_images = get_all_images()
    # get the RGB values for each image
    colors_rgb = [ (image, get_img_avg_rgb(image)) for image in all_images ]
    # add the converted HSV values
    colors_hsv = []
    for tup in colors_rgb:
        image = tup[0]
        rgb = tup[1]
        hsv = colorsys.rgb_to_hsv(*rgb)
        colors_hsv.append((image, rgb, hsv))
    # sort just by hue value
    colors_hsv = sorted(colors_hsv, key = lambda tup: tup[2][0])
    # save the list to a .csv file for browsing
    save_all_image_data_csv(colors_hsv)
    # create a horizontal concatenated image thumbnail
    save_image_list_preview([tup[0] for tup in colors_hsv])

if __name__ == '__main__':
    main()
