#!/usr/bin/env python3
"""
Module with helper functions for image processing tasks
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


# ~~~~~ METHODS ~~~~~ #
# these are mostly legacy functions developed a long time ago that are kept
# because they still work
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
    ignore_csvfile: str = None,
    ignore_list: List[Dict] = None,
    ignore_avg: Avg = None,
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
    ignore_pixels = set() # ['RGB', ... ] ; ['255255255', ... ]
    # load pixels to ignore from a csv file
    # NOTE: this is a really bad method that should be deprecated or rewritten
    if ignore_csvfile != None:
        ignore_pixels_list = load_csv_rgbhsv(input_path = ignore_csvfile)
        ignore_pixels_list = [ (tup[0], tup[1], tup[2]) for tup in ignore_pixels_list ]
        for tup in ignore_pixels_list:
            id = "{0}.{1}.{2}".format(tup[0], tup[1], tup[2])
            ignore_pixels.add(id)
        if _verbose:
            print("Loaded {0} ignore pixels".format(len(ignore_pixels)))

    # load pixels to ignore from a list of dicts or Avg objects
    if ignore_list != None:
        for item in ignore_list:
            if isinstance(item, dict):
                id = "{0}.{1}.{2}".format(item['red'], item['green'], item['blue'])
                ignore_pixels.add(id)
            elif hasattr(item, 'to_dict'):
                d = item.to_dict()
                id = "{0}.{1}.{2}".format(d['red'], d['green'], d['blue'])
                ignore_pixels.add(id)
        if _verbose:
            print("Loaded {0} ignore pixels".format(len(ignore_pixels)))

    # load pixels to ignore from an Avg instance
    if ignore_avg != None:
        id = "{0}.{1}.{2}".format(ignore_avg.red, ignore_avg.green, ignore_avg.blue)
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
        'pixels_counted' : 0,
        'path': image
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
                id = "{0}.{1}.{2}".format(red, green, blue)
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
    Get the average RBG HSV values for all the images in the list
    With optional parallel processing
    Sort the output list based on key
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





# ~~~~~ OBJECTS ~~~~~ #
# custom object class for easily generating image averages
# use this class instead of calling the previous methods directly !!
class Avg(object):
    """
    Holds the attributes of image's average RGB HSV values
    """
    def __init__(self, path: str = None, _verbose: bool = False, *args, **kwargs):
        if path:
            self.path = path
            avg = get_img_avg_rgb(image = self.path, _verbose = _verbose, *args, **kwargs)
            self.red = avg['red']
            self.green = avg['green']
            self.blue = avg['blue']
            self.hue = avg['hue']
            self.saturation = avg['saturation']
            self.value = avg['value']
            self.pixels_total = avg['pixels_total']
            self.pixels_counted = avg['pixels_counted']
            self.pixels_pcnt = avg['pixels_pcnt']

        # initialize empty attributes if using from_dict
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
        objs = []
        avgs = get_avgs(images = paths, sort_key = sort_key, parallel = parallel, _verbose = _verbose, *args, **kwargs)
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
        func = None):
    """
    Print image average RGB values to stdout or file
    """
    path = Path(path)

    if not path.exists():
        print(">>> ERROR: path does not exist: " + str(path))
        raise

    if path.is_dir():
        avgs = Avg().from_dir(dir = path, parallel = int(threads))
        dicts = [avg.to_dict() for avg in avgs]

    if path.is_file():
        avg = Avg(path = path)
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
    _print.set_defaults(func = print_from_path)


    args = parser.parse_args()
    args.func(**vars(args))





if __name__ == '__main__':
    main()
