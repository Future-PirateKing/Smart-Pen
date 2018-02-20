# Using Android IP Webcam video .jpg stream (tested) in Python2 OpenCV3

from collections import deque
from cspaceSliders import FilterWindow
from selenium import webdriver
import argparse
import urllib.request
import cv2
import numpy as np
import time
import math

def move(ptX, ptY):
    ptX = ptX * ((((1366/864))/1366)*100)
    ptY = ptY * ((((768/480))/768)*100)
    print(ptX, ptY)
    move_ver = "document.getElementById('pointer').style.top = '" + str(ptY) + "%'"
    move_hor = "document.getElementById('pointer').style.left = '" + str(ptX) + "%'"
    driver.execute_script(move_hor)
    driver.execute_script(move_ver)

# construct the argument parse and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-b", "--buffer", type=int, default=32,
	help="max buffer size")
args = vars(ap.parse_args())

# Open Chrome and load the HTML file
driver = webdriver.Chrome()
driver.get('file:///C:/Users/Sam/Desktop/SamDavid/BE Project/index.html')

# Replace the URL with your own IPwebcam shot.jpg IP:port
url = "http://192.168.43.1:8080/shot.jpg"


# initialize the list of tracked points, the frame counter,
# and the coordinate deltas
pts = deque(maxlen=args["buffer"])
counter = 0
(dX, dY) = (0, 0)
direction = ""


while True:
    # Use urllib to get the image from the IP camera
    imgResp = urllib.request.urlopen(url)

    # Numpy to convert into a array
    imgNp = np.array(bytearray(imgResp.read()), dtype=np.uint8)

    # Finally decode the array to OpenCV usable format ;)
    img = cv2.imdecode(imgNp, -1)

    '''
    window = FilterWindow('Filter Window', img)
    window.show(verbose=True)

    colorspace = window.colorspace
    lowerb, upperb = window.bounds
    mask = window.mask
    applied_mask = window.applied_mask
    '''

    # This where the code for processing of video starts #

    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    lower_red = np.array([21, 0, 255])
    upper_red = np.array([179, 21, 255])

    mask = cv2.inRange(hsv, lower_red, upper_red)
    #mask = cv2.erode(mask, None, iterations=2)
    mask = cv2.dilate(mask, None, iterations=2)


    _, cnts, hierarchy = cv2.findContours(mask, cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE)
    center = None

    # only proceed if at least one contour was found
    if len(cnts) > 0:
        # find the largest contour in the mask, then use
        # it to compute the minimum enclosing circle and
        # centroid
        c = max(cnts, key=cv2.contourArea)
        ((x, y), radius) = cv2.minEnclosingCircle(c)
        M = cv2.moments(c)
        center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))

        # only proceed if the radius meets a minimum size

        # draw the circle and centroid on the frame,
        # then update the list of tracked points
        cv2.circle(img, (int(x), int(y)), int(radius),
                       (0, 255, 255), 2)
        cv2.circle(img, center, 5, (0, 0, 255), -1)
        pts.appendleft(center)

        move(pts[0][0], pts[0][1])

    # loop over the set of tracked points
    for i in np.arange(1, len(pts)):
        # if either of the tracked points are None, ignore
        # them
        if pts[i - 1] is None or pts[i] is None:
            continue

        # check to see if enough points have been accumulated in
        # the buffer
        try: 
            if counter >= 10 and i == 1 and pts[-10] is not None:
                # compute the difference between the x and y
                # coordinates and re-initialize the direction
                # text variables
                dX = pts[-10][0] - pts[i][0]
                dY = pts[-10][1] - pts[i][1]
                (dirX, dirY) = ("", "")

                # ensure there is significant movement in the
                # x-direction
                if np.abs(dX) > 20:
                    dirX = "East" if np.sign(dX) == 1 else "West"

                # ensure there is significant movement in the
                # y-direction
                if np.abs(dY) > 20:
                    dirY = "North" if np.sign(dY) == 1 else "South"

                # handle when both directions are non-empty
                if dirX != "" and dirY != "":
                    direction = "{}-{}".format(dirY, dirX)

                # otherwise, only one direction is non-empty
                else:
                    direction = dirX if dirX != "" else dirY
        except IndexError:
            time.sleep(0.000001)

        # otherwise, compute the thickness of the line and
        # draw the connecting lines
        thickness = int(np.sqrt(args["buffer"] / float(i + 1)) * 2.5)
        cv2.line(img, pts[i - 1], pts[i], (0, 0, 255), thickness)

    # show the movement deltas and the direction of movement on
    # the frame
    cv2.putText(img, direction, (10, 30), cv2.FONT_HERSHEY_SIMPLEX,
                0.65, (0, 0, 255), 3)
    cv2.putText(img, "dx: {}, dy: {}".format(dX, dY),
                (10, img.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX,
                0.35, (0, 0, 255), 1)
    # End of Processing #

    # put the image on screen

    cv2.imshow('IPWebcam', img)
    #cv2.imshow('mask', mask)
    key = cv2.waitKey(1) & 0xFF
    counter += 1

    # To give the processor some less stress
     #time.sleep(0.1)

    # Quit if q is pressed
    if key == ord('q'):
        break

    '''
    print('Displaying the image with applied mask filtered in', colorspace,
          '\nwith lower bound', lowerb, 'and upper bound', upperb)
    '''