# from lib.dataset.aihub import AIHubDataset
# from lib.core.config import config
import matplotlib.pyplot as plt

# aihub = AIHubDataset(config, "/Users/song-yunsang/Desktop/Business/Butler/Dataset/test/aihub", False, debug=True)
# sample = aihub[3]
# img = sample['images'][0]
# kp = sample['keypoints'][0]
# img = '/Users/song-yunsang/Desktop/Business/Butler/Dataset/test/aihub/source_9/20201024_cat-footpush-000053.mp4/frame_288_timestamp_4800.jpg'
# img = plt.imread(img)
# plt.imshow(img)

# plt.show()


path1 = "/Users/song-yunsang/Desktop/Business/Butler/Dataset/test/aihub/CustomSet/coco/Aihub_COCO_1.json"
path2 = "/Users/song-yunsang/Desktop/Business/Butler/Dataset/test/aihub/CustomSet/coco/Aihub_COCO_2.json"
path3 = "/Users/song-yunsang/Desktop/Business/Butler/Dataset/test/aihub/CustomSet/coco/Aihub_COCO_3.json"
import json
with open(path1, "r") as f:
    a = json.load(f)

with open(path2, "r") as f:
    b = json.load(f)

with open(path3, "r") as f:
    c = json.load(f)
print(len(a['images']))
print(len(b['images']))
print(len(c['images']))

