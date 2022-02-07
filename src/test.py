import pytesseract as py
import cv2

py.pytesseract.tesseract_cmd = r'/opt/homebrew/Cellar/tesseract/5.0.1'
img=cv2.imread(r'image1.png')
print(img.shape)
print(py.image_to_string(img))