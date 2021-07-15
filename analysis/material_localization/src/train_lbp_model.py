from pyimagesearch.localbinarypatterns import LocalBinaryPatterns

from sklearn.metrics import classification_report
from sklearn.preprocessing import StandardScaler
from sklearn.preprocessing import MinMaxScaler
from sklearn.svm import LinearSVC
from sklearn.svm import SVC
from imutils import paths

import argparse
import cv2
import os
import numpy as np
import pickle
import progressbar
import random
import sklearn

import domain

from image_analysis import analyze_image_lbp
from tsne_analysis import generate_tSNE_plot

# handle sklearn versions less than 0.18
if int((sklearn.__version__).split(".")[1]) < 18:
	from sklearn.grid_search import GridSearchCV

# otherwise, sklearn.grid_search is deprecated
# and we'll import GridSearchCV from sklearn.model_selection
else:
	from sklearn.model_selection import GridSearchCV


# Parse arguments
ap = argparse.ArgumentParser()
ap.add_argument("-d", "--dataset", required=True,
	help="path to the training images")
args = vars(ap.parse_args())

# initialize the local binary patterns descriptor along with
# the data and label lists
desc4 = LocalBinaryPatterns(24,4)
desc8 = LocalBinaryPatterns(24,8)


# loop over the training images
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

widgets = ["Analyzing Training Set: ",progressbar.Percentage(), " ", progressbar.Bar(), " ", progressbar.ETA()]
pbar = progressbar.ProgressBar(maxval = len(training_set),widgets=widgets).start()

for i,image_path in enumerate(training_set):
    image = cv2.imread(image_path)
    image_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    image_data = analyze_image_lbp(image_gray,desc4,desc8)
    training_data.append(image_data)

    label = image_path.split(os.path.sep)[-2]
    training_labels.append(label)
    pbar.update(i)

pbar.finish()


# === FIT MODEL === 
print("Fitting Model")
training_data = np.array(training_data).reshape((len(training_set),52))
params = {"C": [0.1, 1.0, 10.0, 100.0, 1000.0, 10000.0]}
model = GridSearchCV(SVC(random_state=42,probability = True,max_iter=50000,class_weight='balanced'),params,cv=3)
model.fit(training_data, training_labels)

# === GENERATE T-SNE PLOT ===
print("Generating t-SNE visualization")
plot_labels = np.asarray([domain.category_ids[c] for c in training_labels])
generate_tSNE_plot(training_data,plot_labels,"tSNE_lbp")

# === ANALYZE TEST SET === 
test_labels = []
test_data = []

widgets = ["Analyzing Test Set: ",progressbar.Percentage(), " ", progressbar.Bar(), " ", progressbar.ETA()]
pbar = progressbar.ProgressBar(maxval = len(testing_set),widgets=widgets).start()
for i,image_path in enumerate(testing_set):
    image = cv2.imread(image_path)
    image_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    image_data = analyze_image_lbp(image_gray,desc4,desc8)
    test_data.append(image_data)
    
    label = image_path.split(os.path.sep)[-2]
    test_labels.append(label)
    pbar.update(i)

pbar.finish()


# === REPORT ON TEST DATA === 
test_data = np.array(test_data).reshape((len(testing_set),52))

predictions_proba = model.predict_proba(test_data)
predictions = np.argmax(predictions_proba,axis = 1)

test_labels = [domain.category_ids[c] for c in test_labels]
test_labels = np.asarray(test_labels)

print(classification_report(test_labels, predictions))


# === SAVE MODEL OUTPUT ===

f = open('model/model_lbp.cpickle', "wb")
f.write(pickle.dumps(model))
f.close()
