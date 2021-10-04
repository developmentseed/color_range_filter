import numpy as np
import cv2
import json
from geojson import Feature, FeatureCollection as fc
from smart_open import open
import shapely
from shapely.geometry import shape, mapping, Point, box, Polygon
import affine


def get_contour(img, lower_range, upper_range, area_range, kernel):
    """Find the required objects

    Args:
        img (array): array img
        lower_range (list): List of lower values for HSV
        upper_range (list):  List of upper values for HSV
        area_range (float): range of are to conosider
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
    erosion = cv2.erode(mask, kernel, iterations=1)
    dilation = cv2.dilate(erosion, kernel, iterations=1)

    # Get countour
    contours, _ = cv2.findContours(dilation, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    contours = sorted(contours, key=lambda c: cv2.contourArea(c), reverse=True)

    contours_fixed = []
    for contour in contours:
        area = cv2.contourArea(contour)
        if area > area_range[0] and area < area_range[1]:
            contours_fixed.append(contour)
    return contours_fixed


def draw_contour(img, contours, output_img_path):
    """Add  contour in a output image.
    Args:
        img (array): image
        contours (arrray): Countor detected
        output_img_path (str)
    """
    for countour in contours:
        cv2.drawContours(img, [countour], 0, [0, 255, 0], 1, cv2.LINE_AA)
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


def get_vector(img, img_bbox, contours, geojson_output):
    features = []
    for contour in contours:
        points = [pixel2GeoPoint(c[0], img_bbox, list(img.shape)) for c in contour]
        area = cv2.contourArea(contour)
        poly = Polygon(points)
        poly = poly.simplify(0.000001, preserve_topology=False)
        feature = Feature(geometry=mapping(poly), properties={"area": area})
        features.append(feature)
    with open(geojson_output, "w") as out_geo:
        out_geo.write(json.dumps(fc([*features])))
