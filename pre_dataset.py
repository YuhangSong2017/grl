#!/usr/bin/env python
# coding=utf-8
import matplotlib as plt
import imageio
import numpy as np
import config
import cv2
import copy
import subprocess
file = 'pong.mp4'
dataset_file = 'dataset_pong_1.npz'
dir = '../../dataset/'
filename = dir + file
vid = imageio.get_reader(filename,  'ffmpeg')
info = vid.get_meta_data()
num_frame = info['nframes']
size = info['size']
print info
num_step = int(info['duration']/config.gan_predict_interval)
frame_per_step = num_frame / num_step
lllast_image = None
llast_image = None
last_image = None
dataset = []
for step in range(0, num_step):

    frame = step * frame_per_step

    image = np.asarray(vid.get_data(frame))/255.0

    c = []
    for color in range(3):
        temp = np.asarray(cv2.resize(image[:,:,color], (config.gan_size, config.gan_size)))
        c += [copy.deepcopy(temp)]

    image = np.asarray(np.add(c[0]*0.299,c[1]*0.587))
    image = np.asarray(np.add(image,c[2]*0.114))

    print 'video>'+str(file)+'\t'+'step>'+str(step)+'\t'+'size>'+str(np.shape(image))
    
    if last_image is None or llast_image is None or lllast_image is None:
        pass
    else:
        pair = np.asarray([lllast_image,llast_image,last_image,image])
        dataset += [copy.deepcopy(np.asarray(pair))]

    lllast_image = copy.deepcopy(llast_image)
    llast_image = copy.deepcopy(last_image)
    last_image = copy.deepcopy(image)

dataset = np.asarray(dataset)

print 'genrate dataset with size>'+str(np.shape(dataset))

np.savez(dir+dataset_file,
         dataset=dataset)

print(s)

