import json
from os.path import join as pjoin, exists
import cv2

import detect_compo.ip_region_proposal as ip


def resize_height_by_longest_edge(img_path, resize_length=800):
    org = cv2.imread(img_path)
    height, width = org.shape[:2]
    if height > width:
        return resize_length
    else:
        return int(resize_length * (height / width))


if __name__ == '__main__':
    # initialization
    input_img_root = "data/Android_GUI_data/combined/"


    key_params = {'min-grad':10, 'ffl-block':5, 'min-ele-area':50, 'merge-contained-ele':True,
                      'max-word-inline-gap':4, 'max-line-gap':4}
    input_imgs = [input_img_root + str(img) + '.jpg' for img in range(72219)]
    input_imgs = sorted(input_imgs, key=lambda x: int(x.split('/')[-1][:-4]))  # sorted by index


    # Load deep learning models in advance
    compo_classifier = None
   

    import detect_text_east.ocr_east as ocr
    import detect_text_east.lib_east.eval as eval
    models = eval.load()
    

    compo_classifier = {}
    from cnn.CNN import CNN
    compo_classifier['Elements'] = CNN('Elements')

    # set the range of target inputs' indices
    num = 0
    start_index = 0 
    end_index = 100000 # 61728
    import os 
    import merge
    import cv2
    for input_img in input_imgs:
        # The whole process takes a long time, you can use start_index to continue
        if not os.path.exists(input_img):
            # some image index do not exists in RICO
            continue
        resized_height = resize_height_by_longest_edge(input_img)
        index = input_img.split('/')[-1][:-4]
        output_root = 'data/output/'
        print(num, input_img)
        num += 1
        if int(index) < start_index:
            continue
        if int(index) > end_index:
            break
        ocr.east(input_img, output_root, models, key_params['max-word-inline-gap'],
                resize_by_height=resized_height, show=False)
        ip.compo_detection(input_img, output_root, key_params,
                        classifier=compo_classifier, resize_by_height=resized_height, show=False)
        output_root = 'data/Android_output/'
        compo_path = pjoin(output_root, 'ip', str(index) + '.json')
        ocr_path = pjoin(output_root, 'ocr', str(index) + '.json')
        merge.incorporate(input_img, compo_path, ocr_path, output_root, params=key_params,
                        resize_by_height=resized_height, show=False, savename=str(index)+'.jpg')

