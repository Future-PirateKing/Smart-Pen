# Using Android IP Webcam video .jpg stream (tested) in Python2 OpenCV3
from cspaceSliders import FilterWindow
import urllib.request
import cv2
import numpy as np
import time

# Replace the URL with your own IPwebcam shot.jpg IP:port
url = "http://192.168.1.101:8080/shot.jpg"
fourcc = cv2.VideoWriter_fourcc(*'XVID')

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
    res = cv2.bitwise_and(img, img, mask=mask)

    kernel = np.ones((5, 5), np.uint8)
    dilation = cv2.dilate(mask, kernel, iterations=1)

    _, contours, hierarchy = cv2.findContours(dilation, cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE)

    if len(contours) > 0:
        cnt = contours[0]
        (x, y), radius = cv2.minEnclosingCircle(cnt)

        center = (int(x), int(y))
        radius = int(radius)

        cv2.circle(img, center, radius, (255, 0, 0), -1, 3)
        cv2.circle(dilation, center, radius, (255, 0, 0), -1, 3)

    # End of Processing #

    # put the image on screen

    cv2.imshow('IPWebcam', img)
    #cv2.imshow('mask', mask)
    #cv2.imshow('res', res)
    cv2.imshow('dilation', dilation)

    # To give the processor some less stress
     #time.sleep(0.1)

    # Quit if q is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

    '''
    print('Displaying the image with applied mask filtered in', colorspace,
          '\nwith lower bound', lowerb, 'and upper bound', upperb)
    '''