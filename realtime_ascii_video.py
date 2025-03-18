import cv2
import numpy as np

from image_to_ascii import *

# Open the default camera
cam = cv2.VideoCapture(0)

# Get the default frame width and height
frame_width = int(cam.get(cv2.CAP_PROP_FRAME_WIDTH))
frame_height = int(cam.get(cv2.CAP_PROP_FRAME_HEIGHT))

detailed_set = [
    "@", "B", "%", "8", "&", "W", "M", "#", "*", "o", "a", "h", "k", "b", "d", "p", "q", "w", "m",
    "Z", "O", "0", "Q", "L", "C", "J", "U", "Y", "X", "z", "c", "v", "u", "n", "x", "r", "j", "f", "t",
    "/", "|", "(", ")", "1", "{", "}", "[", "]", "?", "-", "_", "+", "~", "<", ">", "i", "!", "l", "I",
    ";", ":", ",", "\"", "^", "`", "'.", " "
]

converter = ImageToAsciiConverter(width=150)

while True:
    ret, frame = cam.read()

    if not ret:
        break

    ascii_img = converter.convert(frame, font="fonts/UbuntuMono-B.ttf")  # Convert the frame to ASCII image

    # Convert the PIL image to OpenCV format for display
    ascii_img_cv = cv2.cvtColor(np.array(ascii_img), cv2.COLOR_RGB2BGR)

    # Display the captured frame
    cv2.imshow('Camera', ascii_img_cv)

    # Press 'q' to exit the loop
    if cv2.waitKey(1) == 27: # closes window with the Escape key
        break

# Release the capture and writer objects
cam.release()
cv2.destroyAllWindows()