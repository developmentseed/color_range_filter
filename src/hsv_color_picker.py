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
from utils import (
    draw_contour,
    get_vector,
    get_contour,
    tile_bbox,
    geojson_merge,
    fetch_tile,
    tile_format,
)

image_hsv = None
image_rgb = None
pixel = (0, 0, 0)


def adjust_colors_range():
    """Get the HSV values to adjust the image

    Returns:
        dict: dictionary of values
    """
    # Adjust values to get the desired object
    hMin = cv2.getTrackbarPos("Hue Minimo", "image")
    hMax = cv2.getTrackbarPos("Hue Maximo", "image")
    vMin = cv2.getTrackbarPos("Value Minimo", "image")
    vMax = cv2.getTrackbarPos("Value Maximo", "image")
    sMin = cv2.getTrackbarPos("Saturation Minimo", "image")
    sMax = cv2.getTrackbarPos("Saturation Maximo", "image")
    kernel = cv2.getTrackbarPos("Kernel", "image")
    area = cv2.getTrackbarPos("Area", "image")

    return [hMin, vMin, sMin], [hMax, vMax, sMax]


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


def pick_color(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:
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
        area_range = [area * 10, area * 100000]

        # Print values to use later
        print("##################### HSV values .....")
        print(lower, upper)
        print(lower, upper)
        str_lower = ",".join(str(e) for e in lower.tolist())
        str_upper = ",".join(str(e) for e in upper.tolist())
        str_area = ",".join(str(e) for e in area_range)

        print(f"--hsv_lower={str_lower} \\")
        print(f"--hsv_upper={str_upper} \\")
        print(f"--area={str_area} \\")
        print(f"--kernel={kernel} \\")

        contours, mask, dilation = get_contour(
            image_rgb, lower, upper, area_range, (kernel, kernel)
        )

        if len(contours) > 0:
            # Clone image to set contours
            image_rgb_clone = image_rgb.copy()
            img_contours = cv2.drawContours(
                image_rgb_clone, contours, 0, [0, 255, 0], 1, cv2.LINE_AA
            )
            cv2.imshow("Contours", img_contours)

        cv2.imshow("Mask", mask)
        cv2.imshow("Dilation", dilation)


@click.command(short_help="Get range of colors")
@click.option("--image_file", type=str)
def main(image_file):
    global image_hsv, image_rgb, pixel

    # Set values on images
    cv2.namedWindow("image", cv2.WINDOW_NORMAL)
    cv2.resizeWindow("image", 600, 100)
    cv2.createTrackbar("Pixel_range", "image", 10, 100, lambda: None)
    cv2.createTrackbar("Kernel", "image", 3, 50, lambda: None)
    cv2.createTrackbar("Area", "image", 1, 100, lambda: None)

    # Read image
    image_src = cv2.imread(image_file)
    image_rgb = image_src
    cv2.imshow("RGB", image_src)
    cv2.setMouseCallback("RGB", pick_color)

    # HSV image
    image_hsv = cv2.cvtColor(image_src, cv2.COLOR_RGB2HSV)
    cv2.imshow("HSV", image_hsv)
    cv2.setMouseCallback("HSV", pick_color)

    # Terminate windows
    while True:
        k = cv2.waitKey(1) & 0xFF
        if k == 27:
            break
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
