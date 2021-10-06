"""
script to vectorize range of color to polygons
Author: @developmentseed
Run:
    python src/range.py \
    --img_file="fixture/141155-193764-19.jpeg" \
    --hsv_lower="33,44,50" \
    --hsv_upper="97,131,164"

"""

import numpy as np
import cv2
import click
from pathlib import Path
import glob
from joblib import Parallel, delayed
from tqdm import tqdm

from utils import draw_contour, get_vector, get_contour, tile_bbox, geojson_merge


def extract_range_color(
    img_file,
    hue,
    value,
    saturation,
    kernel,
    area,
    supertile,
    supertile_size,
    tags,
    write_imgs,
):
    # Get path for output image
    img = cv2.imread(img_file)
    img_path = Path(img_file)
    output_img_path = f"{img_path.parent}/{img_path.stem}_output{img_path.suffix}"
    geojson_output = f"{img_path.parent}/{img_path.stem}.geojson"

    # Get bbox for image file
    img_bbox = tile_bbox(img_path.stem, supertile, supertile_size)

    # Get parameters for filter image by range
    area = list(map(int, area.split(",")))
    kernel = (kernel, kernel)
    hue = list(map(int, hue.split(",")))
    value = list(map(int, value.split(",")))
    saturation = list(map(int, saturation.split(",")))
    hsv_lower = [hue[0], value[0], saturation[0]]
    hsv_upper = [hue[1], value[1], saturation[1]]

    # Get tags to add in the polygon
    for t in tags:
        if "=" not in t:
            raise Exception("tags incorrect format, key=value")

    # Getting contours fro range color
    contours, _ = get_contour(img, hsv_lower, hsv_upper, area, kernel)

    # Draw contour in the image
    if write_imgs:
        draw_contour(img, contours, output_img_path)
    # Get vector data from contour
    get_vector(img, img_bbox, contours, geojson_output, tags)
    return geojson_output


@click.command(short_help="Get range color from images")
@click.option(
    "--tiles_folder",
    help="Tiles folder in x-y-x named format",
    type=str,
    default="./../fixture/*.jpeg",
)
@click.option("--hue", type=str)
@click.option("--value", type=str)
@click.option("--saturation", type=str)
@click.option("--area", type=str)
@click.option("--kernel", type=int)
@click.option("--supertile", type=bool, default=False)
@click.option("--supertile_size", type=int, default=256)
@click.option("--tags", help="Tags to add", type=str, multiple=True, default=[])
@click.option("--write_imgs", type=bool, default=False)
@click.option("--geojson_output", type=str)
def main(
    tiles_folder,
    hue,
    value,
    saturation,
    kernel,
    area,
    supertile,
    supertile_size,
    tags,
    geojson_output,
    write_imgs,
):

    images = glob.glob(tiles_folder)
    geojson_files = Parallel(n_jobs=-1)(
        delayed(extract_range_color)(
            img_file,
            hue,
            value,
            saturation,
            kernel,
            area,
            supertile,
            supertile_size,
            tags,
            write_imgs,
        )
        for img_file in tqdm(images, desc=f"Processing images ...", total=len(images))
    )

    geojson_merge(geojson_files, geojson_output)


if __name__ == "__main__":
    main()
