"""
Deep learning for efficient video surveillance segmentation, indexing and retrieval.

@author: Tom
"""

import os
import time
import argparse
import glob
from shutil import copyfile
from keras.models import Model, load_model
from src.yolov2.yolo_utils import decode_predictions
from src.utils.utils import save_object, open_object, make_clean, vid_to_frames,\
                            file_to_categories, atof,natural_keys
from test_yolo import model_prediction_framing
from test_yolo_person import model_prediction_person



def get_args():
    """Declare possible command lines parameters."""
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', "--img", help="Scene Image path", default='.')
    parser.add_argument('-o', "--obj", help="Object image path", default='.')
    parser.add_argument('-c', "--cat", help="Retrieval by category parameter",
                        default='.')
    parser.add_argument('-v', "--vid",
                        help="Path to video we want to convert to frames and analyse",
                        default=0)

    parser.add_argument('-clean', "--cln",
                        help="Set to 1 to clean the folders from all output images, \
                        change the parameters in the function to parameter the \
                        removed folders. Set to 2 if you just want to suppress \
                        all data except code and config files and not run the \
                        program.",
                        default=0)
    args = parser.parse_args()
    return args


if __name__ == '__main__':

    args = get_args()

    if int(args.cln) == 1:
        make_clean()
    if int(args.cln) == 2:
        make_clean(all_data=True)

    #models_path = 'config/models/'
    models_path=os.path.expanduser("model_data/yolo.h5")
    # frames_path = 'data/frames_full_vid/'
    frames_path = 'data/frames_vid_tom/'
    savings_path = 'data/saved_variables/'


    if os.path.isdir(savings_path) is False:
        os.makedirs(savings_path)
    if os.path.isdir(frames_path) is False:
        os.makedirs(frames_path)


    if args.vid:
        nb_img = 0
        for vid in glob.glob(os.path.expanduser(args.vid + '/*.mp4')):
            print("vid",vid)
            nb_img, fps = vid_to_frames(vid, frames_path, nb_img)
            print(nb_img, fps)
            #save_object(int(fps), savings_path+'fps.pkl')
        # save_object(int(fps), savings_path+'fps.pkl')

    # model_prediction_framing()
    model_prediction_person()
