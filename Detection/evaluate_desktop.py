"""
Before running this file, you should first get the prediction result by run "run_on_desktop_set"
"""

import json
import os
iou_treshold = 0.5
def iou(box1, box2):
    '''
    box:[top, left, bottom, right]
    '''
    in_h = min(box1[2], box2[2]) - max(box1[0], box2[0])
    in_w = min(box1[3], box2[3]) - max(box1[1], box2[1])
    inter = 0 if in_h < 0 or in_w < 0 else in_h * in_w
    union = (box1[2] - box1[0]) * (box1[3] - box1[1]) + \
            (box2[2] - box2[0]) * (box2[3] - box2[1]) - inter
    iou = inter / union
    return iou

predict_lst = []
for root, dirs, files in os.walk("data/Desktop_output/result/"):
    for f in files:
        if r'/.DS_Store' in str(os.path.join(root, f)):
            continue
        f = str(os.path.join(root, f))
        if f[-5:]=='.json':
            predict_lst.append(f)

precision_lst = []
recall_lst = []
for predict in predict_lst:
    #box:[top, left, bottom, right]
    predict_box_lst = []
    with open(predict, 'r') as load_f:
        pre_dict = json.load(load_f)
    # print(predict)
    # print(pre_dict)
    width = float(pre_dict['img']['shape'][1])
    height = float(pre_dict['img']['shape'][0])
    for box in pre_dict['compos']:
        pre = []
        pre.append(float(box['column_min']) / width)
        pre.append(float(box['row_min'])/height)
        pre.append(float(box['column_max']) / width)
        pre.append(float(box['row_max']) / height)
        predict_box_lst.append(pre)

    real_box_lst = []
    real = predict.replace('/Desktop_output/result/','/Desktop_GUI_data/label/').replace('.json','.txt')
    with open(real, 'r') as load_f:
        for line in load_f.readlines():
            real = []
            box = line.split(' ')
            real.append(float(box[1]))
            real.append(float(box[2]))
            real.append(float(box[3]))
            real.append(float(box[4]))
            real_box_lst.append(real)

    precision_all = len(predict_box_lst)
    recall_all = len(real_box_lst)
    precision_count = 0
    recall_count = 0

    for pre in predict_box_lst:
        for real in real_box_lst:
            if iou(pre, real) > iou_treshold:
                precision_count+=1
                break


    for real in real_box_lst:
        for pre in predict_box_lst:
            if iou(pre, real) > iou_treshold:
                recall_count+=1
                break

    precision_lst.append(precision_count/precision_all)
    recall_lst.append(recall_count/recall_all)
    # print(precision_count/precision_all)
    # print(recall_count/recall_all)


print('Precision:',sum(precision_lst)/len(precision_lst))
print('Recall:',sum(recall_lst)/len(recall_lst))