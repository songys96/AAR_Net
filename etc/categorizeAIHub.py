# -*- coding: utf-8 -*-
import os
import json

from os.path import join as joinpath
from os.path import exists as isExisted
from os.path import abspath as abspath
from posixpath import join

from aihub_config import KEY_NAME, SKELETON, SPECIES

class AIHubDataset():

    def __init__(self, source):
        """
        :param source    -> folder contained labels  ex. label_1
        """
        self.source = source
        self.cat = None
    
    @staticmethod
    def readCOCO(data):
        '''
        I think 17 kp
        :param info         {'description': 'COCO 2017 Dataset', 'url': 'http://cocodataset.org', 'version': '1.0', 'year': 2017, 'contributor': 'COCO Consortium', 'date_created': '2017/09/01'}
        :param licenses          [{'url': 'http://creativecommons.org/licenses/by-nc-sa/2.0/', 'id': 1, 'name': 'Attribution-NonCommercial-ShareAlike License'}, {'url': 'http://creativecommons.org/licenses/by-nc/2.0/', 'id': 2, 'name': 'Attribution-NonCommercial License'}, {'url': 'http://creativecommons.org/licenses/by-nc-nd/2.0/', 'id': 3, 'name': 'Attribution-NonCommercial-NoDerivs License'}, {'url': 'http://creativecommons.org/licenses/by/2.0/', 'id': 4, 'name': 'Attribution License'}, {'url': 'http://creativecommons.org/licenses/by-sa/2.0/', 'id': 5, 'name': 'Attribution-ShareAlike License'}, {'url': 'http://creativecommons.org/licenses/by-nd/2.0/', 'id': 6, 'name': 'Attribution-NoDerivs License'}, {'url': 'http://flickr.com/commons/usage/', 'id': 7, 'name': 'No known copyright restrictions'}, {'url': 'http://www.usa.gov/copyright.shtml', 'id': 8, 'name': 'United States Government Work'}]
        :param images[0]    {'license': 3, 'file_name': '000000391895.jpg', 'coco_url': 'http://images.cocodataset.org/train2017/000000391895.jpg', 'height': 360, 'width': 640, 'date_captured': '2013-11-14 11:18:45', 'flickr_url': 'http://farm9.staticflickr.com/8186/8119368305_4e622c8349_z.jpg', 'id': 391895}
        :param annotations[0]      {'segmentation': [[267.03, 243.78, 314.59, 154.05, 357.84, 136.76, 374.05, 104.32, 410.81, 110.81, 429.19, 131.35, 420.54, 165.95, 451.89, 209.19, 464.86, 240.54, 480, 253.51, 484.32, 263.24, 496.22, 271.89, 484.32, 278.38, 438.92, 257.84, 401.08, 216.76, 370.81, 247.03, 414.05, 277.3, 433.51, 304.32, 443.24, 323.78, 400, 362.7, 376.22, 375.68, 400, 418.92, 394.59, 424.32, 337.3, 382.16, 337.3, 371.35, 388.11, 327.03, 341.62, 301.08, 311.35, 276.22, 304.86, 263.24, 294.05, 249.19]], 'num_keypoints': 8, 'area': 28292.08625, 'iscrowd': 0, 'keypoints': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 325, 160, 2, 398, 177, 2, 0, 0, 0, 437, 238, 2, 0, 0, 0, 477, 270, 2, 287, 255, 1, 339, 267, 2, 0, 0, 0, 423, 314, 2, 0, 0, 0, 355, 367, 2], 'image_id': 537548, 'bbox': [267.03, 104.32, 229.19, 320], 'category_id': 1, 'id': 183020}
                            dict_keys(['segmentation', 'num_keypoints', 'area', 'iscrowd', 'keypoints', 'image_id', 'bbox', 'category_id', 'id'])
        :param categories          [{'supercategory': 'person', 'id': 1, 'name': 'person', 'keypoints': ['nose', 'left_eye', 'right_eye', 'left_ear', 'right_ear', 'left_shoulder', 'right_shoulder', 'left_elbow', 'right_elbow', 'left_wrist', 'right_wrist', 'left_hip', 'right_hip', 'left_knee', 'right_knee', 'left_ankle', 'right_ankle'], 'skeleton': [[16, 14], [14, 12], [17, 15], [15, 13], [12, 13], [6, 12], [7, 13], [6, 7], [6, 8], [7, 9], [8, 10], [9, 11], [2, 3], [1, 2], [1, 3], [2, 4], [3, 5], [4, 6], [5, 7]]}]
        '''
        info = data['info']
        lic = data['licenses']
        images = data['images']
        anno = data['annotations']
        cat = data['categories']
        print(cat)

    @staticmethod
    def readAnnotation(jsonfile, only_key=True):
        with open(jsonfile, "r") as f:
            info = json.load(f)
            if only_key:
                print(info.keys())
            else:
                print(info)
        return info

    @staticmethod
    def createCategory(label_root_folder, output_folder):
        """
        read all label_count.json which created by self.seperateByCounts
        :param return list
        [
            {
                supercategory   : CAT or DOG,
                id              : 0,
                name            : breed (ex. maltiz)
                keypoints       : ["nose", ...]
                skeleton        : [[0,2], ...]
            }, ...
        ]
        """
        check = []
        categories = []
        cat_id = 0
        cat_dict = {'breed':{"CAT":{},"DOG":{}}, 'id':{}}
        for label in sorted(os.listdir(label_root_folder)):
            if label.split(".")[0][-5:] != "count":
                continue
            filename = joinpath(label_root_folder, label)
            if not isExisted(filename):
                raise FileNotFoundError
            with open(filename, "r") as f:
                data = json.load(f)
                for supercategory in data:
                    if supercategory == "total":
                        continue
                    breeds = data[supercategory].keys()
                    for breed in breeds:
                        if not breed in check:
                            category = {}
                            category['supercategory'] = supercategory
                            category['id'] = cat_id
                            category['name'] = SPECIES[breed]
                            category['keypoints'] = KEY_NAME
                            category['skeleton'] = SKELETON
                            categories.append(category)

                            cat_dict['breed'][supercategory][SPECIES[breed]] = cat_id
                            cat_dict['id'][cat_id] = {"supercategory":supercategory, 'breed' : SPECIES[breed]}

                            check.append(breed)
                            cat_id += 1

        cat_main_file = joinpath(output_folder, "aihub_categories.json")
        cat_id_file = joinpath(output_folder, "aihub_category_index.json")
        with open(cat_main_file, "w") as f:
            json.dump(categories, f)
        with open(cat_id_file, "w") as f:
            json.dump(cat_dict, f)

    def seperateBySpecies(self, output_folder, count=True):
        annos = {}
        folder_name = self.source.split("/")[-1]
        for anno in sorted(os.listdir(self.source)):
            filename = os.path.join(self.source, anno)
            with open(filename, "r") as f:
                info = json.load(f)
                species = info['metadata']['species']
                breed = info['metadata']['animal']['breed']

                breed_dict = annos.get(species, {})
                filename_list = breed_dict.get(breed, [])
                filename_list.append(os.path.join(folder_name, anno))
                breed_dict[breed] = filename_list
                annos[species] = breed_dict

        file_out = joinpath(output_folder, f'{folder_name}_species.json')

        with open(file_out, "w", encoding="utf-8") as f:
            json.dump(annos, f)

        if count == True:
            self.seperateByCounts(file_out, output_folder)

    def seperateByCounts(self, jsonf, output_folder):
        """
        usage   -> after creating seperateBySpecies, use the json file with this param
        """

        with open(jsonf, "r") as f:
            info = json.load(f)
        cell = {}
        total = 0
        for spec in info:
            kind = {}
            for breed in info[spec]:
                count = len(info[spec][breed])
                total+=count
                kind[breed] = count
            cell[spec] = kind
            kind = sorted(kind.items(), key=lambda x:x[1])
        cell['total'] = total

        filename = os.path.join(output_folder, jsonf.split("/")[-1].split(".")[0]+"_count.json")
        with open(filename, "w") as f:
            json.dump(cell, f)
    





    def createCOCOFormat(self, source_folder, category_file, output_folder, config=False):
        """ :return 
                {
                    info
                    licenses
                    images
                    annotations
                    categories
                }
        """
        # config contained current highest image id from all file
        if config:
            img_id = int(config.img_id) + 1
            vid_id = int(config.vid_id) + 1
        else:
            img_id = 0
            vid_id = 0

        # load default setting
        info_coco = self.getInfo()
        lic_coco = self.getLicense()
        cat_coco = self.loadCategoryFile(category_file)
        
        if not self.cat:
            raise FileNotFoundError
        
        coco = {}

        images = []
        annotations = []
        videos = []

        for anno in sorted(os.listdir(source_folder)):
            filename = os.path.join(source_folder, anno)
            video_name = self._getVideoName(filename)
            video = {"vid_name": video_name, 'images': [], 'id': vid_id}
            with open(filename, "r") as f:  
                # :param data   ->  keys : [file_videos, metadata, annotations]
                data = json.load(f)
                meta = data['metadata']
                for frame in data['annotations']:
                    img_coco = self.createCOCOImageFormat(img_id, filename, frame, meta)
                    anno_coco = self.createCOCOAnnotationFormat(img_id, frame, meta)

                    images.append(img_coco)
                    annotations.append(anno_coco)
                    video['images'].append(img_coco['id'])

                    img_id += 1

            videos.append(video)
            vid_id += 1
            break
        coco['info'] = info_coco
        coco['licenses'] = lic_coco
        coco['images'] = images
        coco['annotations'] = annotations
        coco['categories'] = cat_coco
        coco['videos'] = videos

        print(coco.keys())
        
        return coco

    def getInfo(self):
        return {'description': 'AI Hub Dataset', 'url': 'https://aihub.or.kr/aidata/34146', 'version': '1.0', 'year': 2020}

    def getLicense(self):
        return [{'url': 'http://lifelibrary.synology.me', 'id': 0, 'name': 'Attribution-NonCommercial-ShareAlike License'}]

    def loadCategoryFile(self, category_file):
        with open(category_file, "r") as f:
            category = json.load(f)
        self.cat = category
        return category

    def createCOCOImageFormat(self, img_id, filename, frame, meta):
        license = 0
        video_src = "source_" + filename.split(".json")[0].split("/")[-2].split("_")[-1]
        video_name = filename.split(".json")[0].split("/")[-1]
        image_name = f"frame_{frame['frame_number']}_timestamp_{frame['timestamp']}.jpg"
        filename = joinpath(video_src, video_name, image_name)

        height = meta['height']
        width = meta['width']
        id = img_id

        img_coco = {
            'license': license,
            'file_name': filename,
            'height': height,
            'width': width,
            'id':id,
        }
        return img_coco

    def createCOCOAnnotationFormat(self, img_id, frame, meta):
        segmentation = []
        num_keypoints = 15
        area = 0
        iscrowd = 0
        keypoints, num_keypoints = self._alignSkeleton(frame['keypoints'])
        bbox = self._reformBbox(frame['bounding_box'])
        category_id = self._findCategoryId(SPECIES[meta['animal']['breed']])
        anno_coco = {
            "segmentation": segmentation,
            "num_keypoints": num_keypoints,
            "area": area,
            "iscrowd": iscrowd,
            "keypoints": keypoints,
            "image_id": img_id,
            "bbox": bbox,
            "category_id": category_id,
            "id": img_id
        }
        return anno_coco

    def _getVideoName(self, filename):
        # ./path/label_x/vid.mp4.json   =>  ./path/source_x/vid.mp4
        video_src = "source_" + filename.split(".json")[0].split("/")[-2].split("_")[-1]
        video_name = filename.split(".json")[0].split("/")[-1]
        video_name = joinpath(video_src, video_name)
        print(video_name)

    def _alignSkeleton(self, meta_keypoints):
        """
        :param return [x1, y1, v1, x2, y2, v2, ..., ]
        """
        keypoints = []
        num_keypoints = 0
        for i in range(15):
            coord = meta_keypoints[str(i+1)]
            if coord == None:
                keypoints.extend([0,0,0])
            else:
                keypoint = [coord['x'], coord['y'], 2]
                keypoints.extend(keypoint)
                num_keypoints += 1

        return keypoints, num_keypoints

    def _reformBbox(self, meta_bbox):
        """
        aihub bbox = [x, y, width, height] => (left_top = x,y)
        coco is same format
        """
        bbox = [meta_bbox['x'], meta_bbox['y'], meta_bbox['width'], meta_bbox['height']]
        return bbox

    def _findCategoryId(self, breed):
        for c in self.cat:
            if c['name'] == breed:
                return c['id']
        print("_findCategoryId, cannot find category id from self.cat")
        raise ValueError


        '''
        I think 17 kp
        :param meta         {'description': 'COCO 2017 Dataset', 'url': 'http://cocodataset.org', 'version': '1.0', 'year': 2017, 'contributor': 'COCO Consortium', 'date_created': '2017/09/01'}
        :param lic          [{'url': 'http://creativecommons.org/licenses/by-nc-sa/2.0/', 'id': 1, 'name': 'Attribution-NonCommercial-ShareAlike License'}, {'url': 'http://creativecommons.org/licenses/by-nc/2.0/', 'id': 2, 'name': 'Attribution-NonCommercial License'}, {'url': 'http://creativecommons.org/licenses/by-nc-nd/2.0/', 'id': 3, 'name': 'Attribution-NonCommercial-NoDerivs License'}, {'url': 'http://creativecommons.org/licenses/by/2.0/', 'id': 4, 'name': 'Attribution License'}, {'url': 'http://creativecommons.org/licenses/by-sa/2.0/', 'id': 5, 'name': 'Attribution-ShareAlike License'}, {'url': 'http://creativecommons.org/licenses/by-nd/2.0/', 'id': 6, 'name': 'Attribution-NoDerivs License'}, {'url': 'http://flickr.com/commons/usage/', 'id': 7, 'name': 'No known copyright restrictions'}, {'url': 'http://www.usa.gov/copyright.shtml', 'id': 8, 'name': 'United States Government Work'}]
        :param images[0]    {'license': 3, 'file_name': '000000391895.jpg', 'coco_url': 'http://images.cocodataset.org/train2017/000000391895.jpg', 'height': 360, 'width': 640, 'date_captured': '2013-11-14 11:18:45', 'flickr_url': 'http://farm9.staticflickr.com/8186/8119368305_4e622c8349_z.jpg', 'id': 391895}
        :param anno[0]      {'segmentation': [[267.03, 243.78, 314.59, 154.05, 357.84, 136.76, 374.05, 104.32, 410.81, 110.81, 429.19, 131.35, 420.54, 165.95, 451.89, 209.19, 464.86, 240.54, 480, 253.51, 484.32, 263.24, 496.22, 271.89, 484.32, 278.38, 438.92, 257.84, 401.08, 216.76, 370.81, 247.03, 414.05, 277.3, 433.51, 304.32, 443.24, 323.78, 400, 362.7, 376.22, 375.68, 400, 418.92, 394.59, 424.32, 337.3, 382.16, 337.3, 371.35, 388.11, 327.03, 341.62, 301.08, 311.35, 276.22, 304.86, 263.24, 294.05, 249.19]], 'num_keypoints': 8, 'area': 28292.08625, 'iscrowd': 0, 'keypoints': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 325, 160, 2, 398, 177, 2, 0, 0, 0, 437, 238, 2, 0, 0, 0, 477, 270, 2, 287, 255, 1, 339, 267, 2, 0, 0, 0, 423, 314, 2, 0, 0, 0, 355, 367, 2], 'image_id': 537548, 'bbox': [267.03, 104.32, 229.19, 320], 'category_id': 1, 'id': 183020}
                            dict_keys(['segmentation', 'num_keypoints', 'area', 'iscrowd', 'keypoints', 'image_id', 'bbox', 'category_id', 'id'])
        :param cat          [{'supercategory': 'person', 'id': 1, 'name': 'person', 'keypoints': ['nose', 'left_eye', 'right_eye', 'left_ear', 'right_ear', 'left_shoulder', 'right_shoulder', 'left_elbow', 'right_elbow', 'left_wrist', 'right_wrist', 'left_hip', 'right_hip', 'left_knee', 'right_knee', 'left_ankle', 'right_ankle'], 'skeleton': [[16, 14], [14, 12], [17, 15], [15, 13], [12, 13], [6, 12], [7, 13], [6, 7], [6, 8], [7, 9], [8, 10], [9, 11], [2, 3], [1, 2], [1, 3], [2, 4], [3, 5], [4, 6], [5, 7]]}]
        
        '''
        # info = {'description': 'AI Hub Dataset', 'url': 'https://aihub.or.kr/aidata/34146', 'version': '1.0', 'year': 2020}
        # license = [{'url': 'http://creativecommons.org/licenses/by-nc-sa/2.0/', 'id': 0, 'name': 'Attribution-NonCommercial-ShareAlike License'}, {'url': 'http://creativecommons.org/licenses/by-nc/2.0/', 'id': 2, 'name': 'Attribution-NonCommercial License'}]
        # images = data['images']
        # anno = data['annotations']
        # cat = data['categories']


SRC_VID = "/Users/song-yunsang/Desktop/Business/Butler/Dataset/test/aihub/source_9"
SRC_LABEL = "/Users/song-yunsang/Desktop/Business/Butler/Dataset/test/aihub/label_9"
OUTPUT = "/Users/song-yunsang/Desktop/Business/Butler/Dataset/test/aihub/custom_label"

label_root = "/Users/song-yunsang/Desktop/Business/Butler/Dataset/test/aihub/custom_label/custom_label"
label_output = joinpath(label_root, "aihub_coco")

coco = "/Users/song-yunsang/Desktop/Business/Butler/Develop/Dataset/coco/val2017/annotations/person_keypoints_val2017.json"

kp = AIHubDataset(label_root)
kp.createCOCOFormat(SRC_LABEL, label_root+"/aihub_categories.json", label_root)

# co = AIHubDataset.readAnnotation(coco)