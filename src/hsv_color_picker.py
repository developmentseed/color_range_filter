import cv2
import numpy as np
import sys
import click

image_hsv = None
pixel = (0,0,0) #RANDOM DEFAULT VALUE

def check_boundaries(value, tolerance, ranges, upper_or_lower):
    if ranges == 0:
        # set the boundary for hue
        boundary = 180
    elif ranges == 1:
        # set the boundary for saturation and value
        boundary = 255

    if(value + tolerance > boundary):
        value = boundary
    elif (value - tolerance < 0):
        value = 0
    else:
        if upper_or_lower == 1:
            value = value + tolerance
        else:
            value = value - tolerance
    return value

def pick_color(event,x,y,flags,param):
    if event == cv2.EVENT_LBUTTONDOWN:
        pixel = image_hsv[y,x]

        #HUE, SATURATION, AND VALUE (BRIGHTNESS) RANGES. TOLERANCE COULD BE ADJUSTED.
        # Set range = 0 for hue and range = 1 for saturation and brightness
        # set upper_or_lower = 1 for upper and upper_or_lower = 0 for lower
        hue_upper = check_boundaries(pixel[0], 10, 0, 1)
        hue_lower = check_boundaries(pixel[0], 10, 0, 0)
        saturation_upper = check_boundaries(pixel[1], 10, 1, 1)
        saturation_lower = check_boundaries(pixel[1], 10, 1, 0)
        value_upper = check_boundaries(pixel[2], 40, 1, 1)
        value_lower = check_boundaries(pixel[2], 40, 1, 0)

        upper =  np.array([hue_upper, saturation_upper, value_upper])
        lower =  np.array([hue_lower, saturation_lower, value_lower])
        print(lower, upper)

        #A MONOCHROME MASK FOR GETTING A BETTER VISION OVER THE COLORS 
        image_mask = cv2.inRange(image_hsv,lower,upper)
        
        kernel = (2, 2)
        image_mask = cv2.inRange(image_hsv, lower, upper)
        kernel = np.ones(kernel, np.uint8)
        erosion = cv2.erode(image_mask, kernel, iterations=2)
        dilation = cv2.dilate(erosion, kernel, iterations=2)

        cv2.imshow("Mask",image_mask)
        cv2.imshow("Dilation",dilation)

@click.command(short_help="Get range color from images")
@click.option("--image_file", type=str)
def main(image_file):

    global image_hsv, pixel
    image_src = cv2.imread(image_file)
    cv2.imshow("BGR",image_src)

    #CREATE THE HSV FROM THE BGR IMAGE
    image_hsv = cv2.cvtColor(image_src,cv2.COLOR_BGR2HSV)
    cv2.imshow("HSV",image_hsv)

    #CALLBACK FUNCTION
    cv2.setMouseCallback("HSV", pick_color)

    # Terminate windows
    while True:
        k = cv2.waitKey(1) & 0xFF
        if k == 27:
            break
    cv2.destroyAllWindows()

if __name__=='__main__':
    main()