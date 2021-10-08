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

MAX_CROP_RANGE = 10
CROP_RANGE_MUTIPLY = 100

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
    """Function to trigger the clor picker with global values"""
    pick_color("trigger", x_tmp, y_tmp, flags_tmp, param_tmp)


def adjust_colors_range():
    """Function to get the values from sliders
    Retunrs:
    """
    eval_color_range = cv2.getTrackbarPos("Eval color range", "image")
    kernel = cv2.getTrackbarPos("Kernel", "image")
    area = cv2.getTrackbarPos("Area", "image")
    crop_image_range = cv2.getTrackbarPos("Crop image range", "image")
    return eval_color_range, kernel, area, crop_image_range


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


def get_hsv_values(x, y, pixel_range, image_rgb_clone):
    # Get pixels value  from HSV image
    pixel = image_hsv[y, x]
    # Get half of the values
    pixel_range_half = int(pixel_range / 2)

    # Get Range of pixel and get min and max hsv, TODO check if pixel_range  for boundaries
    hue_upper = check_boundaries(pixel[0], pixel_range, 0, 1)
    hue_lower = check_boundaries(pixel[0], pixel_range, 0, 0)
    saturation_upper = check_boundaries(pixel[1], pixel_range, 1, 1)
    saturation_lower = check_boundaries(pixel[1], pixel_range, 1, 0)
    value_upper = check_boundaries(pixel[2], pixel_range + 40, 1, 1)
    value_lower = check_boundaries(pixel[2], pixel_range + 40, 1, 0)
    upper = np.array([hue_upper, saturation_upper, value_upper])
    lower = np.array([hue_lower, saturation_lower, value_lower])

    cv2.rectangle(
        image_rgb_clone,
        (x - pixel_range_half, y - pixel_range_half),
        (x + pixel_range_half, y + pixel_range_half),
        (255, 255, 0),
        3,
    )
    return lower, upper


def draw_rectagles(image_rgb_clone):
    pass


def pick_color(event, x, y, flags, param):
    # set global values
    global contours_global, event_tmp, x_tmp, y_tmp, flags_tmp, param_tmp
    # event_tmp = event

    if event == cv2.EVENT_LBUTTONDOWN or event == "trigger":
        # Save values in global, for useing later to call this function
        x_tmp = x
        y_tmp = y
        flags_tmp = flags
        param_tmp = param

        # Make a clone of the image
        image_rgb_clone = image_rgb.copy()

        # Get Values from window
        pixel_range, kernel, area, crop_range = adjust_colors_range()

        # Extract HSV values
        lower, upper = get_hsv_values(x, y, pixel_range, image_rgb_clone)

        # area range
        area_range = [area * 10, area * 10000]

        # Print values, to use later
        print_values(lower, upper, area_range, kernel)

        image_rgb_ = None
        # Get values from crop area
        if crop_range < MAX_CROP_RANGE:

            crop_range_fixed = crop_range * CROP_RANGE_MUTIPLY
            crop_range_half = int(crop_range_fixed / 2)
            image_rgb_ = image_rgb[
                y - crop_range_half : y + crop_range_half, x - crop_range_half : x + crop_range_half
            ]

            # Draw rectangles, for range color selector and crop selector
            cv2.rectangle(
                image_rgb_clone,
                (x - crop_range_half, y - crop_range_half),
                (x + crop_range_half, y + crop_range_half),
                [255, 235, 59],
                3,
            )

        else:
            image_rgb_ = image_rgb

        # Get contour values for croped or all image
        contours, mask, dilation = get_contour(
            image_rgb_, lower, upper, area_range, (kernel, kernel)
        )

        # Draw crop contours on the original image
        contours_fixed = []
        for contour in contours:
            # In case the had a croped image
            if crop_range < MAX_CROP_RANGE:
                # Get values of the corner to rezise the contour
                x_crop_corner_min = x - crop_range_half
                y_crop_corner_min = y - crop_range_half
                contour = np.add(contour, np.array([[[x_crop_corner_min, y_crop_corner_min]]]))

            image_rgb_clone = cv2.drawContours(
                image_rgb_clone, [contour], 0, [0, 255, 0], 1, cv2.LINE_AA
            )
            contours_fixed.append(contour)

        contours_global = contours_fixed

        # Show images
        cv2.imshow("RGB", image_rgb_clone)
        # cv2.imshow("crop", crop_img_rgb)
        # cv2.imshow("Mask", mask)
        # cv2.imshow("erosion", erosion)
        # cv2.imshow("Dilation", dilation)


@click.command(short_help="Get range of colors")
@click.option("--image_file", type=str)
def main(image_file):
    global image_hsv, image_rgb, pixel

    # Read image
    image_src = cv2.imread(image_file)
    image_rgb = image_src
    cv2.imshow("RGB", image_src)
    cv2.setMouseCallback("RGB", pick_color)
    image_rgb_size = image_rgb.shape[0]

    # Window: Set values on images for selection
    cv2.namedWindow("image", cv2.WINDOW_NORMAL)
    cv2.resizeWindow("image", 700, 80)
    cv2.createTrackbar("Eval color range", "image", 30, 50, set_values)
    cv2.createTrackbar("Kernel", "image", 1, 10, set_values)
    cv2.createTrackbar("Area", "image", 1, 100, set_values)
    cv2.createTrackbar("Crop image range", "image", 1, MAX_CROP_RANGE, set_values)

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
            img_bbox = tile_bbox(file_path.stem, True, image_rgb_size)
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
