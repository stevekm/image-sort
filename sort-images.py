#!/usr/bin/env python
"""
Script to sort images based on HSV values (converted from RGB values)

Outputs a .csv file with the images in order of Hue value

https://www.alanzucconi.com/2015/09/30/colour-sorting/
"""
import os
import csv
import argparse
import colorsys
from PIL import Image

allowed_extensions = [".jpg"]

def get_images(input_dir):
    """
    Returns a list of all the image files in a directory
    """
    all_images = []
    for root, dirs, files in os.walk(input_dir):
        for file in files:
            filename, file_extension = os.path.splitext(file)
            if file_extension in allowed_extensions:
                 all_images.append(os.path.join(root, file))
    return(all_images)

def get_all_images(inputs):
    """
    Get all the unique images in the list of images and directories
    """
    all_images = []

    for item in inputs:
        if os.path.isdir(item):
            dir_images = get_images(input_dir = item)
            for image in dir_images:
                all_images.append(image)
        else:
            filename, file_extension = os.path.splitext(item)
            if file_extension in allowed_extensions:
                 all_images.append(item)

    all_images = list(set(all_images))
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

def save_all_image_data_csv(image_tups, output_file):
    """
    Saves a .csv file with the list of images and their RGB and HSV values

    Parameters
    ----------
    image_tups: list
        a list of tuples in the format [(filepath, (r, g, b), (h, s, v))]
    """
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

def main(**kwargs):
    """
    Main control function for the program
    """
    input = kwargs.pop('input') # list of input items
    output_file = kwargs.pop('output_file') # file to write sorted list to

    # find all the images from the directory
    all_images = get_all_images(inputs = input)

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

    # save the list to a .csv file
    save_all_image_data_csv(image_tups = colors_hsv, output_file = output_file)

def parse():
    """
    Parses script args
    """
    parser = argparse.ArgumentParser(
        description='Sort images based on RGB HSV values')
    parser.add_argument('input',
                        nargs="+",
                        help='Images or directories to file images in')
    parser.add_argument("-o",
        default = "images.rgb.hsv.csv",
        dest = 'output_file',
        help = "Output file")

    args = parser.parse_args()

    main(**vars(args))

if __name__ == '__main__':
    parse()
