import numpy as np
import cv2

pic = cv2.imread('tiny.png')

print(str(pic))

#Opencv reads an image from the top left corner.  Each pixel is an array (BGR)
#Each row is an array of these pixel-rows.  The image is an array of those row-arrays.

#Output:
#[[[  0   0   0]
  #[ 48  48  48]
  #[ 64  64  64]
  #[128 128 128]
  #[160 160 160]]

 #[[  0   0 127]
  #[  0   0 255]
  #[127 127 255]
  #[  0  51 127]
  #[  0 106 255]]

 #[[127 178 255]
  #[  0 106 127]
  #[  0 216 255]
  #[127 233 255]
  #[  0 127  91]]

 #[[  0 255 182]
  #[127 255 218]
  #[  0 127  38]
  #[  0 255  76]
  #[127 255 165]]

 #[[127 127   0]
  #[255 255   0]
  #[255 255 127]
  #[127  74   0]
  #[255 148   0]]

 #[[255 255 127]
  #[127  19   0]
  #[255  38   0]
  #[255 146 127]
  #[127   0  33]]

 #[[255   0  72]
  #[255 127 161]
  #[127   0  87]
  #[255   0 178]
  #[255 127 214]]

 #[[110   0 127]
  #[220   0 255]
  #[237 127 255]
  #[110   0 127]
  #[110   0 255]]

 #[[160 160 160]
  #[128 128 128]
  #[ 64  64  64]
  #[ 48  48  48]
  #[  0   0   0]]

 #[[255 255 255]
  #[255 255 255]
  #[255 255 255]
  #[255 255 255]
  #[255 255 255]]]
  
  
#pic = cv2.cvtColor(pic, cv2.COLOR_BGR2GRAY) 
  
#When we convert to grayscale, everything is just based on intensity.  Each pixel is one point.
#Each row is an array of pixel-points.  The image is an array of row-arrays.  This is one less
#array than before.

#Output:
#[[  0  48  64 128 160]
 #[ 38  76 165  68 138]
 #[195 100 203 227 102]
 #[204 229  86 172 213]
 #[ 89 179 217  58 116]
 #[217  26  51 153  24]
 #[ 51 152  40  82 168]
 #[ 51 101 178  51  89]
 #[160 128  64  48   0]
 #[255 255 255 255 255]]
