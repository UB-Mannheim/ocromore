import json

def get_charconfs(hocr):
    charinfo = {}
    for lines in hocr:
        for word in lines.words:
            for idx, char in enumerate(word.ocr_text):
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
