"""
script to vectorize range of color to polygons
Author: @developmentseed
Run:
    python src/range.py \
    --img_file="fixture/141155-193764-19.jpeg" \
    --hsv_lower="33,44,50" \
    --hsv_upper="97,131,164"

"""
import os
import numpy as np
import cv2
import click
from pathlib import Path
from joblib import Parallel, delayed
from tqdm import tqdm
import json
import glob
from utils import (
    draw_contour,
    get_vector,
    get_contour,
    tile_bbox,
    geojson_merge,
    fetch_tile,
    tile_format,
)


def extract_range_color(
    tile,
    output_folder,
    url_map_service,
    hsv_lower,
    hsv_upper,
    kernel,
    area,
    supertile,
    supertile_size,
    tags,
    write_imgs,
):
    img_file = None
    if supertile:
        img_file = tile
    else:
        # Download tile
        img_file = fetch_tile(tile, url_map_service, output_folder)

    if img_file is not None:
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

        hsv_lower = list(map(int, hsv_lower.split(",")))
        hsv_upper = list(map(int, hsv_upper.split(",")))

        # hsv_lower = [hue[0], value[0], saturation[0]]
        # hsv_upper = [hue[1], value[1], saturation[1]]

        # Get tags to add in the polygon
        for t in tags:
            if "=" not in t:
                raise Exception("tags incorrect format, key=value")

        # Getting contours fro range color
        contours, _, _ = get_contour(img, hsv_lower, hsv_upper, area, kernel)

        # Draw contour in the image
        if write_imgs:
            draw_contour(img, contours, output_img_path)
        # Get vector data from contour
        get_vector(img, img_bbox, contours, geojson_output, tags)

        return geojson_output
    return None


@click.command(short_help="Get range color from images")
@click.option(
    "--geojson_tiles_file", type=str, help="Geojson files of grid of tiles", required=False
)
@click.option("--supertile", type=bool, default=False, required=False)
@click.option("--supertile_size", type=int, default=256, required=False)
@click.option("--supertile_folder", type=str, required=False)
@click.option(
    "--output_folder",
    help="Output folder to store tiles and geojson files",
    type=str,
    required=True,
)
@click.option(
    "--url_map_service", help="Url map service to get the tiles", type=str, required=False
)
@click.option("--hsv_lower", type=str, required=True)
@click.option("--hsv_upper", type=str, required=True)
@click.option("--kernel", type=int, required=True)
@click.option("--area", type=str, required=True)
@click.option("--tags", help="Tags to add", type=str, multiple=True, default=[], required=False)
@click.option("--geojson_output", type=str, required=True)
@click.option("--write_imgs", type=bool, default=False, required=False)
def main(
    geojson_tiles_file,
    supertile,
    supertile_size,
    supertile_folder,
    output_folder,
    url_map_service,
    hsv_lower,
    hsv_upper,
    kernel,
    area,
    tags,
    geojson_output,
    write_imgs,
):

    geojson_files = None
    if supertile:
        # in case we pass the supertiles folder
        supertiles_files = glob.glob(f"{supertile_folder}/*.png")
        geojson_files = Parallel(n_jobs=-1)(
            delayed(extract_range_color)(
                stile,
                output_folder,
                url_map_service,
                hsv_lower,
                hsv_upper,
                kernel,
                area,
                supertile,
                supertile_size,
                tags,
                write_imgs,
            )
            for stile in tqdm(
                supertiles_files,
                desc=f"Downloading and Processing images ...",
                total=len(supertiles_files),
            )
        )

    else:
        # In case we pass a geojson tiles list
        features = json.load(open(geojson_tiles_file, "r")).get("features")
        tiles = [tile_format(f["id"]) for f in features]
        os.makedirs(output_folder, exist_ok=True)
        geojson_files = Parallel(n_jobs=-1)(
            delayed(extract_range_color)(
                tile,
                output_folder,
                url_map_service,
                hsv_lower,
                hsv_upper,
                kernel,
                area,
                supertile,
                supertile_size,
                tags,
                write_imgs,
            )
            for tile in tqdm(tiles, desc=f"Downloading and Processing images ...", total=len(tiles))
        )
    # geojson_files = glob.glob(f"{output_folder}/*.geojson")
    geojson_files = [f for f in geojson_files if f is not None]
    geojson_merge(geojson_files, geojson_output)


if __name__ == "__main__":
    main()
