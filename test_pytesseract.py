
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

# TESSERACT_CONFIG
# psm 11 Sparse text. Find as much text as possible in no particular order
# => just for testing (3 is default)
TESSERACT_CONFIG = \
    '--oem 3 \
    --psm 11 \
    --tessdata-dir "/home/johannes/Repos/tesseract/tessdata/tessdata_fast"'
IMAGE_PATH = '/media/sf_firmprofiles/many_years_firmprofiles/short/oneprof'
FILENAME = 'oneprof.jpg'

filepath = os.path.join(IMAGE_PATH, FILENAME)
image = Image.open(filepath)
# text = pytesseract.image_to_string(image)
print(pytesseract.__doc__)

text = pytesseract.image_to_string(
    image,
    lang='deu',
    config=TESSERACT_CONFIG
)


print("Converted image at", filepath, " to text: ", text)
