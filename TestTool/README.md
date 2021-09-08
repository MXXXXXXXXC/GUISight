# GUISight

>To relieve testing tool's dependency's on GUI API and framework, we develop this tool. It can be easily adapted to the automatic GUI testing of apps from other platform. In this repo, we adapt it to test Linux Desktop apps and Android apps.

## Introduce to this tool

* The GUI-detection technique used in this tool is build upon UIED,  and we improve its performance. Please refer to [this link](https://dl.acm.org/doi/abs/10.1145/3368089.3417940?casa_token=nlSz6krp82MAAAAA:bc8QgFyUCYAZXu4GfcnMPsXGu7PeqB8TK8tuEV08THlwazAdwkuwQku1MeTUSY77rCa4nO6NpOjlKQ) for UIED. And (URL ) for our improvements.
* Our novel testing tool is a combination of vision-based GUI detection and model-based testing. ('') for detail.
   
## How to use?

### Dependency of vision technique we use
* **Python 3.5（3.6）**
* **Numpy > 1.15.2**
* **Opencv > 3.4.2**
* **Tensorflow 1.10.0**
* **Keras 2.2.4**
* **Sklearn 0.22.2**
* **Pandas 0.23.4**

### Installation of GUI detection
Install the mentioned dependencies, and download two pre-trained models from [this link](https://drive.google.com/drive/folders/1MK0Om7Lx0wRXGDfNcyj21B0FL1T461v5?usp=sharing) for EAST text detection and GUI element classification.

Change ``CNN_PATH`` and ``EAST_PATH`` in *configfile/CONFIG.py* to your locations.

### Usage
To test app:
* For android testing, use test_with_model_Android.py. You should provide the class file or jar file of the app.
* For linux desktop app testing, use test_with_model_Linux.py. You should provide the window name, and the class file or jar file. Our tool is not specific to java, you can test new format of apps by kindly replace the function "open_app" in test_helper.

To adapt to a new platform or system:
* You can create a new test_helper including these functions:
* get_window_size: get the location of window (for mobile app, it is full screen)
* screenshot: get a screen shot of the screen. Just a screen capture.
* perform_interaction: Replace the commend in our function with the platform specific commend
* open_app: Open the app
* close_app: Close the app
* check_app: Check if app is still ongoing. You can just return True
   
## File structure
*cnn  configfile  detect_compo detect_text_east result_processing merge.py*
* Please refer to directory "Detection"

*emma_helper.py*
* Record coverage in Linux desktop app testing 

*event.py*
* From GUIdance (url of GUIdance), we use it to achieve some GUI actions in Linux Desktop app

*no_model.py*
* Vision-based Automatic GUI test tool without state model. Perform test actions based on widget types and region.  

*test_helper.py*
* Same structure with Android_test_helper. For test utils in Linux desktop app testing.

*Android_test_helper.py*
* Same structure with test_helper. For test utils in Linux desktop app testing.

*state.py*
* Definition of our state machine and test strategy.

*test_with_model_Linux.py*
* For linux desktop app GUI testing. Only [app name inputs, test_helper, and sleep time] are different from test_with_model_Android.py. 

*test_with_model_Android*
* For Android app GUI testing. 
