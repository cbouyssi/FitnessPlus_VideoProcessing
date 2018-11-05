"""
Deep learning for efficient video surveillance segmentation, indexing and retrieval.

@author: Tom

source : YAD2K
"""

import os
import colorsys
import random
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import tensorflow as tf
from keras import backend as K
from keras.preprocessing import image as kimage
import cv2
from src.utils.utils import file_to_categories

CLASSES_PATH = 'config/coco_classes.txt'
ANCHORS_PATH = 'config/yolo_anchors.txt'
SCORE_THRESHOLD = 0.4
IOU_THRESHOLD = 0.2
TARGET_SHAPE = [608, 608]
HEATMAP_CLASSE = None

def get_features(img, model):
    """Return features of an image from the specified model."""
    if len(np.shape(img)) < 4:
        img = np.expand_dims(img, axis=0)
    features = model.predict(img)
    return features

def save_img_obj(img, path, obj_shape=(64, 64)):
    """Resize and save the given image in the specific path."""
    img = cv2.resize(img, obj_shape)
    cv2.imwrite(path, img)

def img_padding(img):
    #TODO see if really needed. Maybe look for YOLO training performed
    """Pad the image in order to make it match the required size of
    YOLOv2 without deforming it."""
    old_size = img.size
    ratio = float(TARGET_SHAPE[0])/max(old_size)
    new_size = tuple([int(x*ratio) for x in old_size])
    img = img.resize(new_size, Image.ANTIALIAS)
    new_im = Image.new("RGB", TARGET_SHAPE)
    new_im.paste(img, (int((TARGET_SHAPE[0]-new_size[0])/2),
                       int((TARGET_SHAPE[1]-new_size[1])/2)))
    new_im = kimage.img_to_array(new_im)
    return new_im

def img_preprocessing(img_path, crop=None):
    """Preprocess the img by performing the cropping and the padding."""
    img = Image.open(img_path)
    if crop:
        img = img.crop(
            (
                crop[0],
                crop[1],
                crop[2],
                crop[3]
            )
        )
    img = img_padding(img)
    # img = img.resize((416,416), Image.ANTIALIAS)
    # img = kimage.img_to_array(img)
    img /= 255.
    return img

def bbox_center(bbox):
    """Return bbox center from bbox coordinate in the form (left, top
    right, bottom)."""
    return [bbox[0]+(bbox[2]-bbox[0])/2, bbox[1]+(bbox[3]-bbox[1])/2]

def img_evaluation(yolo_model, model_ftrs, img_path, output_path, crop=None):
    #TODO see if returns are really needed or if we create a kf structure
    # for the image
    """Perform YOLO prediction on the given image, extract objects in it
    and compute their feature maps.
    Parameters
    ----------
    yolo_model : keras.model.Model
        YOLOv2 model used for the prediction
    model_ftrs : keras.model.Model
        List containing the index of the frames that contains events to make the
        predictions for them
    img_path : String
        Path to the evaluated image.
    output_path : String
        Path to the folder we want the images with the predictions to be stored
        in.
    Returns
    -------
    preds : list
        Predictions results from YOLOv2 for the image.
    ftrs_obj: list
        List of object features in the image.
    """
    base_img = cv2.imread(img_path)

    if os.path.isdir(output_path) is False:
        os.makedirs(output_path)

    img = img_preprocessing(img_path, crop=crop)

    dict_fr = {0:get_features(img, yolo_model)}
    preds = decode_predictions(dict_fr, image_path=os.path.dirname(img_path),
                               output_path=output_path)

    ftrs_obj = []
    i = 0
    for obj in preds[0]:
        sub = base_img[int(obj[1][1]):int(obj[1][3]),
                       int(obj[1][0]):int(obj[1][2])]
        save_img_obj(sub, os.path.join(output_path, str(i)+'.jpg'))

        img_obj = kimage.load_img(os.path.join(output_path, str(i)+'.jpg'))
        img_obj = kimage.img_to_array(img_obj)
        img_obj /= 255.
        ftrs_obj.append(get_features(img_obj, model_ftrs))
        i += 1
    return preds, ftrs_obj

def decode_predictions(dict_ftrs, target_crop = None,
                       heatmap=None,
                       image_path='data/frames_vid',
                       output_path='data/output_events_box'):
    """Gives YOLOv2 outputs thanks to the feature maps for frames with index in
    idx_events.
    Parameters
    ----------
    dict_ftrs : dict
        Contains features from images with detected events in the video
    heatmap : boolean
        Set to true if you want to predict a heatmap for the frames with events,
        may need to specify the category directly in the code
    image_path : String
        Path to the folder with all images containing events in it
    output_path : String
        Path to the folder we want the imges with the predictions to be stored
        in
    Returns
    -------
    res : list
        List of all object that appeared in the frames with event (one element
        corresponds to one frame)
    """
    if os.path.isdir(output_path) is False:
        os.makedirs(output_path)

    if heatmap is not None:
        if os.path.isdir('data/heatmaps') is False:
            os.makedirs('data/heatmaps')
        global HEATMAP_CLASSE
        HEATMAP_CLASSE = heatmap

    sess = K.get_session()

    #modification
    #yolo_out = K.placeholder(shape=(None, 13, 13, 425))
    yolo_out = K.placeholder(shape=(1, 19, 19, 425))

    class_names = file_to_categories(CLASSES_PATH)

    with open(ANCHORS_PATH) as anchor_file:
        anchors = anchor_file.readline()
        anchors = [float(x) for x in anchors.split(',')]
        anchors = np.array(anchors).reshape(-1, 2)

    # Generate colors for drawing bounding boxes.
    hsv_tuples = [(x / len(class_names), 1., 1.)
                  for x in range(len(class_names))]
    colors = list(map(lambda x: colorsys.hsv_to_rgb(*x), hsv_tuples))
    colors = list(
        map(lambda x: (int(x[0] * 255), int(x[1] * 255), int(x[2] * 255)),
            colors))
    random.seed(10101)  # Fixed seed for consistent colors across runs.
    random.shuffle(colors)  # Shuffle colors to decorrelate adjacent classes.
    random.seed(None)  # Reset seed to default.

    yolo_outputs = yolo_head(yolo_out, anchors, len(class_names))
    input_img_shape = K.placeholder(shape=(2, ))
    boxes, scores, classes, heatmap_score = yolo_eval(
        yolo_outputs,
        input_img_shape,
        HEATMAP_CLASSE,
        score_threshold=SCORE_THRESHOLD,
        iou_threshold=IOU_THRESHOLD)

    res = []
    if target_crop is None:
        wdt, hgt = Image.open(os.path.join(image_path, 'frame%d.jpg'% 0)).size
        target_crop = [0, 0, wdt, hgt]
    # Values needed to project predictions on the original images
    ratio = float(TARGET_SHAPE[0])/max([target_crop[2]-target_crop[0],
                                        target_crop[3]-target_crop[1]])
    new_size = tuple([int(x*ratio) for x in [target_crop[2]-target_crop[0],
                                             target_crop[3]-target_crop[1]]])
    offsets = [(TARGET_SHAPE[0]-new_size[0])/2, (TARGET_SHAPE[0]-new_size[1])/2]

    for idx in list(dict_ftrs.keys()):
        key_image = Image.open(os.path.join(image_path, 'frame%d.jpg'% idx))
        out_boxes, out_scores, out_classes, out_heatmap = sess.run(
            [boxes, scores, classes, heatmap_score],
            feed_dict={
                yolo_out : dict_ftrs[idx],
                input_img_shape: TARGET_SHAPE,
                K.learning_phase(): 0
                })
        # print('Found {} boxes for {}'.format(len(out_boxes), image_file))

        font = ImageFont.truetype(
            font='config/font/FiraMono-Medium.otf',
            size=np.floor(3e-2 * key_image.size[1] + 0.5).astype('int32'))

        thickness = (key_image.size[0] + key_image.size[1]) // 300
        inter_res = []

        if heatmap is not None:
            #modification avant cetait 13
            out_heatmap = np.reshape(out_heatmap, (19, 19, 5))
            hmp = np.zeros((19, 19))
            for i in range(19):
                for j in range(19):
                    hmp[i][j] = sum(out_heatmap[i][j][:])
            hmp = hmp*255
            img = cv2.resize(hmp, (416, 416))
            img = img.astype(np.uint8)
            img_heq = img
            # img_heq = cv2.equalizeHist(img)
            img_name = str(idx)+'heq.jpg'
            cv2.imwrite(os.path.join('data/heatmaps', img_name), img_heq)

        for i, c in reversed(list(enumerate(out_classes))):
            predicted_class = class_names[c]
            box = out_boxes[i]
            score = out_scores[i]
            label = '{} {:.2f}'.format(predicted_class, score)
            draw = ImageDraw.Draw(key_image)
            label_size = draw.textsize(label, font)
            top, left, bottom, right = box
            top = max(0, np.floor(top + 0.5).astype('int32'))
            left = max(0, np.floor(left + 0.5).astype('int32'))
            bottom = min(TARGET_SHAPE[1], np.floor(bottom + 0.5).astype('int32'))
            right = min(TARGET_SHAPE[0], np.floor(right + 0.5).astype('int32'))
            top = (top-offsets[1])/ratio + target_crop[1]
            bottom = (bottom-offsets[1])/ratio + target_crop[1]
            left = (left-offsets[0])/ratio + target_crop[0]
            right = (right-offsets[0])/ratio + target_crop[0]
            inter_res.append([label.rsplit(' ', 1), (left, top, right, bottom)])
            if top - label_size[1] >= 0:
                text_origin = np.array([left, top - label_size[1]])
            else:
                text_origin = np.array([left, top + 1])
            for j in range(thickness):
                draw.rectangle(
                    [left + j, top + j, right - j, bottom - j],
                    outline=colors[c])
            draw.rectangle(
                [tuple(text_origin), tuple(text_origin + label_size)],
                fill=colors[c])
            draw.text(text_origin, label, fill=(0, 0, 0), font=font)
            del draw

        key_image.save(os.path.join(output_path, 'frame%d.jpg'% idx), quality=90)
        res.append(inter_res)

    return res

def yolo_head(feats, anchors, num_classes):
    """Convert final layer features to bounding box parameters.

    Parameters
    ----------
    feats : tensor
        Final convolutional layer features.
    anchors : array-like
        Anchor box widths and heights.
    num_classes : int
        Number of target classes.

    Returns
    -------
    box_xy : tensor
        x, y box predictions adjusted by spatial location in conv layer.
    box_wh : tensor
        w, h box predictions adjusted by anchors and conv spatial resolution.
    box_conf : tensor
        Probability estimate for whether each box contains any object.
    box_class_pred : tensor
        Probability distribution estimate for each box over class labels.
    """
    num_anchors = len(anchors)
    # Reshape to batch, height, width, num_anchors, box_params.
    anchors_tensor = K.reshape(K.variable(anchors), [1, 1, 1, num_anchors, 2])

    # Static implementation for fixed models.
    # TODO: Remove or add option for static implementation.
    # _, conv_height, conv_width, _ = K.int_shape(feats)
    # conv_dims = K.variable([conv_width, conv_height])

    # Dynamic implementation of conv dims for fully convolutional model.
    conv_dims = K.shape(feats)[1:3]  # assuming channels last
    # In YOLO the height index is the inner most iteration.
    conv_height_index = K.arange(0, stop=conv_dims[0])
    conv_width_index = K.arange(0, stop=conv_dims[1])
    conv_height_index = K.tile(conv_height_index, [conv_dims[1]])

    # TODO: Repeat_elements and tf.split doesn't support dynamic splits.
    # conv_width_index = K.repeat_elements(conv_width_index, conv_dims[1], axis=0)
    conv_width_index = K.tile(
        K.expand_dims(conv_width_index, 0), [conv_dims[0], 1])
    conv_width_index = K.flatten(K.transpose(conv_width_index))
    conv_index = K.transpose(K.stack([conv_height_index, conv_width_index]))
    conv_index = K.reshape(conv_index, [1, conv_dims[0], conv_dims[1], 1, 2])
    conv_index = K.cast(conv_index, K.dtype(feats))

    feats = K.reshape(
        feats, [-1, conv_dims[0], conv_dims[1], num_anchors, num_classes + 5])
    conv_dims = K.cast(K.reshape(conv_dims, [1, 1, 1, 1, 2]), K.dtype(feats))

    # Static generation of conv_index:
    # conv_index = np.array([_ for _ in np.ndindex(conv_width, conv_height)])
    # conv_index = conv_index[:, [1, 0]]  # swap columns for YOLO ordering.
    # conv_index = K.variable(
    #     conv_index.reshape(1, conv_height, conv_width, 1, 2))
    # feats = Reshape(
    #     (conv_dims[0], conv_dims[1], num_anchors, num_classes + 5))(feats)

    box_xy = K.sigmoid(feats[..., :2])
    box_wh = K.exp(feats[..., 2:4])
    box_confidence = K.sigmoid(feats[..., 4:5])
    box_class_probs = K.softmax(feats[..., 5:])

    # Adjust preditions to each spatial grid point and anchor size.
    # Note: YOLO iterates over height index before width index.
    box_xy = (box_xy + conv_index) / conv_dims
    box_wh = box_wh * anchors_tensor / conv_dims

    return box_xy, box_wh, box_confidence, box_class_probs

def yolo_eval(yolo_outputs,
              image_shape,
              heatmap_classe,
              max_boxes=10,
              score_threshold=.6,
              iou_threshold=.5
             ):
    """Evaluate YOLO model on given input batch and return filtered boxes
    and heatmap scores."""
    box_xy, box_wh, box_confidence, box_class_probs = yolo_outputs
    boxes = yolo_boxes_to_corners(box_xy, box_wh)
    boxes, scores, classes = yolo_filter_boxes(
        boxes, box_confidence, box_class_probs, threshold=score_threshold)

    # Scale boxes back to original image shape.
    height = image_shape[0]
    width = image_shape[1]
    image_dims = K.stack([height, width, height, width])
    image_dims = K.reshape(image_dims, [1, 4])
    boxes = boxes * image_dims

    # TODO: Something must be done about this ugly hack!
    max_boxes_tensor = K.variable(max_boxes, dtype='int32')
    K.get_session().run(tf.variables_initializer([max_boxes_tensor]))
    nms_index = tf.image.non_max_suppression(
        boxes, scores, max_boxes_tensor, iou_threshold=iou_threshold)
    boxes = K.gather(boxes, nms_index)
    scores = K.gather(scores, nms_index)
    classes = K.gather(classes, nms_index)
    heatmap_score = heatmap_sc(box_confidence, box_class_probs, heatmap_classe)
    return boxes, scores, classes, heatmap_score

def heatmap_sc(box_confidence, box_class_probs, classe):
    """Return hetmap scores for the given category """
    box_scores = box_confidence * box_class_probs
    classes_score = tf.map_fn(lambda x: x[..., classe], box_scores)
    return classes_score

def yolo_filter_boxes(boxes, box_confidence, box_class_probs, threshold=.6):
    """Filter YOLO boxes based on object and class confidence."""
    box_scores = box_confidence * box_class_probs
    box_classes = K.argmax(box_scores, axis=-1)
    box_class_scores = K.max(box_scores, axis=-1)
    prediction_mask = box_class_scores >= threshold

    # TODO: Expose tf.boolean_mask to Keras backend?
    boxes = tf.boolean_mask(boxes, prediction_mask)
    scores = tf.boolean_mask(box_class_scores, prediction_mask)
    classes = tf.boolean_mask(box_classes, prediction_mask)
    return boxes, scores, classes

def yolo_boxes_to_corners(box_xy, box_wh):
    """Convert YOLO box predictions to bounding box corners."""
    box_mins = box_xy - (box_wh / 2.)
    box_maxes = box_xy + (box_wh / 2.)

    return K.concatenate([
        box_mins[..., 1:2],  # y_min
        box_mins[..., 0:1],  # x_min
        box_maxes[..., 1:2],  # y_max
        box_maxes[..., 0:1]  # x_max
    ])
