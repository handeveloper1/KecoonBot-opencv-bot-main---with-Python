from math import pi
from operator import truediv
from string import printable
import cv2 as cv
import numpy as np
import os
import os.path
import win32api, win32con
from numpy.lib.shape_base import tile
from PIL import ImageGrab
from windowcapture import WindowCapture
import keyboard
import time
from math import sqrt
import random
import win32gui, win32ui, win32con





os.chdir(os.path.dirname(os.path.abspath(__file__)))

# List all windows headers for headers.txt
def ListWindowNames():
    def winEnumHandler(hwnd, ctx):
        if win32gui.IsWindowVisible(hwnd):
            print(win32gui.GetWindowText(hwnd))
    win32gui.EnumWindows(winEnumHandler, None)



def findClickPositions(needle_img_path, haystack_img, threshold, debug_mode=None):

    # https://docs.opencv.org/4.2.0/d4/da8/group__imgcodecs.html

    needle_img = cv.imread(needle_img_path, cv.IMREAD_UNCHANGED)
    locations = []
    # Save the dimensions of the needle image

    needle_w = needle_img.shape[1]
    needle_h = needle_img.shape[0]




    # There are 6 methods to choose from:
    # TM_CCOEFF, TM_CCOEFF_NORMED, TM_CCORR, TM_CCORR_NORMED, TM_SQDIFF, TM_SQDIFF_NORMED
    method = cv.TM_CCOEFF_NORMED
    result = cv.matchTemplate(haystack_img, needle_img, method)

    # Get the all the positions from the match result that exceed our threshold
    locations = np.where(result >= threshold)
    locations = list(zip(*locations[::-1]))
    # print(locations)

    # You'll notice a lot of overlapping rectangles get drawn. We can eliminate those redundant
    # locations by using groupRectangles().
    # First we need to create the list of [x, y, w, h] rectangles
    rectangles = []
    for loc in locations:
        rect = [int(loc[0]), int(loc[1]), needle_w, needle_h]
        # Add every box to the list twice in order to retain single (non-overlapping) boxes
        rectangles.append(rect)
        rectangles.append(rect)
    # Apply group rectangles.
    # The groupThreshold parameter should usually be 1. If you put it at 0 then no grouping is
    # done. If you put it at 2 then an object needs at least 3 overlapping rectangles to appear
    # in the result. I've set eps to 0.5, which is:
    # "Relative difference between sides of the rectangles to merge them into a group."
    rectangles, weights = cv.groupRectangles(rectangles, groupThreshold=1, eps=0.5)
    #print(rectangles)

    points = []
    if len(rectangles):
        #print('Found needle.')

        line_color = (0, 255, 0)
        line_type = cv.LINE_4
        marker_color = (255, 0, 255)
        marker_type = cv.MARKER_CROSS

        # Loop over all the rectangles
        for (x, y, w, h) in rectangles:

            # Determine the center position
            center_x = x + int(w/2)
            center_y = y + int(h/2)
            # Save the points
            points.append((center_x, center_y))

            if debug_mode == 'rectangles':
                # Determine the box position
                top_left = (x, y)
                bottom_right = (x + w, y + h)
                # Draw the box
                cv.rectangle(haystack_img, top_left, bottom_right, color=line_color, 
                             lineType=line_type, thickness=2)
            elif debug_mode == 'points':
                # Draw the center point
                cv.drawMarker(haystack_img, (center_x, center_y), 
                              color=marker_color, markerType=marker_type, 
                              markerSize=20, thickness=2)

        #if debug_mode:
            # cv.imshow('Matches', haystack_img)
            # cv.waitKey()
            # cv.imwrite('result_click_point.jpg', haystack_img)

    return points


def tryAllHeaders():
    file = open("headers.txt","r")
    headers = []
    for header in file:
        clearheader = header.replace('\n','')
        headers.append(clearheader)
        # print(headers)
    for header in headers:
        try:
            wincap = WindowCapture(header)
            return header
            break
        except:
            continue

def findmob(wincap,header,mobTreshold):
    file = open("imgdata.txt","r")
    mobs = []
    for mob in file:
        clearmob = mob.replace('\n','')
        mobs.append(clearmob)
    for mob in mobs:
        screen = wincap.get_screenshot()
        points = findClickPositions(mob, screen,mobTreshold, debug_mode='points'  )
        if (len(points)>0):

            return mob
            break



char = "char.jpg"
i = 0
missingWindowHeight = 110
mobTreshold = 0.6
playerTreshold = 0.6

# Try All headers
header = tryAllHeaders()
wincap = WindowCapture(header)
# Find Correct mob
correctmob = findmob(wincap, header, mobTreshold)
loop_time = time.time()
while keyboard.is_pressed('end') == False:
    try:


        screen = wincap.get_screenshot()

        mobPoints = findClickPositions(correctmob, screen, mobTreshold, debug_mode='rectangles')
        print(mobPoints)
        playerLocation = findClickPositions(char, screen, playerTreshold, debug_mode='points')
      

        cv.imshow("Points", screen)
        cv.waitKey(5)
        i += 1

    except:
        print("Cant find mob or character")
