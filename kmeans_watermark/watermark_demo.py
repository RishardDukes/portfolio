import cv2
import numpy as np
from sklearn.cluster import KMeans

img = cv2.imread("input.jpg", cv2.IMREAD_GRAYSCALE)
wm = cv2.imread("watermark.png", cv2.IMREAD_GRAYSCALE)
wm = cv2.resize(wm, (img.shape[1], img.shape[0]))

pixels = img.reshape(-1,1)
kmeans = KMeans(n_clusters=2, random_state=42).fit(pixels)

watermarked = img.copy()
watermarked[wm > 128] = watermarked[wm > 128] // 2

cv2.imwrite("watermarked.jpg", watermarked)