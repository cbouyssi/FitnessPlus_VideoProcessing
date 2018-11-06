#! /usr/bin/env python
"""Run a YOLO_v2 style detection model on test images."""
import argparse
import colorsys
import imghdr
import os
import random
from math import sqrt

import numpy as np
from matplotlib import pyplot as plt

from keras import backend as K
from keras.models import load_model
import cv2
from PIL import Image, ImageDraw, ImageFont

from yad2k.models.keras_yolo import yolo_eval, yolo_head

from src.utils.utils import natural_keys
from src.utils.structure import Person_v2, Person_v3, Machine
from src.utils.tracking_v2 import updatePersons,plot_histo, color_tracking_v2,process_metrics_v2,color_moy_tracking,box_intersection_with_object
from src.utils.monitoringSalle import updateTimeMachine, printMachineState,usedMachine


'''
iou_trheshold has to be small to get better results
Si 2 box n'ont pas assez d'intersection entre elles alors => 2 box
Plus iou eleve plus il faut d'intersection pour que les box soient fusionnes
'''


def model_prediction_person_v2(score_threshold=0.2,iou_threshold=0.2):

    #Machines initialization
    machines = []
    dc = Machine("dc", [0, 400, 300, 1200])
    machines.append(dc)

    model_path = os.path.expanduser('model_data/yolo.h5')
    anchors_path = os.path.expanduser('model_data/yolo_anchors.txt')
    classes_path = os.path.expanduser('model_data/coco_classes.txt')
    test_path = os.path.expanduser('data/frames_vid_tom')
    output_path = os.path.expanduser('data/frames_out_tom_v3')


    if not os.path.exists(output_path):
        print('Creating output path {}'.format(output_path))
        os.mkdir(output_path)

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

    # tracking
    persons={}
    comp=0
    id=0
    # tracking
    files=[file for file in os.listdir(test_path)]
    files.sort(key=natural_keys)
    for image_file in files:
    # for image_file in os.listdir(test_path):
        try:
            image_type = imghdr.what(os.path.join(test_path, image_file))
            if not image_type:
                continue
        except IsADirectoryError:
            continue

        image = Image.open(os.path.join(test_path, image_file))

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

        distance_normalizer=sqrt(pow(image_frame.shape[0]-0,2)+pow(image_frame.shape[1]-0,2))
        # print("distance_normalizer :",distance_normalizer)
        # print("normalized 50 =>",50/distance_normalizer)
        # print("normalized 100 =>",100/distance_normalizer)


        out_boxes, out_scores, out_classes = sess.run(
            [boxes, scores, classes],
            feed_dict={
                yolo_model.input: image_data,
                input_image_shape: [image.size[1], image.size[0]],
                K.learning_phase(): 0
            })
        print('\nFound {} boxes for {}'.format(len(out_boxes), image_file))

        font = ImageFont.truetype(
            font='font/FiraMono-Medium.otf',
            size=np.floor(3e-2 * image.size[1] + 0.5).astype('int32'))
        thickness = (image.size[0] + image.size[1]) // 300

        comp_p=0
        for i, c in reversed(list(enumerate(out_classes))):
            if c==0 :
                comp_p+=1
                predicted_class = class_names[c]
                box = out_boxes[i]
                score = out_scores[i]



                histr=[]

                boolean_intersection=box_intersection_with_object(box,i,out_classes,out_boxes)
                print("Current user intersection with another object : ",boolean_intersection)

                # reshape bounding box into the image border
                x_top,y_left,x_bottom,y_right=box
                x_top = max(0,x_top)
                y_left = max(0, y_left)
                x_bottom = min( x_bottom,image_frame.shape[0])
                y_right = min( y_right,image_frame.shape[1])
                box =x_top,y_left,x_bottom,y_right
                color = ('b','g','r')
                for i,col in enumerate(color):
                	histr.append( cv2.calcHist([image_frame[int(box[0]):int(box[2]), int(box[1]):int(box[3])]],[i],None,[256],[0,1]))


                # plot_histo(histr)
                rgbHist=[]
                moyhistface1=[]
                moyhistface2=[]
                if comp==0 :


                    rgbHist.append(histr)
                    moyhistface1.append(histr)
                    person=Person_v3("person"+ str(id),comp,box,rgbHist, moyhistface1,moyhistface2,1,1,0)

                    persons[person.name]=person
                    print("NEW USER WELCOM =>",person.name)

                    id+=1
                else :
                    print("\n TRACKING COMPUTATION  CURRENT USER",comp_p)
                    dico_histo = color_tracking_v2(histr,persons)
                    print("\n TRACKING COMPUTATION HISTO MOY ============================> CURRENT USER",comp_p)
                    dico_hist_moy=color_moy_tracking(histr,persons)

                    print("\nPROCESS METRICS SELECTION CURRENT USER",comp_p)
                    # name=process_metrics_v2(dico_histo,box,histr,persons,comp,distance_normalizer)
                    name,boolean_redecouverte,key_to_delete=process_metrics_v2(dico_hist_moy,dico_histo,box,histr,persons,comp,distance_normalizer)

                    if name=="default":
                        print("NEW USER WELCOM =>","person"+ str(id))
                        rgbHist.append(histr)
                        moyhistface1.append(histr)
                        person=Person_v3("person"+ str(id),comp,box,rgbHist, moyhistface1,moyhistface2,1,1,0)
                        persons[person.name]=person
                        id+=1
                    else :

                        persons=updatePersons(name,box,histr,persons,boolean_intersection,boolean_redecouverte)
                        if boolean_redecouverte and key_to_delete!="default":
                            print("Je vais supprimer :",key_to_delete)
                            persons.pop(key_to_delete)
                        # inutile la ligne du dessus est suffisante mais pour le display des bounding box j'en ai besoin
                        person=Person_v2(name,comp,box, rgbHist)
                print(person.box)
                if comp % 1== 0: #faut mettre 30 pour de vrai
                    machines = updateTimeMachine(person, machines)

                #before tracking
                # label = '{} {:.2f}'.format(predicted_class, score)
                label = '{} {} {:.2f}'.format(person.name,predicted_class, score)
                draw = ImageDraw.Draw(image)
                label_size = draw.textsize(label, font)

                top, left, bottom, right =box
                # top, left, bottom, right =  [0, 0, 400, 800]
                top = max(0, np.floor(top + 0.5).astype('int32'))
                left = max(0, np.floor(left + 0.5).astype('int32'))
                bottom = min(image.size[1], np.floor(bottom + 0.5).astype('int32'))
                right = min(image.size[0], np.floor(right + 0.5).astype('int32'))

                if top - label_size[1] >= 0:
                    text_origin = np.array([left, top - label_size[1]])
                else:
                    text_origin = np.array([left, top + 1])

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
        output_path=output_path+"/"
        image.save(os.path.expanduser(output_path+ image_file),"PNG", quality=90)

        machines=usedMachine(machines)

        comp+=1
        # que du print
        # for key , person in persons.items():
        #     print(person.name ,len(person.histmoyface1),len(person.histmoyface2))
        print('Found {} boxes for {}'.format(len(out_boxes), image_file))
        printMachineState(machines)

        text = input("pause")


    sess.close()
