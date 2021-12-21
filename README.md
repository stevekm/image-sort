# image-sort

[[Docker Hub](https://hub.docker.com/repository/docker/stevekm/image-sort)]

Program to sort images based on average color values. `imagesort.py` is able to:

- `print` a sorted csv format table of the average RGB (red, green, blue) and HSV (hue, saturation, value) attributes of each image

- create `thumbnail` output of supplied images with numeric filenames ordered by average RGB or HSV values

- create a `collage` output of all thumbnails of all supplied sorted images along with color information on each image's average RGB value

- create an animated `gif` that will quickly flip through all the sorted thumbnails

- perform multi-threaded parallel image processing when files are supplied in a directory

- adjust the size of output images along with the `key` value used for sorting (default: `"hue"`)

- supply a secondary image file with pixels to `ignore` amongst input images, for example to help remove the effects of unwanted background colors on the calculated average RGB values

## Examples

Example commands

- print table of values

```
./imagesort.py print assets/jpg/Animals-1/ --threads 2 --key red --ignore ignore-pixels-white.jpg
```

- save a table of values, then read it back to create thumbnails, collage, and gif

```
./imagesort.py print assets/jpg/Animals-1/ --threads 4 --ignore ignore-pixels-white.jpg > data.csv

mkdir -p output
./imagesort.py thumbnails data.csv --csv --output output/ -x 200 -y 200 --bar 60

./imagesort.py collage data.csv --output collage.jpg --csv -x 200 -y 200 --bar 60 --ncol 5

./imagesort.py gif data.csv --csv --output image.gif -x 150 -y 150 --bar 50
```

Example output

- `collage` output
 
<img src="/examples/collage.jpg" width="400" height="600" />

- `gif` output

![gif](/examples/image.gif)

# Installation

Clone this repo

```
git clone https://github.com/stevekm/image-sort.git
cd image-sort
```

## Install with `conda`

Install dependencies into a local `conda` installation in the current `image-sort` directory

```
make install

# activate the conda env
source conda/bin/activate

# deactivate it when you are done
conda deactivate
```

### Testing

Run the test suite with

```
make test
```

Run the set of example CLI commands with

```
make test-commands
```

## Docker

If you have trouble installing the required dependencies, it can also be run with Docker.

```
docker run -v $PWD:$PWD --workdir $PWD stevekm/image-sort:latest imagesort.py --help
```
