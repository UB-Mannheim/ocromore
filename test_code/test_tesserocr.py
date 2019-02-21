"""
    Applied fix by stweil from https://github.com/tesseract-ocr/tesseract/issues/1045 to make tesserocr work
    for tessocr   https://github.com/sirfz/tesserocr the tesseract.pxd file in the root of repository is  good function ref

    CMD to use tesseract in cmd line with hocr is:
    tesseract  --tessdata-dir /home/johannes/Repos/tesseract/tessdata/tessdata_fast ./oneprof.jpg ./oneprof -l deu -c tessedit_create_hocr=1
"""

import os
os.environ['TESSDATA_PREFIX'] = '/home/johannes/Repos/tesseract/tessdata/tessdata_fast/'

import tesserocr
from tesserocr import PyTessBaseAPI, RIL, iterate_level, PSM, OEM
from PIL import Image
# api2 = PyTessBaseAPI(path='/usr/local/bin/tesseract') 

MY_TESSDATA_PATH = '/home/johannes/Repos/tesseract/tessdata/tessdata_fast/'
# api = PyTessBaseAPI(path=MY_TESSDATA_PATH) # only 2 path definition wors


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

def check_test(): 
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


def get_boxes_with_info():
    image = Image.open('/home/johannes/Repos/tesseract/testing/phototest.tif')

    api.SetImage(image)
    boxes = api.GetComponentImages(RIL.TEXTLINE, True)
    print('Found {} textline image components.'.format(len(boxes)))
    for i, (im, box, _, _) in enumerate(boxes):
        # im is a PIL image object
        # box is a dict with x, y, w and h keys
        api.SetRectangle(box['x'], box['y'], box['w'], box['h'])
        ocrResult = api.GetUTF8Text()
        awc = api.AllWordConfidences()
        awrds  = api.AllWords()
        conf = api.MeanTextConf()
        print(u"Box[{0}]: x={x}, y={y}, w={w}, h={h}, confidence: {1}, text: {2}".format(i, conf, ocrResult, **box))

def classifier_choices():
    api.SetImageFile('/home/johannes/Repos/tesseract/testing/phototest.tif')
    api.SetVariable("save_blob_choices", "T")
    api.SetRectangle(37, 228, 548, 31)
    api.Recognize()

    ri = api.GetIterator()
    level = RIL.SYMBOL
    # level = RIL.PARA paragraj
    for r in iterate_level(ri, level):
        symbol = r.GetUTF8Text(level)  # r == ri
        conf = r.Confidence(level)
        test = r.SetLineSeparator('\a')
        lang = r.WordRecognitionLanguage()
        if symbol:
            print(u'symbol {}, conf: {}'.format(symbol, conf))
        indent = False
        ci = r.GetChoiceIterator()

        for c in ci:
            if indent:
                print('\t\t ')
            print('\t- ')
            choice = c.GetUTF8Text()  # c == ci
            print(u'{} conf: {}'.format(choice, c.Confidence()))
            indent = True
            ci.Next() # j4t 


        print('---------------------------------------------')

# classifier_choices()

def orientation_stuff():
    api2 = PyTessBaseAPI(psm=PSM.OSD_ONLY, path=MY_TESSDATA_PATH) 
    api2.SetImageFile('/home/johannes/Repos/tesseract/testing/eurotext.tif')

    # os = api2.DetectOS()
    os = api2.DetectOrientationScript()  # beide verursachen fehler: 'Speicherzugriffsfehler (Speicherabzug geschrieben)'
    print("Orientation: {orientation}\nOrientation confidence: {oconfidence}\n Script: {script}\nScript confidence: {sconfidence}".format(**os)) 


orientation_stuff()