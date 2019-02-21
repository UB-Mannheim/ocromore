"""
Basically this is stuff from akf-mocrin to test ocropy
"""

import os
import subprocess

IMAGE_PATH = '/media/sf_firmprofiles/many_years_firmprofiles/short/oneprof'
FILENAME = 'oneprof.jpg'

filepath = os.path.join(IMAGE_PATH, FILENAME)

def create_dir(newdir):
    """
    Creates a new directory
    :param_newdir: Directory which should be created
    :return: None
    """
    if not os.path.isdir(newdir):
        try:
            os.makedirs(newdir)
            print(newdir)
        except IOError:
            print("cannot create %s directoy" % newdir)
    return 0


def start_ocropy(file, path_out, ocropy_profile):
    """
    Start ocropus over a cli
    :param file: fileinputpath
    :param fop: fileoutputpath
    :param profile: contains user-specific parameters/option for ocropy
    :return:
    """
    print("Starting ocropy for:" + file.split('/')[-1])

    fname = file.split('/')[-1].split('.')[0]
    create_dir(path_out)
    subprocess.Popen(args=["ocropus-nlbin", file, "-o"+path_out+fname+"/"]).wait()
    subprocess.Popen(args=["ocropus-gpageseg", path_out+fname+"/????.bin.png"]).wait()
    subprocess.Popen(args=["ocropus-rpred", "-Q 4", path_out+fname+"/????/??????.bin.png"]).wait()
    test = ["ocropus-hocr", path_out+fname+"/????.bin.png", "-o"+path_out+"/"+fname.split('/')[-1]+".html"]
    subprocess.Popen(args=["ocropus-hocr", path_out+fname+"/????.bin.png", "-o"+path_out+"/"+fname.split('/')[-1]+".html"]).wait()
    print("Finished ocropy for:" + file.split('/')[-1])
    return 0


start_ocropy(filepath, '.', '')
