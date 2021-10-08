"""
script is to get range of colors 
Author: @developmentseed
Run:
    python hsv_color_picker.py --image_file=data/tree.png

"""
import cv2
import numpy as np
import sys
import click
from pathlib import Path
from utils import (
    draw_contour,
    get_contour,
    get_vector,
    tile_bbox,
    geojson_merge,
    fetch_tile,
    tile_format,
)

image_hsv = None
image_rgb = None
pixel = (0, 0, 0)
contours_global = []
event_tmp = None
x_tmp = None
y_tmp = None
flags_tmp = None
param_tmp = None


def set_values(v):
    print("val...")

    pick_color("trigger", x_tmp, y_tmp, flags_tmp, param_tmp)


def adjust_colors_range():
    pixel_range = cv2.getTrackbarPos("Pixel_range", "image")
    kernel = cv2.getTrackbarPos("Kernel", "image")
    area = cv2.getTrackbarPos("Area", "image")
    return pixel_range, kernel, area


def check_boundaries(value, tolerance, ranges, upper_or_lower):
    if ranges == 0:
        # set the boundary for hue
        boundary = 180
    elif ranges == 1:
        # set the boundary for saturation and value
        boundary = 255

    if value + tolerance > boundary:
        value = boundary
    elif value - tolerance < 0:
        value = 0
    else:
        if upper_or_lower == 1:
            value = value + tolerance
        else:
            value = value - tolerance
    return value


def print_values(lower, upper, area_range, kernel):
    # Print values to use later
    print("##################### HSV values .....")
    str_lower = ",".join(str(e) for e in lower.tolist())
    str_upper = ",".join(str(e) for e in upper.tolist())
    str_area = ",".join(str(e) for e in area_range)
    print(f"--hsv_lower={str_lower} \\")
    print(f"--hsv_upper={str_upper} \\")
    print(f"--area={str_area} \\")
    print(f"--kernel={kernel} \\")


def pick_color(event, x, y, flags, param):
    print("pick_color")

    # set global values
    global contours_global, event_tmp, x_tmp, y_tmp, flags_tmp, param_tmp
    # event_tmp = event

    if event == cv2.EVENT_LBUTTONDOWN or event == "trigger":
        x_tmp = x
        y_tmp = y
        flags_tmp = flags
        param_tmp = param

        pixel = image_hsv[y, x]
        pixel_range, kernel, area = adjust_colors_range()
        # Get Range of pixel and get min and max hsv
        hue_upper = check_boundaries(pixel[0], pixel_range, 0, 1)
        hue_lower = check_boundaries(pixel[0], pixel_range, 0, 0)
        saturation_upper = check_boundaries(pixel[1], pixel_range, 1, 1)
        saturation_lower = check_boundaries(pixel[1], pixel_range, 1, 0)
        value_upper = check_boundaries(pixel[2], pixel_range + 40, 1, 1)
        value_lower = check_boundaries(pixel[2], pixel_range + 40, 1, 0)
        upper = np.array([hue_upper, saturation_upper, value_upper])
        lower = np.array([hue_lower, saturation_lower, value_lower])
        area_range = [area * 1000, area * 1000000]
        print_values(lower, upper, area_range, kernel)
        contours, mask, dilation = get_contour(
            image_rgb, lower, upper, area_range, (kernel, kernel)
        )

        image_rgb_clone = image_rgb.copy()
        cv2.rectangle(
            image_rgb_clone, (x, y), (x + pixel_range, y + pixel_range), (255, 0, 0), 2
        )
        contours_global = contours
        for contour in contours:
            image_rgb_clone = cv2.drawContours(
                image_rgb_clone, [contour], 0, [255, 255, 0], 1, cv2.LINE_AA
            )

        cv2.imshow("RGB", image_rgb_clone)
        # cv2.imshow("Mask", mask)
        # cv2.imshow("erosion", erosion)
        # cv2.imshow("Dilation", dilation)


@click.command(short_help="Get range of colors")
@click.option("--image_file", type=str)
def main(image_file):
    global image_hsv, image_rgb, pixel

    # Set values on images
    cv2.namedWindow("image", cv2.WINDOW_NORMAL)
    cv2.resizeWindow("image", 600, 100)
    cv2.createTrackbar("Pixel_range", "image", 10, 100, set_values)
    cv2.createTrackbar("Kernel", "image", 3, 50, set_values)
    cv2.createTrackbar("Area", "image", 1, 100, set_values)

    # Read image
    image_src = cv2.imread(image_file)
    image_rgb = image_src
    cv2.imshow("RGB", image_src)
    cv2.setMouseCallback("RGB", pick_color)
    # HSV image
    image_hsv = cv2.cvtColor(image_src, cv2.COLOR_RGB2HSV)
    # cv2.imshow("HSV", image_hsv)
    # cv2.setMouseCallback("HSV", pick_color)
    # Terminate windows
    while True:
        k = cv2.waitKey(1) & 0xFF
        if k == 27:
            break

        if cv2.waitKey(1) == 101:
            print("########################")
            print(f"Export data into JOSM")
            print("########################")
            file_path = Path(image_file)
            img_bbox = tile_bbox(file_path.stem, True, 2048)
            get_vector(
                image_src,
                img_bbox,
                contours_global,
                f"data/{file_path.stem}.geojson",
                [],
            )

    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
