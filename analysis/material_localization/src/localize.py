from __future__ import print_function

import argparse
import cv2
import datetime
import h5py
import imutils
import keras
import numpy as np
import os
import pathlib
import pickle
import progressbar
import sqlite3
import tensorflow as tf
import time

from keras.preprocessing.image import ImageDataGenerator
from imutils.feature import FeatureDetector_create, DescriptorExtractor_create
from imutils import paths


import domain

from pyimagesearch.descriptors import DetectAndDescribe
from pyimagesearch.ir import BagOfVisualWords
from pyimagesearch.localbinarypatterns import LocalBinaryPatterns
from pyimagesearch.object_detection.helpers import sliding_window_double
from pyimagesearch.object_detection.helpers import sliding_window_multiple
from pyimagesearch.object_detection.helpers import pyramid
from image_analysis import analyze_image_hs, analyze_image_lbp, analyze_image_bovw
from compare_images import compare_images


# construct the argument parser and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-i", "--images", required=True,
	            help="Path to input images directory")
ap.add_argument("-c", "--codebook", required=True,
	            help="Path to the codebook")
ap.add_argument("-e", "--extractor",default="BRISK")
ap.add_argument("-w", "--wsize",default=100)
ap.add_argument("-k", "--ksize",default=3)
ap.add_argument("-s", "--suffix",default="")
ap.add_argument("-t", "--testing",default=False,
                help="Test mode - only localize images for which a manual annotation exists to test against")




args = vars(ap.parse_args())

# How many classification patches a single window covers on a side
kernel_size = args["ksize"]

# TK TEST
#kernel_size = 10

# Offsets for applying detection windows to subpatches
dx = list(range(kernel_size)) * kernel_size
dy = []
for i in range(kernel_size):
    for j in range(kernel_size):
        dy.append(i)

win_size = args["wsize"]
patch_size = win_size // kernel_size
#output_window_offset = 0 if args["testing"] else -2
output_window_offset = 0
print("Window Size : {}".format(win_size))
print("Patch Size : {}".format(patch_size))

# Initialize the keypoint detector, local invariant descriptor, and the descriptor
# pipeline
detector = FeatureDetector_create("GFTT")
descriptor = DescriptorExtractor_create(args["extractor"])
dad = DetectAndDescribe(detector, descriptor)

# Load inverse document frequency file
idf = pickle.loads(open("model/idf.cpickle","rb").read()).reshape(1,-1)

# Load the codebook vocabulary and initialize the bag-of-visual-words transformer
vocab = pickle.loads(open(args["codebook"], "rb").read())
bovw = BagOfVisualWords(vocab)

# Load the classifier models
model_bovw = pickle.loads(open("model/model.cpickle", "rb").read())
model_lbp = pickle.loads(open("model/model_lbp.cpickle", "rb").read())
model_hs = pickle.loads(open("model/model_hs.cpickle", "rb").read())
model_cnn = keras.models.load_model("model/model_cnn/")
model_stack = pickle.loads(open("model/model_stack.cpickle","rb").read())

desc4 = LocalBinaryPatterns(24,4)
desc8 = LocalBinaryPatterns(24,8)

# Whether to scale the input image down to 1024 width
flag_resize_image = True

# Whether to resize all patches to 364x364. Slows things down immensely, but may be necessary for accuracy?
flag_resize_patch = False

# Whether to show each image to the user as its localized
flag_display = False

# Whether to save all the classified subpatches by category
flag_export_patches = False


# === MAIN SCRIPT === 

# Open connection to records database
conn = sqlite3.connect('training.db')
c = conn.cursor()

# Get some general information about the batch for the records
batch_start_time = time.time()
now = datetime.datetime.now()
fname = pathlib.Path("model/model_stack.cpickle")
ftime = datetime.datetime.fromtimestamp(fname.stat().st_mtime)

# loop over the image paths

images_paths = []
if args["testing"]:
    anno_files = os.listdir(args["images"] + "/../localization_input")
    names = [os.path.basename(n).split(".")[0] for n in anno_files]
    image_paths = [args["images"] + "/" + n + ".JPG" for n in names]

else:
    image_paths = paths.list_images(args["images"])
    

for img_id,image_path in enumerate(image_paths):
    image_start_time = time.time()
    
    print("\n{} : {}".format(str(img_id).zfill(3),image_path))
    
    name = image_path.split("/")[-1].split(".")[0]

    directory = os.path.dirname(image_path)
    
    # image_main is the original image, scaled down to 1024 
    image_main = cv2.imread(image_path)
    if flag_resize_image:
        image_main = imutils.resize(image_main,width=min(1024,image_main.shape[1]))

    # image_gray is resized to 1024 width and in grayscale
    image_gray = cv2.cvtColor(image_main, cv2.COLOR_BGR2GRAY)
    #image_gray = imutils.resize(image_gray, width=min(1024, image_main.shape[1]))

    # image_hsv is resized to 1024 width and hsv space
    image_hsv = cv2.cvtColor(image_main,cv2.COLOR_BGR2HSV)
    #image_hsv = imutils.resize(image_hsv,width = min(1024,image_main.shape[1]))

    #image_display is resized to 1024 width, to be annotated with patch colors
    image_display = image_main.copy()
    #image_display = imutils.resize(image_display, width=min(1024, image_main.shape[1]))

    #img_squares is the size of image_display, and contains the category color squares to draw on top of it
    img_squares = np.zeros(image_display.shape,np.uint8)


    img_width = image_gray.shape[1]
    img_height = image_gray.shape[0]

    patch_width = (img_width // patch_size) + 1
    patch_height = (img_height // patch_size) + 1
    patch_length = patch_width * patch_height

    print("Patch space : {} , {}".format(patch_width,patch_height))

    prediction_list = []
    patch_totals = np.zeros(shape=(patch_width,patch_height,5))

    
    widgets = ["Localizing: ", progressbar.Percentage(), " ", progressbar.Bar(), " ", progressbar.ETA()]
    pbar = progressbar.ProgressBar(maxval = patch_length,widgets=widgets).start()

    for (patch_id,(x,y,patch_array)) in enumerate(sliding_window_multiple( (image_main,image_gray,image_hsv), step_size = patch_size,window_size = (win_size,win_size))):
        window_main,window_gray,window_hsv = patch_array

    
    #for (patch_id,(x,y,window_gray,window_hsv)) in enumerate(sliding_window_double(image_gray,image_hsv,stepSize=patch_size,windowSize=(win_size,win_size))):
        window_data = []
        
        # Find x and y position in the patch grid
        patch_x = patch_id % patch_width
        patch_y = patch_id // patch_width

        # Ensure patch size
        if flag_resize_patch:
            window_main = imutils.resize(window_main,width = 100)
            window_gray = imutils.resize(window_gray,width = 100)
            window_hsv = imutils.resize(window_hsv,width=100)
        
        data_bovw = analyze_image_bovw(window_gray,dad,bovw,idf)
        if data_bovw is None:
            continue
        prediction_bovw = model_bovw.predict_proba(data_bovw)[0]
        window_data.append(prediction_bovw)

        data_hs = analyze_image_hs(window_hsv).transpose()
        prediction_hs = model_hs.predict_proba(data_hs)[0]
        window_data.append(prediction_hs)

        data_lbp = analyze_image_lbp(window_gray,desc4,desc8).reshape(1,-1)
        prediction_lbp = model_lbp.predict_proba(data_lbp)[0]
        window_data.append(prediction_lbp)


        data_cnn = cv2.resize(window_main,(256,256)).reshape((1,256,256,3))
        data_cnn = data_cnn / 255.0
        prediction_cnn = model_cnn.predict(data_cnn)
        window_data.append(prediction_cnn[0])


        window_data = np.concatenate(window_data)
        window_data = window_data.reshape(1,20)


        prediction_stack_proba = model_stack.predict_proba(window_data)[0]

        #Test
        #prediction_stack_proba = prediction_cnn.flatten()
        
        #cv2.imshow("Localization",window_gray)
        #print(window_data)
        #print(prediction_stack_proba)
        #cv2.waitKey(0)

        # Apply window predictions to patches
        for i in range(kernel_size * kernel_size):
            nx = patch_x + dx[i]
            ny = patch_y + dy[i]
            if nx >= patch_width or ny >= patch_height:
                continue
            patch_totals[nx,ny] += prediction_stack_proba # * (1 if i in (5,6,9,10) else 0.5)

        pbar.update(patch_id)
        
    pbar.finish()

    patch_space = np.zeros((patch_width,patch_height))
    
    # Loop through each patch, draw the prediction color and save to text file
    for i in range(patch_length):
        patch_x = i % patch_width
        patch_y = i // patch_width
        pixel_x = patch_x * patch_size
        pixel_y = patch_y * patch_size
        id = np.argmax(patch_totals[patch_x,patch_y])
        patch_space[patch_x,patch_y] = id
        prediction_list.append(patch_totals[patch_x,patch_y])
        cv2.rectangle(img_squares,
                      (pixel_x,pixel_y),
                      (pixel_x + patch_size + output_window_offset,
                       pixel_y + patch_size + output_window_offset),
                      domain.category_colors[id],-1)

        if flag_export_patches and id != 4:
            output_name = "output/subpatches/{}/{}_{}.png".format(domain.category_names[id],name + args["suffix"],i)
            subpatch = image_main[pixel_x:pixel_x + patch_size,pixel_y :pixel_y + patch_size]

            if subpatch.shape[0] == patch_size and subpatch.shape[1] == patch_size:
                cv2.imwrite(output_name,subpatch)



    if args["testing"]:
        patch_space = patch_space.astype(int)
        patch_space = domain.category_colors_np[patch_space]
        cv2.imwrite(directory + "/../localization_output/" + name + "_ps_" + args["suffix"] + ".png",patch_space.transpose(1,0,2))
        comparison_image = cv2.imread(directory + "/../localization_input/" + name + ".png")
        score = compare_images(patch_space,comparison_image)
        print("Image Score : " + str(score))
        
            

    # Draw the category colors onto the image
    #cv2.addWeighted(img_squares,0.5,image_display,0.5,0,image_display)

    img_squares_hsv = cv2.cvtColor(img_squares,cv2.COLOR_BGR2HSV)
    (sh,ss,sv) = cv2.split(img_squares_hsv)

    (imh,ims,imv) = cv2.split(image_hsv)

    image_display = cv2.merge((sh,ss,imv))
    image_display = cv2.cvtColor(image_display,cv2.COLOR_HSV2BGR)

    # Display the image to the user
    if flag_display:
        cv2.imshow("Localization",image_display)
        cv2.waitKey(0)

    # Write the images and text file output
    cv2.imwrite(directory + "/../localization_output_overlay/" + name + args["suffix"] + ".png",image_display)
    cv2.imwrite(directory + "/../localization_output/" + name + args["suffix"] + '.png',img_squares)
    with open("output/localization_probs/" + name + args["suffix"] + ".txt",'w') as f:
        for line in prediction_list:
            f.write(np.array2string(line) + "\n")

    image_end_time = time.time()

    # Create db record
    
    db_timestamp = "{:02d}{:02d}{:02d}{:02d}{:02d}{:02d}".format((now.year % 100),now.month,now.day,now.hour,now.minute,now.second)
    db_image_name = name + args["suffix"]
    db_resolution_x = img_width
    db_resolution_y = img_height
    db_window_size = win_size
    db_patch_size = patch_size
    db_number_of_categories = len(domain.category_names)
    db_localization_time = image_end_time - image_start_time
    db_model_timestamp = "{:02d}{:02d}{:02d}{:02d}{:02d}{:02d}".format((ftime.year % 100),ftime.month,ftime.day,ftime.hour,ftime.minute,ftime.second)
    db_machine_id = 0

    arguments = (db_timestamp,db_image_name,db_resolution_x,db_resolution_y,db_window_size,db_patch_size,db_number_of_categories,db_localization_time,db_model_timestamp,db_machine_id)


    c.execute("INSERT INTO localization (batch_timestamp,image_name,resolution_x,resolution_y,window_size,patch_size,number_of_categories,localization_time,model_date,machine_id) VALUES (?,?,?,?,?,?,?,?,?,?)",arguments)
    conn.commit()

    
conn.close()    
batch_end_time = time.time()


print("Localization of {} images took {} seconds".format(img_id + 1,int(batch_end_time - batch_start_time)))
