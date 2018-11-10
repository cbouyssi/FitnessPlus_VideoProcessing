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


def save_object(obj, filename):
    """Saves a given object under a given filename (.pkl)
    ----------
    obj: any type
        Name of the object we want to save
    filename: String
        Name of the pickle file the object we will be saved in
    """
    with open(filename, 'wb') as output:
        pickle.dump(obj, output, -1)
    output.close()

def open_object(filename):
    """Opens a given object under a given filename (.pkl)
    ----------
    filename: String
        Name of the pickle file the object we will be saved in
    Returns
    -------
    obj: depends on the object type stored under the filename
        object stored under the filename
    """
    with open(filename, 'rb') as pck_file:
        obj = pickle.load(pck_file)
    pck_file.close()
    return obj

def make_clean(frames=False, variables=False, trainings=False, all_data=False):
    """Clean the folders"""
    if all_data:
        rmtree('data', ignore_errors=True)
        rmtree('config/models/training', ignore_errors=True)
        sys.exit('Cleaning performed.')
    rmtree('data/key_frames_box', ignore_errors=True)
    rmtree('data/output_events_box', ignore_errors=True)
    rmtree('data/objects_images', ignore_errors=True)
    rmtree('data/heatmaps', ignore_errors=True)
    if variables:
        rmtree('data/saved_variables', ignore_errors=True)
    if frames:
        rmtree('data/frames_vid', ignore_errors=True)
    if trainings:
        rmtree('config/models/training', ignore_errors=True)

def file_to_categories(filename):
    """Read a file with one category per line and return a list containing them."""
    with open(filename) as classes_file:
        class_idx = classes_file.readlines()
    return [c.strip() for c in class_idx]

def vid_to_frames(vid_path, frames_path, idx):
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
    fps /= fps
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


def bb_intersection_over_union(boxA, boxB):
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
	boxBArea = (boxB[2] - boxB[0] + 1) * (boxB[3] - boxB[1] + 1)

	# compute the intersection over union by taking the intersection
	# area and dividing it by the sum of prediction + ground-truth
	# areas - the interesection area
	iou = interArea / float(boxAArea + boxBArea - interArea)

	# return the intersection over union value
	return iou

def atof(text):
    try:
        retval = float(text)
    except ValueError:
        retval = text
    return retval

def natural_keys(text):

    return [ atof(c) for c in re.split(r'[+-]?([0-9]+(?:[.][0-9]*)?|[.][0-9]+)', text) ]
    
