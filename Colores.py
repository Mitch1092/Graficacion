import cv2 as cv
import numpy as np

img1 = cv.imread('./resources/Negative.jpg',1)
img1a=cv.cvtColor(img1,cv.COLOR_BGR2GRAY)


x,y,z = img1.shape 
img2 = np.zeros((x,y), np.uint8)
b,g,r= cv.split(img1)
cv.imshow('b',b)
cv.imshow('g',g)
cv.imshow('r',r)
mr=cv.merge([img2,img2,r])
mg=cv.merge([img2,g,img2])
mb=cv.merge([b,img2,img2])
cv.imshow('mb',mb)
cv.imshow('mg',mg)
cv.imshow('mr',mr)
nueva=cv.merge([r,g,b])
nueva2=cv.merge([b,g,r])
nueva3=cv.merge([b,r,g])
cv.imshow('n1',nueva)
cv.imshow('n2',nueva2)
cv.imshow('n3',nueva3)
cv.imshow('img',img1)
cv.waitKey()
cv.destroyAllWindows()
