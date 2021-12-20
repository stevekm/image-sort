#!/usr/bin/env python
"""
Makes a collage from image thumbnails loaded from the list
"""
import os
import csv
import argparse
from PIL import Image

def load_images_from_list(list_file):
    """
    Load the file paths from the list file provided

    Returns
    -------
    list
        a list of dicts
    """
    all_images = []
    with open(list_file, "rU") as f:
        reader = csv.DictReader(f, delimiter = ',')
        for row in reader:
            d = {}
            d['path'] = row['path']
            d['red'] = int(row['red'])
            d['blue'] = int(row['blue'])
            d['green'] = int(row['green'])
            d['hue'] = row['hue']
            d['saturation'] = row['saturation']
            d['value'] = row['value']
            all_images.append(d)
    return(all_images)

def make_collage(input_files, output_file, x, y, ncol, bar_height):
    """
    Make a collage image out of the supplied input image

    Parameters
    ----------
    input_files: list
        a list of dicts with image paths and metrics
    output_file: str
        file path to output image location
    x: int
        number of pixels for the width to resize each input image to in the collage
    y: int
        number of pixels for the height to resize each input image to in the collage
    ncol: int
        number of columns to arrange the input images in for the collage
    bar_height: int
        number of pixels for color bar height

    Adapted from https://github.com/fwenzel/collage
    """
    # get configuration for the output collage
    num_input_images = len(input_files)
    img_width = x
    img_height = y
    img_height_padded = y + bar_height
    num_rows = num_input_images // ncol + (1 if num_input_images % ncol else 0)
    canvas_width = img_width * ncol
    canvas_height = img_height_padded * num_rows
    canvas_size = (canvas_width, canvas_height)

    # start collage canvas
    canvas = Image.new('RGB', canvas_size, "black")

    # add each image to the collage canvas
    img_num = 0
    for input_image in input_files:
        img_path = input_image['path']
        red = input_image['red']
        blue = input_image['blue']
        green = input_image['green']
        hue = input_image['hue']
        saturation = input_image['saturation']
        value = input_image['value']
        rgb = (red, blue, green)

        position = img_num
        # line up top-left corner of image placement based on image number
        x = position % ncol
        y = position // ncol
        xoff = x * img_width
        yoff = y * img_height_padded

        # load the input image and resize
        image = Image.open(img_path).resize((img_width, img_height), Image.ANTIALIAS)

        # place color bar on the canvas
        bar_coord = (xoff, yoff, xoff + img_width, yoff + img_height + bar_height)
        canvas.paste(rgb, bar_coord)

        # Place tile on canvas.
        canvas.paste(image, (xoff, yoff))

        img_num += 1

    # save canvas
    canvas.save(output_file)

def main(**kwargs):
    """
    Main control function for the program
    """
    input_file = kwargs.pop('input_file') # file with list of images
    output_file = kwargs.pop('output_file') # file to write sorted list to
    x = int(kwargs.pop('x')) # Width of each image in filmstrip
    y = int(kwargs.pop('y')) # Height of each image in filmstrip
    ncol = int(kwargs.pop('ncol')) # Number of columns in the collage

    # get images from list file
    all_images = load_images_from_list(list_file = input_file)

    make_collage(input_files = all_images,
        output_file = output_file,
        x = x,
        y = y,
        ncol = ncol,
        bar_height = 50)

def parse():
    """
    Parses script args
    """
    parser = argparse.ArgumentParser(
        description='Generate filmstrip from list of images')
    parser.add_argument("-i",
        default = "images.rgb.hsv.csv",
        dest = 'input_file',
        help = "Input list file")
    parser.add_argument("-o",
        default = "collage.jpg",
        dest = 'output_file',
        help = "Output file")
    parser.add_argument("-x",
        default = 300,
        dest = 'x',
        help = "Width of each image in filmstrip")
    parser.add_argument("-y",
        default = 300,
        dest = 'y',
        help = "Height of each image in filmstrip")
    parser.add_argument("--ncol",
        default = 8,
        dest = 'ncol',
        help = "Number of columns in the collage")

    args = parser.parse_args()

    main(**vars(args))

if __name__ == '__main__':
    parse()
