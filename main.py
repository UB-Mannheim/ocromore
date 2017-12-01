
# ! /usr/bin/python3.6
# -*- coding: utf-8 -*-
"""
This is a script for testing different python3.6/python features
and basic functionality, just to learn python from scratch and by doing.
I intend to stick to the PEP-8 coding guidelines.
"""
import os

try:
    import Image
except ImportError:
    from PIL import Image

import pytesseract


pytesseract.pytesseract.tesseract_cmd = '/usr/local/bin/tesseract'

TESSDATA_DIR_CONFIG = \
    '--tessdata-dir "/home/johannes/Repos/tesseract/tessdata/tessdata_fast"'
IMAGE_PATH = '/media/sf_firmprofiles/many_years_firmprofiles/short/oneprof'
FILENAME = 'oneprof.jpg'

filepath = os.path.join(IMAGE_PATH, FILENAME)
image = Image.open(filepath)
# text = pytesseract.image_to_string(image)

text = pytesseract.image_to_string(
    image,
    lang='deu',
    config=TESSDATA_DIR_CONFIG
)

print("Converted image at", filepath, " to text: ", text)
