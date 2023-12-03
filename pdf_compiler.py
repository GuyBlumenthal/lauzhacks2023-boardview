import os
import time

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

file = open('full.tex', 'w+')
file.writelines(template_header)
file.writelines(template_footer)
file.close()
os.system("pdflatex full.tex")


def update_tex(segment_data):
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

    # Save current file data
    with open("full.tex", 'r') as file:
        data = file.readlines()

    data[-1] = new_line

    with open("full.tex", 'w') as file:
        # Replace last data with new data
        file.writelines(data)
        file.writelines(template_footer)


    os.system("pdflatex full.tex")
    time.sleep(0.5)


test_equation_1 = {'image_of_segment': 'images_directory/equation_test.png', 'segment_type': 'equation', 'latex': '\\begin{aligned}\n5+x & =\\frac{25}{10} \\\\\n10(5+x) & =25 \\\\\n50+10 x & =25 \\\\\n10 x & =-25 \\\\\nx & =-2.5\n\\end{aligned}'}
test_equation_2 = {'image_of_segment': 'images_directory/text_and_equation.png', 'segment_type': 'words_and_equation', 'words': 'As seen in the equation below ', 'latex': 'f(x)=x^{2}+\\int_{0}^{1} \\cos (x)'}
test_equation_3 = {'image_of_segment': 'images_directory/plot_test.png', 'segment_type': 'diagram'}

update_tex(test_equation_1)
time.sleep(3)
update_tex(test_equation_2)
time.sleep(3)
update_tex(test_equation_3)

