import json
import string

def get_charconfs(hocr):
    charinfo = {}
    for lines in hocr:
        for word in lines.words:
            for idx, char in enumerate(word.ocr_text):
                if word._xconfs != None:
                    if idx < len(word._xconfs):
                        if char not in charinfo:
                            charinfo[char] = {"Confs": ""}
                            charinfo[char]["Confs"] = [word._xconfs[idx]]
                        else:
                            charinfo[char]["Confs"].append(word._xconfs[idx])
    return charinfo

def dump_charinfo(charinfo,fileout):
    with open(fileout + "_charinfo.json", "w") as output:
        json.dump(charinfo, output, indent=4)
    return 0

def merge_charinfo(files, GROUPS=False):
    charinfomerged = dict()
    groupmember = {"Zeichen":"printable","Buchstaben":"ascii_letters","Zahlen":"digits","Satzzeichen":"punctuation"}
    for file in files:
        with open(file, "r") as input:
            charinfo = json.load(input)
        if not charinfomerged:
            charinfomerged = charinfo
            if GROUPS:
                for member in groupmember:
                    charinfomerged[member] = {"Confs": list()}
        else:
            for char in charinfo:
                if char not in charinfomerged:
                    charinfomerged[char] = {"Confs": list()}
                charinfomerged[char]["Confs"].append(charinfo[char]["Confs"][0])
                if GROUPS:
                    for member in groupmember:
                        if char in getattr(string, groupmember[member]):
                            charinfomerged[member]["Confs"].append(charinfo[char]["Confs"][0])
    return charinfomerged
