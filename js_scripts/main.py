#! /usr/bin/env python
"""Run a YOLO_v2 style detection model on test images."""
import argparse
import colorsys
import imghdr
import os
import random

import numpy as np
from matplotlib import pyplot as plt

from keras import backend as K
from keras.models import load_model
import cv2
from PIL import Image, ImageDraw, ImageFont

from yad2k.models.keras_yolo import yolo_eval, yolo_head
from src.utils.utils import comp_person
from src.utils.structure import Machine
from src.utils.monitoringSalle import updateTimeMachine, printMachineState,usedMachine



# Init Video
video_path=os.path.expanduser("videos/salle.mp4")
vidcap = cv2.VideoCapture(video_path)
# vidcap = cv2.VideoCapture(0) #0 pour utiliser webcam

if(vidcap.isOpened()) :
    print("video opened")
else :
    vidcap.open()
fps = vidcap.get(cv2.CAP_PROP_FPS)
fps=round(fps)

if fps==0 :
    fps=1
print("fps :",fps)


score_threshold=0.3
iou_threshold=0.2
model_path = os.path.expanduser('model_data/yolo.h5')
anchors_path = os.path.expanduser('model_data/yolo_anchors.txt')
classes_path = os.path.expanduser('model_data/coco_classes.txt')
frames_path = 'data/frames_vid_webcam/'
video_path="videos/munich.mp4"

if not os.path.exists(frames_path):
    print('Creating output path {}'.format(frames_path))
    os.mkdir(frames_path)

sess = K.get_session()  # TODO: Remove dependence on Tensorflow session.

with open(classes_path) as f:
    class_names = f.readlines()
class_names = [c.strip() for c in class_names]

with open(anchors_path) as f:
    anchors = f.readline()
    anchors = [float(x) for x in anchors.split(',')]
    anchors = np.array(anchors).reshape(-1, 2)

yolo_model = load_model(model_path)

# Verify model, anchors, and classes are compatible
num_classes = len(class_names)
num_anchors = len(anchors)
# TODO: Assumes dim ordering is channel last
model_output_channels = yolo_model.layers[-1].output_shape[-1]
assert model_output_channels == num_anchors * (num_classes + 5), \
    'Mismatch between model and given anchor and class sizes. ' \
    'Specify matching anchors and classes with --anchors_path and ' \
    '--classes_path flags.'
print('{} model, anchors, and classes loaded.'.format(model_path))

# Check if model is fully convolutional, assuming channel last order.
model_image_size = yolo_model.layers[0].input_shape[1:3]
is_fixed_size = model_image_size != (None, None)

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

# Generate output tensor targets for filtered bounding boxes.
# TODO: Wrap these backend operations with Keras layers.
yolo_outputs = yolo_head(yolo_model.output, anchors, len(class_names))
input_image_shape = K.placeholder(shape=(2, ))
boxes, scores, classes = yolo_eval(
    yolo_outputs,
    input_image_shape,
    score_threshold=score_threshold,
    iou_threshold=iou_threshold)






#Machines initialization
machines = []
traction = Machine("Traction", [105, 129, 285, 207])
bench = Machine("Bench", [155, 227, 272, 267])
shoulderPress=Machine("ShoulderPress",[180,55,340,139])
machines.append(traction)
machines.append(bench)
machines.append(shoulderPress)



# Read video
persons=[]
idx=1;
success, image = vidcap.read()
success = True
while success:


    if idx%fps == 0:
        print(idx)

        # juste pour passer d'une image cv2 a PIL Image
        cv2.imwrite(os.path.join(frames_path, "frame%d.jpg" % idx), image)
        image = Image.open(os.path.join(frames_path, "frame%d.jpg" % idx))

        if is_fixed_size:  # TODO: When resizing we can use minibatch input.
            resized_image = image.resize(
                tuple(reversed(model_image_size)), Image.BICUBIC)
            image_data = np.array(resized_image, dtype='float32')
        else:
            # Due to skip connection + max pooling in YOLO_v2, inputs must have
            # width and height as multiples of 32.
            new_image_size = (image.width - (image.width % 32),
                              image.height - (image.height % 32))
            resized_image = image.resize(new_image_size, Image.BICUBIC)
            image_data = np.array(resized_image, dtype='float32')
            print(image_data.shape)




        image_data /= 255.
        image_frame= np.array(image, dtype='float32')
        image_frame /= 255.
        image_data = np.expand_dims(image_data, 0)  # Add batch dimension.


        out_boxes, out_scores, out_classes = sess.run(
            [boxes, scores, classes],
            feed_dict={
                yolo_model.input: image_data,
                input_image_shape: [image.size[1], image.size[0]],
                K.learning_phase(): 0
            })

        nb_person=comp_person(out_classes)
        print("nb_person :", nb_person)
        if(len(persons)<2) :
            persons.append(nb_person)
        else :
            persons[idx%2]=nb_person

        machines = updateTimeMachine(out_classes,out_boxes, machines)
        machines=usedMachine(machines)
        printMachineState(machines)
        for machine in machines :
            print("taux d'utilisation :",machine.name ,": ",(machine.totalUsedTime*fps)/idx)

        # permet de faire une moyenne mais faudrait mettre 10 plutot
        if idx%(2*fps) == 0 and idx!=0:
            # avec machine used
            avg=np.average(persons)
            print("\nIL Y EXACTEMENT :",avg,"PERSONNES\n")
            out=open("out.txt","w")
            out.write("nb_users:"+str(avg)+"\n")
            for machine in machines :
                out.write(str(machine.name)+":"+str(machine.isUsed)+":"+str(round(100*(machine.totalUsedTime*fps)/idx))+"\n")

            out.close()

            # avec qu'on fasse machine used
            # avg=np.average(persons)
            # print("\nIL Y EXACTEMENT :",avg,"PERSONNES\n")
            # out=open("out.txt","a")
            # out.write("nb_users:"+str(avg)+"\n")
            # out.close()





        # draw machine

        font = ImageFont.truetype(
            font='font/FiraMono-Medium.otf',
            size=np.floor(3e-2 * image.size[1] + 0.5).astype('int32'))
        thickness = (image.size[0] + image.size[1]) // 300

        for machine in machines:
            label = '{} {} '.format(machine.name,machine.isUsed)
            draw = ImageDraw.Draw(image)
            label_size = draw.textsize(label, font)

            top, left, bottom, right =machine.box
            # top, left, bottom, right =  [0, 0, 400, 800]
            top = max(0, np.floor(top + 0.5).astype('int32'))
            left = max(0, np.floor(left + 0.5).astype('int32'))
            bottom = min(image.size[1], np.floor(bottom + 0.5).astype('int32'))
            right = min(image.size[0], np.floor(right + 0.5).astype('int32'))

            if top - label_size[1] >= 0:
                text_origin = np.array([left, top - label_size[1]])
            else:
                text_origin = np.array([left, top + 1])

            if machine.isUsed==True :
                c=1
            else :
                c=2

            # My kingdom for a good redistributable image drawing library.
            for i in range(thickness):
                draw.rectangle(
                    [left + i, top + i, right - i, bottom - i],
                    outline=colors[c])
            draw.rectangle(
                [tuple(text_origin), tuple(text_origin + label_size)],
                fill=colors[c])
            draw.text(text_origin, label, fill=(0, 0, 0), font=font)
            del draw
        image.save(os.path.join(frames_path, "frame%d.jpg" % idx),"PNG", quality=90)

        # input("pause")







    success, image = vidcap.read()
    idx += 1




sess.close()
