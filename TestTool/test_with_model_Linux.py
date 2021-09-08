"""
Most of this file is the same with test_with_model_Android
Only app name inputs, test_helper, and sleep time is different
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

pyautogui.FAILSAFE = False 

State_set = state.UI_state()

def on_release(key):
    global running, quit_counter, State_set
    if key == keyboard.Key.f1:
        quit_counter -= 1
        if quit_counter == 0:
            running = False
            close_app()
            # EH.stop_application()
            # EH.merge_report()
            # EH.show_report()
            State_set.save_all_state()
            print("Stop testing")
            return True


def draw(img, box, px, py):
    # Draw the interacted position on the image
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
    	return str(random.randint(0, 10000))

def resize_height_by_longest_edge(img_path, resize_length=800):
    org = cv2.imread(img_path)
    height, width = org.shape[:2]
    if height > width:
        return resize_length
    else:
        return int(resize_length * (height / width))


if __name__ == '__main__':

    """
    If the application is not run on full screen. You should provide a window for the tool to locate the window.
    You should also provide a (application_class_address and main_class) or jar_address. If the app is in other format(i.e, exe), you can write a simple open function in test_helper
    Our tool is not specific to java, you can test new format of apps by kindly replace the function "open_app" in test_helper
    """

    win_name = 'Address Book' # Name of the target app
    # jar_address = test_app/AddressBook/jar_address
    jar_address = None
    application_class_address = 'test_app/AddressBook'
    main_class = 'AddressBookMain'
    
    # merge_report = True
    # report_type = 'txt'

    total_max_action = 1000 # use for constrain maximum actions in experiment
    max_action_times = 60 # actions in a state
    test_iteration = 10 # an iteration is an execution of all prime paths in the state machine
    
    
    # IMPORT GUI DETECTION METHOD
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
    csv_file = 'runtime_log' + "/" + str(start_time) + "-test.txt"
    with open(csv_file, "w+") as runtime_log:
        runtime_log.write("time,actions,box,interaction,iteration_time,window_name\n")
    

    with keyboard.Listener(on_release=on_release) as listener:
        for test_iter in range(test_iteration):
            test_case_set = State_set.generate_prime_path() # Generate prime paths
            current_state_list = State_set.state_lst.copy() # use for determine states that is not in the state machine

            for test_case in test_case_set: # state sequence
                last_box_id, last_state, inter,  interaction = None, None, None, None
                current_state_index = 0
                if len(State_set.state_lst) != 0:
                    max_in_state_count = random.randint(1, len(State_set.state_lst[0].component))
                else:
                    max_in_state_count = 10

                if len(test_case) <= 1:
                    current_test_state = 0
                    next_test_state = 0
                else:
                    current_test_state = test_case[current_state_index]
                    next_test_state = test_case[current_state_index+1]

                in_state_count = 0
                print('Test Case', test_case, " Begin.")
                # System Command in Thread
                # EH.open_application()
                open_app(application_class_address,main_class,jar_address)
                time.sleep(2.5)

                for action_iter in range(max_action_times):
                    print('Currently it has', len(State_set.state_lst), ' states')
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
                        time.sleep(0.5)
                        if counter >= 3:
                            print("Couldn't find application window!")
                            # end test case
                            close_flag = True
                            break
                    if close_flag:
                        break

                    image = screenshot()[app_y:app_y+app_h, app_x:app_x+app_w]
                    cv2.imwrite('./current.png', image)
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

                    print("Perform Interaction")
                     # Model-based testing
                    best_box_id = -1

                    input_string = generate_input_string()
                    # state information -> get box
                    current_state = State_set.get_state(image, proc_boxes, best_box_id)

                    if current_state.state_id not in current_state_list:
                        # Explore strategy
                        in_state_count = 0
                        best_box_id, best_box = current_state.select_least_visit()
                    elif current_state.state_id == current_test_state or current_state.state_id == next_test_state:
                        # Execute strategy
                        if current_state.state_id == next_test_state:
                            max_in_state_count = random.randint(1, len(current_state.component) * 2)
                            current_state_index += 1
                            in_state_count = 0
                            if current_state_index < len(test_case) - 1:
                                current_test_state = test_case[current_state_index]
                                next_test_state = test_case[current_state_index + 1]
                            elif current_state_index == len(test_case) - 1:
                                current_test_state = test_case[current_state_index]
                                next_test_state = test_case[current_state_index]
                            best_box_id, best_box = current_state.select_random_box()
                        elif in_state_count < max_in_state_count:
                            best_box_id, best_box = current_state.transition_to_id_explore(next_test_state)
                        else:
                            """
                                Here, cluster refers to layouts in section III of GUISight, usually buttons in the same layout have similar function
                                Use widgets from different cluster to achieve transition benefits exploring coverage 
                            """
                            best_box_id, best_box, inter = current_state.transition_to_least_cluster(next_test_state)
                        in_state_count += 1
                    elif current_state.state_id in test_case:
                        # Vision-based testing is not stable, skip states in the sequence is acceptable
                        for idxx, st in enumerate(test_case):
                            if st == current_state.state_id:
                                if idxx < len(test_case) - 1:
                                    current_test_state = st
                                    next_test_state = test_case[idxx + 1]
                                else:
                                    current_test_state = st
                                    next_test_state = st
                            best_box_id, best_box = current_state.no_transition()
                            in_state_count = 1
                    else:
                        # Exception case, update and exit
                        if last_state is not None:
                            if last_state.state_id not in last_state.component_dict[last_box_id]['transition']:
                                last_state.add_transition(last_box_id, current_state.state_id, interaction)
                        break
                    # Update
                    if last_state is not None:
                        if current_state.state_id not in last_state.component_dict[last_box_id]['transition']:
                            last_state.add_transition(last_box_id, current_state.state_id, interaction)

                    last_box_id, last_state = best_box_id, current_state
                    print("Box:", best_box)
                    current_box = copy.deepcopy(best_box)

                    # interaction based on widget type
                    print('Action', actions)
                    x, y, interaction = perform_interaction(best_box, app_x, app_y, app_w, app_h, input_string, inter)
                    inter = None

                    time.sleep(0.3)
                    if not check_app(win_name):
                        close_app(win_name)
                        open_app(application_class_address,main_class,jar_address)
                    draw(raw_img, current_box, x, y)
                    actions += 1

                    end_iteration_time = time.time()
                    State_set.save_all_state() # You can continue testing by loading state machine by .read_state_file

                    if actions > total_max_action:
                        # EH.stop_application()
                        # EH.merge_report()
                        # EH.show_report()
                        close_app(win_name)
                        print("Finished testing!")
                        exit(0)
                    # write test info
                    with open(csv_file, "a") as run_log:
                        run_log.write(str(exec_time) + "," + str(actions) + "," + str(current_box) + "," + str(interaction) + ","+ str(iteration_time) + "," + win_name + "\n")


                # EH.stop_application()

        # EH.merge_report()
        # EH.show_report()
        print("Finished testing!")


