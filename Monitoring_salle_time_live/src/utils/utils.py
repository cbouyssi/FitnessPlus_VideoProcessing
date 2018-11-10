"""
Deep learning for efficient video surveillance segmentation, indexing and retrieval.

@author: Tom
"""

import os
import sys
import pickle
from shutil import rmtree
import cv2
import re

def bb_intersection(boxA, boxB):
    # print("person : ",boxA)
    # print("machine : ",boxB)
    # determine the (x, y)-coordinates of the intersection rectangle
    xA = max(boxA[0], boxB[0])
    yA = max(boxA[1], boxB[1])
    xB = min(boxA[2], boxB[2])
    yB = min(boxA[3], boxB[3])
    # compute the area of intersection rectangle
    interArea = max(0, xB - xA + 1) * max(0, yB - yA + 1)
    # compute the area of both the prediction and ground-truth
    # rectangles
    boxAArea = (boxA[2] - boxA[0] + 1) * (boxA[3] - boxA[1] + 1)
	# print(xA,yA,xB,yB)
	# print("interArea :",interArea)
	# print("boxAArea :",boxAArea)

	# compute the intersection over union by taking the intersection
	# area and dividing it by the sum of prediction + ground-truth
	# areas - the interesection area
    iou = interArea / float(boxAArea )
	# return the intersection over union value
    return iou

def init_video(vid_path):
    """Convert video files to images and save them into the specified path.
    ----------
    vid_path: String
        Path to the video we want to extract the frames from
    frames_path: String
        Path to the folder where we want the frames from the video to be saved in.
    idx: int
        Index we want for the first frame of the video. (useful when you
        convert several videos to avoid name conflicts)
    Returns
    -------
    idx-1: int
        Index of the last frame of the video. (useful when you
        convert several videos to avoid name conflicts)
    fps: float
        Frames per second in the video
    ---------
    """
    vidcap = cv2.VideoCapture(vid_path)
    if(vidcap.isOpened()) :
        print("video opened")
    else :
        vidcap.open()

    fps = vidcap.get(cv2.CAP_PROP_FPS)
    if fps > my_fps :
        fps =my_fps
    fps /= 5
    '''
    J'arrondis fps sinon je vois pas comment le modulo fps peux marcher
    '''
    fps=round(fps)

    success, image = vidcap.read()
    success = True
    while success:
        if idx%1000 == 0:
            print(idx)
        if idx%fps == 0:
            print(idx)

            cv2.imwrite(os.path.join(frames_path, "frame%d.jpg" % idx), image)
        success, image = vidcap.read()
        idx += 1
    return idx-1, fps

def comp_person(out_classes) :
    comp_p=0
    for i, c in reversed(list(enumerate(out_classes))):
        if c==0 :
            comp_p+=1
    return comp_p
