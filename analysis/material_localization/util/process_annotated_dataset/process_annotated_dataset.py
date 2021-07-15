import cv2
import imutils
import numpy as np
import os
import random


image_path = "../../data/test/site_photography_mcguffey/images/"
anno_path = "../../data/test/site_photography_mcguffey/localization_input/"



files = os.listdir(anno_path)


category_goal = 20

window_size = 100

# 0 : red    : brick     : 1 0 0 : 1 
# 1 : blue   : concreate : 0 0 1 : 4
# 2 : green  : metal     : 0 1 0 : 2
# 3 : yellow : wood      : 1 1 0 : 3
# 4 : black  : none      : 0 0 0 : 0

category_bin = np.array([4,0,2,3,1])

element_names = [n.split(".")[0] for n in files]

category_names = ["brick","concrete","metal","wood","z_none"]

for element_name in element_names:
    image = cv2.imread(image_path + element_name + ".jpg")
    image = imutils.resize(image,width=1024)

    anno = cv2.imread(anno_path + element_name + ".png")
    anno = imutils.resize(anno,width=1024)
    anno = anno / 255.0

    category_counts = np.array([0,0,0,0,0])

    #for i in range(20):
    while(True):
        
        
        x = int((anno.shape[0] - window_size) * random.random())
        y = int((anno.shape[1] - window_size) * random.random())

    
        anno_window = anno[x:x+100,y:y+100]

        b,g,r = cv2.split(anno_window)
        r = np.round(r)
        g = np.round(g)
        b = np.round(b)

        total = np.zeros((anno_window.shape[0],anno_window.shape[1]))

        total += np.int8(r * 1)
        total += np.int8((g * 2))
        total += np.int8((b * 4))

        total = np.int8(total)
        total = category_bin[total]
        total = np.float32(total)

    
    
        hist = cv2.calcHist([total],[0],None,[5],[0,5])

        top = np.argmax(hist)

        if (category_counts[top] > category_goal):
            continue

        
        if hist[top] > 5000:
            image_window = image[x:x+100,y:y+100]
            cv2.imwrite("output/{}/{}_{}_{}.png".format(category_names[top],element_name,x,y),image_window)

        category_counts[top] += 1

        print(category_counts)

        if (category_counts >= category_goal).all():
            break

    cv2.imshow("hello",anno_window)
    cv2.waitKey(0)









