#!/usr/bin/env python
"""
Makes a collage from image thumbnails loaded from the list
"""
import os
import argparse
from PIL import Image

def load_images_from_list(list_file):
    """
    Load the file paths from the list file provided

    Returns
    -------
    list
        a list of input image file paths
    """
    all_images = []
    with open(list_file) as f:
        for line in f:
            filepath = line.split(',')[0].strip()
            all_images.append(filepath)
    return(all_images)

def make_collage(input_files, output_file, x, y, ncol):
    """
    Make a collage image out of the supplied input image

    Parameters
    ----------
    input_files: list
        a list of file paths for input images
    output_file: str
        file path to output image location
    x: int
        number of pixels for the width to resize each input image to in the collage
    y: int
        number of pixels for the height to resize each input image to in the collage
    ncol: int
        number of columns to arrange the input images in for the collage

    Adapted from https://github.com/fwenzel/collage
    """
    # get configuration for the output collage
    num_input_images = len(input_files)
    img_width = x
    img_height = y
    num_rows = num_input_images // ncol + (1 if num_input_images % ncol else 0)
    canvas_width = img_width * ncol
    canvas_height = img_height * num_rows
    canvas_size = (canvas_width, canvas_height)

    # start collage canvas
    canvas = Image.new('RGB', canvas_size, "black")

    # add each image to the collage canvas
    img_num = 0
    for input_image in input_files:
        position = img_num
        x = position % ncol
        y = position // ncol
        xoff = x * img_width
        yoff = y * img_height

        # load the input image and resize
        image = Image.open(input_image).resize((img_width, img_height), Image.ANTIALIAS)

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
        ncol = ncol)

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
