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
    """
    all_images = []
    with open(list_file) as f:
        for line in f:
            filepath = line.split(',')[0].strip()
            all_images.append(filepath)
    return(all_images)



def main(**kwargs):
    """
    Main control function for the program
    """
    input_file = kwargs.pop('input_file') # file with list of images
    output_file = kwargs.pop('output_file') # file to write sorted list to
    # x = int(kwargs.pop('x')) # file to write sorted list to
    # y = int(kwargs.pop('y')) # file to write sorted list to

    # get images from list file
    all_images = load_images_from_list(list_file = input_file)
    print(all_images)


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
    # parser.add_argument("-x",
    #     default = 300,
    #     dest = 'x',
    #     help = "Width of each image in filmstrip")
    # parser.add_argument("-y",
    #     default = 300,
    #     dest = 'y',
    #     help = "Height of each image in filmstrip")

    args = parser.parse_args()

    main(**vars(args))

if __name__ == '__main__':
    parse()
