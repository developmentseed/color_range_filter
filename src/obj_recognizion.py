import numpy as np
import cv2
from pathlib import Path
import click
from utils import draw_contour, get_vector, get_contour

AREA_CONSTANT = 100


def adjust_colors_range():
    """Get the HSV values to adjust the image

    Returns:
        dict: dictionary of values
    """
    # Adjust values to get the desired object
    hMin = cv2.getTrackbarPos("Hue_min", "image")
    hMax = cv2.getTrackbarPos("Hue_max", "image")
    vMin = cv2.getTrackbarPos("Value_min", "image")
    vMax = cv2.getTrackbarPos("Value_max", "image")
    sMin = cv2.getTrackbarPos("Saturation_min", "image")
    sMax = cv2.getTrackbarPos("Saturation_max", "image")
    kernel = cv2.getTrackbarPos("Kernel", "image")
    area = cv2.getTrackbarPos("Area", "image")
    lower = [hMin, sMin, vMin]
    upper = [hMax, sMax, vMax]

    return lower, upper, kernel, area


@click.command(short_help="Get range color from images")
@click.option(
    "--image_file",
    help="Imagen file",
    type=str,
    default="./../fixture/141155-193764-19.jpeg",
)
@click.option("--hsv_lower", type=str, default="10,10,10")
@click.option("--hsv_upper", type=str, default="150,150,150")
@click.option("--kernel", type=int)
def main(image_file, hsv_lower, hsv_upper, kernel):

    # Get parameters
    lower = list(map(int, hsv_lower.split(",")))
    upper = list(map(int, hsv_upper.split(",")))

    cv2.namedWindow("image", cv2.WINDOW_NORMAL)
    cv2.resizeWindow("image", 600, 100)
    cv2.createTrackbar("Hue_min", "image", lower[0], 255, lambda: None)
    cv2.createTrackbar("Hue_max", "image", upper[0], 255, lambda: None)
    cv2.createTrackbar("Saturation_min", "image", lower[1], 255, lambda: None)
    cv2.createTrackbar("Saturation_max", "image", upper[1], 255, lambda: None)
    cv2.createTrackbar("Value_min", "image", lower[2], 255, lambda: None)
    cv2.createTrackbar("Value_max", "image", upper[2], 255, lambda: None)

    cv2.createTrackbar("Kernel", "image", kernel, 50, lambda: None)
    cv2.createTrackbar("Area", "image", 1, 100, lambda: None)

    # Get path for output image
    img = cv2.imread(image_file)

    while True:
        hsv_lower, hsv_upper, kernel, area_picked = adjust_colors_range()

        area_set = [area_picked * 100, area_picked * 1000]
        str_lower = ",".join(str(e) for e in hsv_lower)
        str_upper = ",".join(str(e) for e in hsv_upper)
        str_area = ",".join(str(e) for e in area_set)

        print("########################")
        print(hsv_lower, hsv_upper, area_set, (kernel, kernel))

        print(f"--hsv_lower={str_lower} \\")
        print(f"--hsv_upper={str_upper} \\")
        print(f"--area={str_area} \\")
        print(f"--kernel={kernel} \\")

        contours, mask, dilation = get_contour(
            img, hsv_lower, hsv_upper, area_set, (kernel, kernel)
        )

        # if len(contours) > 0:
        # Clone image to set contours
        image_rgb_clone = img.copy()
        img_contours = cv2.drawContours(
            image_rgb_clone, contours, 0, [0, 255, 0], 1, cv2.LINE_AA
        )
        cv2.imshow("Contours", img_contours)

        cv2.imshow("Mask", mask)
        cv2.imshow("Dilation", dilation)

        k = cv2.waitKey(1) & 0xFF
        if k == 27:
            break
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
