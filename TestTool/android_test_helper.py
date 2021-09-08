"""
HELPER for Android app testing
To adapt to a new framework, platform or system
You can create a new test_helper including:
get_window_size: get the location of window (for mobile app, it is full screen)
screenshot: get a screen shot of the screen. Just a screen capture.
perform_interaction: Replace the commend in our function with the platform specific commend
open_app: Open the app
close_app: Close the app
check_app: Check if app is still ongoing. You can just return True
"""

import os
import cv2
import random
import pyautogui
import re
import time



def get_window_size():
    command = "adb shell wm size"
    r = os.popen(command) 
    info = r.readlines()  
    w, h = 1080, 1920 # default
    for line in info:  
        line = line.strip('\r\n')
        line = line.split()
        w, h = line[-1].split('x')
    return 0, 0, int(w), int(h)


def check_app(app):
    command = """ adb shell "dumpsys window | grep mCurrentFocus" """
    r = os.popen(command)  
    info = r.readlines()  

    for line in info: 
        res = re.findall("u0 (.*)/", line)
        if "PopupWindow" in line:
            return True
        if len(res) != 0 and app in res[0]:
            return True
    print("Not in app")
    os.system('adb shell input keyevent 4')
    command = """ adb shell "dumpsys window | grep mCurrentFocus" """
    r = os.popen(command)  
    info = r.readlines()  
    for line in info:  
        res = re.findall("u0 (.*)/", line)
        if len(res) != 0 and app == res[0]:
            return True
    os.system('adb shell input keyevent 3')
    os.system('adb shell input tap 100 1800')

    command = """ adb shell "dumpsys window | grep mCurrentFocus" """
    r = os.popen(command)  
    info = r.readlines() 
    for line in info: 
        res = re.findall("u0 (.*)/", line)
        if len(res) != 0 and app == res[0]:
            return True
    return False


def screenshot():
    command = "adb shell screencap -p /sdcard/screenshot.png"
    os.system(command)
    command = "adb pull /sdcard/screenshot.png screenshots/screenshot.png"
    os.system(command)
    img = cv2.imread('screenshots/screenshot.png', 0)
    w, h,  = img.shape
    img = img[30:h,0:w] # delete Android top bar
    return img


def click(x, y):
    command = 'adb shell input tap %s %s' % (x, y)
    os.system(command)


def swipe(x1, y1, x2, y2):
    command = 'adb shell input swipe %s %s %s %s' % (x1, y1, x2, y2)
    os.system(command)


def input_text(text):
    command = """adb shell input text '%s' """ % text
    print (command)
    os.system(command)


def open_app(name):
    command = """adb shell am start %s""" % name
    os.system(command)


def close_app(name):
    command = """adb shell am force-stop %s""" % name
    os.system(command)


def perform_interaction(best_box, app_x, app_y, app_w, app_h, input_string, given_inter=None):
    interaction = []

    def random_test(x, y, random_interaction):
        if random_interaction == 'click':
            print('click %s %s' % (x, y))
            click(x, y)
            interaction.append(['click', (x, y)])
        if random_interaction == 'swipe':
            x1, y1 = x, y
            x_mod = (0.5 - random.random()) * best_box[3]
            y_mod = (0.5 - random.random()) * best_box[4]
            x2 = int(max(app_x, min(app_x + app_w, app_x + ((best_box[1] + x_mod) * app_w))))
            y2 = int(max(app_y, min(app_y + app_h, app_y + ((best_box[2] + y_mod) * app_h))))
            print('swipe %s %s %s %s' % (x1, y1, x2, y2))
            swipe(x1, y1, x2, y2)
            interaction.append(['swipe', (x1, y1, x2, y2)])

        elif random_interaction == 'input text':
            print('input text')
            input_text(input_string)
            print('type %s' % input_string)
            interaction.append(['input text', input_string])

    def do_inter(inter, position):
        if inter == 'click':
            x,y = position
            print('click %s %s' % (x, y))
            click(x, y)
            interaction.append(['click', (x, y)])
        if inter == 'swipe':
            x1, y1, x2, y2 = position
            print('swipe %s %s %s %s' % (x1, y1, x2, y2))
            swipe(x1, y1, x2, y2)
            interaction.append(['swipe', (x1, y1, x2, y2)])

        elif inter == 'input text':
            input_string = position
            input_text(input_string)
            print('type %s' % input_string)
            interaction.append(['type', input_string])


    best_box[1], best_box[2], best_box[3], best_box[4] = float(best_box[1]), float(best_box[2]), float(best_box[3]), float(best_box[4])
    x_mod = (0.5-random.random())*(best_box[3]-best_box[1])
    y_mod = (0.5-random.random())*(best_box[4]-best_box[2])
    x = int(max(app_x, min(app_x + app_w, app_x + (((best_box[3]+best_box[1])/2+x_mod)*app_w))))
    y = int(max(app_y, min(app_y + app_h, app_y + (((best_box[4]+best_box[2])/2+y_mod)*app_h))))
    typ = best_box[0][0]

    if given_inter:
        for inter,pos in given_inter:
            do_inter(inter,pos)
        return x_mod, y_mod, interaction

    if typ in ['Button', 'ToggleButton', 'RadioButton', 'Switch', 'ProcessBar', 'Checkbox', 'ImageButton', 'Text']:
        random_test(x, y, 'click')

    if typ in ['SeekBar', 'RatingBar', 'Spinner']:
        # left click, right click, double click, press and move (scroll), scroll
        random_interaction = random.random()
        if random_interaction < 0.6:
            random_test(x, y, 'click')
        else:
            random_test(x, y, 'swipe')

    if typ in ['ImageView', 'Background', 'VideoView', 'Chronometer']:
        # left click, right click, double click, press and move (select an area), scroll
        random_interaction = random.random()
        if random_interaction < 0.6:
            random_test(x, y, 'click')
        else:
            random_test(x, y, 'swipe')

    if typ in ['TextView', 'EditText']:
        # left click, right click, double click, press and move (select an area), scroll
        random_interaction = random.random()
        if random_interaction < 0.4:
            random_test(x, y, 'swipe')
        else:
            random_test(x, y, 'click')

        random_test(x, y, 'input text')

    return x_mod, y_mod, interaction

