#!/usr/bin/env python
"""
"""
from PIL import Image

def get_img_rgbs(image):
    """
    Get the RGB values for every pixel in an image
    """
    img = Image.open(image).convert('RGB')
    pixels = img.load()
    for x in range(img.size[0]):
        for y in range(img.size[1]):
            yield(pixels[x, y])


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
