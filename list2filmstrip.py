#!/usr/bin/env python
"""
Make a horizontal filmstrip image from thumbnails of all the images in the list file
"""
import os
import argparse
from PIL import Image

def load_images_from_list(list_file):
    """
    Load the file paths from the list file provided
    """
    all_images = []
    with open(list_file) as f:
        for line in f:
            filepath = line.split(',')[0].strip()
            all_images.append(filepath)
    return(all_images)

def save_image_list_preview(images, output_file, x = 300, y = 300):
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
        resized = Image.open(image).resize((x, y))
        new_images.append(resized)

    widths, heights = zip(*(i.size for i in new_images))
    total_width = sum(widths)
    max_height = max(heights)
    new_im = Image.new('RGB', (total_width, max_height))
    x_offset = 0
    for im in new_images:
        new_im.paste(im, (x_offset,0))
        x_offset += im.size[0]
    new_im.save(output_file)

def main(**kwargs):
    """
    Main control function for the program
    """
    input_file = kwargs.pop('input_file') # file with list of images
    output_file = kwargs.pop('output_file') # file to write sorted list to
    x = int(kwargs.pop('x')) # file to write sorted list to
    y = int(kwargs.pop('y')) # file to write sorted list to

    # get images from list file
    all_images = load_images_from_list(list_file = input_file)

    save_image_list_preview(
        images = all_images,
        output_file = output_file,
        x = x,
        y = y
        )

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
        default = "filmstrip.jpg",
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

    args = parser.parse_args()

    main(**vars(args))

if __name__ == '__main__':
    parse()
