import cv2
import numpy as np
from PIL import Image

# import image
image = cv2.imread('egitim.jpg')

# grayscale
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

# binary
gray = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 1085,31)

# dilation
kernel = np.ones((2, 1), np.uint8)
img_dilation = cv2.dilate(gray, kernel, iterations=1)

#find contours
ctrs, hier = cv2.findContours(img_dilation.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

# sort contours
sorted_ctrs = sorted(ctrs, key=lambda ctr: cv2.boundingRect(ctr)[0])

cv2.imwrite("dilation.png", cv2.bitwise_not(img_dilation))
image3 = Image.open("dilation.png")

name=str(input("eklenecek karakteri girin:"))
for i, ctr in enumerate(sorted_ctrs):
    # Get bounding box
    x, y, w, h = cv2.boundingRect(ctr)

    # Getting ROI
    target = image3.crop((x, y, x + w, y + h))
    roi = target.convert('P', colors=255, palette=Image.ADAPTIVE)


    if w > 5 and h > 5: # çok küçük karakterler eğitim için kullanılamaz
        roi.save("chars/"+"{}".format(name)+" ({}).png".format(i))
        #cv2.imwrite('chars/{}.png'.format(name), roi)

cv2.imshow('marked areas', image)
cv2.waitKey(0)