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
import os
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
        paths: List[str],
        sort_key: str = "hue",
        threads: int = 2,
        _verbose: bool = False,
        *args, **kwargs) -> List[Avg]:
        """
        Return a list of Avg objects by evaluating a list of paths in parallel
        """
        avgs = []
        # run in single-threaded mode
        if threads == 1:
            for path in paths:
                avgs.append(cls.get_avg_rgb_hsv(path, *args, **kwargs))

        # run in multi-threaded mode
        else:
            pool = Pool(int(threads))

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

    @classmethod
    def from_csv(cls, csv_file: str) -> List[Avg]:
        int_attrs = ['red', 'green', 'blue', 'value', 'pixels_total', 'pixels_counted' ]
        float_attrs = ['hue', 'saturation', 'pixels_pcnt']
        avgs = []
        with open(csv_file, "r") as f:
            reader = csv.DictReader(f, delimiter = ',')
            for row in reader:
                for key in int_attrs:
                    row[key] = int(row[key])
                for key in float_attrs:
                    row[key] = float(row[key])
                avgs.append(cls.from_dict(row))
        return(avgs)






# ~~~~~ CLI ~~~~~ #
# functions for running the module as a command line script
def load_all_pixels(path: str) -> List[Tuple[int, int, int]]:
    all_pixels = []
    # load the unique pixels from the file
    img = Image.open(path).convert('RGB')
    pixels = img.load()
    size_x = img.size[0]
    size_y = img.size[1]

    for x in range(img.size[0]): # iterate over all x pixels
        for y in range(img.size[1]): # iterate over all y pixels
            red = pixels[x, y][0]
            green = pixels[x, y][1]
            blue = pixels[x, y][2]
            all_pixels.append((red, green, blue))
    return(all_pixels)

def write_csv(dicts: List[Dict], output_file: str):
    with open(output_file, "w") as fout:
        fieldnames = dicts[0].keys()
        writer = csv.DictWriter(fout, fieldnames = fieldnames)
        writer.writeheader()
        for d in dicts:
            writer.writerow(d)

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

    ignore_pixels = []
    if ignore_file:
        ignore_pixels = set(load_all_pixels(ignore_file))

    if ignore_pixels:
        avg_args['ignore_vals'] = ignore_pixels

    if not path.exists():
        print(">>> ERROR: path does not exist: " + str(path))
        raise

    if path.is_dir():
        avgs = Avg().from_dir(dir = path, threads = int(threads), **avg_args)
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


def make_thumbnail(
        red: int,
        blue: int,
        green: int,
        input_path: str,
        output_path: str,
        img_width: int = 300,
        img_height: int = 300,
        bar_height: int = 50,
        ) -> output_path:
    """
    Make a thumbnail from a single image and its average RGB values
    Using the avg RBG as a background color upon which to place and scaled version
    Of the input image file
    Final thumbnail size will be img_width * img_height + bar_height
    """
    # start collage canvas with a background color of the avg RGB values
    canvas_size = (img_width, img_height + bar_height)
    canvas = Image.new('RGB', canvas_size, (red, blue, green))
    # load image and add to canvas
    image = Image.open(input_path).resize((img_width, img_height), Image.ANTIALIAS)
    canvas.paste(image, (0, 0))
    canvas.save(output_path)
    return(output_path)


def make_thumbnails(
        output_dir: str,
        input_path: str = None, # a single input file or directory
        input_files: List[str] = None, # list of file paths
        input_avgs: List[Avg] = None, # list of Avg instances
        x: int = 300,
        y: int = 300,
        bar_height: int = 50,
        ignore_file: str = None,
        rename: bool = True,
        *args, **kwargs) -> List[str]:
    """
    Create thumbnail images with average color information
    In parallel for all supplied images
    """
    if not input_files and not input_avgs and not input_path:
        print(">>> ERROR: either input_avgs or input_files or input_path must be supplied")
        raise

    avg_args = {}
    ignore_pixels = []
    if ignore_file:
        ignore_pixels = set(load_all_pixels(ignore_file))

    if ignore_pixels:
        avg_args['ignore_vals'] = ignore_pixels

    # if input_path was passed, use it to find input_files
    if input_path:
        input_path = Path(input_path)
        # find all files in the dir
        if input_path.is_dir():
            input_files = [ p for p in input_path.glob('**/*') if p.is_file() ]
        elif input_path.is_file():
            input_files = [input_path]

    if not input_avgs:
        input_avgs = []

    if input_files and not input_avgs:
        # NOTE: the images will get sorted by avg RGB HSV here unless sort_key = False is pased
        input_avgs = Avg().from_list(paths = input_files, *args, **avg_args, **kwargs)

    # make a list of tuples for the values we need to make each thumbnail
    rgb_paths = []
    for i, avg in enumerate(input_avgs):
        if rename:
            output_path = os.path.join(output_dir, str(i + 1) + '.jpg')
        else:
            output_path = os.path.join(output_dir, os.path.basename(avg.path))
        rgb_path = (avg.red, avg.blue, avg.green, avg.path, output_path)
        rgb_paths.append(rgb_path)

    # collect output paths for the completed thumbnails
    output_paths = []
    for red, blue, green, input_path, output_path in rgb_paths:
        kwds = {
            'red': red,
            'blue': blue,
            'green': green,
            'input_path': input_path,
            'output_path': output_path,
            'img_width': x,
            'img_height': y,
            'bar_height': bar_height
            }
        output = make_thumbnail(**kwds)
        output_paths.append(output)
    return(output_paths)

def make_collage(
        input_dicts: List[Dict] = None,
        input_avgs: List[Avg] = None,
        input_path: str = None, # dir or csv or file list to load files from
        input_is_csv: bool = False,
        output_file: str = "collage.jpg",
        x: int = 300, # width of each image
        y: int = 300, # height of each image
        ncol: int = 8, # number of columns in the collage
        bar_height: int = 50, # height for average colore bar on each image
        *args, **kwargs) -> str:
    """
    Make a collage image out of the supplied input image
    Adapted from https://github.com/fwenzel/collage
    """
    if not any([input_dicts, input_avgs, input_path]):
        print(">>> ERROR: either input_avgs or input_dicts or input_path must be supplied")
        raise

    if input_path and not input_avgs:
        if input_is_csv:
            input_avgs = Avg.from_csv(input_path)
        else:
            # NOTE: this will automatically apply sorting
            input_avgs = Avg.from_dir(dir = input_path, *args, **kwargs)

    if input_dicts and not input_avgs:
        input_avgs = [ Avg.from_dict(d) for d in input_dicts ]

    # get configuration for the output collage
    num_input_images = len(input_avgs)
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
    for avg in input_avgs:
        rgb = (avg.red, avg.blue, avg.green)

        # line up top-left corner of image placement based on image number
        position = img_num
        x = position % ncol
        y = position // ncol
        xoff = x * img_width
        yoff = y * img_height_padded

        # load the input image and resize
        image = Image.open(avg.path).resize((img_width, img_height), Image.ANTIALIAS)

        # place color bar on the canvas
        bar_coord = (xoff, yoff, xoff + img_width, yoff + img_height + bar_height)
        canvas.paste(rgb, bar_coord)

        # Place tile on canvas.
        canvas.paste(image, (xoff, yoff))

        img_num += 1

    # save canvas
    canvas.save(output_file)

    return(output_file)

def main():
    """
    Main control function for running the module from command line
    """
    # top level CLI arg parser; args common to all output files go here
    parser = argparse.ArgumentParser(description = '')

    # add sub-parsers for specific file outputs
    subparsers = parser.add_subparsers(help ='Sub-commands available')

    # subparser for printing avg table output
    _print = subparsers.add_parser('print', help = 'Print sorted image data to console')
    _print.add_argument(dest = 'path', help = 'Input path to file or dir to print data for')
    _print.add_argument('--output', dest = 'output_file', default = "-", help = 'The name of the output file')
    _print.add_argument('--threads', dest = 'threads', default = 4, help = 'Number of files to process in parallel')
    _print.add_argument('--ignore', dest = 'ignore_file', default = None, help = 'File with pixels that should be ignored when calculating averages')
    _print.set_defaults(func = print_from_path)
    """
    $ bin/img.py print assets/ --threads 6 --ignore ignore-pixels-white.jpg
    $ bin/img.py print assets/ --threads 6 --ignore ignore-pixels-white.jpg > data.csv
    """

    # subparser for making thumbnails
    _thumbnails = subparsers.add_parser('thumbnails', help = 'Create thumbnails which include the average color for each image')
    _thumbnails.add_argument('input_path', help = 'Input path to file or dir to make thumbnails for')
    _thumbnails.add_argument('-o', '--output', dest = 'output_dir', required = True, help = 'The name of the output directory')
    _thumbnails.add_argument('--threads', dest = 'threads', default = 4, help = 'Number of files to process in parallel')
    _thumbnails.add_argument('--ignore', dest = 'ignore_file', default = None, help = 'File with pixels that should be ignored when calculating averages')
    _thumbnails.add_argument('--no-rename', dest = 'rename', action = "store_false", help = 'Do not rename the output files. WARNING: files with the same basename will get overwritten')
    _thumbnails.set_defaults(func = make_thumbnails)
    """
    $ bin/img.py thumbnails assets/ --output thumbnail_output/ --threads 6
    """

    # subparser for making collage
    _collage = subparsers.add_parser('collage', help = 'Create collage from all images which includes the average color for each image')
    _collage.add_argument('input_path', help = 'Input path to file or dir to make thumbnails for')
    _collage.add_argument('-o', '--output', dest = 'output_file', default = 'collage.jpg', help = 'Output file')
    _collage.add_argument('--threads', dest = 'threads', default = 4, help = 'Number of files to process in parallel from dir input')
    _collage.add_argument('--csv', dest = 'input_is_csv', action = "store_true", help = 'Input item is a .csv file to load data from')
    _collage.set_defaults(func = make_collage)
    """
    $ bin/img.py collage assets/ --output collage.jpg --threads 6
    $ bin/img.py collage data.csv --output collage.jpg --csv
    """

    args = parser.parse_args()
    args.func(**vars(args))

if __name__ == '__main__':
    main()
