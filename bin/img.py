#!/usr/bin/env python3
"""
Module with helper functions for image processing tasks

Notes
---------------
https://codegolf.stackexchange.com/questions/53621/force-an-average-on-an-image
http://pythonicprose.blogspot.com/2009/09/python-find-average-rgb-color-for-image.html
https://www.hackzine.org/getting-average-image-color-from-python.html
https://stackoverflow.com/questions/6208980/sorting-a-list-of-rgb-triplets-into-a-spectrum
"""
from __future__ import annotations # python 3.7+
import sys
import csv
from PIL import Image
import colorsys
from multiprocessing import Pool
from pathlib import Path
import argparse
from typing import Generator, Tuple, List, Dict

class Avg(object):
    """
    Holds the attributes of image's average RGB HSV values
    """
    def __init__(self,
            path: str = None,
            _verbose: bool = False,
            ignore_vals: List[Tuple[int, int, int]] = None,
            *args, **kwargs):
        if path:
            self.path = path
            avg = self.get_avg_rgb_hsv(
                path = self.path, _verbose = _verbose, ignore_vals = ignore_vals, *args, **kwargs)
            self.red = avg['red']
            self.green = avg['green']
            self.blue = avg['blue']
            self.hue = avg['hue']
            self.saturation = avg['saturation']
            self.value = avg['value']
            self.pixels_total = avg['pixels_total']
            self.pixels_counted = avg['pixels_counted']
            self.pixels_pcnt = avg['pixels_pcnt']

        # initialize empty attributes if using from_dict method
        else:
            self.path = None
            self.red = None
            self.green = None
            self.blue = None
            self.hue = None
            self.saturation = None
            self.value = None
            self.pixels_total = None
            self.pixels_counted = None
            self.pixels_pcnt = None

    @staticmethod
    def get_avg_rgb_hsv(
            path: str,
            _verbose: bool = False,
            ignore_vals: List[Tuple[int, int, int]] = None,
            *args, **kwargs) -> Dict:
        """
        Get the average RGB and HSV values from an image file path
        """
        # check if there are some pixels to ignore
        ignore_pixel_ids = set()
        if ignore_vals:
            for vals in ignore_vals:
                id = "{}.{}.{}".format(vals[0], vals[1], vals[2]) # RGB values
                ignore_pixel_ids.add(id)

        img = Image.open(path).convert('RGB')
        pixels = img.load()
        size_x = img.size[0]
        size_y = img.size[1]
        avg = {
            'red': 0,
            'green': 0,
            'blue': 0,
            'pixels_total' : size_x * size_y,
            'pixels_counted' : 0,
            'path': path
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
                if len(ignore_pixel_ids) > 0:
                    id = "{0}.{1}.{2}".format(red, green, blue)
                    if id not in ignore_pixel_ids:
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

    def to_dict(self):
        d = {
        'red': self.red,
        'green': self.green,
        'blue': self.blue,
        'hue': self.hue,
        'saturation': self.saturation,
        'value': self.value,
        'pixels_total': self.pixels_total,
        'pixels_counted': self.pixels_counted,
        'pixels_pcnt': self.pixels_pcnt,
        'path': self.path
        }
        return(d)

    def __repr__(self):
        r = 'Avg(' + 'path=' + self.path.__repr__()
        r += ')'
        return(r)

    @classmethod
    def from_dict(cls, d: Dict) -> Avg:
        """
        Return an Avg instance from a pre-made dict of values
        """
        avg = cls()
        attrs = ['path', 'red', 'green', 'blue', 'hue', 'saturation', 'value', 'pixels_total', 'pixels_counted', 'pixels_pcnt']
        for a in attrs:
            setattr(avg, a, d[a])
        return(avg)

    @classmethod
    def from_list(cls,
        paths: List,
        sort_key: str = "hue",
        parallel: int = 2,
        _verbose: bool = False,
        *args, **kwargs) -> List[Avg]:
        """
        Return a list of Avg objects by evaluating a list of paths in parallel
        """
        avgs = []
        # run in single-threaded mode
        if parallel == 1:
            for path in paths:
                avgs.append(cls.get_avg_rgb_hsv(path, *args, **kwargs))

        # run in multi-threaded mode
        else:
            pool = Pool(int(parallel))

            # generate the aysnc result instances
            results = []
            for path in paths:
                result = pool.apply_async(cls.get_avg_rgb_hsv, args=(path, *args), kwds=kwargs)
                results.append(result)

             # get each result
            for result in results:
                avg = result.get()
                avgs.append(avg)

        if sort_key:
            avgs = sorted(avgs, key = lambda avg: avg[sort_key])

        objs = []
        for avg in avgs:
            obj = cls().from_dict(avg)
            objs.append(obj)

        return(objs)

    @classmethod
    def from_dir(cls, dir: str, *args, **kwargs) -> List[Avg]:
        path = Path(dir)
        paths = [ p for p in path.glob('**/*') if p.is_file() ]
        avgs = Avg().from_list(paths = paths, *args, **kwargs)
        return(avgs)





# ~~~~~ CLI ~~~~~ #
# functions for running the module as a command line script
def print_from_path(
        path: str,
        output_file: str = '-',
        threads: int = 4,
        ignore_file: str = None,
        func = None):
    """
    Print image average RGB values to stdout or file
    """
    path = Path(path)
    avg_args = {}

    ignore_pixels = set()
    if ignore_file:
        # load the unique pixels from the file
        img = Image.open(ignore_file).convert('RGB')
        pixels = img.load()
        size_x = img.size[0]
        size_y = img.size[1]

        for x in range(img.size[0]): # iterate over all x pixels
            for y in range(img.size[1]): # iterate over all y pixels
                red = pixels[x, y][0]
                green = pixels[x, y][1]
                blue = pixels[x, y][2]
                ignore_pixels.add((red, green, blue))

    if ignore_pixels:
        avg_args['ignore_vals'] = ignore_pixels

    if not path.exists():
        print(">>> ERROR: path does not exist: " + str(path))
        raise

    if path.is_dir():
        avgs = Avg().from_dir(dir = path, parallel = int(threads), **avg_args)
        dicts = [avg.to_dict() for avg in avgs]

    if path.is_file():
        avg = Avg(path = path, **avg_args)
        dicts = [avg.to_dict()]

    if output_file == '-':
        fout = sys.stdout # with open(sys.stdout) as fout:
    else:
        fout = open(output_file, "w")
    fieldnames = dicts[0].keys()
    writer = csv.DictWriter(fout, fieldnames = fieldnames)
    writer.writeheader()
    for d in dicts:
        writer.writerow(d)

    fout.close()


def main():
    """
    Main control function for running the module from command line
    """
    # top level CLI arg parser; args common to all output files go here
    parser = argparse.ArgumentParser(description = '')

    # add sub-parsers for specific file outputs
    subparsers = parser.add_subparsers(help ='Sub-commands available')
    _print = subparsers.add_parser('print', help = 'Print sorted image data to console')
    _print.add_argument(dest = 'path', help = 'Input path to file or dir to print data for')
    _print.add_argument('--output', dest = 'output_file', default = "-", help = 'The name of the output file')
    _print.add_argument('--threads', dest = 'threads', default = 4, help = 'Number of files to process in parallel')
    _print.add_argument('--ignore', dest = 'ignore_file', default = None, help = 'File with pixels that should be ignored when calculating averages')
    _print.set_defaults(func = print_from_path)
    """
    $ bin/img.py print assets/ --threads 6 --ignore ignore-pixels-white.jpg
    """

    args = parser.parse_args()
    args.func(**vars(args))

if __name__ == '__main__':
    main()
