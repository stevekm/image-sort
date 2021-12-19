#!/usr/bin/env python3
"""
Module with helper functions for image processing tasks
"""
import csv
from PIL import Image
import colorsys
from multiprocessing import Pool
from typing import Generator, Tuple, List, Dict

def get_img_rgbs(image: str) -> Generator[Tuple[int, int, int], None, None]:
    """
    Get the RGB values for every pixel in an image

    Usage
    -----
        pixels = [(red, green, blue) for red, green, blue in get_img_rgbs("color.jpg")]
    """
    img = Image.open(image).convert('RGB')
    pixels = img.load()
    for x in range(img.size[0]):
        for y in range(img.size[1]):
            yield(pixels[x, y])

def get_img_rbg_hsv(
    image: str
    ) -> Generator[Tuple[int, int, int, float, float, int], None, None]:
    """
    Get the RGB and HSV values for every pixel in an image

    Usage
    -----
        pixels = [(red, green, blue, hue, saturation, value) for red, green, blue, hue, saturation, value in get_img_rbg_hsv("color.jpg")]
    """
    for red, green, blue in get_img_rgbs(image):
        hue, saturation, value = colorsys.rgb_to_hsv(red, green, blue)
        yield(red, green, blue, hue, saturation, value)

def load_csv_rgbhsv(
    input_path: str
    ) -> List[Tuple[str, str, str, str, str, str]]:
    """
    Load the RGB and HSV values from a .csv file

    TODO: deprecate this !!
    """
    pixels = []
    with open(input_path) as f:
        reader = csv.reader(f)
        for row in reader:
            red = row[0]
            green = row[1]
            blue = row[2]
            hue = row[3]
            saturation = row[4]
            value = row[5]
            pixels.append((red, green, blue, hue, saturation, value))
    return(pixels)


def get_img_avg_rgb(
    image: str,
    ignore: str = None,
    _verbose: bool = True
    ) -> Dict:
    """
    Gets the average RGB of an image

    Notes
    ---------------
    https://codegolf.stackexchange.com/questions/53621/force-an-average-on-an-image
    http://pythonicprose.blogspot.com/2009/09/python-find-average-rgb-color-for-image.html
    https://www.hackzine.org/getting-average-image-color-from-python.html
    https://stackoverflow.com/questions/6208980/sorting-a-list-of-rgb-triplets-into-a-spectrum
    """
    ignore_pixels = set()
    if ignore != None:
        ignore_pixels_list = load_csv_rgbhsv(input_path = ignore)
        ignore_pixels_list = [ (tup[0], tup[1], tup[2]) for tup in ignore_pixels_list ]
        for tup in ignore_pixels_list:
            id = "{0}{1}{2}".format(tup[0], tup[1], tup[2])
            ignore_pixels.add(id)
        if _verbose:
            print("Loaded {0} ignore pixels".format(len(ignore_pixels)))
    img = Image.open(image).convert('RGB')
    pixels = img.load()
    size_x = img.size[0]
    size_y = img.size[1]
    avg = {
        'red': 0,
        'green': 0,
        'blue': 0,
        'pixels_total' : size_x * size_y,
        'pixels_counted' : 0
        }

    if _verbose:
        print("Loaded image: {0} total pixels".format(avg['pixels_total']))

    # add up the RGB values for all pixels
    for x in range(img.size[0]): # iterate over all x pixels
        for y in range(img.size[1]): # iterate over all y pixels
            red = pixels[x, y][0]
            green = pixels[x, y][1]
            blue = pixels[x, y][2]

            # skip the pixel if it matches one of the ignored pixels
            if len(ignore_pixels) > 0:
                id = "{0}{1}{2}".format(red, green, blue)
                if id not in ignore_pixels:
                    avg['red'] += red
                    avg['green'] += green
                    avg['blue'] += blue
                    avg['pixels_counted'] += 1
            else:
                avg['red'] += red
                avg['green'] += green
                avg['blue'] += blue
                avg['pixels_counted'] += 1
    # calculate averages
    avg['red'] = avg['red'] // avg['pixels_counted']
    avg['green'] = avg['green'] // avg['pixels_counted']
    avg['blue'] = avg['blue'] // avg['pixels_counted']

    # convert to HSV
    hue, saturation, value = colorsys.rgb_to_hsv(avg['red'], avg['green'], avg['blue'])
    avg['hue'] = hue
    avg['saturation'] = saturation
    avg['value'] = value

    # calculate percent
    avg['pixels_pcnt'] = round((float(avg['pixels_counted']) / float(avg['pixels_total'])) * 100, 1)

    return(avg)


def get_avgs(
        images: List[str],
        sort_key: str = "hue",
        parallel: int = 1,
        *args,
        **kwargs) -> List[Dict]:
    """
    Get the average RBG HSV values for all the images
    """
    avgs = []
    # run in single-threaded mode
    if parallel == 1:
        for image in images:
            avgs.append(get_img_avg_rgb(image, *args, **kwargs))

    # run in multi-threaded mode
    else:
        pool = Pool(int(parallel))

        # generate the aysnc result instances
        results = []
        for image in images:
            result = pool.apply_async(get_img_avg_rgb, args=(image, *args), kwds=kwargs)
            result_tup = (image, result)
            results.append(result_tup)

         # get each result
        for result_tup in results:
            image, result = result_tup
            avg = result.get()
            avgs.append(avg)

    if sort_key:
        avgs = sorted(avgs, key = lambda avg: avg[sort_key])

    return(avgs)
