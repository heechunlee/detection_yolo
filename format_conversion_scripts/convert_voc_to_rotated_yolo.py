import glob
import os
import pickle
import xml.etree.ElementTree as ET
from os import listdir, getcwd
from os.path import join
import numpy as np 

dirs = ['detect']
classes = ['1', '2', '3', '4', '5']

def getImagesInDir(dir_path):
    image_list = []
    # Check whether image file is '.jpg' or '.png' 
    for filename in glob.glob(dir_path + '/*.jpg'):
        image_list.append(filename)

    return image_list

def convert(size, params):
    cx = params[0]/size[0]
    cy = params[1]/size[1]
    w_scaled = params[2]/size[0]
    h_scaled = params[3]/size[1]

    angle = params[4]*180/np.pi 
    if angle>=0 and angle<180: 
        angle = angle 
    elif angle<0 and angle>-180: 
        angle = angle+180

    #if (angle>=0 and angle<np.pi/2) or (angle>=np.pi and angle<np.pi*3/2):
    #    angle = -angle 
    #else: 
    #   angle = np.pi-angle 
    #cos_theta = np.cos(angle)
    #sin_theta = np.sin(angle)
    return (cx, cy, w_scaled, h_scaled, angle)

def convert_annotation(dir_path, output_path, image_path):
    basename = os.path.basename(image_path)
    basename_no_ext = os.path.splitext(basename)[0]

    in_file = open(dir_path + '/' + basename_no_ext + '.xml')
    out_file = open(output_path + basename_no_ext + '.txt', 'w')
    tree = ET.parse(in_file)
    root = tree.getroot()
    size = root.find('size')
    w_abs = int(size.find('width').text)
    h_abs = int(size.find('height').text)

    for obj in root.iter('object'):
        difficult = obj.find('difficult').text
        cls = obj.find('name').text
        if cls not in classes or int(difficult)==1:
            continue
        cls_id = classes.index(cls)
        xmlrobox = obj.find('robndbox')
        if xmlrobox: 
            #b = (float(xmlrobox.find('xmin').text), float(xmlrobox.find('xmax').text), float(xmlrobox.find('ymin').text), float(xmlrobox.find('ymax').text))
            params = (float(xmlrobox.find('cx').text), 
                        float(xmlrobox.find('cy').text), 
                        float(xmlrobox.find('w').text), 
                        float(xmlrobox.find('h').text), 
                        float(xmlrobox.find('angle').text))
            params_converted = convert((w_abs,h_abs), params)
            out_file.write(str(cls_id) + " " + " ".join([str(a) for a in params_converted]) + '\n')
        else: 
            continue

cwd = getcwd()

for dir_path in dirs:
    full_dir_path = cwd + '/' + dir_path
    output_path = full_dir_path +'/rotated_yolo/'

    if not os.path.exists(output_path):
        os.makedirs(output_path)

    image_paths = getImagesInDir(full_dir_path)
    list_file = open(full_dir_path + '.txt', 'w')

    for image_path in image_paths:
        list_file.write(image_path + '\n')
        convert_annotation(full_dir_path, output_path, image_path)
    list_file.close()

    print("Finished processing: " + dir_path)