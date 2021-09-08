"""
Some changes in lib_ip are not elaborate in the paper
UIED is a very good tool
We only make some trival improvements on it
Most functions in this file are our improvement methods
"""
"""
I will update this file later, it is not human readable now. Please wait
"""
import cv2
from os.path import join as pjoin
import time
import json
import numpy as np
import detect_compo.lib_ip.ip_preprocessing as pre
import detect_compo.lib_ip.ip_draw as draw
import detect_compo.lib_ip.ip_detection as det
import detect_compo.lib_ip.ip_segment as seg
import detect_compo.lib_ip.file_utils as file
import detect_compo.lib_ip.block_division as blk
import detect_compo.lib_ip.Component as Compo
from configfile.CONFIG_UIED import Config
C = Config()


# def processing_block(org, binary, blocks, block_pad):
#     image_shape = org.shape
#     uicompos_all = []
#     for block in blocks:
#         # *** Step 2.1 *** check: examine if the block is valid layout block
#         if block.block_is_top_or_bottom_bar(image_shape, C.THRESHOLD_TOP_BOTTOM_BAR):
#             continue
#         if block.block_is_uicompo(image_shape, C.THRESHOLD_COMPO_MAX_SCALE):
#             uicompos_all.append(block)
#
#         # *** Step 2.2 *** binary map processing: erase children block -> clipping -> remove lines(opt)
#         binary_copy = binary.copy()
#         for i in block.children:
#             blocks[i].block_erase_from_bin(binary_copy, block_pad)
#         block_clip_bin = block.compo_clipping(binary_copy)
#         # det.line_removal(block_clip_bin, show=True)
#
#         # *** Step 2.3 *** component extraction: detect components in block binmap -> convert position to relative
#         uicompos = det.component_detection(block_clip_bin)
#         Compo.cvt_compos_relative_pos(uicompos, block.bbox.col_min, block.bbox.row_min)
#         uicompos_all += uicompos
#     return uicompos_all


def nesting_inspection(org, grey, compos, ffl_block):
    '''
    Inspect all big compos through block division by flood-fill
    :param ffl_block: gradient threshold for flood-fill
    :return: nesting compos
    '''
    nesting_compos = []
    for i, compo in enumerate(compos):
        if compo.height > 50:
            replace = False
            clip_org = compo.compo_clipping(org)
            clip_grey = compo.compo_clipping(grey)
            n_compos = blk.block_division(clip_grey, org, grad_thresh=ffl_block, show=False)
            Compo.cvt_compos_relative_pos(n_compos, compo.bbox.col_min, compo.bbox.row_min)
            # draw.draw_bounding_box(org, n_compos, show=True, name='nest in block', wait_key=0)
            for n_compo in n_compos:
                if n_compo.redundant:
                    compos[i] = n_compo
                    replace = True
                    #########
                    break
                # if not replace:
                #     nesting_compos.append(n_compo)
            if not replace:
                nesting_compos += n_compos
            ##########
    return nesting_compos

def text_cheeck(compos,texts):
    for comp in compos:
        box = [comp.bbox.row_min, comp.bbox.row_max, comp.bbox.col_min, comp.bbox.col_max]
        for text in texts:
            if cal_iou(box,text)[0] > 0.5:
                comp.istext =True

def comp_cluster(org, compos,show,wai_key):
    
    lst = []
    for idx,comp in enumerate(compos):
        lst.append([comp.area,comp.width/comp.height,comp.bbox, idx])
    lst.sort(key=lambda x:x[0],reverse=True)
    lst2 = lst.copy()

    cls_dic = {}
    height = org.shape[0]
    width = org.shape[1]
    min_area = width*height*0.01
    # print(org.shape)

    """
    Cluster
    """
    for comp in lst:
        area = comp[0]
        rat = comp[1]
        comp_height = comp[2].height
        comp_width = comp[2].width
        center = ((comp[2].col_min + comp[2].col_max)/2,(comp[2].row_min + comp[2].row_max)/2)
        for comp2 in lst2:
            """
            distance, ratio, area
            """
            if compos[comp[3]].istext or compos[comp2[3]].istext:
                continue
            if area < comp2[0] or comp2[3] == comp[3]:
                continue
            if area*0.85 > comp2[0]:
                break
            if area < min_area:
                if abs(comp[2].row_min/height - comp2[2].row_min/height) > 0.01 and \
                        abs(comp[2].col_min/width - comp2[2].col_min/width) > 0.01:
                    continue
            if abs(rat - comp2[1]) > 0.1:
                continue
            center2 = ((comp2[2].col_min + comp2[2].col_max) / 2, (comp2[2].row_min + comp2[2].row_max) / 2)

            if abs(center[0] - center2[0]) < 4.5 * comp_width and abs(center[1] - center2[1]) < 4.5 * comp_height:
                # print(comp2[3], 'and', comp[3],'!!!')
                compos[comp2[3]].connect_field.append(comp[3])
                compos[comp[3]].connect_field.append(comp2[3])
                # compos[comp2[3]].cls = compos[comp[3]].cls

    cls = 0
    for comp in compos:
        if comp.cls == None:
            comp.cls = cls
            cls += 1
        else:
            continue

        cur_lst = comp.connect_field.copy()
        cur_field = comp.connect_field.copy()
        while len(cur_lst) != 0:
            con_idx = cur_lst.pop(0)
            for i in compos[con_idx].connect_field:
                if i not in cur_field:
                    cur_lst.append(i)
                    cur_field.append(i)

        for idx in cur_field:
            compos[idx].cls = comp.cls

    # print(cls)

    for comp in compos:
        if comp.cls not in cls_dic.keys():
            cls_dic[comp.cls] = [1,]
        else:
            cls_dic[comp.cls][0] += 1
            # print(compos[comp[3]].cls,'+',1)

    # print(org.shape)


    img = org.copy()
    for i in range(cls):
        top,down,left,right = 10000,0,10000,0
        if cls_dic[i][0] < 3:
            del cls_dic[i]
            continue
        com_lst = []
        for comp in lst:
            if compos[comp[3]].cls == i:
                com_lst.append([comp[3],compos[comp[3]]])
                if comp[2].row_min < top:
                    top = comp[2].row_min
                if comp[2].row_max > down:
                    down = comp[2].row_max
                if comp[2].col_min < left:
                    left = comp[2].col_min
                if comp[2].col_max > right:
                    right = comp[2].col_max
        cls_dic[i].append(com_lst)
        cls_dic[i].append([top,down,left,right])
        # print([top,down,left,right])
        cv2.rectangle(img,(left,top),(right,down),(0,255,0),3)

    if show:
        cv2.imshow('cluster', img)
        cv2.waitKey(wai_key)
    return cls_dic

def refine_cluster(org, cls_dic, compos, b_shape,show,wai_key):
    """
    Sorry...It is not human readable.. I will update it later..
    1.learn if has strict layout
    2.inner -> give box
    3.edge -> refinement
    :param cls_dic: cluster dictionary:
    :return:
    """
    new_comp = []
    draw_lst = []
    img = org.copy()
    for cls in cls_dic.keys():
        row_lst, col_lst, cur_lst = [],[],[]
        cur_lst = [x[1] for x in cls_dic[cls][1]]
        avg_height, avg_width = 0,0
        for idx,comp in enumerate(cur_lst):
            # print("box:",comp.bbox.col_max,comp.bbox.col_min,comp.bbox.row_max, comp.bbox.row_min)
            avg_width += comp.bbox.col_max - comp.bbox.col_min
            avg_height += comp.bbox.row_max - comp.bbox.row_min
            col_lst.append([comp.bbox.col_min,comp.bbox.row_min, idx])
            row_lst.append([comp.bbox.col_min,comp.bbox.row_min, idx])
        avg_height /= len(cur_lst)
        avg_width /= len(cur_lst)

        col_lst.sort(key=lambda x: x[0])
        row_lst.sort(key=lambda x: x[1])

        height = cls_dic[cls][2][1] - cls_dic[cls][2][0]
        width = cls_dic[cls][2][3] - cls_dic[cls][2][2]
        # print('Refine')
        # print(avg_height,height, avg_width,width)
        if height < avg_height*1.05:
            # print('One row')
            # one regular row， gap can only be 1,2,3,4*
            div_col = []
            for idx in range(len(col_lst)):
                div_col.append(col_lst[idx+1][0]-col_lst[idx][0])
                if idx == len(col_lst) - 2:
                    break
            min_gap = min(div_col)
            regular_flg = True
            for gap in div_col:
                # print(gap,min([abs(gap-x*min_gap)for x in [1,2,3,4]]))
                if min([abs(gap-x*min_gap)/x for x in [1,2,3,4]]) > max([0.2*min_gap,1]):
                    regular_flg = False
                    break
            if regular_flg:
                # print('It is regular row')
                #先全给
                for idx in range(len(col_lst)):
                    if col_lst[idx+1][0] > col_lst[idx][0] + min_gap * 1.1:
                        #create new compo
                        # print('Find missed box')
                        num = int((col_lst[idx+1][0] - col_lst[idx][0]) / min_gap)
                        for k in range(num-1):
                            region = []
                            for i in range(int(avg_height)):
                                for j in range(int(avg_width)):
                                    region.append(( cls_dic[cls][2][0]+i,col_lst[idx][0]+(k+1)*min_gap+j))
                            draw_lst.append([cls_dic[cls][2][0],cls_dic[cls][2][0]+int(avg_height)
                                             , col_lst[idx][0]+(k+1)*min_gap, col_lst[idx][0]+(k+1)*min_gap+int(avg_width)])
                            # print('Add box')
                            new = Compo.Component(region,b_shape)
                            new.cls = cls
                            new_comp.append(new)
                    if idx == len(col_lst) - 2:
                        break

        elif width < avg_width*1.05:
            # print('One column')
            # one regular col
            div_row = []
            for idx in range(len(row_lst)):
                div_row.append(row_lst[idx + 1][1] - row_lst[idx][1])
                if idx == len(row_lst) - 2:
                    break
            min_gap = min(div_row)
            regular_flg = True
            for gap in div_row:
                if min([abs(gap - x * min_gap)/x for x in [1, 2, 3, 4]]) > max([0.05 * min_gap, 1]):
                    regular_flg = False
                    break
            if regular_flg:
                # print('It is regular column')
                for idx in range(len(row_lst)):
                    if row_lst[idx+1][1] > row_lst[idx][1] + min_gap * 1.1:
                        #create new compo
                        # print('Find missed box')
                        num = int((row_lst[idx + 1][1] - row_lst[idx][1]) / min_gap)
                        # print(num)
                        for k in range(num-1):
                            region = []
                            for i in range(int(avg_height)):
                                for j in range(int(avg_width)):
                                    region.append(( row_lst[idx][1]+(k+1)*min_gap+i,cls_dic[cls][2][2]+j))
                            draw_lst.append([row_lst[idx][1]+(k+1)*min_gap, row_lst[idx][1]+(k+1)*min_gap + int(avg_height)
                                                , cls_dic[cls][2][2], cls_dic[cls][2][2] + int(avg_width)])
                            # print('Add box')
                            new = Compo.Component(region,b_shape)
                            new.cls = cls
                            new_comp.append(new)
                    if idx == len(col_lst) - 2:
                        break

        else:
            # more than one row and col -> should be box layout
            # print('Box layout')
            # cluster by row
            # min row gap
            div_row = []
            for idx in range(len(row_lst)):
                div_row.append(row_lst[idx + 1][1] - row_lst[idx][1])
                if idx == len(row_lst) - 2:
                    break

            # min col gap
            div_col = []
            for idx in range(len(col_lst)):
                div_col.append(col_lst[idx + 1][0] - col_lst[idx][0])
                if idx == len(col_lst) - 2:
                    break
            row_gap = None
            col_gap = None
            regular_row = True
            regular_col = True
            for gap in sorted(div_row):
                if gap < avg_height and gap > avg_height * 0.05:
                    regular_row = False
                if gap > avg_height:
                    row_gap = gap
                    break



            for gap in sorted(div_col):
                if gap < avg_width and gap > avg_width * 0.05:
                    regular_col = False
                if gap > avg_width:
                    col_gap = gap
                    break

            if not row_gap or not col_gap:
                # print("Overlap, drop cluster")
                continue

            for gap in div_row:
                if min([abs(gap - x * row_gap)/max([x,1]) for x in [0, 1, 2, 3, 4]]) > max([0.2 * row_gap, 1]):
                    regular_row = False
                    break

            for gap in div_col:
                if min([abs(gap-x*col_gap)/max([x,1]) for x in [0,1,2,3,4]]) > max([0.2 * col_gap,1]):
                    regular_col = False
                    break



            if regular_row and regular_col:
                # print('Rectangle box layout')
                # it's rectangle layout, cluster by row -> to every single row
                cluster_set = []
                row_num = 0
                one_row = []
                for comp in row_lst:
                    # print(comp)
                    if comp[1] - cls_dic[cls][2][0] < avg_height*1.1 + row_num * row_gap:
                        one_row.append(comp)
                    else:
                        cluster_set.append(one_row.copy())
                        row_num += 1
                        one_row = []
                        one_row.append(comp)

                cluster_set.append(one_row.copy())
                # print("There are ",len(cluster_set)," rows")
                # print(avg_height,row_gap)
                for row_set in cluster_set:
                    row_set.sort(key=lambda x:x[0])
                    top, down, left, right = 10000, 0, 10000, 0
                    for item in row_set:
                        comp = cur_lst[item[2]].bbox
                        # print(comp.row_min,comp.row_max,comp.col_min,comp.col_max)
                        if comp.row_min < top:
                            top = comp.row_min
                        if comp.row_max > down:
                            down = comp.row_max
                        if comp.col_min < left:
                            left = comp.col_min
                        if comp.col_max > right:
                            right = comp.col_max
                    # print(row_set[0][0],cls_dic[cls][2][2])
                    if row_set[0][0] - cls_dic[cls][2][2] > avg_width:
                        num = int((row_set[0][0] - cls_dic[cls][2][2])/col_gap)
                        for k in range(num):
                            # print("Miss first box")
                            region = []
                            for i in range(int(avg_height)):
                                for j in range(int(avg_width)):
                                    region.append(( top + i,cls_dic[cls][2][2] + k*col_gap + j))
                            new_box = [top, down, cls_dic[cls][2][2] + k*col_gap,
                                       cls_dic[cls][2][2] + k*col_gap + int(avg_width)]
                            # print(new_box)
                            for comp in compos:
                                comp_box = [comp.bbox.row_min, comp.bbox.row_max, comp.bbox.col_min, comp.bbox.col_max]
                                if comp_box[0] > top and comp_box[1] < down and comp_box[2] > left and comp_box[3] < right:
                                    pass
                                    # print('Find Suit', comp_box)
                                if cal_iou(comp_box, new_box)[0] > 0.5:
                                    # print("Add new box")
                                    draw_lst.append(new_box)
                                    new = Compo.Component(region, b_shape)
                                    new.cls = cls
                                    new_comp.append(new)
                                    break
                    # print(row_set, cls_dic[cls][2][3],row_set[len(row_set)-1][0],avg_width)
                    if cls_dic[cls][2][3] - row_set[len(row_set)-1][0] > avg_width*1.1:
                        num = int((cls_dic[cls][2][3] - row_set[len(row_set)-1][0]) / col_gap)
                        for k in range(num):
                            # print("Miss last box")
                            region = []
                            for i in range(int(avg_height)):
                                for j in range(int(avg_width)):
                                    region.append((top + i,cls_dic[cls][2][3] - int(avg_width) - k*col_gap  + j))
                            new_box = [top, down, cls_dic[cls][2][3] - int(avg_width) - k*col_gap,
                                       cls_dic[cls][2][3]- k*col_gap]
                            for comp in compos:
                                comp_box = [comp.bbox.row_min, comp.bbox.row_max, comp.bbox.col_min, comp.bbox.col_max]
                                if cal_iou(comp_box, new_box)[0] > 0.5:
                                    # print("Add new box")
                                    draw_lst.append(new_box)
                                    new = Compo.Component(region, b_shape)
                                    new.cls = cls
                                    new_comp.append(new)
                                    break

                    for idx in range(len(row_set)):
                        # print(len(row_set))
                        if len(row_set)< 2:
                            break

                        if row_set[idx + 1][0] > row_set[idx][0] + col_gap * 1.1:

                            # create new compo
                            # print('Find missed box')
                            # print(idx,row_set[idx + 1][0], row_set[idx][0],col_gap)
                            num = int((row_set[idx + 1][0] - row_set[idx][0]) / col_gap)
                            for k in range(num-1):
                                region = []
                                for i in range(int(avg_height)):
                                    for j in range(int(avg_width)):
                                        region.append(( top + i, row_set[idx][0] + (k+1) * col_gap + j))
                                new_box = [top, down, row_set[idx][0] + (k+1) * col_gap,
                                                 row_set[idx][0] + (k+1) * col_gap + int(avg_width)]
                                for comp in compos:
                                    comp_box = [comp.bbox.row_min,comp.bbox.row_max,comp.bbox.col_min,comp.bbox.col_max]
                                    if cal_iou(comp_box,new_box)[0] > 0.5:
                                        # print("Add new box")
                                        draw_lst.append(new_box)
                                        new = Compo.Component(region, b_shape)
                                        new.cls = cls
                                        new_comp.append(new)
                                        # print('component box',new_box)
                                        # print(new.bbox.row_min,new.bbox.row_max,new.bbox.col_min,new.bbox.col_max)
                                        break
                        if idx == len(row_set) - 2:
                            break

            elif regular_row:
                # row is regular, cluster by row -> to every single row
                # print('box with row')
                cluster_set = []
                row_num = 0
                one_row = []
                for comp in row_lst:
                    if comp[1] - cls_dic[cls][2][0] < avg_height * 1.1 + row_num * row_gap:
                        one_row.append(comp)
                    else:
                        cluster_set.append(one_row.copy())
                        row_num += 1
                        one_row = []
                        one_row.append(comp)
                cluster_set.append(one_row.copy())
                for row_set in cluster_set:
                    top, down, left, right = 10000, 0, 10000, 0
                    row_set.sort(key=lambda x:x[0])
                    for item in row_set:
                        comp = cur_lst[item[2]].bbox
                        if comp.row_min < top:
                            top = comp.row_min
                        if comp.row_max > down:
                            down = comp.row_max
                        if comp.col_min < left:
                            left = comp.col_min
                        if comp.col_max > right:
                            right = comp.col_max
                    div_col = []
                    if len(row_set) < 2:
                        continue
                    for idx in range(len(row_set)):
                        div_col.append(row_set[idx + 1][0] - row_set[idx][0])
                        if idx == len(row_set) - 2:
                            break
                    min_gap = min(div_col)
                    if min_gap == 0 :
                        continue
                    for idx in range(len(row_set)):
                        if row_set[idx + 1][0] > row_set[idx][0] + min_gap * 1.1:
                            # create new compo
                            num = int((row_set[idx + 1][0] - row_set[idx][0]) / min_gap)
                            for k in range(num-1):
                                region = []
                                for i in range(int(avg_height)):
                                    for j in range(int(avg_width)):
                                        region.append(( top + i, row_set[idx][0] + (k+1)*min_gap + j))
                                new_box = [top, down, row_set[idx][0] + (k+1)*min_gap,
                                           row_set[idx][0] + (k+1)*min_gap + int(avg_width)]

                                draw_lst.append(new_box)
                                new = Compo.Component(region, b_shape)
                                new.cls = cls
                                new_comp.append(new)
                        if idx == len(row_set) - 2:
                            break


            elif regular_col:
                # col is regular, cluster by col -> to every single col
                # print('box with col')
                cluster_set = []
                col_num = 0
                one_col = []
                for comp in col_lst:
                    if comp[0] - cls_dic[cls][2][2] < avg_width*1.1 + col_num * col_gap:
                        one_col.append(comp)
                    else:
                        cluster_set.append(one_col.copy())
                        col_num += 1
                        one_col = []
                        one_col.append(comp)
                cluster_set.append(one_col.copy())
                for col_set in cluster_set:
                    top, down, left, right = 10000, 0, 10000, 0
                    col_set.sort(key=lambda x: x[1])
                    for item in col_set:

                        comp = cur_lst[item[2]].bbox
                        # print(comp.row_min,comp.row_max,comp.col_min,comp.col_max)
                        if comp.row_min < top:
                            top = comp.row_min
                        if comp.row_max > down:
                            down = comp.row_max
                        if comp.col_min < left:
                            left = comp.col_min
                        if comp.col_max > right:
                            right = comp.col_max
                    div_row = []
                    if len(col_set) < 2:
                        continue
                    for idx in range(len(col_set)):
                        div_row.append(col_set[idx + 1][1] - col_set[idx][1])
                        if idx == len(col_set) - 2:
                            break
                    min_gap = min(div_row)
                    # if min_gap < avg_width:
                    #     continue
                    if min_gap == 0 :
                        continue

                    for idx in range(len(col_set)):
                        if len(col_set)< 2:
                            break
                        if col_set[idx + 1][1] > col_set[idx][1] + min_gap * 1.1:
                            # create new compo
                            num = int((col_set[idx + 1][1] - col_set[idx][1]) / min_gap)
                            for k in range(num-1):
                                region = []
                                for i in range(int(avg_height)):
                                    for j in range(int(avg_width)):
                                        region.append(( col_set[idx][1] + (k+1)*min_gap + i, top+ j))

                                new_box = [col_set[idx][1] + (k+1)*min_gap,
                                           col_set[idx][1] + (k+1)*min_gap + int(avg_width),left,right]

                                draw_lst.append(new_box)
                                new = Compo.Component(region, b_shape)
                                new.cls = cls
                                new_comp.append(new)
                        if idx == len(col_set) - 2:
                            break

    for rec in draw_lst:
        cv2.rectangle(img, (rec[2], rec[0]), (rec[3], rec[1]), (0, 255, 0), 3)


    if show:
        cv2.imshow('refine_cluster', img)
        cv2.waitKey(wai_key)

    return new_comp

def delete_noise(cls_dic, compos):
    del_lst = []
    re_lst = []
    for idx,comp in enumerate(compos):
        box1 = [comp.bbox.row_min, comp.bbox.row_max, comp.bbox.col_min, comp.bbox.col_max]
        for idx2,comp2 in enumerate(compos):
            if idx == idx2:
                continue
            if comp.cls not in cls_dic.keys() or comp2.cls in cls_dic.keys():
                continue
            box2 = [comp2.bbox.row_min,comp2.bbox.row_max,comp2.bbox.col_min,comp2.bbox.col_max]
            if cal_iou(box1,box2)[1] > 0.5:
                del_lst.append(idx2)
                # print('delete',box2)

    # print('delete these',del_lst)
    for idx,comp in enumerate(compos):
        if idx not in del_lst:
            re_lst.append(comp)

    return re_lst



def merge_small_component(org, compos,b_shape,show,wai_key):
    big_compo = []
    for idx,comp in enumerate(compos):
        pos = [comp.bbox.col_min,comp.bbox.row_min]
        for idx2,comp2 in enumerate(compos):
            if idx2 <= idx:
                continue
            pos2 = [comp2.bbox.col_min, comp2.bbox.row_min]
            if abs(pos[0]-pos2[0]) < comp.width + comp2.width and abs(pos[1]-pos2[1]) < comp.height + comp2.height:
                # print('Add connect field')
                comp.connect_field.append(idx2)
                comp2.connect_field.append(idx)
    cls = 0
    # print(len(compos))
    for comp in compos:
        if comp.cls == None:
            comp.cls = cls
            cls += 1
        else:
            continue

        cur_lst = comp.connect_field.copy()
        cur_field = comp.connect_field.copy()
        while len(cur_lst) != 0:
            con_idx = cur_lst.pop(0)
            for i in compos[con_idx].connect_field:
                if i not in cur_field:
                    cur_lst.append(i)
                    cur_field.append(i)

        for idx in cur_field:
            compos[idx].cls = comp.cls
    cls_dic = {}
    # print(cls)
    for comp in compos:
        if comp.cls not in cls_dic.keys():
            cls_dic[comp.cls] = [1,]
        else:
            cls_dic[comp.cls][0] += 1
            # print(compos[comp[3]].cls,'+',1)

    img = org.copy()
    for i in range(cls):
        top, down, left, right = 10000, 0, 10000, 0
        if cls_dic[i][0] < 2:
            continue
        # print('one big')
        for comp in compos:
            if comp.cls == i:
                if comp.bbox.row_min < top:
                    top = comp.bbox.row_min
                if comp.bbox.row_max > down:
                    down = comp.bbox.row_max
                if comp.bbox.col_min < left:
                    left = comp.bbox.col_min
                if comp.bbox.col_max > right:
                    right = comp.bbox.col_max
        region = []
        for i in range(int(down - top)):
            for j in range(int(right -  left)):
                region.append((top + i, left + j))
        new = Compo.Component(region, b_shape)
        big_compo.append(new)
        cv2.rectangle(img, (left, top), (right, down), (0, 255, 0), 3)

    if show:
        cv2.imshow('big', img)
        cv2.waitKey(wai_key)
    return big_compo

def cal_iou(box1, box2):

    ymin1, ymax1, xmin1, xmax1  = box1
    ymin2, ymax2, xmin2, xmax2  = box2
    # 计算每个矩形的面积
    s1 = (xmax1 - xmin1) * (ymax1 - ymin1)  # C的面积
    s2 = (xmax2 - xmin2) * (ymax2 - ymin2)  # G的面积

    # 计算相交矩形
    xmin = max(xmin1, xmin2)
    ymin = max(ymin1, ymin2)
    xmax = min(xmax1, xmax2)
    ymax = min(ymax1, ymax2)

    w = max(0, xmax - xmin)
    h = max(0, ymax - ymin)
    area = w * h  # C∩G的面积
    iou1 = area / s1
    iou2 =  area / s2
    iou = area / (s1 + s2 - area)
    return [iou1,iou2, iou]

def nest_in_cluster():
    # accept all rectangle widget outside
    # only accept irrgular widget appearing in certain rules inside

    pass

def delete_comp_outside_cluster(cls_dic,compos):
    #so that merge will not contain cluster
    """
    if has cluster inside -> pure color background, don't merge contained
    if img background -> can't find cluster -> find pure color is reasonable
    if not img background(pure color background) -> flood fill on gradient is enough, no need merge
    """
    del_comp = []
    for idx, comp in enumerate(compos):
        box1 = [comp.bbox.row_min, comp.bbox.row_max, comp.bbox.col_min, comp.bbox.col_max]
        for idx2, comp2 in enumerate(compos):
            if idx == idx2:
                continue
            if comp.cls not in cls_dic.keys() or comp2.cls in cls_dic.keys():
                continue
            box2 = [comp2.bbox.row_min, comp2.bbox.row_max, comp2.bbox.col_min, comp2.bbox.col_max]
            #
            if cal_iou(box1, box2)[0] >=0.5 and cal_iou(box1, box2)[0] > cal_iou(box1, box2)[1]:
                del_comp.append(idx2)
                # print('del',box2)
    new_comp = []
    for idx, comp in enumerate(compos):
        if idx not in del_comp:
            new_comp.append(comp)
    return new_comp

def compo_detection(input_img_path, output_root, uied_params,
                    resize_by_height=600,
                    classifier=None, show=False, wai_key=0):

    start = time.perf_counter()
    name = input_img_path.split('/')[-1][:-4]
    ocr_path = pjoin(output_root, 'ocr', str(name) + '.json')
    texts = []
    for text in json.load(open(ocr_path, 'r'))['compos']:
        element = [text['row_min'], text['row_max'], text['column_min'], text['column_max']]
        texts.append(element)
    ip_root = file.build_directory(pjoin(output_root, "ip"))
    # time1 = time.time()
    # *** Step 1 *** pre-processing: read img -> get binary map
    org, grey = pre.read_img(input_img_path, resize_by_height)
    binary = pre.binarization(org, grad_min=int(uied_params['min-grad']), show=show, wait_key=wai_key)
    # time2 = time.time()
    # *** Step 2 *** element detection
    det.rm_line(binary, show=show, wait_key=wai_key)
    # time3 = time.time()
    # det.rm_line_v_h(binary, show=show)
    uicompos,small = det.component_detection(binary, min_obj_area=int(uied_params['min-ele-area']))
    # time4 = time.time()
    # draw.draw_bounding_box(org, small, show=show, name='small', wait_key=wai_key)
    if len(small) != 0:
        uicompos += merge_small_component(org,small,binary.shape,show,wai_key)
    # draw.draw_bounding_box(org, uicompos, show=show, name='components', wait_key=wai_key)
    # time5 = time.time()
    # text_cheeck(uicompos,texts)
    cluster = comp_cluster(org,uicompos,show,wai_key)
    uicompos += refine_cluster(org,cluster,uicompos,binary.shape,show,wai_key)
    uicompos = delete_noise(cluster,uicompos)
    uicompos = delete_comp_outside_cluster(cluster, uicompos)
    # draw.draw_bounding_box(org, uicompos, show=show, name='after refine', wait_key=wai_key)
    # time6 = time.time()
    # *** Step 3 *** results refinement
    uicompos = det.merge_intersected_corner(uicompos, org, is_merge_contained_ele=uied_params['merge-contained-ele'],
                                            max_gap=(0, 0), max_ele_height=25)
    Compo.compos_update(uicompos, org.shape)
    Compo.compos_containment(uicompos)
    # draw.draw_bounding_box(org, uicompos, show=show, name='merged', wait_key=wai_key)
    # time7 = time.time()
    # *** Step 4 ** nesting inspection: treat the big compos as block and check if they have nesting element
    uicompos += nesting_inspection(org, grey, uicompos, ffl_block=uied_params['ffl-block'])
    uicompos = det.compo_filter(uicompos, min_area=int(uied_params['min-ele-area']))
    Compo.compos_update(uicompos, org.shape)
    # draw.draw_bounding_box(org, uicompos, show=show, name='merged compo', write_path=pjoin(ip_root, 'result.jpg'), wait_key=wai_key)
    # time8 = time.time()
    # *** Step 5 *** Image Inspection: recognize image -> remove noise in image -> binarize with larger threshold and reverse -> rectangular compo detection
    # if classifier is not None:
    #     classifier['Image'].predict(seg.clipping(org, uicompos), uicompos)
    #     draw.draw_bounding_box_class(org, uicompos, show=show)
    #     uicompos = det.rm_noise_in_large_img(uicompos, org)
    #     draw.draw_bounding_box_class(org, uicompos, show=show)
    #     det.detect_compos_in_img(uicompos, binary_org, org)
    #     draw.draw_bounding_box(org, uicompos, show=show)
    # if classifier is not None:
    #     classifier['Noise'].predict(seg.clipping(org, uicompos), uicompos)
    #     draw.draw_bounding_box_class(org, uicompos, show=show)
    #     uicompos = det.rm_noise_compos(uicompos)

    # *** Step 6 *** element classification: all category classification
    if classifier is not None:
        classifier['Elements'].predict(seg.clipping(org, uicompos), uicompos)
        draw.draw_bounding_box_class(org, uicompos, show=show, name='cls', write_path=pjoin(ip_root, 'result.jpg'))
        draw.draw_bounding_box_class(org, uicompos, write_path=pjoin(output_root, 'result.jpg'))
    # time9 = time.time()
    Compo.compos_update(uicompos, org.shape)
    file.save_corners_json(pjoin(ip_root, name + '.json'), uicompos)
    file.save_corners_json(pjoin(output_root, 'compo.json'), uicompos)
    # seg.dissemble_clip_img_fill(pjoin(output_root, 'clips'), org, uicompos)
    # time10 = time.time()
    print("[Compo Detection Completed in %.3f s] %s" % (time.perf_counter() - start, input_img_path))
    # print("time in ip:", time2 - time1, time3 - time2, time4 - time3, time5 - time4, time6 - time5, time7 - time6, time8 - time7, time9 - time8,time10-time9)

    # if show:
    #     cv2.destroyAllWindows()
