import cv2
import numpy as np

def extract_color_histogram(img_path: str):
    img = cv2.imread(img_path)
    if img is None:
        return None
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    hist = cv2.calcHist([hsv],[0,1,2],None,[8,8,8],[0,256,0,256,0,256])
    hist = cv2.normalize(hist, hist).flatten()
    return hist
