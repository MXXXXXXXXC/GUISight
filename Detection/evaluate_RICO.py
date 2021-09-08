"""
This is to evaluate the detection technique on RICO data set and record result on different iou
"""


import cv2
import os
import json

count = 0

def iou(box1, box2):
    '''

    '''
    in_h = min(box1[2], box2[2]) - max(box1[0], box2[0])
    in_w = min(box1[3], box2[3]) - max(box1[1], box2[1])
    inter = 0 if in_h < 0 or in_w < 0 else in_h * in_w
    union = (box1[2] - box1[0]) * (box1[3] - box1[1]) + \
            (box2[2] - box2[0]) * (box2[3] - box2[1]) - inter
    iou = inter / union
    return iou


def load_component(address_json):
    with open(address_json, 'r') as load_f:
        pre_dict = json.load(load_f)
    # print(address_json)
    # print(predict)
    # print(pre_dict)
    width = float(pre_dict['img']['shape'][1])
    height = float(pre_dict['img']['shape'][0])
    predict_box_lst = []
    for box in pre_dict['compos']:
        pre = []
        pre.append(float(box['column_min']) )
        pre.append(float(box['row_min']) )
        pre.append(float(box['column_max']) )
        pre.append(float(box['row_max']))
        predict_box_lst.append(pre)

    return predict_box_lst, width, height

def test(address_img):
    global count
    count += 1
    if count > 1000:
        count = 0
        print('finish',1000)
    address_json = address_img.replace('.jpg', '.json')
    address_json_2 = address_json.replace('Android_GUI_data/combined','Android_output/result')
    if not os.path.exists(address_json_2):
        # print(address_json_2)
        return ['-1,-1,-1' for i in range(5)]
    comp_detect,ww,hh = load_component(address_json_2)


    with open(address_json, 'r') as load_f:
        load_dict = json.load(load_f)

    # print(load_dict['activity'].keys())
    UItree = load_dict['activity']['root']
    UIlst = [UItree, ]
    UI = []
    bounds = []
    while len(UIlst) != 0:
        UItree = UIlst.pop(0)
        if isinstance(UItree,dict):
            if 'class' in UItree.keys() and 'bounds' in UItree.keys():
                if UItree['bounds'] not in bounds and [0, 0, 0, 0] not in UItree['bounds']:
                    UI.append([UItree['class'], UItree['bounds']])
                    bounds.append(UItree['bounds'])
            elif 'bounds' in UItree.keys():
                if UItree['bounds'] not in bounds and [0, 0, 0, 0] not in UItree['bounds']:
                    UI.append(['Unknown', UItree['bounds']])
                    bounds.append(UItree['bounds'])

            if 'children' in UItree.keys():
                UIlst += UItree['children']

    # top left down right
    UI_SHOW = []
    for ui in UI:
        if 'Layout' not in ui[0] and 'android.widget' in ui[0]:
            UI_SHOW.append(ui)


    UI = UI_SHOW
    if len(UI) < 10:
        return ['-1,-1,-1' for i in range(10)]
    # print(UI)
    img = cv2.imread(address_img)
    # print(ww,hh)
    set1 = []
    no_top = False
    no_buttom = False
    for compo in UI:
        # print('not result:', compo)
        bbox = compo[1]
        bbox = [bbox[0]  / 1440, bbox[1]  / 2560, bbox[2] / 1440, bbox[3] / 2560]

        set1.append(bbox)
        if bbox[3] < 0.03:
            no_top = True
        if bbox[1] > 0.95:
            no_buttom = True
        # board = cv2.rectangle(board, (bbox[0], bbox[1]), (bbox[2], bbox[3]), color, line)
    # print(set1)
    # print('//////////////////////////')
    set2 = []
    for compo in comp_detect:
        # print('result:', compo)
        bbox = compo
        bbox = [bbox[0] / ww, bbox[1] / hh, bbox[2]  / ww, bbox[3]  / hh]
        # board = cv2.rectangle(board, (bbox[0], bbox[1]), (bbox[2], bbox[3]), color, line)
        if not no_top and bbox[3] < 0.03:
            continue
        if not no_buttom and bbox[1] > 0.95:
            continue

        set2.append(bbox)
    # print(set2)
    # print('//////////////////////////')
    result = []
    for iou_treshold in [0.1,0.2,0.3,0.4,0.5]:
        precision_all = len(set2)
        recall_all = len(set1)
        precision_count = 0
        recall_count = 0

        for pre in set2:
            for real in set1:
                if iou(pre, real) > iou_treshold:
                    precision_count+=1
                    break


        for real in set1:
            for pre in set2:
                if iou(pre, real) > iou_treshold:
                    recall_count+=1
                    break

        precision = precision_count / precision_all
        recall = recall_count / recall_all
        result.append(str(iou_treshold) + ',' + str(precision) + ',' + str(recall))


    return result
    #
    # cv2.imshow(address_img, board)
    # cv2.waitKey(0)

img_list = []
for root, dirs, files in os.walk("data/Android_GUI_data/combined"):
    for f in files:
        if r'/.DS_Store' in str(os.path.join(root, f)):
            continue
        f = str(os.path.join(root, f))
        if f[-4:]=='.jpg':
            img_list.append(f)


import csv
with open('./result.csv','w') as f:
    # If you want to compare UIED and GUISight(reproduce the result in the paper), please save to different csv file and import them in 'RICO_difference.py"
    csv_writer = csv.writer(f)
    for img in img_list:
        result = test(img)
        # print(result)
        result = [img,] + result
        csv_writer.writerow(result)

# with open('./result.csv','r') as f:
#     f_csv = csv.reader(f)
#     valid_num = 0
#     idx = 0
#     avg_pre = [0 for i in range(5)]
#     avg_rec = [0 for i in range(5)]
#     for idx,row in enumerate(f_csv):

#         for i in range(5):
#             if row[1].split(',')[1] == '-1':
#                 break
#             result = row[i+1].split(',')
#             avg_pre[i] += float(result[1])
#             avg_rec[i] += float(result[2])
#             valid_num += 1

#     valid_num = valid_num/5
#     print(idx,valid_num)
#     for i in range(5):
#         print('0.' + str(i+1),avg_pre[i]/valid_num,avg_rec[i]/valid_num)



