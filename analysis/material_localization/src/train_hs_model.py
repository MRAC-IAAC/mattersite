import argparse
import cv2
import numpy as np
import os
import pickle
import progressbar
import random
import sklearn

from sklearn.metrics import classification_report
from sklearn.preprocessing import StandardScaler
from sklearn.preprocessing import MinMaxScaler
from sklearn.svm import LinearSVC
from sklearn.svm import SVC
from imutils import paths

import domain

from image_analysis import analyze_image_hs
from tsne_analysis import generate_tSNE_plot

# handle sklearn versions less than 0.18
if int((sklearn.__version__).split(".")[1]) < 18:
	from sklearn.grid_search import GridSearchCV

# otherwise, sklearn.grid_search is deprecated
# and we'll import GridSearchCV from sklearn.model_selection
else:
	from sklearn.model_selection import GridSearchCV


# === SETUP ===
ap = argparse.ArgumentParser()
ap.add_argument("-d", "--dataset", required=True,
	help="Path to the directory that contains the original images")
args = vars(ap.parse_args())

image_paths = list(paths.list_images(args["dataset"]))
random.shuffle(image_paths)

split_point = int(len(image_paths) / 5 * 3)

training_set = image_paths[:split_point]
testing_set = image_paths[split_point:]

print("Found {} training images".format(len(training_set)))
print("Found {} testing images".format(len(testing_set)))

# === ANALYZE TRAINING SET ===
data = []
labels = []

widgets = ["Analyzing Training Set: ",progressbar.Percentage(), " ", progressbar.Bar(), " ", progressbar.ETA()]
pbar = progressbar.ProgressBar(maxval = len(training_set),widgets=widgets).start()

for i,image_path in enumerate(training_set):
    image = cv2.imread(image_path)
    image = cv2.cvtColor(image,cv2.COLOR_BGR2HSV)

    data_hs = analyze_image_hs(image)
    data.append(data_hs)

    label = image_path.split(os.path.sep)[-2]
    labels.append(label)
    pbar.update(i)

pbar.finish()


# === FIT MODEL === 
print("Fitting Model")
data = np.array(data).reshape((len(training_set),32))
params = {"C": [0.1, 1.0, 10.0, 100.0, 1000.0, 10000.0]}
model = GridSearchCV(SVC(random_state=42,probability = True,max_iter=50000,class_weight='balanced'),params,cv=3)
model.fit(data, labels)

# === GENERATE T-SNE PLOT ===
print("Generating t-SNE visualization")
labels = np.asarray([domain.category_ids[c] for c in labels])
generate_tSNE_plot(data,labels,"tSNE_hs")

# === ANALYSE TEST SET === 
test_labels = []
test_data = []

widgets = ["Analyzing Testing Set: ",progressbar.Percentage(), " ", progressbar.Bar(), " ", progressbar.ETA()]
pbar = progressbar.ProgressBar(maxval = len(testing_set),widgets=widgets).start()

for i,image_path in enumerate(testing_set):
    image = cv2.imread(image_path)
    image = cv2.cvtColor(image,cv2.COLOR_BGR2HSV)

    data_hs = analyze_image_hs(image)
    test_data.append(data_hs)
    
    label = image_path.split(os.path.sep)[-2]
    test_labels.append(label)
    pbar.update(i)

pbar.finish()


# === REPORT ON TEST DATA === 
test_data = np.array(test_data).reshape((len(testing_set),32))

predictions_proba = model.predict_proba(test_data)
predictions = np.argmax(predictions_proba,axis = 1)

test_labels = [domain.category_ids[c] for c in test_labels]
test_labels = np.asarray(test_labels)

print(classification_report(test_labels, predictions))


# === SAVE MODEL OUTPUT ===
f = open('model/model_hs.cpickle', "wb")
f.write(pickle.dumps(model))
f.close()


