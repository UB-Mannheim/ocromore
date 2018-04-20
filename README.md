# ![ocromore](docs/img/ocromore_logo.png)

![license](https://img.shields.io/badge/license-Apache%20License%202.0-blue.svg)

Originally written by Johannes Stegmüller and Jan Kamlah.

## Overview

`ocromore` is a command line driven post-processing tool for ocr-outputs.  

The main purpose is to combine multiple ocr-outputs for better recognition results.
It can also be used to find optimal settings for ocr software, to visualize different 
information about the ocr results or context, or just query various things.

First, the program parses the different ocr-output files and saves the results to a sqlite-database.
The purpose of this database is to serve as an exchange and store platform using 
[pandas](https://pandas.pydata.org/) as handler.
Using the [dataframe](https://pandas.pydata.org/pandas-docs/stable/generated/pandas.DataFrame.html)-objectifier from pandas a wide-range of performant use-cases like Multiple sequence alignment (MSA) is possible.
To evaluate the results you can either use the commonly used
[isri tools](https://github.com/eddieantonio/isri-ocr-evaluation-tools) to generate a accuracy report, or do visual comparison with diff-tools like [meld](http://meldmerge.org/).

Note that the automatic processing will sometimes need some manual adjustments.

### Beta Results
The software is currently optimized for the [DFG-Project "Aktienführer II"](https://www.bib.uni-mannheim.de/projekte/aktienfuehrer2/) and our current character accuracy (ignoring whitespaces) results are:

| OCR-Engine |   AKF-II   |  UNLV   |
|:----------:|:----------:|:-------:|
| Abbyy      |  84,08 %   | 88.85 % |
| Ocropus (default en-model)    |     | 87.33 % | 
| Ocropus  (trained)   |  98,67 %   |  | 
| Tesseract  |  98,79 %   | 96.59 % |
| MSA        |  99,19 %   | 96.73 % |


You can find the AKF-II result in [docs/results](./docs/results).
The results for UNLV are not optimized but still there is some improvement.
You can find the UNLV results in [Testfiles/results](./Testfiles/results).

### Roadmap
✓  Parse files to the database  
✓  Preprocess file information    
✓  Combine file information  
✓  Evaluate results against groundtruth  
✓  Visual comparision (result vs. gt) with diff-tool  
✓  Store results in txt-file   
✘  Store results in database/hocr-files  
✘  Plot results in different ways (with matplotlib)

#### Supported fileformats
✓  hocr (with confidences)   
✓  abbyy-xml (with confidences "ASCII")
 
## Installation

### Requirements

#### Install:

- linux distribution, e.g. [Ubuntu][ubuntu-link]
- [Python 3.6][python-link]
- [PyCharm][pycharm-link] (some functions depend on the IDE)
- [Meld][meld-link]
- [ISRI Analytic Tools for OCR Evaluation][isri-link]

Recommended:

- [hocr-tools][hocr-link]

#### Alternative docker (for windows recommended):

For the CLI commands:

```
docker build -t ocromore .
docker run -it -v `PWD`:/home/developer/coding/ocromore  ocromore
```

To run the scripts for visual results in your OS:  
(not available in the docker-image) 

- install Python and Requirements   
- install [Meld][meld-link] (for windows)  
- Add to environment variables (ENV)
     - Variable = "Path"
     - Value = {directory to meld}\meld.exe

#### Developing

The project was written in PyCharm 2017.3 (CE),   
so if you are a developer it's recommended to use it. 

Python 3.6.3 (default, Oct  6 2017, 08:44:35)   
[GCC 5.4.0 20160609] on linux  
Tested on: Ubuntu17.10

Meld is the default diff-tool,  
but you can easily implemented the diff-tool of your choice. 

The ISRI Tools are necessary for the evaluation, but not for the combine process.

[ubuntu-link]: https://www.ubuntu.com/
[python-link]: https://www.anaconda.com/download/
[pycharm-link]: https://www.jetbrains.com/pycharm/
[meld-link]: http://meldmerge.org/
[isri-link]: https://github.com/eddieantonio/isri-ocr-evaluation-tools
[hocr-link]: https://github.com/tmbdev/hocr-tools
    
#### Building instructions

Dependencies can be installed into a Python Virtual Environment:

    $ virtualenv ocromore_venv/
    $ source ocromore_venv/bin/activate
    $ pip install -r requirements.txt

## Process steps

![ocromore-overview](docs/img/process_steps.jpg)

   1. Parsing all ocr-outputfiles to an database  
      (This step only has to be done once)
   2. Pre-process the gathered information  
      The results from the following processes can also 
      be stored directly to the database
        + Line-matching all files 
        + Unspacing words in each file  
          Unspacing means to delete whitespaces in spaced text  
          (E.g. H e l l o => Hello)
        + Word-matching all files per line   
   3. Combine file information
      + Different compare methods
        + Textdistance-Keying
             + Levenshtein
             + Damerau-Levenshtein
             + ...
        + Multi-Sequence-Alignment (MSA)
            + pivot-based
            + linewise/wordwise
            + Adjustable search-space-processor correction
                + Matching similar character
                + Whitespace/Wildcard improvements
            + Adjustable decision parameter
                + Char confidence 
                + Best-of-n
   
   4. The output can be stored in the database and/or 
   as *.txt or *.hocr.
   
   5. Evaluate the output against groundtruth files or each other and generate a accuracy report.
   Or compare the files visual via diff-tools.


## Running

### Example
First of all you have to adjust the config-files.
There are two main config-files in "./configuartion/":
   + to_db_reader
        + path to ocr ocr-files (e.g. hocr)
        + parameter for parsing hocr to db
            + naming etc.
   + voter
        + path to db
        + parameter for combining the information from the ocr-files
        
The parameter to perform the examples are set as default.  
So you can just run the following commands.

At the current stage it is recommended to use PyCharm to perform the next steps.
        
Parse files to db and do preprocessing:

    # All parameters can set in the to_db_reader config
    # set HOCR2SQL parse files to db 
    # set POS parameter, to set the naming of db and tables 
    # set PREPROCSSING (It is recommended to perform the preprocessing steps directly after parsing  
    # but it is not necassary)
    
    $ python3 ./plt_charinfo.py
    
Combine files and generate a accuracy report:

    # All parameters can set in the voter config
    # set DO_MSA_BEST to perform msa (not Textdistance) method
    # set DO_ISRI_VAL to generate a accuracy report
    
    $ python3 ./main_msa_ndist_charconf.py
    
To perform a visual comparision:

    $ python3 ./result_visualization.py

The result are stored in ./Testfiles/tableparser_output/
