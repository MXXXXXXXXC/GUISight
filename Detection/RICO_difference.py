"""
Where our method get different result with UIED 
"""

import csv

f_write = open('diff_in_result.csv','w')
fw = csv.writer(f_write)
for iou in range(5):
    iou += 1
    valid_num_recall = 0
    valid_num_precision = 0
    idx = 0
    avg_pre = [0 for i in range(10)]
    avg_rec = [0 for j in range(10)]
    guisight_csv_list = []
    uied_csv_list = []
    f_uied = open('result_uied.csv', 'r')
    f_guisight = open('result_guisight.csv', 'r')

    f_csv_uied = csv.reader(f_uied)
    f_csv_guisight = csv.reader(f_guisight)
    for idx,row_guisight in enumerate(f_csv_guisight):
        guisight_csv_list.append(row_guisight[iou+1].split(','))

    for idx,row_uied in enumerate(f_csv_uied):
        uied_csv_list.append(row_uied[iou+1].split(','))
    guisight_recall = 0
    uied_recall = 0
    guisight_pre = 0
    uied_pre = 0
    for idx, row_uied in enumerate(uied_csv_list):
        if row_uied[1] == '-1':
            continue
        row_guisight = guisight_csv_list[idx]
        if row_guisight[1] == '-1':
            continue

        if float(row_guisight[2]) != float(row_uied[2]):
            guisight_recall += float(row_guisight[2])
            uied_recall += float(row_uied[2])
            valid_num_recall += 1
        if float(row_guisight[1]) != float(row_uied[1]):
            guisight_pre += float(row_guisight[1])
            uied_pre += float(row_uied[1])
            valid_num_precision += 1
    if valid_num_recall:
        print('recall in',str((iou+1)*10)+'%',idx,valid_num_recall,guisight_recall/valid_num_recall,uied_recall/valid_num_recall )
    if valid_num_precision:
        print('precision in',str((iou+1)*10)+'%',idx,valid_num_precision,guisight_pre/valid_num_precision,uied_pre/valid_num_precision )
        
# Name  ||Number of image selected || improved || origin ||
# recall in 10% 2999 0.48347949777658494 0.3515186522936398
# precision in 10% 6564 0.3960511694549967 0.42967809440491783
# recall in 20% 2949 0.39106360610222235 0.2810191329807417
# precision in 20% 6453 0.3173672833864317 0.3494376106187804
# recall in 30% 2792 0.32805220526693485 0.2403042330081544
# precision in 30% 6325 0.26765479427681516 0.2965383929829262
# recall in 40% 2564 0.2844191583159835 0.21135595601789894
# precision in 40% 6178 0.22983988700063512 0.2553549814386722
# recall in 50% 2442 0.24577210938532124 0.17752042729109957
# precision in 50% 5963 0.1979967002939781 0.21785215406723502
