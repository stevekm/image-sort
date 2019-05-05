#!/usr/bin/env python
"""
Script to convert an image file to RGB and HSL values
"""
import os
import csv
import argparse
import colorsys
from PIL import Image
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

def main(**kwargs):
    """
    Main control function for the program
    """
    input = kwargs.pop('input')[0] # list of input items
    input_path = os.path.realpath(input)
    output_file = kwargs.pop('output_file') # file to write sorted list to
    red, green, blue = get_img_avg_rgb(input_path)
    hue, saturation, value = colorsys.rgb_to_hsv(red, green, blue)
    with open(output_file, "w") as f:
        writer = csv.writer(f)
        writer.writerow([ input_path, red, green, blue, hue, saturation, value ])


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
        help = "Output file")

    args = parser.parse_args()

    main(**vars(args))

if __name__ == '__main__':
    parse()
