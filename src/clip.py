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
import glob
from joblib import Parallel, delayed
from tqdm import tqdm
import json
import geopandas as gpd


@click.command(short_help="Get range color from images")
@click.option("--geojson_data", type=str)
@click.option("--geojson_poly", type=str)
@click.option("--geojson_output", type=str)
def main(geojson_data, geojson_poly, geojson_output):

    print(geojson_dataless)

    gdf = gpd.read_file(geojson_data)
    print(gdf)

    # poly = json.load(open(ggeojson_poly, "r")).get("features")[0]
    # print(poly)

    # world = gpd.read_file(ggeojson_poly)
    # africa = world[world[“continent”] == “Africa”]
    # poly = Polygon([(-35, 0), (-35, 60), (60, 60), (60, 0), (0, 0)])
    # polygon = geopandas.GeoDataFrame([1], geometry=[poly], crs=world.crs)


if __name__ == "__main__":
    main()
