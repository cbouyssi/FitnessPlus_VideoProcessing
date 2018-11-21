#! /usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import division, print_function, absolute_import

import os
from timeit import time
import warnings
import sys
import cv2
import numpy as np
from PIL import Image

warnings.filterwarnings('ignore')

from monitoring_salle import updateTimeMachine_tracks, usedMachine, printMachineState, Machine

def main():

    #Added for Gym monitoring
    #Machines initialization
    machines = []
    pec_deck = Machine("Pec deck", [215, 150, 280, 295])
    traction = Machine("Traction", [135, 105, 207, 295])
    bench = Machine("Bench", [55, 200, 140, 350])
    machines.append(traction)
    machines.append(pec_deck)
    machines.append(bench)


    writeVideo_flag = True

    video_capture = cv2.VideoCapture('videos/2.mp4')

    if writeVideo_flag:
    # Define the codec and create VideoWriter object
        w = int(video_capture.get(3))
        h = int(video_capture.get(4))
        fourcc = cv2.VideoWriter_fourcc(*'MJPG')
        out = cv2.VideoWriter('output_test_2.avi', fourcc, 15, (w, h))
        list_file = open('detection.txt', 'w')
        frame_index = -1

    fps = 0.0
    count = 0

    while True:
        ret, frame = video_capture.read()  # frame shape 640*480*3
        count += 1
        #print("Frame : ",count)
        if (count-1) % 400 !=0 :
            continue
        if ret != True:
            break;
        t1 = time.time()
    
        image = Image.fromarray(frame)
        
        machines = usedMachine(machines)
        printMachineState(machines)

        for machine in machines:
            bbox = machine.box
            color = (0,0,0)
            if True:
                color = (0,0,255) #Red
            else:
                color = (0,255,0) #Green
            cv2.rectangle(frame, (int(bbox[0]), int(bbox[1])), (int(bbox[2]), int(bbox[3])),color, 2)
            cv2.putText(frame, str(machine.name),(int(bbox[0]), int(bbox[1])),0, 5e-3 * 200, (0,255,0),2)
        
        if writeVideo_flag:
            # save a frame
            out.write(frame)
            frame_index = frame_index + 1
            list_file.write(str(frame_index)+' ')
            list_file.write('\n')

        fps  = ( fps + (1./(time.time()-t1)) ) / 2
        print("fps= %f"%(fps))

        # Press Q to stop!
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    video_capture.release()
    if writeVideo_flag:
        out.release()
        list_file.close()
    cv2.destroyAllWindows()

if __name__ == '__main__':
    main()
