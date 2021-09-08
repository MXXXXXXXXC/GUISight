from os.path import join as pjoin
import cv2
import os


def resize_height_by_longest_edge(img_path, resize_length=800):
    org = cv2.imread(img_path)
    height, width = org.shape[:2]
    if height > width:
        return resize_length
    else:
        return int(resize_length * (height / width))


if __name__ == '__main__':
    img_lst = []
    name_lst = []
    for root, dirs, files in os.walk("./data/Desktop_GUI_data/img/"):
        for f in files:
            if r'/.DS_Store' in str(os.path.join(root, f)):
                continue
            image = str(os.path.join(root, f))
            name_lst.append(f)
            img_lst.append(image)

    import detect_text_east.ocr_east as ocr
    import detect_text_east.lib_east.eval as eval
    import detect_compo.ip_region_proposal as ip
    import merge
    from cnn.CNN import CNN

    models = eval.load()
    classifier = {}
    # classifier['Image'] = CNN('Image')
    classifier['Elements'] = CNN('Elements')

    for idx in name_lst:
        key_params = {'min-grad':10, 'ffl-block':5, 'min-ele-area':50, 'merge-contained-ele':True,
                      'max-word-inline-gap':4, 'max-line-gap':4}

        # set input image path
        input_path_img = img_lst.pop(0)
        output_root = 'data/output/'
        resized_height = resize_height_by_longest_edge(input_path_img)
        os.makedirs(pjoin(output_root, 'ocr'), exist_ok=True)
        ocr.east(input_path_img, output_root, models, key_params['max-word-inline-gap'],
                 resize_by_height=resized_height, show=False)

        os.makedirs(pjoin(output_root, 'ip'), exist_ok=True)
        ip.compo_detection(input_path_img, output_root, key_params,
                           classifier=classifier, resize_by_height=resized_height, show=False)

        name = input_path_img.split('/')[-1][:-4]
        compo_path = pjoin(output_root, 'ip', str(name) + '.json')
        ocr_path = pjoin(output_root, 'ocr', str(name) + '.json')
        output_root = 'data/Desktop_output/'
        merge.incorporate(input_path_img, compo_path, ocr_path, output_root, params=key_params,
                          resize_by_height=resized_height, show=False,savename=idx)
