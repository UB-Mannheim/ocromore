"""
    Applied fix by stweil from https://github.com/tesseract-ocr/tesseract/issues/1045 to make tesserocr
"""

import os
os.environ['TESSDATA_PREFIX'] = '/home/johannes/Repos/tesseract/tessdata/tessdata_fast/'

import tesserocr
from tesserocr import PyTessBaseAPI, RIL
from PIL import Image
# api2 = PyTessBaseAPI(path='/usr/local/bin/tesseract') 

api = PyTessBaseAPI(path='/home/johannes/Repos/tesseract/tessdata/tessdata_fast/') # only 2 path definition wors


# export TESSDATA_PREFIX=/home/johannes/Repos/tesseract/tessdata/tessdata_fast # do that in bash 

IMAGE_PATH = '/media/sf_firmprofiles/many_years_firmprofiles/short/oneprof'
FILENAME = 'oneprof.jpg'

filepath = os.path.join(IMAGE_PATH, FILENAME)
image = Image.open(filepath)

def get_rectangle(image):

    # print("TESSDATA_PREFIX path: ", os.environ['TESSDATA_PREFIX'])
    # print("tesserocr tesseract-version is:", tesserocr.tesseract_version())  # print tesseract-ocr version
    # print("getlanguages result is:", tesserocr.get_languages())  # prints tessdata path and list of available languages
    api.SetImage(image)
    boxes = api.GetComponentImages(RIL.TEXTLINE, True)
    print('Found {} textline image components.'.format(len(boxes)))
    for i, (im, box, _, _) in enumerate(boxes):
        # im is a PIL image object
        # box is a dict with x, y, w and h keys
        api.SetRectangle(box['x'], box['y'], box['w'], box['h'])
        ocrResult = api.GetUTF8Text()
        conf = api.MeanTextConf()
        print(ocrResult)   


# get_rectangle(image)


api.SetImageFile(image)
api.SetVariable("save_blob_choices", "T")
api.SetRectangle(37, 228, 548, 31)
api.Recognize()

ri = api.GetIterator()
level = RIL.SYMBOL
for r in iterate_level(ri, level):
    symbol = r.GetUTF8Text(level)  # r == ri
    conf = r.Confidence(level)
    if symbol:
        print("symbol ", symbol, " confidence", conf)
    indent = False
    ci = r.GetChoiceIterator()
    for c in ci:
        if indent:
            print('\t\t '),
        print('\t- '),
        choice = c.GetUTF8Text()  # c == ci
        print(u'{} conf: {}'.format(choice, c.Confidence()))
        indent = True
    print('---------------------------------------------')