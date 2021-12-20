#!/usr/bin/env python3
"""
"""
import sys
import os
import unittest
import shutil
from tempfile import mkdtemp
import colorsys
from img import get_img_rgbs, get_img_avg_rgb, get_img_rbg_hsv, get_avgs
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

class TestIMG(unittest.TestCase):
    def setUp(self):
        """this gets run for each test case"""
        self.tmpdir = mkdtemp()

    def tearDown(self):
        """this gets run for each test case"""
        shutil.rmtree(self.tmpdir)

    def test_get_img_rgbs(self):
        """
        Make sure that we can get the correct RGB values for sample images
        """
        # test multiple colors
        pixels = [(red, green, blue) for red, green, blue in get_img_rgbs(colors_jpg)]
        expected = [(254, 0, 0), (255, 255, 103), (1, 255, 2), (1, 0, 254)]
        self.assertEqual(pixels, expected)

        # test just black
        pixels = [(red, green, blue) for red, green, blue in get_img_rgbs(black_jpg)]
        expected = [(0, 0, 0)]
        self.assertEqual(pixels, expected)

        # test just white
        pixels = [(red, green, blue) for red, green, blue in get_img_rgbs(white_jpg)]
        expected = [(255, 255, 255)]
        self.assertEqual(pixels, expected)


    def test_get_img_rbg_hsv(self):
        """
        Test that the correct RGB HSV values are returned
        """
        # test just black
        pixels = [(red, green, blue, hue, saturation, value) for red, green, blue, hue, saturation, value in get_img_rbg_hsv(black_jpg)]
        expected = [(0, 0, 0, 0.0, 0.0, 0)]
        self.assertEqual(pixels, expected)
        # test just green
        pixels = [(red, green, blue, hue, saturation, value) for red, green, blue, hue, saturation, value in get_img_rbg_hsv(green_jpg)]
        expected = [(1, 255, 1, 0.3333333333333333, 0.996078431372549, 255)]
        self.assertEqual(pixels, expected)


    def test_get_img_avg_rgb(self):
        """
        Make sure the correct average pixel values are returned for an image
        """
        # get average for mixed colors
        avg = get_img_avg_rgb(colors_jpg, _verbose = False)
        self.assertDictEqual(avg, colors_expected)

        # write out a tmp file that should equate to green
        green_csv = os.path.join(self.tmpdir, "green.csv")
        values = [1, 255, 2, 0.5, 0, 255]
        with open(green_csv, "w") as f:
            f.write(','.join([ str(v) for v in values ]))
        # get the average after subtracting the green values
        avg = get_img_avg_rgb(colors_jpg, ignore_csvfile = green_csv,  _verbose = False)
        self.assertDictEqual(avg, colors_minus_green_expected)

        # use a dict of values for the ignore pixel list
        ignore_list = [{'red': 1, 'green': 255, 'blue': 2}]
        avg = get_img_avg_rgb(colors_jpg, ignore_list = ignore_list,  _verbose = False)
        self.assertDictEqual(avg, colors_minus_green_expected)

        # use an Avg instance to ignore from
        ignore_avg = Avg.from_dict({'red': 1, 'green': 255, 'blue': 2, 'hue': 0, 'saturation': 0, 'value': 0, 'path': 'foo', 'pixels_total': 0, 'pixels_counted': 0, 'pixels_pcnt': 0})
        avg = get_img_avg_rgb(colors_jpg, ignore_avg = ignore_avg,  _verbose = False)
        self.assertDictEqual(avg, colors_minus_green_expected)

    def test_get_avgs(self):
        """
        Check that the correct averages are returned for image files
        """
        # get just average of colors.jpg
        avgs = get_avgs([colors_jpg], _verbose = False)
        expected = [colors_expected]
        self.assertEqual(avgs, expected)

        # get average while ignoring green pixels
        # write out a tmp file that should equate to green
        green_csv = os.path.join(self.tmpdir, "green.csv")
        values = [1, 255, 2, 0.5, 0, 255]
        with open(green_csv, "w") as f:
            f.write(','.join([ str(v) for v in values ]))
        avgs = get_avgs([colors_jpg], ignore_csvfile = green_csv, _verbose = False)
        expected = [colors_minus_green_expected]
        self.assertEqual(avgs, expected)

        # get averages from multiple images
        # default sort key = hue
        avgs = get_avgs([colors_jpg, green_jpg, white_jpg], _verbose = False)
        expected = [white_expected, colors_expected, green_expected]
        self.assertEqual(avgs, expected)

        # with no sort key
        avgs = get_avgs([colors_jpg, green_jpg, white_jpg], sort_key = False, _verbose = False)
        expected = [colors_expected, green_expected, white_expected]
        self.assertEqual(avgs, expected)

        # run multiple in parallel
        avgs = get_avgs([colors_jpg, green_jpg, white_jpg], parallel = 2, _verbose = False)
        expected = [white_expected, colors_expected, green_expected]
        self.assertEqual(avgs, expected)

class TestAvg(unittest.TestCase):
    def test_avg(self):
        """
        Check that the Avg class returns expected values
        """
        avg = Avg(path = colors_jpg)
        expected = {'blue': 89, 'pixels_total': 4, 'saturation': 0.2992125984251969, 'pixels_pcnt': 100.0, 'pixels_counted': 4, 'hue': 0.16666666666666666, 'value': 127, 'green': 127, 'red': 127}
        for key in expected.keys():
            self.assertEqual(getattr(avg, key), expected[key])

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




if __name__ == "__main__":
    unittest.main()
