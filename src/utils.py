import os
import numpy as np
import cv2
import json
from geojson import Feature, FeatureCollection as fc
from smart_open import open
import shapely
from shapely.geometry import shape, mapping, Point, box, Polygon, MultiPolygon
import affine
import mercantile
from joblib import Parallel, delayed
from tqdm import tqdm
import requests


def get_contour(img, lower_range, upper_range, area_range, kernel):
    """Find the required objects

    Args:
        img (array): array img
        lower_range (list): List of lower values for HSV
        upper_range (list):  List of upper values for HSV
        area_range (list): range of are to conosider
        kernel (tupple): kernet to fix the object
    """
    lower = np.array(lower_range)
    upper = np.array(upper_range)

    # Gray color
    hsv = cv2.cvtColor(img, cv2.COLOR_RGB2HSV)
    # cretae mask for desired object
    mask = cv2.inRange(hsv, lower, upper)

    # Adjust image for remove noise
    kernel = np.ones(kernel, np.uint8)
    erosion = cv2.erode(mask, kernel, iterations=2)
    dilation = cv2.dilate(erosion, kernel, iterations=2)

    # Get countour
    contours, _ = cv2.findContours(dilation, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    contours = sorted(contours, key=lambda c: cv2.contourArea(c), reverse=True)

    contours_fixed = []
    for contour in contours:
        area = cv2.contourArea(contour)
        if area > area_range[0] and area < area_range[1]:
            contours_fixed.append(contour)
    return contours_fixed, mask, dilation


def draw_contour(img, contours, output_img_path):
    """Add  contour in a output image.
    Args:
        img (array): image
        contours (arrray): Countor detected
        output_img_path (str)
    """
    # for countour in contours:
    cv2.drawContours(img, contours, 0, [0, 255, 0], 1, cv2.LINE_AA)
    cv2.imwrite(output_img_path, img)


def pixel2GeoPoint(pixelCoord, img_bbox, img_shape):
    pxbox = 0, 0, pixelCoord[0], pixelCoord[1]
    width = img_bbox[2] - img_bbox[0]
    height = img_bbox[3] - img_bbox[1]
    a = affine.Affine(
        width / img_shape[0],
        0.0,
        img_bbox[0],
        0.0,
        (0 - height / img_shape[1]),
        img_bbox[3],
    )
    a_lst = [a.a, a.b, a.d, a.e, a.xoff, a.yoff]
    poly = shapely.affinity.affine_transform(box(*pxbox), a_lst)
    bounds = poly.bounds
    return Point(bounds[2], bounds[1])


def get_vector(img, img_bbox, contours, geojson_output, tags):
    features = []
    for contour in contours:
        points = [pixel2GeoPoint(c[0], img_bbox, list(img.shape)) for c in contour]
        area = cv2.contourArea(contour)
        poly = Polygon(points)

        poly = poly.buffer(0.00001, join_style=1).buffer(-0.00001, join_style=1)
        poly = poly.simplify(0.000002, preserve_topology=True)
        feature = Feature(geometry=mapping(poly), properties={"area": area})
        # Add tags
        for t in tags:
            k, v = t.split("=")
            feature["properties"][k] = v

        features.append(feature)
    with open(geojson_output, "w") as out_geo:
        out_geo.write(json.dumps(fc([*features])))
        print(f"Contours save at ..{geojson_output}")


def tile_bbox(tile_name, supertile, supertile_size):
    TILE_SIZE = 256
    if supertile:
        tile = list(map(int, tile_name[:-3].split("-")))
        polygons = []
        for t in range(0, int(supertile_size / TILE_SIZE)):
            t_bbox = mercantile.bounds(tile[0] + t, tile[1] + t, tile[2])
            polygon = shapely.geometry.box(*t_bbox, ccw=True)
            polygons.append(polygon)
        polygons = MultiPolygon(polygons)
        return polygons.bounds

    else:
        tile = list(map(int, tile_name.split("-")))
        img_bbox = mercantile.bounds(tile[0], tile[1], tile[2])
        return img_bbox


def geojson_merge(geojsons, geojson_output):
    with open(geojson_output, "w") as outfile:
        features = [json.load(open(f, "r")).get("features") for f in geojsons]
        features = [item for sub_features in features for item in sub_features]
        with open(geojson_output, "w") as out_geo:
            out_geo.write(json.dumps(fc(features)))


def fetch_tile(tile, url_map_service, tiles_folder):
    """Fetch a tiles"""
    x, y, z = tile
    url = url_map_service.format(x=x, z=z, y=y)
    tilefilename = f"{tiles_folder}/{x}-{y}-{z}.png"
    if not os.path.isfile(tilefilename):
        r = requests.get(url, timeout=2000)
        if r.status_code == 200:
            with open(tilefilename, "wb") as f:
                f.write(r.content)
            return tilefilename
        else:
            logger.error(f"No found image... {url}")
            return None
    return tilefilename


def tile_format(line):
    str_tile = (
        line.replace('"', "")
        .replace("(", "")
        .replace(")", "")
        .replace("\n", "")
        .replace(", ", "-")
        .replace(",", "-")
    )
    return list(map(int, str_tile.split("-")))
