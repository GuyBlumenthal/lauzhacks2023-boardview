from pic2tex import image_request
import json
import time
import os

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
    word_data = segment_json["word_data"]
    # Check if image is not interperetable as equation
    if "error_id" in word_data[0]:
        segment_data.update({"segment_type":"diagram"})

    else:
        # Check if segment is just equation
        if len(segment_json["word_data"]) == 1:
            segment_data.update({"segment_type":"equation"})
            segment_data.update({"latex":word_data[0]["latex"]})

        # Check if segment is equation with words
        else:
            segment_data.update({"segment_type":"words_and_equation"})
            word_string = ""
            for i in range(len(segment_json["word_data"]) - 1):
                word_string += segment_json["word_data"][i]["text"] + " "
            segment_data.update({"words":word_string})
            segment_data.update({"latex":word_data[-1]["latex"]})

    return segment_data

test_image_reg = {
    'img1' : 'images_directory/blackboard.png'
}

data_set = {}

data_set.update({'img1': test_image_reg["img1"]})
data_set['img1'] = convert_new_segment(data_set["img1"])
print(data_set)

