# ------------------------------------------------------------------------------
# Copyright (c) Microsoft
# Licensed under the MIT License.
# Written by Bin Xiao (Bin.Xiao@microsoft.com)
# ------------------------------------------------------------------------------

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import copy
import logging
import random
import os

import cv2
import numpy as np
import torch
from torch.utils.data import Dataset

# from utils.transforms import get_affine_transform
# from utils.transforms import affine_transform
# from utils.transforms import fliplr_joints


logger = logging.getLogger(__name__)


class JointsVideoDataset(Dataset):
    def __init__(self, cfg, root, is_train, transform=None):
        self.num_joints = 0
        self.pixel_std = 200
        self.flip_pairs = []
        self.parent_ids = []

        self.is_train = is_train
        self.root = root

        self.output_path = cfg.OUTPUT_DIR

        ## todo: will be added on config
        # self.scale_factor = cfg.DATASET.SCALE_FACTOR
        # self.rotation_factor = cfg.DATASET.ROT_FACTOR
        # self.flip = cfg.DATASET.FLIP
        # self.image_size = cfg.MODEL.IMAGE_SIZE
        # self.target_type = cfg.MODEL.EXTRA.TARGET_TYPE
        # self.heatmap_size = cfg.MODEL.EXTRA.HEATMAP_SIZE
        # self.sigma = cfg.MODEL.EXTRA.SIGMA

        self.transform = transform
        self.db = []

    def _get_db(self):
        raise NotImplementedError

    def evaluate(self, cfg, preds, output_dir, *args, **kwargs):
        return
        raise NotImplementedError

    def __len__(self,):
        return len(self.db)

    def __getitem__(self, idx):
        """
        :param return
            {
                "images" : [frames, width, height, channel],
                "keypoints" : (frames, 3),
                "meta": {
                    "filename": json_path,
                    "frames" : frame_num,
                    ...
                    }
            }
        """
        db_rec = copy.deepcopy(self.db[idx])

        # image files to numpy 
        # return (frames, channel, heigth, width)
        images_db = db_rec['images']
        images = []
        for image in images_db:
            if not os.path.exists(image):
                print("Image is not exists")
            img_np = cv2.imread(image, cv2.IMREAD_COLOR | cv2.IMREAD_IGNORE_ORIENTATION)
            images.append(img_np)

        if len(images) == 0:
            logger.error('=> fail to read {}'.format(db_rec['meta']['filename']))
            raise ValueError('Fail to read {}'.format(db_rec['meta']['filename']))

        keypoints = db_rec['keypoints']
        meta = db_rec['meta']

        sample = {
            "images" : images,
            "keypoints" : keypoints,
            "meta" : meta
        }

        ## todo: this will be modified
        if self.transform:
            sample = self.transform(sample)

        else:
            sample['images'] = np.array(images)
            sample['keypoints'] = np.array(keypoints)

        return sample

        ## todo: have to understand

        # joints = db_rec['joints_3d']
        # joints_vis = db_rec['joints_3d_vis']

        # c = db_rec['center']
        # s = db_rec['scale']
        # score = db_rec['score'] if 'score' in db_rec else 1
        # r = 0

        # if self.is_train:
        #     sf = self.scale_factor
        #     rf = self.rotation_factor
        #     s = s * np.clip(np.random.randn()*sf + 1, 1 - sf, 1 + sf)
        #     r = np.clip(np.random.randn()*rf, -rf*2, rf*2) \
        #         if random.random() <= 0.6 else 0

        #     if self.flip and random.random() <= 0.5:
        #         data_numpy = data_numpy[:, ::-1, :]
        #         joints, joints_vis = fliplr_joints(
        #             joints, joints_vis, data_numpy.shape[1], self.flip_pairs)
        #         c[0] = data_numpy.shape[1] - c[0] - 1

        # trans = get_affine_transform(c, s, r, self.image_size)
        # input = cv2.warpAffine(
        #     data_numpy,
        #     trans,
        #     (int(self.image_size[0]), int(self.image_size[1])),
        #     flags=cv2.INTER_LINEAR)

        # if self.transform:
        #     input = self.transform(input)

        # for i in range(self.num_joints):
        #     if joints_vis[i, 0] > 0.0:
        #         joints[i, 0:2] = affine_transform(joints[i, 0:2], trans)

        # target, target_weight = self.generate_target(joints, joints_vis)

        # target = torch.from_numpy(target)
        # target_weight = torch.from_numpy(target_weight)

        # meta = {
        #     'image': image_file,
        #     'filename': filename,
        #     'imgnum': imgnum,
        #     'joints': joints,
        #     'joints_vis': joints_vis,
        #     'center': c,
        #     'scale': s,
        #     'rotation': r,
        #     'score': score
        # }

    # def generate_target(self, joints, joints_vis):
    #     '''
    #     :param joints:  [num_joints, 3]
    #     :param joints_vis: [num_joints, 3]
    #     :return: target, target_weight(1: visible, 0: invisible)
    #     '''
    #     target_weight = np.ones((self.num_joints, 1), dtype=np.float32)
    #     target_weight[:, 0] = joints_vis[:, 0]

    #     assert self.target_type == 'gaussian', \
    #         'Only support gaussian map now!'

    #     if self.target_type == 'gaussian':
    #         target = np.zeros((self.num_joints,
    #                            self.heatmap_size[1],
    #                            self.heatmap_size[0]),
    #                           dtype=np.float32)

    #         tmp_size = self.sigma * 3

    #         for joint_id in range(self.num_joints):
    #             feat_stride = self.image_size / self.heatmap_size
    #             mu_x = int(joints[joint_id][0] / feat_stride[0] + 0.5)
    #             mu_y = int(joints[joint_id][1] / feat_stride[1] + 0.5)
    #             # Check that any part of the gaussian is in-bounds
    #             ul = [int(mu_x - tmp_size), int(mu_y - tmp_size)]
    #             br = [int(mu_x + tmp_size + 1), int(mu_y + tmp_size + 1)]
    #             if ul[0] >= self.heatmap_size[0] or ul[1] >= self.heatmap_size[1] \
    #                     or br[0] < 0 or br[1] < 0:
    #                 # If not, just return the image as is
    #                 target_weight[joint_id] = 0
    #                 continue

    #             # # Generate gaussian
    #             size = 2 * tmp_size + 1
    #             x = np.arange(0, size, 1, np.float32)
    #             y = x[:, np.newaxis]
    #             x0 = y0 = size // 2
    #             # The gaussian is not normalized, we want the center value to equal 1
    #             g = np.exp(- ((x - x0) ** 2 + (y - y0) ** 2) / (2 * self.sigma ** 2))

    #             # Usable gaussian range
    #             g_x = max(0, -ul[0]), min(br[0], self.heatmap_size[0]) - ul[0]
    #             g_y = max(0, -ul[1]), min(br[1], self.heatmap_size[1]) - ul[1]
    #             # Image range
    #             img_x = max(0, ul[0]), min(br[0], self.heatmap_size[0])
    #             img_y = max(0, ul[1]), min(br[1], self.heatmap_size[1])

    #             v = target_weight[joint_id]
    #             if v > 0.5:
    #                 target[joint_id][img_y[0]:img_y[1], img_x[0]:img_x[1]] = \
    #                     g[g_y[0]:g_y[1], g_x[0]:g_x[1]]

    #     return target, target_weight

