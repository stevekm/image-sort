# image-sort

Program to sort images based on color values.

## Contents

- `sort-images.py`: script to sort all supplied images based on color (defaults to sorting by Hue value), individual images can be passed or directories containing images. Saves a .csv file with the images in sorted order (`images.rgb.hsv.csv`)

- `list2filmstrip.py`: Reads the contents of `images.rgb.hsv.csv` and generates a horizontal filmstrip image to show the sorted images in sequence (`filmstrip.jpg`).

- `list2collage.py`: Reads the contents of `images.rgb.hsv.csv` and generates a two dimensional collage to show the sorted images in sequence (`collage.jpg`).

# Installation

Clone this repo

```
git clone https://github.com/stevekm/image-sort.git
cd image-sort
```

Install dependencies

```
make conda-install
```

- Dependencies are installed into a `conda` installation in the current directory

# Usage

Run a test with the included images in the `assets` directory

```
make run
```

Run with another directory

```
run IMGDIR=/path/to/some/directory
```

The scripts can be run individually with custom configs if the required dependencies are installed.

# Software

Dependencies are installed by default with `conda` from the Makefile recipe `make conda-install`

- Python 2.7 (required for `PIL`)

- PIL (Python Imaging Library)

- GNU Makefile

Tested on macOS 10.12.6

# References

https://www.alanzucconi.com/2015/09/30/colour-sorting/

https://smart.servier.com/image-set-download/

https://adamspannbauer.github.io/2018/03/02/app-icon-dominant-colors/

https://github.com/fwenzel/collage
