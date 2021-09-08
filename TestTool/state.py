"""
Core state model definition and explore strategy
"""
import random
import numpy
from PIL import Image
import cv2
import json


class State:
    def __init__(self, image, component, dhash, id):
        if isinstance(component, list) and len(component) != 0:
            self.component = component
            self.component_dict = self.generate_dict()
        elif isinstance(component, dict) and len(component.keys()) != 0:
            self.component = [comp['box'] for comp in component.values()]
            self.component_dict = component
        else:
            self.component = [[['None', -1], 0.5, 0.5, 0.99, 0.99], ]
            self.component_dict = self.generate_dict()
        # or a list of image
        img = image
        name = './state/' + str(id) + '.png'
        cv2.imwrite(name, img)
        self.cluster_dict = self.generate_cluster_dict()
        self.dhash = dhash
        self.state_id = id

    def generate_cluster_dict(self):
        cluster_dict = {}
        for comp in self.component:
            if comp[0][1] != -1:
                cluster_dict[comp[0][1]] = 0
        return cluster_dict

    def transition_to_id(self, state_id):
        transition_list = []
        for comp_id in self.component_dict.keys():
            if state_id in self.component_dict[comp_id]['transition']:
                transition_list.append(comp_id)
        if len(transition_list) != 0:
            comp_idx = random.randint(0, len(transition_list) - 1)
            self.component_dict[transition_list[comp_idx]]['visit'] += 1
            return transition_list[comp_idx], self.component_dict[transition_list[comp_idx]]['box']
        else:
            return self.select_random_box_empty()

    def transition_to_least_cluster(self, state_id):
        transition_list = []
        for comp_id in self.component_dict.keys():
            if state_id in self.component_dict[comp_id]['transition']:
                transition_list.append(comp_id)
        if len(transition_list) != 0:
            least_visit_time = self.component_dict[transition_list[0]]['cluster']
            for comp_id in transition_list:
                if self.cluster_dict[self.component_dict[comp_id]['cluster']] < least_visit_time:
                    least_visit_time = self.cluster_dict[self.component_dict[comp_id]['cluster']]
            transition_list_cluster = []
            for comp_id in transition_list:
                if self.cluster_dict[self.component_dict[comp_id]['cluster']] == least_visit_time:
                    transition_list_cluster.append(comp_id)
            least_visit_idx = transition_list_cluster[random.randint(0, len(transition_list_cluster) - 1)]
            action = []
            for state_id_2, inter in self.component_dict[least_visit_idx]['action2transition']:
                if state_id_2 == state_id:
                    action.append(inter)
            if len(action) == 0:
                return self.select_random_box_empty()
            return least_visit_idx, self.component_dict[least_visit_idx]['box'], action[random.randint(0, len(action) - 1)]
        else:
            return self.select_random_box_empty()

    def transition_to_id_explore(self, state_id):
        not_transition_list = []
        for comp_id in self.component_dict.keys():
            if state_id in self.component_dict[comp_id]['transition'] or len(self.component_dict[comp_id]['transition']) == 0 or (len(self.component_dict[comp_id]['transition']) == 1 and self.state_id in self.component_dict[comp_id]['transition']):
                not_transition_list.append(comp_id)
        if len(not_transition_list) != 0:
            comp_idx = random.randint(0, len(not_transition_list) - 1)
            self.component_dict[not_transition_list[comp_idx]]['visit'] += 1
            return not_transition_list[comp_idx], self.component_dict[not_transition_list[comp_idx]]['box']
        else:
            return self.select_random_box()

    def no_transition(self):
        transition_list = []
        for comp_id in self.component_dict.keys():
            if len(self.component_dict[comp_id]['transition']) == 0:
                transition_list.append(comp_id)
        comp_idx = random.randint(0, len(transition_list) - 1)
        self.component_dict[transition_list[comp_idx]]['visit'] += 1
        return transition_list[comp_idx], self.component_dict[transition_list[comp_idx]]['box']

    def generate_dict(self):
        dic = {}
        for idx, box in enumerate(self.component):
            dic[idx] = {'box': box, 'cluster': box[0][1], 'type': box[0][0], 'visit': 0, 'transition': [], 'action2transition': []}
        return dic

    def select_random_box(self):
        comp_id = random.randint(0, len(self.component) - 1)
        self.component_dict[comp_id]['visit'] += 1
        return comp_id, self.component_dict[comp_id]['box']

    def select_random_box_empty(self):
        comp_id = random.randint(0, len(self.component) - 1)
        self.component_dict[comp_id]['visit'] += 1
        return comp_id, self.component_dict[comp_id]['box'], None

    def select_least_visit(self):
        not_visit = []
        visit = self.get_least_visit()
        for comp_id in self.component_dict.keys():
            if self.component_dict[comp_id]['visit'] == visit:
                not_visit.append(comp_id)
        comp_idx = random.randint(0, len(not_visit) - 1)
        self.component_dict[not_visit[comp_idx]]['visit'] += 1
        return not_visit[comp_idx], self.component_dict[not_visit[comp_idx]]['box']

    def get_least_visit(self):
        visit = self.component_dict[0]['visit']
        for comp_id in self.component_dict.keys():
            if self.component_dict[comp_id]['visit'] <= visit:
                visit = self.component_dict[comp_id]['visit']

        return visit

    def is_visit_all(self):
        for comp_id in self.component_dict.keys():
            if self.component_dict[comp_id]['visit'] == 0:
                return False

        return True

    def add_transition(self, component_id, state_id, inter):
        self.component_dict[component_id]['transition'].append(state_id)
        self.component_dict[component_id]['action2transition'].append([state_id, inter])

    def add_new_component(self, new_state_component):
        new_comp = []
        for new_state_box in new_state_component:
            new_flag = True
            for box in self.component:
                if self.iou(box[1:], new_state_box[1:]) > 0.9:
                    new_flag = False
                    break
            if new_flag:
                new_comp.append(new_state_box)
        pre_len = len(self.component)
        self.component += new_comp
        for idx, box in enumerate(new_comp):
            self.component_dict[pre_len + idx] = {'box': box, 'cluster': box[0][1], 'type': box[0][0], 'visit': 0, 'transition': [], 'action2transition': []}

    def return_transition_pair(self):
        reverse_dict = {}
        for comp_id in self.component_dict.keys():
            for state_id in self.component_dict[comp_id]['transition']:
                if state_id not in reverse_dict.keys():
                    reverse_dict[state_id] = [comp_id, ]
                else:
                    reverse_dict[state_id].append(comp_id)

        return reverse_dict

    @staticmethod
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

    def overlap_percentage(self, new_state_component):
        recall_count = 0
        for box in self.component:
            for new_state_box in new_state_component:
                if self.iou(box[1:], new_state_box[1:]) > 0.8:
                    recall_count += 1
                    break
        return recall_count/len(new_state_component) if len(new_state_component) != 0 else 0


class DHash(object):
    @staticmethod
    def calculate_hash(image):
        """
        计算图片的dHash值
        :param image: PIL.Image
        :return: dHash值,string类型
        """
        difference = DHash.__difference(image)
        # 转化为16进制(每个差值为一个bit,每8bit转为一个16进制)
        decimal_value = 0
        hash_string = ""
        for index, value in enumerate(difference):
            if value:  # value为0, 不用计算, 程序优化
                decimal_value += value * (2 ** (index % 8))
            if index % 8 == 7:  # 每8位的结束
                hash_string += str(hex(decimal_value)[2:].rjust(2, "0"))  # 不足2位以0填充。0xf=>0x0f
                decimal_value = 0
        return hash_string

    @staticmethod
    def hamming_distance(first, second):
        """
        计算两张图片的汉明距离(基于dHash算法)
        :param first: Image或者dHash值(str)
        :param second: Image或者dHash值(str)
        :return: hamming distance. 值越大,说明两张图片差别越大,反之,则说明越相似
        """
        # A. dHash值计算汉明距离
        if isinstance(first, str):
            return DHash.__hamming_distance_with_hash(first, second)

        # B. image计算汉明距离
        hamming_distance = 0
        image1_difference = DHash.__difference(first)
        image2_difference = DHash.__difference(second)
        for index, img1_pix in enumerate(image1_difference):
            img2_pix = image2_difference[index]
            if img1_pix != img2_pix:
                hamming_distance += 1
        return hamming_distance

    @staticmethod
    def __difference(image):
        """
        *Private method*
        计算image的像素差值
        :param image: PIL.Image
        :return: 差值数组。0、1组成
        """
        resize_width = 9
        resize_height = 8
        # 1. resize to (9,8)
        grayscale_image = Image.fromarray(image)
        smaller_image = grayscale_image.resize((resize_width, resize_height))
        # grayscale_image = Image.fromarray(cv2.cvtColor(smaller_image, cv2.COLOR_BGR2RGB))
        # 2. 灰度化 Grayscale
        # grayscale_image = smaller_image.convert("L")
        # 3. 比较相邻像素
        pixels = list(smaller_image.getdata())
        difference = []
        for row in range(resize_height):
            row_start_index = row * resize_width
            for col in range(resize_width - 1):
                left_pixel_index = row_start_index + col
                difference.append(pixels[left_pixel_index] > pixels[left_pixel_index + 1])
        return difference

    @staticmethod
    def __hamming_distance_with_hash(dhash1, dhash2):
        """
        *Private method*
        根据dHash值计算hamming distance
        :param dhash1: str
        :param dhash2: str
        :return: 汉明距离(int)
        """
        difference = (int(dhash1, 16)) ^ (int(dhash2, 16))
        return bin(difference).count("1")


class UI_state:
    def __init__(self):
        self.D_hash = DHash()
        self.state_lst = []
        self.last_state = None

    def get_state(self, image, component_list, box_id):
        dhash = self.D_hash.calculate_hash(image)
        is_new, state = self.is_new_state(component_list, dhash)
        if is_new:
            state = self.add_new_state(image, component_list, dhash)
            if self.last_state is not None and box_id != -1:
                self.last_state.add_transition(box_id, len(self.state_lst)-1)
        self.last_state = state
        return state

    def add_new_state(self, image, component, dhash):
        new_state = State(image, component, dhash, len(self.state_lst))
        self.state_lst.append(new_state)
        return new_state

    def is_new_state(self, component, dhash):
        similar_state = []
        for state in self.state_lst:
            widget_overlap = state.overlap_percentage(component)
            if widget_overlap > 0.8 or (self.D_hash.hamming_distance(state.dhash, dhash) <= 5 and widget_overlap > 0.6):
                similar_state.append([widget_overlap, state])
        if len(similar_state) > 0:
            similar_state.sort(key=lambda x: x[0], reverse=True)
            return [False, similar_state[0][1]]
        return [True, None]

    def generate_state_transition(self):
        transition_dict = {}
        for state in self.state_lst:
            # do not assign widgets
            transition_dict[state.state_id] = state.return_transition_pair().keys()
        return transition_dict

    def save_all_state(self, address='./state/state_info.json'):
        all_state_info = {}
        for state in self.state_lst:
            name = './state/'+str(state.state_id)+'.png'
            state_info = {'id': state.state_id, 'dhash': state.dhash, 'image': name, 'component': state.component_dict}
            all_state_info[state.state_id] = state_info
        with open(address, 'w') as json_file:
            json.dump(all_state_info, json_file)

    def read_state_file(self, address='./state/state_info.json'):
        all_state_info = json.loads(address)
        for state_id in all_state_info.keys():
            image = cv2.imread(all_state_info[state_id]['image'], 0)
            component = all_state_info[state_id]['component']
            dhash = all_state_info[state_id]['dhash']
            new_state = State(image, component, dhash, len(self.state_lst))
            self.state_lst.append(new_state)

    def generate_simple_path(self):
        transition_dict = self.generate_state_transition()
        simple_path_list = []
        init_state_transition = transition_dict[0]
        test_state_sequence = []

        def depth_first_search(state_id, state_transition, test_sequence):
            test_sequence.append(state_id)
            end_flg = True
            for stateID in state_transition:
                if stateID not in test_sequence:
                    end_flg = False
            if end_flg:
                simple_path_list.append(test_sequence)
                return
            for stateID in state_transition:
                if stateID not in test_sequence:
                    depth_first_search(stateID, transition_dict[stateID], test_sequence.copy())

        depth_first_search(0, init_state_transition, test_state_sequence)

        return simple_path_list

    def generate_prime_path(self):
        if len(self.state_lst) <= 1:
            print("Only one state")
            return [[0, ], ]
        return self.generate_simple_path()

    def generate_prime_path_2(self):
        if len(self.state_lst) <= 1:
            return self.state_lst
        simple_path_list = self.generate_simple_path()
        simple_path_len_dict = {}
        for simple_path in simple_path_list:
            if len(simple_path) not in simple_path_len_dict.keys():
                simple_path_len_dict[len(simple_path)] = [simple_path, ]
            else:
                simple_path_len_dict[len(simple_path)].append(simple_path)

        prime_path_set = []

        for i in range(len(self.state_lst) - 1):
            if i+1 in simple_path_len_dict.keys():
                path_set1 = simple_path_len_dict[i+1]
            else:
                path_set1 = []
            if i+2 in simple_path_len_dict.keys():
                path_set2 = simple_path_len_dict[i+2]
            else:
                path_set2 = []

            for path1 in path_set1:
                is_prime = True
                for path2 in path_set2:
                    if path1 == path2[:-1]:
                        is_prime = False
                        break
                if is_prime:
                    prime_path_set.append(path1)
        return prime_path_set

