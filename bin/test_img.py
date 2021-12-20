#!/usr/bin/env python3
"""
"""
import sys
import os
import unittest
import shutil
from tempfile import mkdtemp
import colorsys
# from img import get_img_rgbs, get_img_avg_rgb, get_img_rbg_hsv, get_avgs
from img import Avg

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
        avgs = Avg().from_list(paths = paths, parallel = 1)
        for i, e in enumerate([white_expected, colors_expected, green_expected]):
            for key in e.keys():
                self.assertEqual(getattr(avgs[i], key), e[key])





if __name__ == "__main__":
    unittest.main()
