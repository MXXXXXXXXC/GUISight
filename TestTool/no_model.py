"""
Delete state model from test_with_model_Linux
"""
import numpy as np
import sys
import random
from os.path import join as pjoin
import cv2
import os
import pyautogui
import json
import copy
import time
from pynput import keyboard
from test_helper import get_window_size, screenshot, perform_interaction,open_app,close_app,check_app
import state
# from emma_helper import EmmaHelper


running = True

quit_counter = 3

pyautogui.FAILSAFE = False # disables the fail-safe


def on_release(key):
    global running, quit_counter
    if key == keyboard.Key.f1:
        quit_counter -= 1
        if quit_counter == 0:
            running = False
            # EH.stop_application()
            # EH.merge_report()
            # EH.show_report()
            print("Stop testing")
            return True


def draw(img, box, px, py):
    height, width = img.shape[:2]
    x1 = max(int(width * box[1]), 0)
    y1 = max(int(height * box[2]), 0)
    x2 = int(width * box[3])
    y2 = int(height * box[4])
    color = (100, 100, 100)
    cv2.rectangle(img, (x1, y1),
                  (x2, y2),
                  (color[0], color[1], color[2], 0.2), 2)

    cv2.circle(img, (int((x1+x2)/2 + px* width), int((y1+y2)/2+ py * height)), 2, (100, 100, 100), 0)
    addr = time.time()
    cv2.imwrite("./draw/%s.png"% addr, img)

def generate_input_string():
    if random.random() < 0.5:
        return "Hello World!"
    else:
    	return str(random.randint(1000, 2000))

def resize_height_by_longest_edge(img_path, resize_length=800):
    org = cv2.imread(img_path)
    height, width = org.shape[:2]
    if height > width:
        return resize_length
    else:
        return int(resize_length * (height / width))


if __name__ == '__main__':
    # Use One of the folowing
    """
    If the application is not run on full screen. You should provide a window for the tool to locate the window.
    You should also provide a (application_class_address and main_class) or jar_address. If the app is in other format, you can write a simple open function in test_helper
    """

    win_name = 'Address Book'
    # jar_address = test_app/AddressBook/jar_address
    application_class_address = 'test_app/AddressBook'
    main_class = 'AddressBookMain'

    merge_report = True
    report_type = 'txt'
    total_max_action = 1000

    print("Loading model")
    import detect_text_east.ocr_east as ocr
    import detect_text_east.lib_east.eval as eval
    import detect_compo.ip_region_proposal as ip
    import merge
    from cnn.CNN import CNN
    models = eval.load()
    classifier = {'Elements': CNN('Elements'), }
    key_params = {'min-grad': 10, 'ffl-block': 5, 'min-ele-area': 50, 'merge-contained-ele': True,
                  'max-word-inline-gap': 4, 'max-line-gap': 4}

    print("Start Application")
    # EH = EmmaHelper(application_class_address, main_class, report_type, merge_report, jar_address)
    # EH.remove_report()

    start_time = time.time()
    actions = 0
    csv_file = './runtime_log' + "/" + str(start_time) + "-test.csv"
    with open(csv_file, "w+") as runtime_log:
        runtime_log.write("time,actions,box,interaction,iteration_time,window_name\n")

    with keyboard.Listener(on_release=on_release) as listener:
        current_state_index = 0
        # EH.open_application()
        time.sleep(2.5)

        for action_iter in range(total_max_action):
            iteration_time = time.time()
            exec_time = time.time() - start_time

            print("Locate Window")
            app_x, app_y, app_w, app_h = get_window_size(win_name)
            time.sleep(0.3)
            counter = 0
            close_flag = False
            while app_w == 0:
                counter += 1
                app_x, app_y, app_w, app_h = get_window_size(win_name) 
                app_y += 15
                app_h -= 30
	
                time.sleep(0.5)
                if counter >= 3:
                    print("Couldn't find application window!")
                    # end test case
                    close_flag = True
                    break
            if close_flag:
                # EH.stop_application()
                # EH.merge_report()
                time.sleep(3)
                # EH.open_application()

            image = screenshot()[app_y:app_y+app_h, app_x:app_x+app_w]
            try:
            	cv2.imwrite('./current.png', image)
            except:
            	continue
            input_path_img = './current.png'
            image = np.array(image)
            raw_img = copy.copy(image)
            output_root = 'data/test/output'

            print("Doing Detection")
            # prediction
            resized_height = resize_height_by_longest_edge(input_path_img)
            os.makedirs(pjoin(output_root, 'ocr'), exist_ok=True)
            ocr.east(input_path_img, output_root, models, key_params['max-word-inline-gap'],
                     resize_by_height=resized_height, show=False)

            os.makedirs(pjoin(output_root, 'ip'), exist_ok=True)
            # switch of the classification func
            ip.compo_detection(input_path_img, output_root, key_params,
                               classifier=classifier, resize_by_height=resized_height, show=False)
            name = input_path_img.split('/')[-1][:-4]

            compo_path = pjoin(output_root, 'ip', str(name) + '.json')
            ocr_path = pjoin(output_root, 'ocr', str(name) + '.json')
            merge.incorporate(input_path_img, compo_path, ocr_path, output_root, params=key_params,
                              resize_by_height=resized_height, show=False)

            predict_box_lst = []
            print("Load boxes")
            with open(output_root + '/result.json', 'r') as load_f:
                pre_dict = json.load(load_f)
                # print(pre_dict)
                width = float(pre_dict['img']['shape'][1])
                height = float(pre_dict['img']['shape'][0])
                # print(width, height)
                for box in pre_dict['compos']:
                    # x1,y1,x2,y2
                    pre = [(box['class'], box['cluster']), float(box['column_min']) / width, float(box['row_min']) / height,
                           float(box['column_max']) / width, float(box['row_max']) / height]
                    predict_box_lst.append(pre)
            proc_boxes = predict_box_lst[:]
            best_box = proc_boxes[random.randint(0, len(proc_boxes) - 1)]
            print("Box:", best_box)
            current_box = copy.deepcopy(best_box)
            input_string = generate_input_string()
            # interaction based on widget type
            print('Action', actions)
            x, y, interaction = perform_interaction(best_box, app_x, app_y, app_w, app_h, input_string, None)

            draw(raw_img, current_box, x, y)
            actions += 1

            end_iteration_time = time.time()

            if actions > total_max_action:
                # EH.stop_application()
                # EH.merge_report()
                # EH.show_report()
                print("Finished testing!")
                exit(0)
            # write test info
        # EH.stop_application()
        # EH.merge_report()
        # EH.show_report()
        print("Finished testing!")


