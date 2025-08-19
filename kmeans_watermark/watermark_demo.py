# import cv2
# import numpy as np
# from sklearn.cluster import KMeans

# img = cv2.imread("input.jpg", cv2.IMREAD_GRAYSCALE)
# wm = cv2.imread("watermark.png", cv2.IMREAD_GRAYSCALE)
# wm = cv2.resize(wm, (img.shape[1], img.shape[0]))

# pixels = img.reshape(-1,1)
# kmeans = KMeans(n_clusters=2, random_state=42).fit(pixels)

# watermarked = img.copy()
# watermarked[wm > 128] = watermarked[wm > 128] // 2

# cv2.imwrite("watermarked.jpg", watermarked)

## ABOVE IS MY ORIGINAL CODE. BELOW CHATGPT HELPED FIX MY ISSUE.

import os, cv2
import numpy as np
from sklearn.cluster import KMeans

HERE = os.path.dirname(__file__)
img = cv2.imread(os.path.join(HERE, "input.jpg"), cv2.IMREAD_GRAYSCALE)
wm  = cv2.imread(os.path.join(HERE, "watermark.png"), cv2.IMREAD_GRAYSCALE)

# Safety checks
assert img is not None, f"Couldn't read input.jpg at {os.path.join(HERE,'input.jpg')}"
assert wm  is not None, f"Couldn't read watermark.png at {os.path.join(HERE,'watermark.png')}"

# Match sizes
wm = cv2.resize(wm, (img.shape[1], img.shape[0]))

# (Optional) KMeans just to keep the example complete
pixels = img.reshape(-1, 1)
_ = KMeans(n_clusters=2, random_state=42).fit(pixels)

watermarked = img.copy()
watermarked[wm > 128] = watermarked[wm > 128] // 2

cv2.imwrite(os.path.join(HERE, "watermarked.jpg"), watermarked)
print("[ok] wrote:", os.path.join(HERE, "watermarked.jpg"))
