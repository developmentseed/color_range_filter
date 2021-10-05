import json
import click
from smart_open import open
import os
from geojson import FeatureCollection as fc
from joblib import Parallel, delayed
from tqdm import tqdm
import requests

# docker run --rm -v ${PWD}:/mnt/data/ developmentseed/geokit:node.latest geokit tilecover data/area.geojson --zoom=20 > data/tiles.geojson

def fetch_tile(tile, tiles_folder):
    """Fetch a tiles"""
    x, y, z = tile
    url = url_map_service.format(x=x, z=z, y=y)
    tilefilename = f"{tiles_folder}/{x}-{y}-{z}.png"
    if not os.path.isfile(tilefilename):
        r = requests.get(url, timeout=2000)
        if r.status_code == 200:
            with open(tilefilename, "wb") as f:
                f.write(r.content)
        else:
            logger.error(f"No found image... {url}")
            tilefilename = "_"
    return tilefilename


fc_data = json.load(open("data/tiles.geojson", "r")).get("features")
url_map_service = "https://tiles.lulc.ds.io/mosaic/naip.latest/tiles/{z}/{x}/{y}?bidx=1,2,3"
tiles = [f['properties']['tiles'] for f in fc_data]

tiles_folder = "data/tiles_20"
os.makedirs(tiles_folder, exist_ok=True)
for tile in tiles:
    print(tile)

    fetch_tile(tile, tiles_folder)
