import argparse
import cv2
import datetime
import numpy as np
import os
import pickle
import progressbar
import random
import sklearn
import sqlite3
import time

import tensorflow as tf
from keras.preprocessing.image import ImageDataGenerator
import keras

from pyimagesearch.descriptors import DetectAndDescribe
from pyimagesearch.ir import BagOfVisualWords
from pyimagesearch.localbinarypatterns import LocalBinaryPatterns
from sklearn.metrics import classification_report
from sklearn.preprocessing import StandardScaler
from sklearn.preprocessing import MinMaxScaler
from sklearn.svm import LinearSVC
from sklearn.svm import SVC
from imutils import paths
from imutils.feature import FeatureDetector_create, DescriptorExtractor_create

import domain

from image_analysis import analyze_image_bovw, analyze_image_hs, analyze_image_lbp
from tsne_analysis import generate_tSNE_plot

# handle sklearn versions less than 0.18
if int((sklearn.__version__).split(".")[1]) < 18:
	from sklearn.grid_search import GridSearchCV

# otherwise, sklearn.grid_search is deprecated
# and we'll import GridSearchCV from sklearn.model_selection
else:
	from sklearn.model_selection import GridSearchCV

ap = argparse.ArgumentParser()
ap.add_argument("-d", "--dataset", required=True,
	help="Path to the directory that contains the original images")
ap.add_argument("-b", "--codebook", required=True,
	help="Path to the codebook")
ap.add_argument("-m", "--model", required=True,
	help="Path to the classifier")
ap.add_argument("-t","--start_time", required=True,
                help="Timestamp of overall setup start")
ap.add_argument("-c","--cluster_count", required=True,
                help="Number of clusters used")
ap.add_argument("-s","--sampling_percentage", required=True,
                help="Sampling Percentage")
args = vars(ap.parse_args())

model_bovw = pickle.loads(open("model/model.cpickle", "rb").read())
model_lbp = pickle.loads(open("model/model_lbp.cpickle", "rb").read())
model_hs = pickle.loads(open("model/model_hs.cpickle", "rb").read())
model_cnn = keras.models.load_model("model/model_cnn/")

detector = FeatureDetector_create("GFTT")
descriptor = DescriptorExtractor_create("BRISK")
dad = DetectAndDescribe(detector, descriptor)

desc4 = LocalBinaryPatterns(24,4)
desc8 = LocalBinaryPatterns(24,8)

# Load the codebook vocabulary and initialize the bag-of-visual-words transformer
vocab = pickle.loads(open(args["codebook"], "rb").read())
bovw = BagOfVisualWords(vocab)
idf = pickle.loads(open("model/idf.cpickle","rb").read())

image_paths = list(paths.list_images(args["dataset"]))
random.shuffle(image_paths)

split_point = int(len(image_paths) / 5 * 3)

training_set = image_paths[:split_point]
testing_set = image_paths[split_point:]

print("Found {} training images".format(len(training_set)))
print("Found {} testing images".format(len(testing_set)))


# === ANALYZE TRAINING SET ===

training_data = []
training_labels = []

widgets = ["Analyzing Training Set : ",progressbar.Percentage(), " ", progressbar.Bar(), " ", progressbar.ETA()]
pbar = progressbar.ProgressBar(maxval = len(training_set),widgets=widgets).start()


for img_id,image_path in enumerate(training_set):
    image_data = []
    
    # Get bovw proba
    image_main = cv2.imread(image_path)
    image_gray = cv2.cvtColor(image_main, cv2.COLOR_BGR2GRAY)
    image_hsv = cv2.cvtColor(image_main,cv2.COLOR_BGR2HSV)

    bovw_data = analyze_image_bovw(image_gray,dad,bovw,idf)
    if bovw_data is None:
        continue
    prediction_bovw = model_bovw.predict_proba(bovw_data)[0]
    image_data.append(prediction_bovw)

    data_hs = analyze_image_hs(image_hsv).transpose()
    prediction_hs = model_hs.predict_proba(data_hs)[0]
    image_data.append(prediction_hs)

    data_lbp = analyze_image_lbp(image_gray,desc4,desc8).reshape(1,-1)
    prediction_lbp = model_lbp.predict_proba(data_lbp)[0]
    image_data.append(prediction_lbp)

    data_cnn = cv2.resize(image_main,(256,256)).reshape(1,256,256,3)
    data_cnn = data_cnn / 255.0
    prediction_cnn = model_cnn.predict(data_cnn)
    image_data.append(prediction_cnn[0])

    image_data = np.concatenate(image_data)
    training_data.append(image_data)
    
    label = image_path.split(os.path.sep)[-2]
    training_labels.append(label)
    pbar.update(img_id)

pbar.finish()


print("Fitting Model")

train_length = len(training_data)
training_data = np.array(training_data).reshape(train_length,20)


params = {"C": [0.1, 1.0, 10.0, 100.0, 1000.0, 10000.0]}
model_stack = GridSearchCV(SVC(random_state=42,probability = True,max_iter=50000,class_weight='balanced'),params,cv=3)

model_stack.fit(training_data, training_labels)

# === GENERATE T-SNE PLOT ===
print("Generating t-SNE visualization")
plot_labels = np.asarray([domain.category_ids[c] for c in training_labels])
generate_tSNE_plot(training_data,plot_labels,"tSNE_stack")

test_labels = []
test_data = []

widgets = ["Analyzing test set: ",progressbar.Percentage(), " ", progressbar.Bar(), " ", progressbar.ETA()]
pbar = progressbar.ProgressBar(maxval = len(testing_set),widgets=widgets).start()
for img_id,image_path in enumerate(testing_set):
    image_data = []
    
    # Get bovw proba
    image_main = cv2.imread(image_path)
    image_gray = cv2.cvtColor(image_main, cv2.COLOR_BGR2GRAY)
    image_hsv = cv2.cvtColor(image_main,cv2.COLOR_BGR2HSV)

    data_bovw = analyze_image_bovw(image_gray,dad,bovw,idf)
    if data_bovw is None:
        continue
    prediction_bovw = model_bovw.predict_proba(data_bovw)[0]
    image_data.append(prediction_bovw)

    data_hs = analyze_image_hs(image_hsv).transpose()
    prediction_hs = model_hs.predict_proba(data_hs)[0]
    image_data.append(prediction_hs)

    data_lbp = analyze_image_lbp(image_gray,desc4,desc8).reshape(1,-1)
    prediction_lbp = model_lbp.predict_proba(data_lbp)[0]
    image_data.append(prediction_lbp)

    data_cnn = cv2.resize(image_main,(256,256)).reshape(1,256,256,3)
    data_cnn = data_cnn / 255.0
    prediction_cnn = model_cnn.predict(data_cnn)
    image_data.append(prediction_cnn[0])

    image_data = np.concatenate(image_data)
    test_data.append(image_data)
    
    label = image_path.split(os.path.sep)[-2]
    test_labels.append(label)

    pbar.update(img_id)

pbar.finish()


# === REPORT ON TEST DATA ===
test_length = len(test_data)
test_data = np.array(test_data).reshape(test_length,20)

predictions_proba = model_stack.predict_proba(test_data)
predictions = np.argmax(predictions_proba,axis = 1)
test_labels = [domain.category_ids[c] for c in test_labels]
test_labels = np.asarray(test_labels)

print(classification_report(test_labels, predictions))
classification_report_dict = classification_report(test_labels,predictions,output_dict = True)


# === SAVE MODEL OUTPUT ===
f = open('model/model_stack.cpickle', "wb")
f.write(pickle.dumps(model_stack))
f.close()


# === WRITE RESULTS TO SQL DATABASE ===
now = datetime.datetime.now()

db_timestamp = "{:02d}{:02d}{:02d}{:02d}{:02d}{:02d}".format((now.year % 100),now.month,now.day,now.hour,now.minute,now.second)
db_machine_id = 0
db_project_version = 2
db_training_time = int(time.time()) - int(args["start_time"])
db_training_set_size = len(list(paths.list_images(args["dataset"])))
db_number_of_categories = 5
db_cluster_count = int(args["cluster_count"])
db_sampling_percentage = float(args["sampling_percentage"])
db_f1_brick = classification_report_dict["0"]["f1-score"]
db_f1_concrete = classification_report_dict["1"]["f1-score"]
db_f1_metal = classification_report_dict["2"]["f1-score"]
db_f1_wood = classification_report_dict["3"]["f1-score"]
db_f1_none = classification_report_dict["4"]["f1-score"]

conn = sqlite3.connect('training.db')
c = conn.cursor()

arguments = (db_timestamp,db_machine_id,db_project_version,db_training_time,db_training_set_size,db_number_of_categories,db_cluster_count,db_sampling_percentage,db_f1_brick,db_f1_concrete,db_f1_metal,db_f1_wood,db_f1_none)
c.execute("INSERT INTO training (timestamp,machine_id,project_version,training_time,training_set_size,category_count,cluster_count,sampling_percentage,f1_brick,f1_concrete,f1_metal,f1_wood,f1_none) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)",arguments)
conn.commit()

conn.close()    

