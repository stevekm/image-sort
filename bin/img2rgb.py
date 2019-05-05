#!/usr/bin/env python
"""
Convert a single image to a list of its unique RGB and HSV values
"""
import os
import csv
import argparse
import colorsys
from img import get_img_rgbs

def main(**kwargs):
    """
    Main control function for the program
    """
    input = kwargs.pop('input')[0] # list of input items
    input_path = os.path.realpath(input)
    output_file = kwargs.pop('output_file') # file to write sorted list to
    pixels = set((red, green, blue) for red, green, blue in get_img_rgbs(input_path))
    with open(output_file, "w") as f:
        writer = csv.writer(f)
        for red, green, blue in pixels:
            hue, saturation, value = colorsys.rgb_to_hsv(red, green, blue)
            writer.writerow([ red, green, blue, hue, saturation, value ])

def parse():
    """
    Parses script args
    """
    parser = argparse.ArgumentParser(
        description='Convert image to average RGB HSV values')
    parser.add_argument('input',
                        nargs=1,
                        help='Image file input')
    parser.add_argument("-o",
        default = "image.rgb.hsv.csv",
        dest = 'output_file',
        help = "Output file to write values to")

    args = parser.parse_args()

    main(**vars(args))

if __name__ == '__main__':
    parse()
