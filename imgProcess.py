import cv2 as cv
import numpy as np


class imgProcess:

    # properties
    imgToFind = None
    needle_w = 0
    needle_h = 0
    method = None
    # constructor
    def __init__(self, imgToFind_path):
        # load the image we're trying to match
        # https://docs.opencv.org/4.2.0/d4/da8/group__imgcodecs.html
        self.imgToFind = cv.imread(imgToFind_path, cv.IMREAD_UNCHANGED)

        # Save the dimensions of the needle image
        self.needle_w = self.imgToFind.shape[1]
        self.needle_h = self.imgToFind.shape[0]

        # There are 6 methods to choose from:
        # TM_CCOEFF, TM_CCOEFF_NORMED, TM_CCORR, TM_CCORR_NORMED, TM_SQDIFF, TM_SQDIFF_NORMED
        self.method = cv.TM_CCOEFF_NORMED

    def find(self, imgSource, threshold=0.5, debug_mode=None):
        # run the OpenCV algorithm
        result = cv.matchTemplate(imgSource, self.imgToFind, self.method)

        # Get the all the positions from the match result that exceed our threshold
        locations = np.where(result >= threshold)
        locations = list(zip(*locations[::-1]))
        #print(locations)

        # You'll notice a lot of overlapping rectangles get drawn. We can eliminate those redundant
        # locations by using groupRectangles().
        # First we need to create the list of [x, y, w, h] rectangles
        rectangles = []
        for loc in locations:
            rect = [int(loc[0]), int(loc[1]), self.needle_w, self.needle_h]
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

        # points = []
        dectected=0
        if len(rectangles):
            for (x, y, w, h) in rectangles:
                dectected+=1

                # Determine the center position
                # center_x = x + int(w/2)
                # center_y = y + int(h/2)
                # Save the points
                # points.append((center_x, center_y))

                    # Determine the box position
                    # top_left = (x, y)
                    # bottom_right = (x + w, y + h)
                    # Draw the box
                cv.rectangle(imgSource,(x,y),(x+w,y+h),color=(0,0,255),lineType=cv.LINE_4,thickness=2)
        

        # if debug_mode:
        #     a = cv.imshow('Watch Rat', imgSource) 
        #     #cv.waitKey()
        #     #cv.imwrite('result_click_point.jpg', imgSource)
        return dectected
