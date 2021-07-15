
import cv2

from os import listdir

files = listdir("input")

max_size = 1024

for f in files:
    print(f)
    img = cv2.imread("input/" + f)
    w = img.shape[1]
    h = img.shape[0]

    factor = (max_size / w) if (w > h) else (max_size / h)

    img = cv2.resize(img,(int(w * factor),int(h * factor)))

    cv2.imwrite("output/" + f,img)

