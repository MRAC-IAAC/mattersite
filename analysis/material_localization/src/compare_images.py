import cv2
import numpy as np

def compare_images(img_output,img_anno):
    """ Compares a output 'image' in patch space, with the manually annotated image originally in image space"""
    img_anno = cv2.resize(img_anno,(img_output.shape[:2]))
    img_output = img_output.transpose(1,0,2)

    #print(img_output.shape)
    #print(img_anno.shape)

    #cv2.imwrite("comp_output.png",img_output)
    #cv2.imwrite("comp_anno.png",img_anno)
    comparison = img_output == img_anno
    score = 1.0 * comparison.all(axis=2).sum() / (img_output.shape[0] * img_output.shape[1])

    return(score)
