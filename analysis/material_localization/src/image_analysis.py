import cv2
import numpy as np

def analyze_image_bovw(image_gray,dad,bovw,idf):
    """
    Takes a image in grayscale
    Returns a bovw histogram
    """

    (kps,descs) = dad.describe(image_gray)

    if kps is None or descs is None:
        return None

    hist = bovw.describe(descs)
    hist /= hist.sum()
    hist = hist.toarray()

    if idf is not None:
        hist *= idf

    return hist

def analyze_image_hs(image_hs,normalize = False):
    """ 
    Takes an image in HSV format
    Returns an array of the 16-part hue histogram and the 16-part saturation histogram
    """
    
    (h,s,v) = cv2.split(image_hs)

    # Turn image into 1d array
    h_flat = h.reshape(1,h.shape[0] * h.shape[1])
    s_flat = s.reshape(1,s.shape[0] * s.shape[1])

    if normalize:
        h_min = int(np.min(h_flat))
        h_max = int(np.max(h_flat))
        s_min = int(np.min(s_flat))
        s_max = int(np.max(s_flat))
    else:
        h_min = 0
        h_max = 180
        s_min = 0
        s_max = 256

    if h_max == 0:
        h_max = 1
    if s_max == 0:
        s_max = 1


    # Calculate histograms
    hist_hue = cv2.calcHist(h_flat,[0],None,[16],[h_min,h_max])
    hist_sat = cv2.calcHist(s_flat,[0],None,[16],[s_min,s_max])

    # Normalize Histograms
    hist_hue /= hist_hue.sum()
    hist_sat /= hist_sat.sum()

    combined = np.concatenate([hist_hue,hist_sat])

    return(combined)


def analyze_image_lbp(image_gray,desc4,desc8):
    """
    Takes an image in grayscale
    Returns an array combining the size 4 and size 8 descriptor histograms
    """
    
    hist4 = desc4.describe(image_gray)
    hist4 /= hist4.sum()
    
    hist8 = desc8.describe(image_gray)
    hist8 /= hist8.sum()

    combined = np.concatenate([hist4,hist8])

    return(combined)
    
