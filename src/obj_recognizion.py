import numpy as np
import cv2
from pathlib import Path
import click
from utils import draw_contour, get_vector, get_contour


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
    return {
        "lower": [hMin, vMin, sMin],
        "upper": [hMax, vMax, sMax],
        "kernel": kernel,
        "area": area,
    }


@click.command(short_help="Get range color from images")
@click.option(
    "--img_file",
    help="Imagen file",
    type=str,
    default="./../fixture/141155-193764-19.jpeg",
)
def main(img_file):
    # Get path for output image
    img = cv2.imread(img_file)
    img_path = Path(img_file)

    while True:
        obj_color_range = adjust_colors_range()
        area = [obj_color_range["area"] * 10, obj_color_range["area"] * 10000]
        kernel = obj_color_range["kernel"]
        hsv_lower = obj_color_range["lower"]
        hsv_upper = obj_color_range["upper"]

        print("########################")
        print(
            f"Hue: [{hsv_lower[0]}, {hsv_upper[0]}] \n Value: [{hsv_lower[1]}, {hsv_upper[1]}]\n Saturation: [{hsv_lower[2]}, {hsv_upper[2]}] \n Area: {area} \n Kernel: {kernel}"
        )
        print("########################")

        _, dilation = get_contour(img, hsv_lower, hsv_upper, area, (kernel, kernel))
        cv2.imshow("Contour", dilation)
        k = cv2.waitKey(1) & 0xFF
        if k == 27:
            break
    cv2.destroyAllWindows()


cv2.namedWindow("image", cv2.WINDOW_NORMAL)
cv2.resizeWindow("image", 600, 100)
cv2.createTrackbar("Hue Minimo", "image", 50, 255, lambda: None)
cv2.createTrackbar("Hue Maximo", "image", 150, 255, lambda: None)
cv2.createTrackbar("Value Minimo", "image", 50, 255, lambda: None)
cv2.createTrackbar("Value Maximo", "image", 150, 255, lambda: None)
cv2.createTrackbar("Saturation Minimo", "image", 50, 255, lambda: None)
cv2.createTrackbar("Saturation Maximo", "image", 150, 255, lambda: None)
cv2.createTrackbar("Kernel", "image", 0, 50, lambda: None)
cv2.createTrackbar("Area", "image", 0, 100, lambda: None)


if __name__ == "__main__":
    main()
