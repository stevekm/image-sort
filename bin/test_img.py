#!/usr/bin/env python3
"""
"""
import sys
import os
import unittest
import shutil
from tempfile import mkdtemp
import colorsys
import hashlib
from img import Avg
from img import make_thumbnail, make_thumbnails


# get paths to the fixture image files
THIS_DIR = os.path.dirname(os.path.realpath(__file__))
fixtures_dir = os.path.join(THIS_DIR, "fixtures")
white_jpg = os.path.join(fixtures_dir, "white.jpg")
black_jpg = os.path.join(fixtures_dir, "black.jpg")
green_jpg = os.path.join(fixtures_dir, "green.jpg")
colors_jpg = os.path.join(fixtures_dir, "colors.jpg")


# these are the expected average values for each image
colors_expected = {'red': 127, 'green': 127, 'blue': 89, 'pixels_total': 4, 'pixels_counted': 4, 'hue': 0.16666666666666666, 'saturation': 0.2992125984251969, 'value': 127, 'pixels_pcnt': 100.0, 'path': colors_jpg}

colors_minus_green_expected = {'blue': 119, 'pixels_total': 4, 'saturation': 0.5, 'pixels_pcnt': 75.0, 'pixels_counted': 3, 'hue': 0.9333333333333333, 'value': 170, 'green': 85, 'red': 170, 'path': colors_jpg}

white_expected = {'red': 255, 'green': 255, 'blue': 255, 'pixels_total': 1, 'pixels_counted': 1, 'hue': 0.0, 'saturation': 0.0, 'value': 255, 'pixels_pcnt': 100.0, 'path': white_jpg}

green_expected = {'red': 1, 'green': 255, 'blue': 1, 'pixels_total': 1, 'pixels_counted': 1, 'hue': 0.3333333333333333, 'saturation': 0.996078431372549, 'value': 255, 'pixels_pcnt': 100.0, 'path': green_jpg}


def md5_file(filename: str) -> str:
    """
    Get md5sum of a file by reading it in small chunks. This avoids issues with Python memory usage when hashing large files.
    """
    with open(filename, "rb") as f:
        file_hash = hashlib.md5()
        chunk = f.read(8192)
        while chunk:
            file_hash.update(chunk)
            chunk = f.read(8192)
    hash = file_hash.hexdigest()
    return(hash)


class TestAvg(unittest.TestCase):
    def test_avg(self):
        """
        Check that the Avg class returns expected values
        """
        avg = Avg(path = colors_jpg)
        expected = {'blue': 89, 'pixels_total': 4, 'saturation': 0.2992125984251969, 'pixels_pcnt': 100.0, 'pixels_counted': 4, 'hue': 0.16666666666666666, 'value': 127, 'green': 127, 'red': 127}
        for key in expected.keys():
            self.assertEqual(getattr(avg, key), expected[key])

        # test with ignore_vals for green
        avg = Avg(path = colors_jpg, ignore_vals = [(1, 255, 2)] )
        for key in colors_minus_green_expected.keys():
            self.assertEqual(getattr(avg, key), colors_minus_green_expected[key])

    def test_from_dict(self):
        """
        Check that Avg objects is instantiated from a dict of values
        """
        d = {'blue': 89, 'pixels_total': 4, 'saturation': 0.2992125984251969, 'pixels_pcnt': 100.0, 'pixels_counted': 4, 'hue': 0.16666666666666666, 'value': 127, 'green': 127, 'red': 127, 'path': colors_jpg}
        avg = Avg().from_dict(d)
        for key in d.keys():
            self.assertEqual(getattr(avg, key), d[key])

    def test_from_list(self):
        """
        Check that a list of Avg objects can be instantiated from a list of paths
        """
        paths = [colors_jpg, green_jpg, white_jpg]
        avgs = Avg().from_list(paths = paths, sort_key = False)
        for i, e in enumerate([colors_expected, green_expected, white_expected]):
            for key in e.keys():
                self.assertEqual(getattr(avgs[i], key), e[key])

        # with sort key
        # make sure to use  threads = 1 so that list is returned in same order it went in for test case!!
        avgs = Avg().from_list(paths = paths, threads = 1)
        for i, e in enumerate([white_expected, colors_expected, green_expected]):
            for key in e.keys():
                self.assertEqual(getattr(avgs[i], key), e[key])


class TestThumbnails(unittest.TestCase):
    def setUp(self):
        """this gets run for each test case"""
        self.preserve = False # save the tmpdir
        self.tmpdir = mkdtemp() # dir = THIS_DIR

    def tearDown(self):
        """this gets run for each test case"""
        if not self.preserve:
            # remove the tmpdir upon test completion
            shutil.rmtree(self.tmpdir)

    def test_make_thumbnail(self):
        """
        Test that a single thumbnail is created as expected
        """
        avg = Avg(path = colors_jpg)
        output_file = os.path.join(self.tmpdir, "0.jpg")
        output = make_thumbnail(red = avg.red, blue = avg.blue, green = avg.green, input_path = avg.path, output_path = output_file)
        md5 = md5_file(output)
        expected = '83a42111ab98bf1d5b472f5df3b6ef9d'
        self.assertEqual(md5, expected)

    # def test_make_thumbnail_from_avgs_ignore(self):
    #     # test with ignore file
    #     # ignore_file
    #     self.preserve = True
    #     print()
    #     print(self.tmpdir)

    def test_make_thumbnails_from_avgs(self):
        """
        Test that multiple thumbnails can be created from Avg instances
        """
        input_avgs = Avg.from_list([colors_jpg, green_jpg], threads = 1)
        outputs = make_thumbnails(output_dir = self.tmpdir, input_avgs = input_avgs)
        md5s = [ md5_file(o) for o in outputs ]
        expected = ['83a42111ab98bf1d5b472f5df3b6ef9d', '842d20107511fe23c0d8510bb7cde137']
        self.assertEqual(md5s, expected)

    def test_make_thumbnails_from_files(self):
        """
        Test that thumbnails are made from multiple input files
        """
        input_files = [colors_jpg, green_jpg]
        outputs = make_thumbnails(output_dir = self.tmpdir, input_files = input_files)
        md5s = [ md5_file(o) for o in outputs ]
        expected = ['83a42111ab98bf1d5b472f5df3b6ef9d', '842d20107511fe23c0d8510bb7cde137']
        self.assertEqual(md5s, expected)


if __name__ == "__main__":
    unittest.main()
