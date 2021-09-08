# GUI detection of GUISight

>[UIED](https://dl.acm.org/doi/abs/10.1145/3368089.3417940?casa_token=nlSz6krp82MAAAAA:bc8QgFyUCYAZXu4GfcnMPsXGu7PeqB8TK8tuEV08THlwazAdwkuwQku1MeTUSY77rCa4nO6NpOjlKQ) is a very good tool in GUI detection. We only do some improvements on UIED, the main part of this file comes from UIED, you can switch between GUISight and UIED by rename detect_compo_UIED to detect_compo

## What is it?

UI Element Detection (UIED) is an old-fashioned computer vision (CV) based element detection approach for graphic user interface. 

The input of UIED could be various UI image, such as mobile app or web page screenshot, UI design drawn by Photoshop or Sketch, and even some hand-drawn UI design. Then the approach detects and classifies text and graphic UI elements, and exports the detection result as JSON file for future application. 

UIED comprises two parts to detect UI text and graphic elements, such as button, image and input bar. 
* For text, it leverages a state-of-the-art scene text detector [EAST](https://github.com/argman/EAST) to perfrom detection. 

* For graphical elements, it uses old-fashioned CV and image processing algorithms with a set of creative innovations to locate the elements and applies a CNN to achieve classification. 

Main part of GUISight's improvment upon UIED is in detect_compo\ip_region_proposal.py
   
## How to use?

### Dependency
* **Python 3.5（3.6）**
* **Numpy > 1.15.2**
* **Opencv > 3.4.2**
* **Tensorflow 1.10.0**
* **Keras 2.2.4**
* **Sklearn 0.22.2**
* **Pandas 0.23.4**

### Installation
Install the mentioned dependencies, and download two pre-trained models from [this link](https://drive.google.com/drive/folders/1MK0Om7Lx0wRXGDfNcyj21B0FL1T461v5?usp=sharing) for EAST text detection and GUI element classification.

Change ``CNN_PATH`` and ``EAST_PATH`` in *config/CONFIG.py* to your locations.

Unzip data.zip

### Usage
To test your own image(s):
* For testing single image, change ``input_path_img`` in *run_single.py* to your own input image and the results will be outputted to ``output_root``.

To reproduce the result in GUISight paper:
* For desktop data set:
    1. Run run_on_desktop_set.py 
    2. Run evaluate_desktop.py
* For RICO data set:
    1. Please download the RICO data set from  https://storage.googleapis.com/crowdstf-rico-uiuc-4540/rico_dataset_v0.1/unique_uis.tar.gz and put it in data/Android_GUI_data
    2. Run run_on_RICO_set.py 
    3. Run evaluate_RICO.py
    4. Run RICO_difference.py
   
## File structure
*cnn/*
* Used to train classifier for graphic UI elements
* Set path of the CNN classification model

*config/*
* Set data paths 
* Set parameters for graphic elements detection

*output/*
* Input UI images and output detection results

*detect_compo_UIED/*
* Graphic UI elemnts localization
* Graphic UI elemnts classification by CNN
* To use UIED: Rename this directory to 'detect_compo'

*detect_compo/*
* Improved detect_compo. ADD: Small widget detection & Refinement in layout & Aviod removal of weel-predicted widgets

*detect_text_east/*
* UI text detection by EAST

*result_processing/*
* Result evaluation and visualizition

*merge.py*
* Merge the results from the graphical UI elements detection and text detection 

*run_single.py*
* Process a signle image

*run_on_desktop_set.py(new)*
* Get the prediction result of desktop GUI data set 

*evaluate_desktop.py(new)*
* Evalutae the result in desktop data set

*run_on_RICO_set.py(new)*
* Get the prediction result of RICO data set 

*evalute_RICO.py(new)*
* Evalutae the technique on RICO data set and save the result in different iou.

*RICO_difference.py(new)*
* To evaluate two detection technique on RICO data set and record result on different iou
