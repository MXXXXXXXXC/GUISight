"""
Function "get_window_size" is from GUIdance
"""

"""
HELPER for linux desktop app testing
To adapt to a new framework, platform or system
You can create a new test_helper including:
get_window_size: get the location of window (for mobile app, it is full screen)
screenshot: get a screen shot of the screen. Just a screen capture.
perform_interaction: Replace the commend in our function with the platform specific commend
open_app: Open the app
close_app: Close the app
check_app: Check if app is still ongoing. You can just return True
"""

import Xlib
from Xlib.display import Display
import random
import subprocess
import traceback
import os
import cv2
debug = False
import time
import pyautogui
from event import MouseEvent, KeyEvent, ScrollEvent 
rightpress = False
leftpress = True

display = Display()

def close_app(app_name):
    # If not work, change the input
    commend = """ps -a | grep %s | xargs kill -9"""%app_name
    os.system(commend)

def open_app(java_class_path, main_class,jar_file = None):
    # ....
    if jar_file is not None:
        commend = """java -jar %s"""%jar_file
    else:
        commend = """java -cp %s %s"""%(java_class_path, main_class)
    os.system(commend)

def check_app():
    return True

def generate_input_string():
    if random.random() < 0.5:
        return "Hello World!"
    else:
        return str(random.randint(-10000, 10000))

def screenshot():
    img_file = os.environ.get("OUT_DIR", "./")
    if not img_file.endswith("/"):
        img_file += "/"

    img_file += "screenshots/"

    #convert seconds since epoch to minutes

    if not os.path.isdir(img_file):
        os.makedirs(img_file)
    img_file += str(int(time.time())) + "-screenshot.png"

    os.system("import -silent -window root " + img_file)
    img = cv2.imread(img_file, 0)

    return img


def perform_interaction(best_box, app_x, app_y, app_w, app_h, input_string=generate_input_string(), assign_action=None):
    global rightpress, leftpress
    events = []
    interaction = []
    def random_test(events,x,y,type):
        global rightpress, leftpress
        random_interaction = type
        action = random.randint(0, 9)
        if random_interaction == 'left click':
            print('left click')
            pyautogui.leftClick(x, y)

        if random_interaction == 'double click':
            print('double click')
            pyautogui.doubleClick(x, y)
        elif random_interaction == 'right click':
            print('right click')
            pyautogui.rightClick(x, y)
        elif random_interaction == 'right press':
            print('right press')
            pyautogui.mouseDown(x, y, 'right')
            rightpress = True
        elif random_interaction == 'left press':
            print('left press')
            pyautogui.mouseDown(x, y, 'left')
            leftpress = True
        elif random_interaction == 'press and move':
            print('press and move')
            if random.random() < 0.5:
                pyautogui.mouseDown(x, y, 'right')
                x_mod = (0.5 - random.random()) * best_box[3]
                y_mod = (0.5 - random.random()) * best_box[4]
                x = int(max(app_x, min(app_x + app_w, app_x + ((best_box[1] + x_mod) * app_w))))
                y = int(max(app_y, min(app_y + app_h, app_y + ((best_box[2] + y_mod) * app_h))))
                pyautogui.mouseUp(x, y, 'right')
            else:
                pyautogui.mouseDown(x, y, 'left')
                x_mod = (0.5 - random.random()) * best_box[3]
                y_mod = (0.5 - random.random()) * best_box[4]
                x = int(max(app_x, min(app_x + app_w, app_x + ((best_box[1] + x_mod) * app_w))))
                y = int(max(app_y, min(app_y + app_h, app_y + ((best_box[2] + y_mod) * app_h))))
                pyautogui.mouseUp(x, y, 'left')
        elif random_interaction == 'left click and type':
            print('left click and type')
            pyautogui.leftClick(x, y)
            events.append(KeyEvent(time.time(), input_string))
        elif random_interaction == 'type':
            print('type')
            pyautogui.leftClick(x, y)
            events.append(KeyEvent(time.time(), input_string))
        elif random_interaction == 'scroll':
            print('scroll')
            step = random.randint(1, 10)
            events.append(ScrollEvent(time.time(), step, step, x, y))
        interaction.append([random_interaction,(x,y)])
        return events

    def do_inter(assign_action):
        random_interaction = assign_action[0]
        x,y = assign_action[1]
        if random_interaction == 'left click':
            print('left click')
            pyautogui.leftClick(x, y)

        if random_interaction == 'double click':
            print('double click')
            pyautogui.doubleClick(x, y)
        elif random_interaction == 'right click':
            print('right click')
            pyautogui.rightClick(x, y)
        elif random_interaction == 'right press':
            print('right press')
            pyautogui.mouseDown(x, y, 'right')
            rightpress = True
        elif random_interaction == 'left press':
            print('left press')
            pyautogui.mouseDown(x, y, 'left')
            leftpress = True
        elif random_interaction == 'press and move':
            print('press and move')
            if random.random() < 0.5:
                pyautogui.mouseDown(x, y, 'right')
                x_mod = (0.5 - random.random()) * best_box[3]
                y_mod = (0.5 - random.random()) * best_box[4]
                x = int(max(app_x, min(app_x + app_w, app_x + ((best_box[1] + x_mod) * app_w))))
                y = int(max(app_y, min(app_y + app_h, app_y + ((best_box[2] + y_mod) * app_h))))
                pyautogui.mouseUp(x, y, 'right')
            else:
                pyautogui.mouseDown(x, y, 'left')
                x_mod = (0.5 - random.random()) * best_box[3]
                y_mod = (0.5 - random.random()) * best_box[4]
                x = int(max(app_x, min(app_x + app_w, app_x + ((best_box[1] + x_mod) * app_w))))
                y = int(max(app_y, min(app_y + app_h, app_y + ((best_box[2] + y_mod) * app_h))))
                pyautogui.mouseUp(x, y, 'left')
        elif random_interaction == 'left click and type':
            print('left click and type')
            pyautogui.leftClick(x, y)
            events.append(KeyEvent(time.time(), input_string))
        elif random_interaction == 'type':
            print('type')
            pyautogui.leftClick(x, y)
            events.append(KeyEvent(time.time(), input_string))
        elif random_interaction == 'scroll':
            print('scroll')
            step = random.randint(1, 10)
            events.append(ScrollEvent(time.time(), step, step, x, y))

    best_box[1], best_box[2], best_box[3], best_box[4] = float(best_box[1]), float(best_box[2]), float(best_box[3]), float(best_box[4])
    x_mod = (0.5-random.random())*(best_box[3]-best_box[1])
    y_mod = (0.5-random.random())*(best_box[4]-best_box[2])
    x = int(max(app_x, min(app_x + app_w, app_x + (((best_box[3]+best_box[1])/2+x_mod)*app_w))))
    y = int(max(app_y, min(app_y + app_h, app_y + (((best_box[4]+best_box[2])/2+y_mod)*app_h))))
    typ = best_box[0][0]
    if assign_action:
        do_inter(assign_action)
        return x_mod, y_mod, assign_action
    if rightpress:
        pyautogui.mouseUp(x, y, 'right')
        rightpress = False
    if leftpress:
        pyautogui.mouseUp(x, y, 'left')
        leftpress = False

    if typ in ['Button', 'ToggleButton', 'RadioButton', 'Switch', 'ProcessBar', 'Checkbox', 'ImageButton', 'Text']:
        # 3 click
        random_interaction = random.random()
        if random_interaction < 0.33:
            events = random_test(events, x, y, 'left click')
        elif random_interaction < 0.66:
            events = random_test(events, x, y,  'right click')
        else:
            events = random_test(events, x, y,  'double click')

    if typ in ['SeekBar', 'RatingBar', 'Spinner']:
        # left click, right click, double click, press and move (scroll), scroll
        random_interaction = random.random()
        if random_interaction < 0.2:
            events = random_test(events, x, y,  'left click')
        elif random_interaction < 0.4:
            events = random_test(events, x, y,  'right click')
        elif random_interaction < 0.6:
            events = random_test(events, x, y, 'double click')
        elif random_interaction < 0.8:
            events = random_test(events, x, y, 'press and move')
        else:
            events = random_test(events, x, y, 'scroll')

    if typ in ['ImageView', 'Background', 'VideoView', 'Chronometer']:
        # left click, right click, double click, press and move (select an area), scroll
        random_interaction = random.random()
        if random_interaction < 0.2:
            events = random_test(events, x, y, 'left click')
        elif random_interaction < 0.4:
            events = random_test(events, x, y, 'right click')
        elif random_interaction < 0.6:
            events = random_test(events, x, y, 'double click')
        elif random_interaction < 0.8:
            events = random_test(events, x, y, 'press and move')
            random_interaction = random.random()
            if random_interaction < 0.33:
                events = random_test(events, x, y, 'left click')
            elif random_interaction < 0.66:
                events = random_test(events, x, y, 'right click')
        else:
            events = random_test(events, x, y, 'scroll')
        # the predictor is not precise, every thing is Image View
        if random.random() < 0.5:
            events = random_test(events, x, y, 'type')

    if typ in ['TextView', 'EditText']:
        # left click, right click, double click, press and move (select an area), scroll
        random_interaction = random.random()
        if random_interaction < 0.2:
            events = random_test(events, x, y, 'left click and type')
        elif random_interaction < 0.4:
            events = random_test(events, x, y, 'right click')
        elif random_interaction < 0.6:
            events = random_test(events, x, y, 'double click')
        elif random_interaction < 0.8:
            events = random_test(events, x, y, 'press and move')
            random_interaction = random.random()
            if random_interaction < 0.33:
                events = random_test(events, x, y, 'left click')
            elif random_interaction < 0.66:
                events = random_test(events, x, y, 'right click')
        else:
            events = random_test(events, x, y, 'scroll')
        events = random_test(events, x, y, 'type')

    for event in events:
        event.perform()
    return x_mod, y_mod, interaction


def get_window_size(window_name):
    return get_window_size_focus(window_name, focus=True)


def get_window_size_focus(window_name, focus=True):
    # From the code of GUIdance paper
    # Return the position of application window
    global true_window, display
    sub_window = False

    try:
        root = display.screen().root
        win_names = window_name.split("|||")

        # win_names.append("java") # java file browser

        # windowIDs = root.get_full_property(display.intern_atom('_NET_CLIENT_LIST'), Xlib.X.AnyPropertyType).value

        raw_windows = root.query_tree().children

        all_windows = raw_windows
        wid = 0
        win = None
        windows = []
        while len(all_windows) > 0:
            window = all_windows.pop(0)
            #window = display.create_resource_object('window', windowID)
            try:
                # to handle bad windows

                matched = False
                win_name = window.get_wm_name()
                add_child = True
                if isinstance(win_name, bytes):
                    win_name = win_name.decode()
                # workaround for java apps
                while not win_name is None and "focusproxy" in win_name.lower():
                    window = window.query_tree().parent
                    win_name = window.get_wm_name()
                    if isinstance(win_name, bytes):
                        win_name = win_name.decode()
                    add_child = False

                name = win_name
                tag = ""
                tags = window.get_wm_class()
                if tags != None and len(tags) > 1:
                    tag = tags[1]

                children = window.query_tree().children

                if (children is not None) and len(children) > 0:
                    for w_c in children:
                        if add_child:
                            all_windows.append(w_c)
                if name is None or window.get_wm_normal_hints() is None or window.get_attributes().map_state != Xlib.X.IsViewable:
                    continue


                if isinstance(name, str) or isinstance(tag, str):
                    for w_n in win_names:
                        if w_n.lower() in name.lower() or w_n.lower() in tag.lower():
                            if 'eclipse' in window.get_wm_name():
                                continue
                            matched = True
                            win = window
                            windows.append(win)
                            break

                if debug:
                    print("[Window]", window.get_wm_name(), window.get_wm_class())

            except Exception as s:
                print('Exception:', str(s))

        if debug:
            print("--------------------")
            for window in windows:
                print("[Selected Window]", window.get_wm_name(), window.get_wm_class())
        if len(windows) > 1 :
            win_sel = None
            while win_sel is None and len(windows) > 0:
                c_win = windows.pop(-1)#random.randint(0, len(windows)-1))

                win_sel = c_win

            if not win_sel is None:
                win = win_sel

        else:
            win = windows[0]

        name = win.get_wm_name() # Title

        if focus:
            win.set_input_focus(Xlib.X.RevertToParent, Xlib.X.CurrentTime)
            win.configure(stack_mode=Xlib.X.Above)

        geom = win.get_geometry()

        app_x, app_y, app_w, app_h = (geom.x, geom.y, geom.width, geom.height)

        try:
            parent_win = win.query_tree().parent

            while parent_win != 0:
                #print(parent_win)
                p_geom = parent_win.get_geometry()
                app_x += p_geom.x
                app_y += p_geom.y
                parent_win = parent_win.query_tree().parent
        except Exception as e:
            print('[Window Parent Error] Screen cap failed: '+ str(e))
            traceback.print_stack()
        return app_x, app_y, app_w, app_h
    except Exception as e:
        print('[Window Error] Screen cap failed: ' + str(e))
        # traceback.print_stack()
    return 0, 0, 0, 0



