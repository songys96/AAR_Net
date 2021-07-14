# -*- coding: utf-8 -*-

import os
import sys
import time

import pickle
import logging
import easydict
import functools

from collections import defaultdict
from collections import OrderedDict

import json
import numpy as np
# from dataset.JointsVideoDataset import JointsVideoDataset

logger = logging.getLogger(__name__)

def timer(func):
    @functools.wraps(func)
    def wrapper_timer(*args, **kwargs):
        start_time = time.perf_counter()
        value = func(*args, **kwargs)

        end_time = time.perf_counter()
        run_time = end_time - start_time
        print(f"Finished {func.__name__} in {run_time:.4f} secs")
        return value
    return wrapper_timer

class AIHubDataset():
    '''
    return 
    gt_dt = [
        {
            "images" : [img_1, img_2, img_3],              # img = image path
            "keypoints" : [[15,3],[15,3],[15,3],...],      # 15 points, 3 channel(x, y, existence)
            "meta" :                                      
                { 
                    seq, species, action, location, 
                    height, width, animal, owner, inspect
                } 
        },

        {
            "images" : video_folder_2,
            "keypoints" : [{kp_1},{kp_2},{kp_2}],
            "meta" : {}
        }
        
        ...
    ]

    * CAUTION *
    Korean Encoding Error can be occured.
    so you should change Folder Name 
    원천데이터_1    ->     source_1
    라벨링데이터_1   ->     label_1

    if Training:
        root will be Training folder containing 9 label folders and 9 source folders 
    elif Validating:
        root will be Validating folder containing a folder

    "keypoints": {
        0: "nose",
        1: "center_forehead",
        2: "end_mouth",
        3: "center_mouth",
        4: "neck",
        5: "front_right_shoulder",
        6: "front_left_shoulder",
        7: "front_right_ankle",
        8: "front_left_ankle",
        9: "back_right_femur",
        10: "back_left_femur",
        11: "back_right_ankle",
        12: "back_left_ankle",
        13: "tail_start",
        14: "tail_end",
    },
	"skeleton": [
            [0,1],[1,2],[2,3],[0,4],[1,4],[3,4],
            [4,13],
            [4,5],[4,6],[5,7],[6,8],
            [13,9],[13,10],[9,11],[10,12],
            [13,14]
        ]
    
    '''
    def __init__(self, cfg, root, transform=None):

        # super().__init__(cfg, root, transform)
        # self.nms_thre = cfg.TEST.NMS_THRE
        # self.image_thre = cfg.TEST.IMAGE_THRE
        # self.oks_thre = cfg.TEST.OKS_THRE
        # self.in_vis_thre = cfg.TEST.IN_VIS_THRE
        # self.bbox_file = cfg.TEST.COCO_BBOX_FILE
        # self.use_gt_bbox = cfg.TEST.USE_GT_BBOX
        # self.image_width = cfg.MODEL.IMAGE_SIZE[0]
        # self.image_height = cfg.MODEL.IMAGE_SIZE[1]
        # self.aspect_ratio = self.image_width * 1.0 / self.image_height
        # self.pixel_std = 200

        # # load image file names
        # self.image_set_index = self._load_image_set_index()
        # self.num_images = len(self.image_set_index)
        # logger.info('=> num_images: {}'.format(self.num_images))
        self.root = root
        self.num_joints = 15
        self.flip_pairs = [[5, 6], [7, 8], [9, 10], [11, 12]]
        self.parent_ids = None

        self.errors = {"no_vid":[], "no_json":[]}
        self.db = self._get_db()

        # logger.info('=> load {} samples'.format(len(self.db)))


    def _get_db(self):
        """
        return format
        {
            "images" : images,
            "keypoints" : [{kp_1},{kp_2},{kp_2}],
            "meta" : meta
        }
        """
        gt_db = self._load_data()
        print(np.array(gt_db[0]['keypoints']).shape)
        return gt_db

    @timer
    def _load_data(self):
        data = []

        annotation_files = self._load_annotations()
        # annotation_files like ['label_9/20201024_cat-footpush-000053.mp4.json', 'label_9/20201024_cat-sitdown-000071.mp4.json', ...]
        print("total annotaion files : ", len(annotation_files))
        i = 0
        for anno in annotation_files:
            source_folder = "source_" + anno.split("/")[0][-1]
            
            # load json file
            video_info = None
            with open(os.path.join(self.root, anno)) as f:
                video_info = json.load(f)
            if not video_info:
                self.errors["no json"].append(anno)
                continue
            
            # get file list
            video_folder = anno.split("/")[-1].split(".json")[0]
            video_folder = os.path.join(self.root, source_folder, video_folder)
            if not os.path.exists(video_folder):
                self.errors["no_vid"].append(anno)
                continue
            
            # get images and keypoints
            images = []
            keypoints = []

            frames_info = video_info["annotations"]
            for frame_info in frames_info:
                frame_number = frame_info['frame_number']
                timestamp = frame_info['timestamp']
                keypoint = self._make_keypoint_to_np(frame_info['keypoints'])
                img_name = f'frame_{frame_number}_timestamp_{timestamp}.jpg'
                if os.path.exists(os.path.join(video_folder,img_name)):
                    images.append(img_name)
                    keypoints.append(keypoint)
            # get metadata
            metadata = video_info["metadata"]

            data.append(
                {
                    "images" : images,
                    "keypoints" : keypoints,
                    "meta" : metadata
                }
            )    
            if i > 5:
                break
            else:
                i += 1        
        return data
            
    def _load_annotations(self):
        annotation_files = []
        for folder_name in sorted(os.listdir(self.root)):

            # todo: Korean Encoding Error so you should CHANGE FOLDER NAME
            if not "." in folder_name and "label" in folder_name:
                annos = sorted(os.listdir(os.path.join(self.root, folder_name)))
                annos = list(map(self._join_path(folder_name), annos))
                annotation_files.extend(annos)
        return annotation_files
    
    def _join_path(self, folder):
        def _join_folder(filename):
            return os.path.join(folder, filename)
        return _join_folder

    def _resize_data(self):
        pass

    def _make_keypoint_to_np(self, keypoint):
        """
        {'1': {'x': 430, 'y':405}, ...} => [ [430,405,1], [0, 0, 0], ... ]
        """
        keypoints = []
        for i in range(15):
            id = str(i+1)
            if keypoint[id] is not None:
                x, y = keypoint[id]['x'], keypoint[id]['y']
                keypoints.append([x,y,1])
            else:
                keypoints.append([0,0,0])
        if len(keypoints) != self.num_joints:
            raise ValueError

        return np.array(keypoints)



    # need double check this API and classes field
    def evaluate(self, cfg, preds, output_dir, all_boxes, img_path,
                 *args, **kwargs):
        res_folder = os.path.join(output_dir, 'results')
        if not os.path.exists(res_folder):
            os.makedirs(res_folder)
        res_file = os.path.join(
            res_folder, 'keypoints_%s_results.json' % self.image_set)

        # person x (keypoints)
        _kpts = []
        for idx, kpt in enumerate(preds):
            _kpts.append({
                'keypoints': kpt,
                'center': all_boxes[idx][0:2],
                'scale': all_boxes[idx][2:4],
                'area': all_boxes[idx][4],
                'score': all_boxes[idx][5],
                'image': int(img_path[idx][-16:-4])
            })
        # image x person x (keypoints)
        kpts = defaultdict(list)
        for kpt in _kpts:
            kpts[kpt['image']].append(kpt)

        # rescoring and oks nms
        num_joints = self.num_joints
        in_vis_thre = self.in_vis_thre
        oks_thre = self.oks_thre
        oks_nmsed_kpts = []
        for img in kpts.keys():
            img_kpts = kpts[img]
            for n_p in img_kpts:
                box_score = n_p['score']
                kpt_score = 0
                valid_num = 0
                for n_jt in range(0, num_joints):
                    t_s = n_p['keypoints'][n_jt][2]
                    if t_s > in_vis_thre:
                        kpt_score = kpt_score + t_s
                        valid_num = valid_num + 1
                if valid_num != 0:
                    kpt_score = kpt_score / valid_num
                # rescoring
                n_p['score'] = kpt_score * box_score

        self._write_coco_keypoint_results(
            oks_nmsed_kpts, res_file)
        if 'test' not in self.image_set:
            info_str = self._do_python_keypoint_eval(
                res_file, res_folder)
            name_value = OrderedDict(info_str)
            return name_value, name_value['AP']
        else:
            return {'Null': 0}, 0
a = AIHubDataset("cfg", "/Users/song-yunsang/Desktop/Business/Butler/Dataset/test/aihub")

