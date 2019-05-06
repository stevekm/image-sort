#!/usr/bin/env python
"""
Makes thumbnails from all images in the supplied .csv file
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

def make_thumbnails(input_files, output_dir, x, y, bar_height):
    """
    """
    img_width = x
    img_height = y

    num_images = len(input_files)
    for i, input_image in enumerate(input_files):
        output_path = os.path.realpath(os.path.join(output_dir, str(i + 1) + '.jpg'))
        red = input_image['red']
        blue = input_image['blue']
        green = input_image['green']
        img_path = input_image['path']
        rgb = (red, blue, green)

        # start collage canvas
        canvas_size = (img_width, img_height + bar_height)
        canvas = Image.new('RGB', canvas_size, rgb)

        # load image
        image = Image.open(img_path).resize((img_width, img_height), Image.ANTIALIAS)
        # add to canvas
        canvas.paste(image, (0, 0))

        canvas.save(output_path)

def main(**kwargs):
    """
    Main control function for the program
    """
    input_file = kwargs.pop('input_file') # file with list of images
    output_dir = kwargs.pop('output_dir') # file to write sorted list to
    x = int(kwargs.pop('x')) # Width of each image
    y = int(kwargs.pop('y')) # Height of each image

    # get images from list file
    all_images = load_images_from_list(list_file = input_file)

    make_thumbnails(input_files = all_images,
        output_dir = output_dir,
        x = x,
        y = y,
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
        default = "output",
        dest = 'output_dir',
        help = "Output directory")
    parser.add_argument("-x",
        default = 300,
        dest = 'x',
        help = "Width of each thumbnail")
    parser.add_argument("-y",
        default = 300,
        dest = 'y',
        help = "Height of each thumbnail")

    args = parser.parse_args()

    main(**vars(args))

if __name__ == '__main__':
    parse()
