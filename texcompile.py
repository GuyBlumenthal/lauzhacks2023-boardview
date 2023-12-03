from pic2tex import image_request
import json
import time
import os
import cv2

from pathlib import Path

IMG_DIR = Path("out/")
data_base = {}

template_header = [
    "\\documentclass[12pt]{article}\n",
    "\\usepackage{float}\n"
    "\\usepackage{sectsty}\n",
    "\\usepackage{graphicx}\n",
    "\\usepackage{amsmath, amsthm, amssymb}\n"
    # Margins
    "\\topmargin=-0.45in\n",
    "\\evensidemargin=0in\n",
    "\\oddsidemargin=0in\n",
    "\\textwidth=6.5in\n",
    "\\textheight=9.0in\n",
    "\\headsep=0.25in\n",
    "\\font\\myfont=cmr12 at 40pt\n",

    "\\newenvironment{segment}[2][Captured note:]{\\begin{trivlist}",
    "\\item[\\hskip \\labelsep {\\bfseries #1}\\hskip \\labelsep {\\bfseries #2.}]}{\\end{trivlist}}\n",

    "\\title{{\\myfont Live Meeting Notes}}\n",
    "\\author{Board Scribe}"
    "\\date{\\today}\n",

    "\\begin{document}\n",
    "\\maketitle\n",
]

template_footer = [
    "\\end{document}"
]

def update_data_base(update_id, update_img):
    # Save the image for sending to api
    img_path = str(IMG_DIR / f"img_{update_id}.png")
    cv2.imwrite(img_path, update_img)
    
    image_data = convert_new_segment(img_path)
    data_base[update_id] = image_data

    return

def convert_new_segment(image):
    '''
    arguments:
        - image: new image from segmentation, given as a .png
    output:
        - segment_data: list of data from segment converted by Mathpix
    '''

    segment_data = {}
    segment_data.update({"image_of_segment":image})
    segment_json = image_request(image)
    print(segment_json)
    
    if "error" in segment_json:
        print('type is image')
        segment_data.update({"segment_type":"diagram"})
    else:
        word_data = segment_json["word_data"]

        # Check if image is not interperetable as equation
        if "error_id" in word_data[0]:
            print('type is image')
            segment_data.update({"segment_type":"diagram"})

        else:
            if "latex" in word_data[-1]:
                # Check if segment is just equation
                if len(segment_json["word_data"]) == 1:
                    print('type is equation')
                    segment_data.update({"segment_type":"equation"})
                    segment_data.update({"latex":word_data[0]["latex"]})

                # Check if segment is equation with words
                else:
                    print('type is words and equation')
                    segment_data.update({"segment_type":"words_and_equation"})
                    word_string = ""
                    for i in range(len(segment_json["word_data"]) - 1):
                        word_string += segment_json["word_data"][i]["text"] + " "
                    segment_data.update({"words":word_string})
                    segment_data.update({"latex":word_data[-1]["latex"]})
            else:
                print('type is words')
                segment_data.update({"segment_type":"words"})
                word_string = ""
                for i in range(len(segment_json["word_data"])):
                    word_string += segment_json["word_data"][i]["text"] + " "
                segment_data.update({"words":word_string})

    return segment_data

def initialise_tex():
    IMG_DIR.mkdir(parents= True, exist_ok = True)    

    file = open('full.tex', 'w+')

    file.writelines(template_header)
    file.writelines(template_footer)

    file.close()
    
    os.system("pdflatex full.tex")
    
    return

def get_data():
    return data_base

def get_tex_line(segment_data):
    # Add equation
    if segment_data["segment_type"] == "equation":
        math_code = '\[' + segment_data["latex"] + '\]\n'
        new_line = '\\begin{segment}{(index)}\n' + math_code + '\\end{segment}\n' + '\\vspace{10pt}\n'

    # Add equation with text
    elif segment_data["segment_type"] == "words_and_equation":
        math_code = '\[' + segment_data["latex"] + '\]\n'
        words = segment_data["words"] + '\n'
        new_line = '\\begin{segment}{(index)}\n' + words + math_code + '\\end{segment}\n' + '\\vspace{10pt}\n'

    # Add diagram
    elif segment_data["segment_type"] == "diagram":
        loc = segment_data["image_of_segment"]
        graphic = '\\includegraphics[width=10cm]{' + loc + '}\n'
        new_line = '\\begin{segment}{(index)}\n' + '\\begin{figure}[H]\n\\centering\n' + graphic + '\\end{figure}\n\\end{segment}\n' + '\\vspace{10pt}\n' 

    elif segment_data["segment_type"] == "words":
        words = segment_data["words"] + '\n'
        new_line = '\\begin{segment}{(index)}\n' + words + '\\end{segment}\n' + '\\vspace{10pt}\n'

    return new_line


def end_file(data):
    with open("full.tex", 'w') as file:
        # Replace last data with new data
        file.writelines(template_header)
        file.writelines(data)
        file.writelines(template_footer)


    os.system("pdflatex full.tex")