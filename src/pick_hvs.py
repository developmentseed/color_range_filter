import cv2
import imutils
import numpy as np
import sys
import click

image_hsv = None
pixel = (20, 60, 80)
# mouse callback function


def pick_color(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:
        pixel = image_hsv[y, x]
        # you might want to adjust the ranges(+-10, etc):
        # range_pixels = 10
        upper = np.array([pixel[0] + range_pixels, pixel[1] + range_pixels, pixel[2] + range_pixels])
        lower = np.array([pixel[0] - range_pixels, pixel[1] - range_pixels, pixel[2] - range_pixels])

        # print(pixel, lower, upper)
        print("######################## Max and Min")
        print(f"--hue={lower[0]},{upper[0]} \\")
        print(f"--saturation={lower[2]},{upper[2]} \\")
        print(f"--value={lower[1]},{upper[1]} \\")

        kernel = (2, 2)
        image_mask = cv2.inRange(image_hsv, lower, upper)
        kernel = np.ones(kernel, np.uint8)
        erosion = cv2.erode(image_mask, kernel, iterations=2)
        dilation = cv2.dilate(erosion, kernel, iterations=2)

        cv2.imshow("mask", image_mask)
        cv2.imshow("dilation", dilation)


@click.command(short_help="Get range color from images")
@click.option("--image_file", type=str)
def main(image_file):
    global image_hsv, pixel
    img = cv2.imread(image_file)

    img = imutils.resize(img, height=img.shape[0])
    cv2.imshow("bgr", img)
    cv2.namedWindow("hsv")
    cv2.setMouseCallback("hsv", pick_color)

    image_hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    cv2.imshow("hsv", image_hsv)

    # Terminate windows
    while True:
        k = cv2.waitKey(1) & 0xFF
        if k == 27:
            break
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
