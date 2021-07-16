# -*- coding: utf-8 -*-
import os
import json

from os.path import join as joinpath
from os.path import exists as isExisted
from os.path import abspath as abspath

from aihub_config import KEY_NAME, SKELETON, SPECIES, INFO, LICENSES, CATEGORY_FILE

class AIHubDataset():

    def __init__(self):
        self.cat = None

    def createCategory(self, label_root_folder, output_folder):
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

        return cat_main_file, cat_id_file

    def seperateBySpecies(self, source_folder, output_folder, count=True):
        annos = {}
        folder_name = source_folder.split("/")[-1]
        for anno in sorted(os.listdir(source_folder)):
            filename = joinpath(source_folder, anno)
            with open(filename, "r") as f:
                info = json.load(f)
                species = info['metadata']['species']
                breed = info['metadata']['animal']['breed']

                breed_dict = annos.get(species, {})
                filename_list = breed_dict.get(breed, [])
                filename_list.append(joinpath(folder_name, anno))
                breed_dict[breed] = filename_list
                annos[species] = breed_dict

        file_out = joinpath(output_folder, f'{folder_name}_species.json')

        with open(file_out, "w", encoding="utf-8") as f:
            json.dump(annos, f)

        if count == True:
            self.seperateByCounts(file_out, output_folder)
        
        return file_out

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

        filename = joinpath(output_folder, jsonf.split("/")[-1].split(".")[0]+"_count.json")
        with open(filename, "w") as f:
            json.dump(cell, f)
        
        return filename
    





    def convertToCOCO(self, source_folder, category_file, output_folder, config_file=False):
        """ 
        :param source_folder : ./path/Dataset/label_x
        :param category_file : ./path/Dataset/aihub_categories.json
        :param output_folder : ./path/Dataset/
        :param config        : ./path/Dataset/aihub_config.py
        :return 
            {
                info:           {'description': 'AI Hub Dataset', 'url': 'https://aihub.or.kr/aidata/34146', 'version': '1.0', 'year': 2020}
                licenses:       [{'url': 'http://lifelibrary.synology.me', 'id': 0, 'name': 'Attribution-NonCommercial-ShareAlike License'}]
                images:         [{license: int, file_name: str, height: int, width: int, id: int,}, ...]
                annotations:    [{segmentation: [], num_keypoints: int, area: int, iscrowd: int, keypoints: [15x3], image_id: int, bbox: [4x1], category_id: int, id: int}]
                categories:     
                videos:         
            }
        """
        # config contained current img_id, vid_id, process
        if config_file:
            img_id, vid_id, process = self._loadConfig(config_file)
            if source_folder.split("/")[-1] in process:
                print("already existed on config.json")
                return 
        else:
            img_id, vid_id, process = 0, 0, []

        # load default setting
        info_coco = INFO
        lic_coco = LICENSES
        cat_coco = self.loadCategoryFile()
        
        if not self.cat:
            raise FileNotFoundError
        
        coco = {}
        coco_id = source_folder.split("/")[-1][-1]

        images = []
        annotations = []
        videos = []

        # iterate json file from folder 
        for anno in sorted(os.listdir(source_folder)):
            filename = joinpath(source_folder, anno)
            # video_name : /source_x/vid.mp4
            video_name = self._getVideoName(filename)                                   
            video = {"vid_name": video_name, 'images': [], 'id': vid_id}
            with open(filename, "r") as f:  
                # :param data   ->  keys : [file_videos, metadata, annotations]
                data = json.load(f)
                meta = data['metadata']
                for frame in data['annotations']:
                    img_coco = self.createCOCOImageFormat(img_id, vid_id, filename, frame, meta)
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

        output_file = joinpath(output_folder, f"Aihub_COCO_{coco_id}.json")
        with open(output_file, "w") as f:
            json.dump(coco, f)

        self._updateConfig(config_file, source_folder, img_id, vid_id, process)

        return coco

    def loadCategoryFile(self):
        try:
            with open(CATEGORY_FILE, "r") as f:
                category = json.load(f)
            self.cat = category
            return category
        except:
            print("loadCategoryFile, cannot read CATEGORY FILE, plz check aihub_config.py")
            raise ValueError
    


    def createCOCOImageFormat(self, img_id, vid_id, filename, frame, meta):
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
            'vid_id':vid_id
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
    
    def _loadConfig(config_file):
        with open(config_file, "r") as f:
            config = json.load(f)
        try:
            img_id = int(config['img_id']) + 1
            vid_id = int(config['vid_id']) + 1
            process = config['process']
        except:
            print("config file is not properly constructed")
            raise ValueError
            img_id, vid_id, process = 0, 0, []
        return img_id, vid_id, process
    
    def _updateConfig(self, config_file, source_folder, img_id, vid_id, process):
        label = source_folder.split("/")[-1]
        process.append(label)
        config = {
            'img_id': img_id,
            'vid_id': vid_id,
            'process': process
        }
        with open(config_file, "w") as f:
            json.dump(config, f)


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

if __file__ == "__main__":
    SRC_LABEL = "/Users/song-yunsang/Desktop/Business/Butler/Dataset/test/aihub/label_9"
    OUTPUT = "/Users/song-yunsang/Desktop/Business/Butler/Dataset/test/aihub/CustomSet"
    dataset = AIHubDataset()

    print("Start Seperating")
    dataset.seperateBySpecies(SRC_LABEL, OUTPUT)
    print("Seperated Done")
    
    print("-"*20)
    
    # print("Start Categorizing")
    # dataset.createCategory(SRC_LABEL, OUTPUT)
    # print("Categorizing Done")

    # print("-"*20)
    # dataset.convertToCOCO()




# SRC_VID = "/Users/song-yunsang/Desktop/Business/Butler/Dataset/test/aihub/source_9"
# label_root = "/Users/song-yunsang/Desktop/Business/Butler/Dataset/test/aihub/"
# label_output = joinpath(label_root, "aihub_coco")

# coco = "/Users/song-yunsang/Desktop/Business/Butler/Develop/Dataset/coco/val2017/annotations/person_keypoints_val2017.json"

# kp = AIHubDataset(label_root)
# kp.convertToCOCO(SRC_LABEL, label_root+"/aihub_categories.json", label_root)

# # co = AIHubDataset.readAnnotation(coco)