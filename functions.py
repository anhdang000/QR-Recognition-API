import cv2, os, skimage
import numpy as np
from skimage import filters, img_as_ubyte
from skimage.io import imsave, imread
from skimage.color import rgb2gray


def ensure_dir(file_path):
  directory = os.path.dirname(file_path)
  if not os.path.exists(directory):
    os.makedirs(directory)

def check_sep(path):
  if path[-1] == os.path.sep:
    return path
  else:
    return path + os.path.sep

def rename(file, filter):
  file_address = file.split(check_sep(IN_DIR))[1]
  ensure_dir(os.path.join(OUT_DIR, filter, file_address))
  return os.path.join(OUT_DIR, filter, file_address)

def apply_brightness_contrast(file):
  image = cv2.imread(cv2.samples.findFile(file))
  brightness=0
  contrast=1.6
  image = cv2.convertScaleAbs(image, alpha=contrast, beta=brightness)

  return image

def apply_invert(file):
  image = cv2.imread(cv2.samples.findFile(file))
  inv  = ~image
  return inv

def apply_invert_multiply(file):
  image = cv2.imread(cv2.samples.findFile(file))
  img = image.astype(np.float32)
  inv  = ~image
  inv = inv.astype(np.float32)
  return np.multiply(img,  inv)/255

def apply_invert_screen(file):
  image = cv2.imread(cv2.samples.findFile(file))
  img = image.astype(np.float32)
  inv  = ~image
  inv = inv.astype(np.float32)
  return 255 - np.multiply(255 - img, 255 - inv)/255

def apply_invert_darken(file):
  image = cv2.imread(cv2.samples.findFile(file))
  img = image.astype(np.float32)
  inv  = ~image
  inv = inv.astype(np.float32)
  return np.minimum(img, inv)

def apply_invert_lighten(file):
  image = cv2.imread(cv2.samples.findFile(file))
  img = image.astype(np.float32)
  inv  = ~image
  inv = inv.astype(np.float32)
  return np.maximum(img, inv)

def apply_invert_overlay(file):
  image = cv2.imread(cv2.samples.findFile(file))
  img = image.astype(np.float32)
  inv  = ~image
  inv = inv.astype(np.float32)
  mask = img >= 127.5 
  a = np.where(mask==0, (2*np.multiply(img,  inv)) , 0)
  b = np.where(mask==1, (65025-2*np.multiply(255 - img, 255 - inv)) , 0)
  return (a+b)/255

def apply_invert_softlight(file):
  image = cv2.imread(cv2.samples.findFile(file))
  img = image.astype(np.float32)
  inv  = ~image
  inv = inv.astype(np.float32)
  mask = inv >= 127.5 
  a = np.where(mask==0, (2*np.multiply(img/255,  inv/255) + np.multiply(np.square(img/255), (1 - 2*inv/255))) , 0)
  b = np.where(mask==1, (2*np.multiply(img/255, 1 - inv/255) + np.multiply(np.sqrt(img/255), (2*inv/255 - 1))) , 0)
  return (a+b)*255

def apply_li_tri(file):
  image = imread(file)
  blur = skimage.color.rgb2gray(image)
  thresh_tri = skimage.filters.threshold_triangle(blur)
  mask_tri = blur < thresh_tri
  thresh_li = skimage.filters.threshold_li(blur)
  mask_li = blur < thresh_li
  not_li = ~mask_li
  not_tri = ~mask_tri
  mask_out_li_in_tri = np.multiply(not_li, mask_tri)
  mask_out_li_out_tri = np.multiply(not_li, not_tri)
  sel2 = np.zeros_like(image)
  sel2[mask_out_li_out_tri] = image[mask_out_li_out_tri]
  sel2 = cv2.medianBlur(sel2, ksize=3)
  sel = np.zeros_like(image)
  sel.fill(255)
  sel[mask_li]  = image[mask_li] /2
  sel[mask_out_li_in_tri] = image[mask_out_li_in_tri]
  sel[mask_out_li_out_tri] = sel2[mask_out_li_out_tri]
  return sel[:, :, ::-1]
